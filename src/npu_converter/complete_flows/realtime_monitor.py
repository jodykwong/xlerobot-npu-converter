#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
模型精度验证系统 - 实时精度监控
=====================================

这是Story 2.7: 模型精度验证系统的实时监控组件。

功能特性:
- 实时精度指标监控
- 阈值越界告警
- 精度趋势分析
- 实时指标展示

作者: Claude Code / BMM Method
创建: 2025-10-28
版本: 1.0.0

BMM v6 Phase 2: 核心功能实现
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Callable
from dataclasses import dataclass, field
from collections import deque

from npu_converter.logging.logger import ConversionLogger


logger = ConversionLogger(__name__)


@dataclass
class MetricAlert:
    """指标告警"""
    metric_name: str
    current_value: float
    threshold_value: float
    severity: str  # info, warning, critical
    message: str
    timestamp: datetime
    model_name: str = ""


@dataclass
class RealtimeMetrics:
    """实时指标"""
    accuracy: float = 0.0
    precision: float = 0.0
    recall: float = 0.0
    f1_score: float = 0.0
    inference_time: float = 0.0
    throughput: float = 0.0
    memory_usage: float = 0.0
    timestamp: datetime = field(default_factory=datetime.now)


class RealtimeMonitor:
    """
    实时精度监控系统

    监控模型验证过程中的各项指标，提供实时告警和趋势分析。
    """

    def __init__(
        self,
        accuracy_threshold: float = 0.98,
        max_inference_time: float = 30.0,
        history_size: int = 100
    ):
        """
        初始化实时监控

        Args:
            accuracy_threshold: 精度阈值
            max_inference_time: 最大推理时间
            history_size: 历史数据保存大小
        """
        self.accuracy_threshold = accuracy_threshold
        self.max_inference_time = max_inference_time
        self.history_size = history_size

        # 指标历史
        self.metrics_history: deque = deque(maxlen=history_size)

        # 告警回调
        self.alert_callbacks: List[Callable[[MetricAlert], None]] = []

        # 当前监控状态
        self.is_monitoring = False
        self.current_metrics: Optional[RealtimeMetrics] = None

        self.logger = logger
        self.logger.info("实时监控系统已初始化", extra={
            'accuracy_threshold': accuracy_threshold,
            'max_inference_time': max_inference_time
        })

    def add_alert_callback(self, callback: Callable[[MetricAlert], None]):
        """
        添加告警回调

        Args:
            callback: 告警回调函数
        """
        self.alert_callbacks.append(callback)
        self.logger.debug("添加告警回调函数")

    async def start_monitoring(self, model_name: str = ""):
        """开始监控"""
        self.is_monitoring = True
        self.logger.info(f"开始实时监控: {model_name}")

    async def stop_monitoring(self):
        """停止监控"""
        self.is_monitoring = False
        self.logger.info("停止实时监控")

    async def update_metrics(
        self,
        metrics: RealtimeMetrics,
        model_name: str = ""
    ):
        """
        更新实时指标

        Args:
            metrics: 实时指标
            model_name: 模型名称
        """
        if not self.is_monitoring:
            return

        self.current_metrics = metrics

        # 添加到历史
        self.metrics_history.append(metrics)

        # 检查阈值告警
        await self._check_thresholds(metrics, model_name)

        self.logger.debug("更新实时指标", extra={
            'accuracy': metrics.accuracy,
            'inference_time': metrics.inference_time
        })

    async def _check_thresholds(
        self,
        metrics: RealtimeMetrics,
        model_name: str
    ):
        """检查阈值并触发告警"""
        alerts = []

        # 检查精度阈值
        if metrics.accuracy < self.accuracy_threshold:
            severity = 'critical' if metrics.accuracy < 0.95 else 'warning'
            alerts.append(MetricAlert(
                metric_name='accuracy',
                current_value=metrics.accuracy,
                threshold_value=self.accuracy_threshold,
                severity=severity,
                message=f"精度低于阈值: {metrics.accuracy:.2%} < {self.accuracy_threshold:.2%}",
                timestamp=datetime.now(),
                model_name=model_name
            ))

        # 检查推理时间阈值
        if metrics.inference_time > self.max_inference_time:
            alerts.append(MetricAlert(
                metric_name='inference_time',
                current_value=metrics.inference_time,
                threshold_value=self.max_inference_time,
                severity='warning',
                message=f"推理时间超出阈值: {metrics.inference_time:.2f}s > {self.max_inference_time:.2f}s",
                timestamp=datetime.now(),
                model_name=model_name
            ))

        # 触发告警
        for alert in alerts:
            await self._trigger_alert(alert)

    async def _trigger_alert(self, alert: MetricAlert):
        """触发告警"""
        self.logger.warning(f"触发告警: {alert.message}", extra={
            'metric_name': alert.metric_name,
            'severity': alert.severity,
            'model_name': alert.model_name
        })

        # 调用告警回调
        for callback in self.alert_callbacks:
            try:
                callback(alert)
            except Exception as e:
                self.logger.error("告警回调执行失败", error=e)

    def get_current_metrics(self) -> Optional[RealtimeMetrics]:
        """获取当前指标"""
        return self.current_metrics

    def get_metrics_history(
        self,
        duration_minutes: Optional[int] = None
    ) -> List[RealtimeMetrics]:
        """
        获取指标历史

        Args:
            duration_minutes: 时间范围（分钟）

        Returns:
            List[RealtimeMetrics]: 指标历史列表
        """
        if duration_minutes is None:
            return list(self.metrics_history)

        cutoff_time = datetime.now() - timedelta(minutes=duration_minutes)
        return [
            m for m in self.metrics_history
            if m.timestamp >= cutoff_time
        ]

    def get_trend_analysis(self) -> Dict[str, Any]:
        """
        获取精度趋势分析

        Returns:
            Dict: 趋势分析结果
        """
        if not self.metrics_history:
            return {}

        metrics_list = list(self.metrics_history)

        # 计算趋势
        accuracy_trend = self._calculate_trend([m.accuracy for m in metrics_list])
        performance_trend = self._calculate_trend([m.inference_time for m in metrics_list])

        # 计算统计信息
        recent_metrics = metrics_list[-10:]  # 最近10个数据点
        avg_accuracy = sum(m.accuracy for m in recent_metrics) / len(recent_metrics)
        avg_inference_time = sum(m.inference_time for m in recent_metrics) / len(recent_metrics)

        # 检查稳定性
        accuracy_stability = self._calculate_stability([m.accuracy for m in recent_metrics])

        return {
            'timestamp': datetime.now().isoformat(),
            'data_points': len(metrics_list),
            'accuracy_trend': accuracy_trend,
            'performance_trend': performance_trend,
            'current_accuracy': metrics_list[-1].accuracy if metrics_list else 0.0,
            'current_inference_time': metrics_list[-1].inference_time if metrics_list else 0.0,
            'avg_accuracy': avg_accuracy,
            'avg_inference_time': avg_inference_time,
            'accuracy_stability': accuracy_stability,
            'alerts_count': len([
                m for m in recent_metrics
                if m.accuracy < self.accuracy_threshold
            ])
        }

    def _calculate_trend(self, values: List[float]) -> str:
        """计算趋势方向"""
        if len(values) < 2:
            return 'stable'

        # 简单线性回归
        n = len(values)
        sum_x = sum(range(n))
        sum_y = sum(values)
        sum_xy = sum(i * v for i, v in enumerate(values))
        sum_x2 = sum(i * i for i in range(n))

        slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x * sum_x)

        if slope > 0.001:
            return 'improving'
        elif slope < -0.001:
            return 'degrading'
        else:
            return 'stable'

    def _calculate_stability(self, values: List[float]) -> str:
        """计算稳定性"""
        if len(values) < 2:
            return 'stable'

        mean = sum(values) / len(values)
        variance = sum((v - mean) ** 2 for v in values) / len(values)
        std_dev = variance ** 0.5

        # 稳定性基于变异系数
        cv = std_dev / mean if mean > 0 else 0

        if cv < 0.01:
            return 'very_stable'
        elif cv < 0.05:
            return 'stable'
        elif cv < 0.1:
            return 'unstable'
        else:
            return 'very_unstable'

    async def export_monitoring_report(
        self,
        output_path: str,
        format: str = 'json'
    ) -> str:
        """
        导出监控报告

        Args:
            output_path: 输出路径
            format: 输出格式

        Returns:
            str: 报告文件路径
        """
        from pathlib import Path
        import json

        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)

        # 收集数据
        history = list(self.metrics_history)
        trend = self.get_trend_analysis()

        report_data = {
            'timestamp': datetime.now().isoformat(),
            'monitoring_duration': len(history),
            'trend_analysis': trend,
            'metrics_history': [
                {
                    'accuracy': m.accuracy,
                    'precision': m.precision,
                    'recall': m.recall,
                    'f1_score': m.f1_score,
                    'inference_time': m.inference_time,
                    'throughput': m.throughput,
                    'memory_usage': m.memory_usage,
                    'timestamp': m.timestamp.isoformat()
                }
                for m in history
            ]
        }

        # 保存报告
        if format == 'json':
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(report_data, f, indent=2, ensure_ascii=False)

        self.logger.info(f"监控报告已导出: {output_file}")
        return str(output_file)


async def alert_handler(alert: MetricAlert):
    """告警处理器示例"""
    print(f"\n🚨 告警触发!")
    print(f"   指标: {alert.metric_name}")
    print(f"   当前值: {alert.current_value:.4f}")
    print(f"   阈值: {alert.threshold_value:.4f}")
    print(f"   严重程度: {alert.severity}")
    print(f"   消息: {alert.message}")
    print(f"   时间: {alert.timestamp.strftime('%Y-%m-%d %H:%M:%S')}")


async def main():
    """主函数 - 示例用法"""
    # 创建监控系统
    monitor = RealtimeMonitor(
        accuracy_threshold=0.98,
        max_inference_time=30.0
    )

    # 添加告警回调
    monitor.add_alert_callback(alert_handler)

    # 开始监控
    await monitor.start_monitoring("test_model")

    # 模拟指标更新
    import random
    random.seed(42)

    for i in range(10):
        metrics = RealtimeMetrics(
            accuracy=0.95 + random.random() * 0.05,
            inference_time=0.3 + random.random() * 0.5,
            throughput=2.0 + random.random() * 2.0,
            timestamp=datetime.now()
        )

        await monitor.update_metrics(metrics, "test_model")
        await asyncio.sleep(0.1)

    # 停止监控
    await monitor.stop_monitoring()

    # 获取趋势分析
    trend = monitor.get_trend_analysis()
    print(f"\n📊 趋势分析:")
    print(f"   精度趋势: {trend['accuracy_trend']}")
    print(f"   性能趋势: {trend['performance_trend']}")
    print(f"   当前精度: {trend['current_accuracy']:.2%}")
    print(f"   稳定性: {trend['accuracy_stability']}")

    # 导出报告
    report_path = await monitor.export_monitoring_report(
        "reports/realtime_monitor.json"
    )
    print(f"\n📄 监控报告已导出: {report_path}")


if __name__ == "__main__":
    asyncio.run(main())
