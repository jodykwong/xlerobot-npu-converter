#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
模型精度验证系统 - 批量验证管理器
=====================================

这是Story 2.7: 模型精度验证系统的批量验证组件。

功能特性:
- 多模型批量验证
- 并发验证处理
- 进度跟踪
- 汇总报告生成

作者: Claude Code / BMM Method
创建: 2025-10-28
版本: 1.0.0

BMM v6 Phase 2: 核心功能实现
"""

import asyncio
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Callable
from dataclasses import dataclass, field
from collections import defaultdict

from npu_converter.core.models.result_model import ValidationResult, ValidationStatus
from npu_converter.core.models.progress_model import ProgressModel, ProgressType
from npu_converter.logging.logger import ConversionLogger
from npu_converter.complete_flows.model_validator import ModelValidator, ValidationConfig


logger = ConversionLogger(__name__)


@dataclass
class BatchValidationTask:
    """批量验证任务"""
    model_path: str
    model_name: str
    model_type: str
    priority: int = 0  # 0=normal, 1=high
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class BatchValidationResult:
    """批量验证结果"""
    batch_id: str
    timestamp: datetime
    total_models: int
    passed_models: int
    failed_models: int
    warning_models: int
    results: List[ValidationResult]
    summary: Dict[str, Any]


class BatchValidator:
    """
    批量模型验证管理器

    支持多模型并发验证，提供进度跟踪和汇总报告。
    """

    def __init__(
        self,
        config: ValidationConfig,
        max_workers: int = 4,
        progress_callback: Optional[Callable[[ProgressModel], None]] = None
    ):
        """
        初始化批量验证器

        Args:
            config: 验证配置
            max_workers: 最大并发工作线程数
            progress_callback: 进度回调函数
        """
        self.config = config
        self.max_workers = max_workers
        self.progress_callback = progress_callback

        # 批量验证记录
        self.batch_history: List[BatchValidationResult] = []
        self.active_batches: Dict[str, BatchValidationResult] = {}

        self.logger = logger

        self.logger.info("批量验证器已初始化", extra={
            'max_workers': max_workers
        })

    async def validate_batch(
        self,
        tasks: List[BatchValidationTask],
        batch_name: Optional[str] = None
    ) -> BatchValidationResult:
        """
        执行批量验证

        Args:
            tasks: 验证任务列表
            batch_name: 批量名称

        Returns:
            BatchValidationResult: 批量验证结果
        """
        batch_id = batch_name or f"batch_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        self.logger.info(f"开始批量验证: {batch_id}", extra={
            'model_count': len(tasks),
            'batch_id': batch_id
        })

        # 创建验证器实例
        validator = ModelValidator(
            config=self.config,
            progress_callback=self._create_progress_callback(batch_id)
        )

        # 按优先级排序
        sorted_tasks = sorted(tasks, key=lambda t: t.priority, reverse=True)

        # 创建批量结果
        batch_result = BatchValidationResult(
            batch_id=batch_id,
            timestamp=datetime.now(),
            total_models=len(sorted_tasks),
            passed_models=0,
            failed_models=0,
            warning_models=0,
            results=[],
            summary={}
        )

        # 记录活动批次
        self.active_batches[batch_id] = batch_result

        # 进度通知
        if self.progress_callback:
            self.progress_callback(ProgressModel(
                progress_type=ProgressType.VALIDATION_STARTED,
                message=f"开始批量验证: {batch_id} ({len(sorted_tasks)}个模型)",
                percent=0
            ))

        try:
            # 并发验证
            results = await self._validate_concurrent(
                validator, sorted_tasks, batch_id
            )

            # 收集结果
            batch_result.results = results

            # 统计结果
            for result in results:
                if result.status == ValidationStatus.PASSED:
                    batch_result.passed_models += 1
                elif result.status == ValidationStatus.FAILED:
                    batch_result.failed_models += 1
                else:
                    batch_result.warning_models += 1

            # 生成汇总
            batch_result.summary = await self._generate_summary(results)

            self.logger.info(f"批量验证完成: {batch_id}", extra={
                'total': batch_result.total_models,
                'passed': batch_result.passed_models,
                'failed': batch_result.failed_models,
                'success_rate': batch_result.passed_models / batch_result.total_models if batch_result.total_models > 0 else 0
            })

            # 添加到历史
            self.batch_history.append(batch_result)

            # 清理活动批次
            del self.active_batches[batch_id]

            # 进度通知
            if self.progress_callback:
                self.progress_callback(ProgressModel(
                    progress_type=ProgressType.VALIDATION_COMPLETED,
                    message=f"批量验证完成: {batch_result.passed_models}/{batch_result.total_models} 通过",
                    percent=100
                ))

            return batch_result

        except Exception as e:
            self.logger.error(f"批量验证失败: {batch_id}", error=e)
            # 从活动批次中移除
            if batch_id in self.active_batches:
                del self.active_batches[batch_id]
            raise

    async def _validate_concurrent(
        self,
        validator: ModelValidator,
        tasks: List[BatchValidationTask],
        batch_id: str
    ) -> List[ValidationResult]:
        """并发执行验证任务"""
        results = []

        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # 提交所有任务
            future_to_task = {
                executor.submit(
                    asyncio.run,
                    validator.validate_model(task.model_path, task.model_type)
                ): task
                for task in tasks
            }

            # 收集结果
            completed = 0
            for future in as_completed(future_to_task):
                task = future_to_task[future]
                try:
                    result = future.result()
                    results.append(result)
                    completed += 1

                    # 更新进度
                    progress_percent = int((completed / len(tasks)) * 100)
                    if self.progress_callback:
                        self.progress_callback(ProgressModel(
                            progress_type=ProgressType.VALIDATION_PROGRESS,
                            message=f"完成验证: {task.model_name} ({completed}/{len(tasks)})",
                            percent=progress_percent
                        ))

                except Exception as e:
                    self.logger.error(f"验证任务失败: {task.model_name}", error=e)
                    # 创建失败结果
                    results.append(ValidationResult(
                        model_path=task.model_path,
                        model_type=task.model_type,
                        status=ValidationStatus.FAILED,
                        error_message=str(e)
                    ))
                    completed += 1

        return results

    async def _generate_summary(self, results: List[ValidationResult]) -> Dict[str, Any]:
        """生成汇总信息"""
        if not results:
            return {}

        # 基础统计
        total = len(results)
        passed = sum(1 for r in results if r.status == ValidationStatus.PASSED)
        failed = sum(1 for r in results if r.status == ValidationStatus.FAILED)
        warnings = sum(1 for r in results if r.status == ValidationStatus.WARNING)

        # 精度统计
        valid_metrics = [r.metrics for r in results if r.metrics]
        if valid_metrics:
            avg_accuracy = sum(m.accuracy for m in valid_metrics) / len(valid_metrics)
            max_accuracy = max(m.accuracy for m in valid_metrics)
            min_accuracy = min(m.accuracy for m in valid_metrics)

            avg_inference_time = sum(m.inference_time for m in valid_metrics) / len(valid_metrics)
        else:
            avg_accuracy = max_accuracy = min_accuracy = 0.0
            avg_inference_time = 0.0

        # 按类型统计
        by_type = defaultdict(lambda: {'total': 0, 'passed': 0, 'failed': 0})
        for result in results:
            by_type[result.model_type]['total'] += 1
            if result.status == ValidationStatus.PASSED:
                by_type[result.model_type]['passed'] += 1
            elif result.status == ValidationStatus.FAILED:
                by_type[result.model_type]['failed'] += 1

        # 错误分析
        errors = {}
        for result in results:
            if result.error_message:
                error_type = result.error_message.split(':')[0]
                errors[error_type] = errors.get(error_type, 0) + 1

        return {
            'total_models': total,
            'passed_models': passed,
            'failed_models': failed,
            'warning_models': warnings,
            'success_rate': passed / total if total > 0 else 0,
            'accuracy_stats': {
                'avg_accuracy': avg_accuracy,
                'max_accuracy': max_accuracy,
                'min_accuracy': min_accuracy
            },
            'performance_stats': {
                'avg_inference_time': avg_inference_time
            },
            'by_model_type': dict(by_type),
            'error_analysis': errors,
            'validation_time': sum(r.validation_time for r in results if r.validation_time)
        }

    def _create_progress_callback(self, batch_id: str) -> Optional[Callable[[ProgressModel], None]]:
        """创建进度回调"""
        if not self.progress_callback:
            return None

        def callback(progress: ProgressModel):
            progress.batch_id = batch_id
            self.progress_callback(progress)

        return callback

    def get_batch_history(self) -> List[BatchValidationResult]:
        """获取批量验证历史"""
        return self.batch_history

    def get_active_batches(self) -> List[str]:
        """获取活动批次列表"""
        return list(self.active_batches.keys())

    async def cancel_batch(self, batch_id: str) -> bool:
        """
        取消批量验证

        Args:
            batch_id: 批次ID

        Returns:
            bool: 是否成功取消
        """
        if batch_id not in self.active_batches:
            self.logger.warning(f"批次不存在: {batch_id}")
            return False

        # TODO: 实现取消逻辑
        # - 停止工作线程
        # - 清理资源

        self.logger.info(f"批量验证已取消: {batch_id}")
        return True

    async def export_batch_report(
        self,
        batch_result: BatchValidationResult,
        output_path: str,
        format: str = 'json'
    ) -> str:
        """
        导出批量验证报告

        Args:
            batch_result: 批量验证结果
            output_path: 输出路径
            format: 输出格式

        Returns:
            str: 报告文件路径
        """
        from pathlib import Path
        import json

        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)

        # 准备报告数据
        report_data = {
            'batch_info': {
                'batch_id': batch_result.batch_id,
                'timestamp': batch_result.timestamp.isoformat(),
                'total_models': batch_result.total_models
            },
            'summary': batch_result.summary,
            'results': [
                {
                    'model_path': r.model_path,
                    'model_type': r.model_type,
                    'status': r.status.value,
                    'accuracy': r.metrics.accuracy if r.metrics else 0.0,
                    'validation_time': r.validation_time,
                    'error_message': r.error_message
                }
                for r in batch_result.results
            ]
        }

        # 保存报告
        if format == 'json':
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(report_data, f, indent=2, ensure_ascii=False)

        self.logger.info(f"批量验证报告已导出: {output_file}")
        return str(output_file)


async def progress_handler(progress: ProgressModel):
    """进度处理器示例"""
    print(f"  {progress.message} ({progress.percent}%)")


async def main():
    """主函数 - 示例用法"""
    # 创建配置
    config = ValidationConfig(
        accuracy_threshold=0.98,
        max_inference_time=30.0
    )

    # 创建批量验证器
    batch_validator = BatchValidator(
        config=config,
        max_workers=2,
        progress_callback=progress_handler
    )

    # 创建验证任务
    tasks = [
        BatchValidationTask(
            model_path="models/model1.onnx",
            model_name="model1",
            model_type="vits_cantonese",
            priority=1
        ),
        BatchValidationTask(
            model_path="models/model2.onnx",
            model_name="model2",
            model_type="sensevoice",
            priority=0
        ),
        BatchValidationTask(
            model_path="models/model3.onnx",
            model_name="model3",
            model_type="piper_vits",
            priority=0
        )
    ]

    # 执行批量验证
    result = await batch_validator.validate_batch(tasks, "test_batch")

    print(f"\n📊 批量验证结果:")
    print(f"   批次ID: {result.batch_id}")
    print(f"   总模型: {result.total_models}")
    print(f"   通过: {result.passed_models}")
    print(f"   失败: {result.failed_models}")
    print(f"   告警: {result.warning_models}")

    # 导出报告
    report_path = await batch_validator.export_batch_report(
        result,
        "reports/batch_validation.json"
    )
    print(f"\n📄 报告已导出: {report_path}")


if __name__ == "__main__":
    asyncio.run(main())
