"""
Batch Processor

Provides batch processing and concurrent loading capabilities:
- Batch preprocessing for multiple models
- Concurrent model loading
- Progress tracking and status callbacks
- Error handling and recovery mechanisms
"""

import logging
from typing import List, Dict, Any, Optional, Callable, Union
from concurrent.futures import ThreadPoolExecutor, as_completed, Future
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
import numpy as np

from .pipeline import PreprocessingPipeline, PreprocessingConfig
from ..loaders.onnx_loader import ONNXModelLoader
from ..models.onnx_model import ONNXModel, TensorInfo
from ..validation.compatibility import CompatibilityChecker, FullCompatibilityResult
from ..utils.progress_tracker import ProgressTracker
from ..utils.error_handler import ErrorHandler

logger = logging.getLogger(__name__)


class ProcessingStatus(Enum):
    """Processing status enumeration."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class BatchItem:
    """Individual item in a batch processing job."""
    id: str
    source: Union[str, Path, Any]  # Model source (file, URL, or object)
    status: ProcessingStatus = ProcessingStatus.PENDING
    result: Optional[ONNXModel] = None
    error: Optional[str] = None
    start_time: Optional[float] = None
    end_time: Optional[float] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def duration(self) -> Optional[float]:
        """Get processing duration in seconds."""
        if self.start_time and self.end_time:
            return self.end_time - self.start_time
        return None


@dataclass
class BatchResult:
    """Result of batch processing operation."""
    total_items: int
    successful_items: int
    failed_items: int
    items: List[BatchItem]
    start_time: float
    end_time: float
    processing_time: float
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)

    @property
    def success_rate(self) -> float:
        """Get success rate as percentage."""
        if self.total_items == 0:
            return 0.0
        return (self.successful_items / self.total_items) * 100.0

    @property
    def average_processing_time(self) -> float:
        """Get average processing time per item."""
        if self.successful_items == 0:
            return 0.0
        return self.processing_time / self.successful_items


class BatchProcessor:
    """
    Batch processor for ONNX models with concurrent loading and preprocessing.

    This class provides efficient batch processing capabilities for multiple
    ONNX models, with progress tracking and error recovery.
    """

    def __init__(
        self,
        max_workers: int = 10,
        loader: Optional[ONNXModelLoader] = None,
        preprocessor: Optional[PreprocessingPipeline] = None,
        compatibility_checker: Optional[CompatibilityChecker] = None
    ) -> None:
        """
        Initialize the batch processor.

        Args:
            max_workers: Maximum number of concurrent workers
            loader: ONNXModelLoader instance (creates new if None)
            preprocessor: PreprocessingPipeline instance (creates new if None)
            compatibility_checker: CompatibilityChecker instance (creates new if None)
        """
        self.max_workers = max(1, max_workers)
        self.loader = loader or ONNXModelLoader()
        self.preprocessor = preprocessor or PreprocessingPipeline()
        self.compatibility_checker = compatibility_checker or CompatibilityChecker()
        self.progress_tracker = ProgressTracker("BatchProcessor")
        self.error_handler = ErrorHandler()

        logger.info(f"Initialized BatchProcessor with {self.max_workers} workers")

    def batch_load(
        self,
        sources: List[Union[str, Path, Any]],
        progress_callback: Optional[Callable[[int, int], None]] = None,
        status_callback: Optional[Callable[[str, ProcessingStatus], None]] = None
    ) -> BatchResult:
        """
        Load multiple ONNX models concurrently.

        Args:
            sources: List of model sources
            progress_callback: Optional callback for progress updates (completed, total)
            status_callback: Optional callback for status updates (item_id, status)

        Returns:
            BatchResult with loading results
        """
        logger.info(f"Starting batch loading of {len(sources)} models")

        # Initialize batch items
        items = [
            BatchItem(id=f"item_{i}", source=source)
            for i, source in enumerate(sources)
        ]

        start_time = self.progress_tracker.get_timestamp()

        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all loading tasks
            future_to_item = {
                executor.submit(self._load_single_model, item): item
                for item in items
            }

            completed = 0
            successful = 0

            # Process completed futures
            for future in as_completed(future_to_item):
                item = future_to_item[future]
                item.end_time = self.progress_tracker.get_timestamp()

                try:
                    result = future.result()
                    item.result = result
                    item.status = ProcessingStatus.COMPLETED
                    successful += 1
                    logger.debug(f"Successfully loaded model: {item.id}")

                except Exception as e:
                    item.error = str(e)
                    item.status = ProcessingStatus.FAILED
                    logger.error(f"Failed to load model {item.id}: {e}")

                finally:
                    completed += 1

                    # Update progress
                    if progress_callback:
                        progress_callback(completed, len(items))

                    # Update status
                    if status_callback:
                        status_callback(item.id, item.status)

        end_time = self.progress_tracker.get_timestamp()

        result = BatchResult(
            total_items=len(sources),
            successful_items=successful,
            failed_items=len(sources) - successful,
            items=items,
            start_time=start_time,
            end_time=end_time,
            processing_time=end_time - start_time
        )

        logger.info(f"Batch loading complete: {result.success_rate:.1f}% success rate")
        return result

    def batch_preprocess(
        self,
        models: List[ONNXModel],
        configs: Optional[List[PreprocessingConfig]] = None,
        progress_callback: Optional[Callable[[int, int], None]] = None,
        status_callback: Optional[Callable[[str, ProcessingStatus], None]] = None
    ) -> BatchResult:
        """
        Preprocess multiple ONNX models concurrently.

        Args:
            models: List of loaded ONNX models
            configs: Optional list of preprocessing configs (uses default if None)
            progress_callback: Optional callback for progress updates
            status_callback: Optional callback for status updates

        Returns:
            BatchResult with preprocessing results
        """
        logger.info(f"Starting batch preprocessing of {len(models)} models")

        if configs is None:
            configs = [PreprocessingConfig() for _ in models]

        if len(configs) != len(models):
            raise ValueError("Number of configs must match number of models")

        # Initialize batch items
        items = [
            BatchItem(id=f"model_{i}", source=models[i])
            for i in range(len(models))
        ]

        start_time = self.progress_tracker.get_timestamp()

        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all preprocessing tasks
            future_to_item = {
                executor.submit(self._preprocess_single_model, item, configs[i]): item
                for i, item in enumerate(items)
            }

            completed = 0
            successful = 0

            # Process completed futures
            for future in as_completed(future_to_item):
                item = future_to_item[future]
                item.end_time = self.progress_tracker.get_timestamp()

                try:
                    # Update model with preprocessing metadata
                    future.result()
                    item.status = ProcessingStatus.COMPLETED
                    successful += 1
                    logger.debug(f"Successfully preprocessed model: {item.id}")

                except Exception as e:
                    item.error = str(e)
                    item.status = ProcessingStatus.FAILED
                    logger.error(f"Failed to preprocess model {item.id}: {e}")

                finally:
                    completed += 1

                    # Update progress
                    if progress_callback:
                        progress_callback(completed, len(items))

                    # Update status
                    if status_callback:
                        status_callback(item.id, item.status)

        end_time = self.progress_tracker.get_timestamp()

        result = BatchResult(
            total_items=len(models),
            successful_items=successful,
            failed_items=len(models) - successful,
            items=items,
            start_time=start_time,
            end_time=end_time,
            processing_time=end_time - start_time
        )

        logger.info(f"Batch preprocessing complete: {result.success_rate:.1f}% success rate")
        return result

    def batch_validate(
        self,
        models: List[ONNXModel],
        progress_callback: Optional[Callable[[int, int], None]] = None,
        status_callback: Optional[Callable[[str, ProcessingStatus], None]] = None
    ) -> List[Optional[FullCompatibilityResult]]:
        """
        Validate multiple ONNX models concurrently.

        Args:
            models: List of ONNX models to validate
            progress_callback: Optional callback for progress updates
            status_callback: Optional callback for status updates

        Returns:
            List of FullCompatibilityResult (None for failed validations)
        """
        logger.info(f"Starting batch validation of {len(models)} models")

        results: List[Optional[FullCompatibilityResult]] = []

        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all validation tasks
            future_to_index = {
                executor.submit(self._validate_single_model, model): i
                for i, model in enumerate(models)
            }

            completed = 0

            # Initialize results list
            results = [None] * len(models)

            # Process completed futures
            for future in as_completed(future_to_index):
                index = future_to_index[future]
                item_id = f"model_{index}"

                try:
                    result = future.result()
                    results[index] = result
                    logger.debug(f"Successfully validated model: {item_id}")

                except Exception as e:
                    logger.error(f"Failed to validate model {item_id}: {e}")
                    results[index] = None

                finally:
                    completed += 1

                    # Update progress
                    if progress_callback:
                        progress_callback(completed, len(models))

                    # Update status
                    if status_callback:
                        status_callback(item_id, ProcessingStatus.COMPLETED if results[index] else ProcessingStatus.FAILED)

        valid_count = sum(1 for r in results if r is not None)
        logger.info(f"Batch validation complete: {valid_count}/{len(models)} successful")
        return results

    def _load_single_model(self, item: BatchItem) -> ONNXModel:
        """Load a single model from a batch item."""
        item.start_time = self.progress_tracker.get_timestamp()
        item.status = ProcessingStatus.RUNNING

        if isinstance(item.source, (str, Path)):
            if str(item.source).startswith(('http://', 'https://')):
                return self.loader.load_from_url(item.source)
            else:
                return self.loader.load_from_file(item.source)
        else:
            # Assume it's a ModelProto object
            return self.loader.load_from_object(item.source)

    def _preprocess_single_model(self, item: BatchItem, config: PreprocessingConfig) -> None:
        """Preprocess a single model from a batch item."""
        item.start_time = self.progress_tracker.get_timestamp()
        item.status = ProcessingStatus.RUNNING

        model = item.result
        if not model:
            raise ValueError(f"No model result found for item {item.id}")

        # Update preprocessing metadata
        model.metadata.description = f"Preprocessed with config: {config.normalize_mode}"
        item.metadata["preprocessing_config"] = config

    def _validate_single_model(self, model: ONNXModel) -> FullCompatibilityResult:
        """Validate a single model."""
        return self.compatibility_checker.full_compatibility_check(model)

    def get_processing_stats(self, result: BatchResult) -> Dict[str, Any]:
        """
        Get processing statistics from a batch result.

        Args:
            result: BatchResult to analyze

        Returns:
            Dictionary with processing statistics
        """
        durations = [item.duration for item in result.items if item.duration is not None]

        return {
            "total_items": result.total_items,
            "successful_items": result.successful_items,
            "failed_items": result.failed_items,
            "success_rate": result.success_rate,
            "total_processing_time": result.processing_time,
            "average_processing_time": result.average_processing_time,
            "min_processing_time": min(durations) if durations else 0.0,
            "max_processing_time": max(durations) if durations else 0.0,
            "total_errors": len(result.errors),
            "total_warnings": len(result.warnings)
        }
