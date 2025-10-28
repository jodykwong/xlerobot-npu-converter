"""
ONNX Model Loader

Provides unified interface for loading ONNX models from multiple sources:
- Local file loading (.onnx files)
- Memory object loading (ModelProto objects)
- URL remote loading (HTTP/HTTPS downloads)
- Batch loading for multiple models
"""

import logging
import hashlib
from pathlib import Path
from typing import List, Union, Optional, Any
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
import requests

import onnx
from onnx import ModelProto

from ..core.interfaces.base_converter import BaseConverter
from ..models.conversion_model import ConversionModel
from ..models.config_model import ConfigModel
from ..models.progress_model import ProgressModel
from ..models.result_model import ResultModel
from ..interfaces.validator import ValidationResult
from ..models.onnx_model import ONNXModel, TensorInfo, OperatorInfo, VersionInfo, ModelMetadata
from .metadata_extractor import ModelMetadataExtractor
from ..utils.error_handler import ErrorHandler
from ..utils.progress_tracker import ProgressTracker

logger = logging.getLogger(__name__)


class ONNXModelLoader(BaseConverter):
    """
    Unified ONNX model loader supporting multiple input sources.

    This class extends BaseConverter to provide ONNX-specific loading
    capabilities while maintaining compatibility with the converter framework.
    """

    def __init__(self, config: Optional[ConfigModel] = None) -> None:
        """
        Initialize the ONNX model loader.

        Args:
            config: Optional configuration for the loader
        """
        super().__init__(
            name="ONNXModelLoader",
            version="1.0.0",
            config=config
        )
        self.metadata_extractor = ModelMetadataExtractor()
        self.error_handler = ErrorHandler()
        self.progress_tracker = ProgressTracker("ONNXLoader")

        logger.info(f"Initialized {self.name} v{self.version}")

    def load_from_file(self, model_path: Union[str, Path]) -> ONNXModel:
        """
        Load ONNX model from a local file.

        Args:
            model_path: Path to the .onnx file

        Returns:
            ONNXModel instance with loaded model and metadata

        Raises:
            ConversionError: If loading fails
        """
        self.status = "loading_file"
        model_path = Path(model_path)

        logger.info(f"Loading ONNX model from file: {model_path}")

        try:
            # Validate file exists
            if not model_path.exists():
                raise FileNotFoundError(f"Model file not found: {model_path}")

            if not model_path.suffix.lower() == ".onnx":
                raise ValueError(f"Invalid file extension: {model_path.suffix}. Expected .onnx")

            # Load model
            model_proto = onnx.load(str(model_path))

            # Create ONNXModel instance
            onnx_model = ONNXModel(
                model_proto=model_proto,
                model_path=model_path,
                raw_size=model_path.stat().st_size,
                loaded_at=datetime.now()
            )

            # Extract metadata
            self._extract_all_metadata(onnx_model)

            self.status = "loaded"
            logger.info(f"Successfully loaded model: {onnx_model}")
            return onnx_model

        except Exception as e:
            self.status = "error"
            error_msg = f"Failed to load model from file {model_path}: {e}"
            logger.error(error_msg)
            raise self.error_handler.handle_error(e, {"source": "file", "path": str(model_path)})

    def load_from_object(self, model_proto: ModelProto) -> ONNXModel:
        """
        Load ONNX model from a ModelProto object.

        Args:
            model_proto: ONNX ModelProto object

        Returns:
            ONNXModel instance with loaded model and metadata

        Raises:
            ConversionError: If loading fails
        """
        self.status = "loading_object"
        logger.info("Loading ONNX model from ModelProto object")

        try:
            if not isinstance(model_proto, ModelProto):
                raise TypeError(f"Expected ModelProto, got {type(model_proto)}")

            # Create ONNXModel instance
            onnx_model = ONNXModel(
                model_proto=model_proto,
                model_path=None,
                raw_size=model_proto.ByteSize(),
                loaded_at=datetime.now()
            )

            # Extract metadata
            self._extract_all_metadata(onnx_model)

            self.status = "loaded"
            logger.info(f"Successfully loaded model from object: {onnx_model}")
            return onnx_model

        except Exception as e:
            self.status = "error"
            error_msg = f"Failed to load model from object: {e}"
            logger.error(error_msg)
            raise self.error_handler.handle_error(e, {"source": "object"})

    def load_from_url(self, url: str, cache_dir: Optional[Path] = None) -> ONNXModel:
        """
        Load ONNX model from a remote URL.

        Args:
            url: URL to download the model from
            cache_dir: Optional directory to cache downloaded models

        Returns:
            ONNXModel instance with loaded model and metadata

        Raises:
            ConversionError: If loading fails
        """
        self.status = "loading_url"
        logger.info(f"Loading ONNX model from URL: {url}")

        try:
            # Validate URL
            if not url.startswith(('http://', 'https://')):
                raise ValueError(f"Invalid URL protocol. Expected http:// or https://, got {url}")

            # Determine cache path
            if cache_dir is None:
                cache_dir = Path.home() / ".cache" / "xlerobot" / "models"

            cache_dir.mkdir(parents=True, exist_ok=True)

            # Generate cache filename from URL hash
            url_hash = hashlib.md5(url.encode()).hexdigest()
            cache_path = cache_dir / f"{url_hash}.onnx"

            # Download if not cached or force refresh
            if not cache_path.exists():
                logger.info(f"Downloading model from {url}")
                response = requests.get(url, timeout=300)
                response.raise_for_status()

                with open(cache_path, 'wb') as f:
                    f.write(response.content)
                logger.info(f"Model cached to {cache_path}")
            else:
                logger.info(f"Using cached model from {cache_path}")

            # Load from cached file
            onnx_model = self.load_from_file(cache_path)
            onnx_model.model_path = Path(url)  # Keep original URL as path

            self.status = "loaded"
            logger.info(f"Successfully loaded model from URL: {url}")
            return onnx_model

        except Exception as e:
            self.status = "error"
            error_msg = f"Failed to load model from URL {url}: {e}"
            logger.error(error_msg)
            raise self.error_handler.handle_error(e, {"source": "url", "url": url})

    def batch_load(self, model_sources: List[Union[str, Path, ModelProto]]) -> List[ONNXModel]:
        """
        Load multiple ONNX models concurrently.

        Args:
            model_sources: List of model sources (paths, URLs, or ModelProto objects)

        Returns:
            List of ONNXModel instances

        Raises:
            ConversionError: If batch loading fails
        """
        self.status = "batch_loading"
        logger.info(f"Starting batch loading of {len(model_sources)} models")

        try:
            loaded_models = []
            max_workers = min(len(model_sources), 10)  # Limit concurrent connections

            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                # Submit all loading tasks
                future_to_source = {
                    executor.submit(self._load_single_model, source): source
                    for source in model_sources
                }

                # Collect results as they complete
                for future in as_completed(future_to_source):
                    source = future_to_source[future]
                    try:
                        model = future.result()
                        loaded_models.append(model)
                        logger.info(f"Loaded model from source: {source}")
                    except Exception as e:
                        logger.error(f"Failed to load model from source {source}: {e}")
                        # Continue loading other models

            logger.info(f"Batch loading completed. Loaded {len(loaded_models)}/{len(model_sources)} models")
            return loaded_models

        except Exception as e:
            self.status = "error"
            error_msg = f"Batch loading failed: {e}"
            logger.error(error_msg)
            raise self.error_handler.handle_error(e, {"source": "batch", "count": len(model_sources)})

    def validate_model(self, model: ONNXModel) -> ValidationResult:
        """
        Validate an ONNX model for compatibility and correctness.

        Args:
            model: ONNXModel instance to validate

        Returns:
            ValidationResult containing validation results
        """
        self.status = "validating"
        logger.info(f"Validating model: {model}")

        try:
            # Check if model is loaded
            if not model.is_loaded:
                return ValidationResult(
                    is_valid=False,
                    errors=["Model is not loaded"],
                    warnings=[]
                )

            # Check metadata completeness
            warnings = []
            if not model.input_tensors:
                warnings.append("Model has no input tensors")
            if not model.output_tensors:
                warnings.append("Model has no output tensors")

            # Check model structure
            errors = []
            if model.operator_count == 0:
                errors.append("Model has no operators")

            # Check for common issues
            if model.has_operator("Loop"):
                warnings.append("Model contains Loop operators which may not be supported by all runtimes")

            is_valid = len(errors) == 0

            result = ValidationResult(
                is_valid=is_valid,
                errors=errors,
                warnings=warnings
            )

            logger.info(f"Validation complete. Valid: {is_valid}, Errors: {len(errors)}, Warnings: {len(warnings)}")
            return result

        except Exception as e:
            logger.error(f"Validation failed: {e}")
            return ValidationResult(
                is_valid=False,
                errors=[f"Validation error: {e}"],
                warnings=[]
            )

    def _load_single_model(self, source: Union[str, Path, ModelProto]) -> ONNXModel:
        """Load a single model from various sources."""
        if isinstance(source, ModelProto):
            return self.load_from_object(source)
        elif isinstance(source, (str, Path)):
            source_str = str(source)
            if source_str.startswith(('http://', 'https://')):
                return self.load_from_url(source_str)
            else:
                return self.load_from_file(source)
        else:
            raise TypeError(f"Unsupported source type: {type(source)}")

    def _extract_all_metadata(self, model: ONNXModel) -> None:
        """Extract all metadata from a loaded model."""
        logger.info("Extracting metadata from loaded model")

        # Extract metadata
        model.metadata = self.metadata_extractor.extract_model_metadata(model)

        # Extract input tensors
        model.input_tensors = self.metadata_extractor.extract_input_tensors(model)

        # Extract output tensors
        model.output_tensors = self.metadata_extractor.extract_output_tensors(model)

        # Extract operators
        model.operators = self.metadata_extractor.extract_operators(model)

        # Extract version info
        model.version_info = self.metadata_extractor.extract_version_info(model)

        logger.info("Metadata extraction complete")

    # BaseConverter abstract methods implementation
    def validate_input(
        self,
        model_path: Union[str, Path],
        config: Optional[ConfigModel] = None
    ) -> ValidationResult:
        """Validate input model and configuration."""
        try:
            onnx_model = self.load_from_file(model_path)
            return self.validate_model(onnx_model)
        except Exception as e:
            return ValidationResult(
                is_valid=False,
                errors=[str(e)],
                warnings=[]
            )

    def prepare_conversion(
        self,
        model_path: Union[str, Path],
        config: Optional[ConfigModel] = None
    ) -> ConversionModel:
        """Prepare the conversion process."""
        onnx_model = self.load_from_file(model_path)
        return ConversionModel(
            input_path=Path(model_path),
            output_path=None,
            config=config or self.config,
            metadata={
                "model": onnx_model,
                "input_tensors": onnx_model.input_tensors,
                "output_tensors": onnx_model.output_tensors,
                "operators": onnx_model.operators
            }
        )

    def convert(
        self,
        conversion_model: ConversionModel,
        progress_callback: Optional[callable] = None
    ) -> ResultModel:
        """Execute the main conversion process."""
        # For loader, conversion is just loading and metadata extraction
        model = conversion_model.metadata.get("model")
        if not model:
            raise ValueError("Model not found in conversion metadata")

        return ResultModel(
            success=True,
            output_path=conversion_model.input_path,
            metadata=conversion_model.metadata
        )

    def export_results(
        self,
        result: ResultModel,
        output_path: Union[str, Path],
        format: str = "default"
    ) -> bool:
        """Export conversion results."""
        # Loader doesn't export results, just loading
        return True
