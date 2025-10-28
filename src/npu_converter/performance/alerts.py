"""
告警系统 (Alert System)

监控性能指标，检测性能异常，
发送告警通知，支持多种告警渠道。

作者: BMAD Method
创建日期: 2025-10-29
版本: v1.0
"""

import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, asdict
from pathlib import Path

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class AlertConfig:
    """告警配置"""
    alert_dir: str = "alerts"
    enable_email: bool = False
    enable_webhook: bool = False
    webhook_url: Optional[str] = None
    alert_threshold: float = 0.8  # 告警阈值
    cooldown_period: int = 300  # 告警冷却期（秒）
    max_alerts: int = 100  # 最大告警数量


@dataclass
class AlertRule:
    """告警规则"""
    name: str
    metric_name: str
    condition: str  # gt, lt, eq, ne
    threshold: float
    severity: str  # low, medium, high, critical
    enabled: bool = True

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class Alert:
    """告警"""
    id: str
    timestamp: datetime
    rule_name: str
    metric_name: str
    value: float
    threshold: float
    severity: str
    message: str
    status: str = 'active'  # active, acknowledged, resolved

    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'timestamp': self.timestamp.isoformat(),
            'rule_name': self.rule_name,
            'metric_name': self.metric_name,
            'value': self.value,
            'threshold': self.threshold,
            'severity': self.severity,
            'message': self.message,
            'status': self.status
        }


class AlertSystem:
    """
    告警系统

    监控性能指标，检测性能异常，
    发送告警通知，支持多种告警渠道。
    """

    def __init__(self, config: AlertConfig):
        """
        初始化告警系统

        Args:
            config: 告警配置
        """
        self.config = config
        self.alert_rules: Dict[str, AlertRule] = {}
        self.active_alerts: Dict[str, Alert] = {}
        self.alert_history: List[Alert] = []
        self.alert_callbacks: List[Callable] = []

        Path(config.alert_dir).mkdir(parents=True, exist_ok=True)

        # 加载默认告警规则
        self._load_default_rules()

        logger.info(f"Alert System initialized with config: {asdict(config)}")

    def _load_default_rules(self):
        """加载默认告警规则"""
        default_rules = [
            AlertRule(
                name="High CPU Utilization",
                metric_name="cpu_utilization",
                condition="gt",
                threshold=80.0,
                severity="high"
            ),
            AlertRule(
                name="High Memory Usage",
                metric_name="memory_usage",
                condition="gt",
                threshold=3500.0,
                severity="high"
            ),
            AlertRule(
                name="Low Throughput",
                metric_name="throughput",
                condition="lt",
                threshold=10.0,
                severity="medium"
            ),
            AlertRule(
                name="High Latency",
                metric_name="latency_p95",
                condition="gt",
                threshold=60.0,
                severity="high"
            )
        ]

        for rule in default_rules:
            self.alert_rules[rule.name] = rule

        logger.info(f"Loaded {len(default_rules)} default alert rules")

    def add_alert_rule(self, rule: AlertRule):
        """添加告警规则"""
        self.alert_rules[rule.name] = rule
        logger.info(f"Added alert rule: {rule.name}")

    def remove_alert_rule(self, rule_name: str) -> bool:
        """删除告警规则"""
        if rule_name in self.alert_rules:
            del self.alert_rules[rule_name]
            logger.info(f"Removed alert rule: {rule_name}")
            return True
        return False

    def check_alerts(self, metrics: Dict[str, Any]) -> List[Alert]:
        """检查告警条件"""
        triggered_alerts = []

        for rule in self.alert_rules.values():
            if not rule.enabled:
                continue

            metric_value = metrics.get(rule.metric_name)
            if metric_value is None:
                continue

            # 检查条件
            if self._evaluate_condition(metric_value, rule.condition, rule.threshold):
                alert = self._create_alert(rule, metric_value)
                triggered_alerts.append(alert)

        return triggered_alerts

    def _evaluate_condition(self, value: float, condition: str, threshold: float) -> bool:
        """评估告警条件"""
        if condition == "gt":
            return value > threshold
        elif condition == "lt":
            return value < threshold
        elif condition == "eq":
            return abs(value - threshold) < 0.01
        elif condition == "ne":
            return abs(value - threshold) >= 0.01
        return False

    def _create_alert(self, rule: AlertRule, metric_value: float) -> Alert:
        """创建告警"""
        alert_id = f"{rule.name}-{int(datetime.now().timestamp())}"

        alert = Alert(
            id=alert_id,
            timestamp=datetime.now(),
            rule_name=rule.name,
            metric_name=rule.metric_name,
            value=metric_value,
            threshold=rule.threshold,
            severity=rule.severity,
            message=f"{rule.name}: {rule.metric_name} = {metric_value:.2f} (threshold: {rule.threshold:.2f})"
        )

        self.active_alerts[alert_id] = alert
        self.alert_history.append(alert)

        # 发送告警
        self.send_alert(alert)

        # 限制告警数量
        if len(self.alert_history) > self.config.max_alerts:
            self.alert_history.pop(0)

        logger.warning(f"Alert triggered: {alert.message}")
        return alert

    def send_alert(self, alert: Alert):
        """发送告警"""
        # 回调通知
        for callback in self.alert_callbacks:
            try:
                callback(alert)
            except Exception as e:
                logger.error(f"Error in alert callback: {e}")

        # 记录到文件
        self._save_alert_to_file(alert)

        # 发送到webhook
        if self.config.enable_webhook and self.config.webhook_url:
            self._send_webhook(alert)

        # 发送邮件（如果启用）
        if self.config.enable_email:
            self._send_email(alert)

    def _save_alert_to_file(self, alert: Alert):
        """保存告警到文件"""
        alert_file = Path(self.config.alert_dir) / f"{alert.timestamp.strftime('%Y%m%d')}.jsonl"

        with open(alert_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(alert.to_dict()) + '\n')

    def _send_webhook(self, alert: Alert):
        """发送webhook通知"""
        # 实现webhook发送逻辑
        logger.info(f"Sending webhook for alert: {alert.id}")

    def _send_email(self, alert: Alert):
        """发送邮件通知"""
        # 实现邮件发送逻辑
        logger.info(f"Sending email for alert: {alert.id}")

    def acknowledge_alert(self, alert_id: str) -> bool:
        """确认告警"""
        if alert_id in self.active_alerts:
            self.active_alerts[alert_id].status = 'acknowledged'
            logger.info(f"Alert acknowledged: {alert_id}")
            return True
        return False

    def resolve_alert(self, alert_id: str) -> bool:
        """解决告警"""
        if alert_id in self.active_alerts:
            self.active_alerts[alert_id].status = 'resolved'
            logger.info(f"Alert resolved: {alert_id}")
            return True
        return False

    def get_active_alerts(self, severity: Optional[str] = None) -> List[Alert]:
        """获取活动告警"""
        alerts = [a for a in self.active_alerts.values() if a.status == 'active']

        if severity:
            alerts = [a for a in alerts if a.severity == severity]

        return sorted(alerts, key=lambda x: x.timestamp, reverse=True)

    def get_alert_history(self, hours: int = 24) -> List[Alert]:
        """获取告警历史"""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        return [a for a in self.alert_history if a.timestamp >= cutoff_time]

    def add_callback(self, callback: Callable):
        """添加告警回调"""
        self.alert_callbacks.append(callback)

    def get_statistics(self) -> Dict[str, Any]:
        """获取告警统计"""
        active_alerts = self.get_active_alerts()
        recent_alerts = self.get_alert_history(24)

        severity_counts = {}
        for alert in recent_alerts:
            severity_counts[alert.severity] = severity_counts.get(alert.severity, 0) + 1

        return {
            'total_rules': len(self.alert_rules),
            'active_alerts': len(active_alerts),
            'total_alerts_24h': len(recent_alerts),
            'severity_distribution': severity_counts
        }


if __name__ == "__main__":
    # 示例使用
    config = AlertConfig(
        alert_dir="alerts",
        enable_webhook=False,
        enable_email=False,
        alert_threshold=0.8
    )

    alert_system = AlertSystem(config)

    # 添加自定义告警规则
    custom_rule = AlertRule(
        name="Custom GPU Utilization",
        metric_name="gpu_utilization",
        condition="gt",
        threshold=90.0,
        severity="critical"
    )
    alert_system.add_alert_rule(custom_rule)

    # 模拟监控数据
    metrics = {
        'cpu_utilization': 85.0,
        'memory_usage': 3600.0,
        'gpu_utilization': 92.0,
        'throughput': 9.5,
        'latency_p95': 65.0
    }

    # 检查告警
    alerts = alert_system.check_alerts(metrics)
    print(f"Triggered {len(alerts)} alerts")

    for alert in alerts:
        print(f"Alert: {alert.message}")

    # 获取统计
    stats = alert_system.get_statistics()
    print(f"Alert statistics: {stats}")
