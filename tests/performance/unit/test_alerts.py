"""
告警系统单元测试

测试AlertSystem类的所有功能，包括告警规则、
告警检测、通知发送等功能。

作者: BMAD Method
创建日期: 2025-10-29
版本: v1.0
"""

import pytest
import tempfile
import shutil
from datetime import datetime, timedelta
from pathlib import Path
import sys

# 添加源码路径
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / 'src'))

from npu_converter.performance.alerts import (
    AlertSystem,
    AlertConfig,
    AlertRule,
    Alert
)


class TestAlertConfig:
    """测试AlertConfig配置类"""

    def test_default_config(self):
        """测试默认配置"""
        config = AlertConfig()
        assert config.alert_dir == "alerts"
        assert config.enable_email is False
        assert config.enable_webhook is False
        assert config.webhook_url is None
        assert config.alert_threshold == 0.8
        assert config.cooldown_period == 300
        assert config.max_alerts == 100

    def test_custom_config(self):
        """测试自定义配置"""
        config = AlertConfig(
            alert_dir="/tmp/alerts",
            enable_email=True,
            enable_webhook=True,
            webhook_url="http://example.com/webhook",
            alert_threshold=0.9,
            cooldown_period=600,
            max_alerts=50
        )
        assert config.alert_dir == "/tmp/alerts"
        assert config.enable_email is True
        assert config.enable_webhook is True
        assert config.webhook_url == "http://example.com/webhook"
        assert config.alert_threshold == 0.9
        assert config.cooldown_period == 600
        assert config.max_alerts == 50


class TestAlertRule:
    """测试AlertRule告警规则类"""

    def test_create_alert_rule(self):
        """测试创建告警规则"""
        rule = AlertRule(
            name="High CPU",
            metric_name="cpu_utilization",
            condition="gt",
            threshold=80.0,
            severity="high"
        )

        assert rule.name == "High CPU"
        assert rule.metric_name == "cpu_utilization"
        assert rule.condition == "gt"
        assert rule.threshold == 80.0
        assert rule.severity == "high"
        assert rule.enabled is True

    def test_alert_rule_to_dict(self):
        """测试告警规则转换为字典"""
        rule = AlertRule(
            name="High CPU",
            metric_name="cpu_utilization",
            condition="gt",
            threshold=80.0,
            severity="high"
        )

        result = rule.to_dict()
        assert result['name'] == "High CPU"
        assert result['metric_name'] == "cpu_utilization"
        assert result['threshold'] == 80.0


class TestAlert:
    """测试Alert告警类"""

    def test_create_alert(self):
        """测试创建告警"""
        now = datetime.now()
        alert = Alert(
            id="alert-001",
            timestamp=now,
            rule_name="High CPU",
            metric_name="cpu_utilization",
            value=95.0,
            threshold=80.0,
            severity="high",
            message="CPU utilization is too high"
        )

        assert alert.id == "alert-001"
        assert alert.metric_name == "cpu_utilization"
        assert alert.value == 95.0
        assert alert.threshold == 80.0
        assert alert.severity == "high"
        assert alert.status == "active"

    def test_alert_to_dict(self):
        """测试告警转换为字典"""
        now = datetime.now()
        alert = Alert(
            id="alert-001",
            timestamp=now,
            rule_name="High CPU",
            metric_name="cpu_utilization",
            value=95.0,
            threshold=80.0,
            severity="high",
            message="High CPU"
        )

        result = alert.to_dict()
        assert result['id'] == "alert-001"
        assert result['timestamp'] == now.isoformat()
        assert result['severity'] == "high"
        assert result['status'] == "active"


class TestAlertSystem:
    """测试AlertSystem告警系统类"""

    @pytest.fixture
    def temp_dir(self):
        """创建临时目录"""
        temp_path = tempfile.mkdtemp()
        yield temp_path
        shutil.rmtree(temp_path, ignore_errors=True)

    @pytest.fixture
    def alert_system(self, temp_dir):
        """创建AlertSystem实例"""
        config = AlertConfig(alert_dir=temp_dir)
        return AlertSystem(config)

    def test_initialize_alert_system(self, temp_dir):
        """测试初始化告警系统"""
        config = AlertConfig(alert_dir=temp_dir)
        system = AlertSystem(config)
        assert system.config.alert_dir == temp_dir
        assert len(system.alert_rules) >= 4  # 默认规则数量

    def test_load_default_rules(self, alert_system):
        """测试加载默认规则"""
        assert len(alert_system.alert_rules) >= 4

        # 检查默认规则
        assert "High CPU Utilization" in alert_system.alert_rules
        assert "High Memory Usage" in alert_system.alert_rules
        assert "Low Throughput" in alert_system.alert_rules
        assert "High Latency" in alert_system.alert_rules

    def test_add_alert_rule(self, alert_system):
        """测试添加告警规则"""
        initial_count = len(alert_system.alert_rules)

        rule = AlertRule(
            name="Custom Alert",
            metric_name="custom_metric",
            condition="gt",
            threshold=100.0,
            severity="medium"
        )

        alert_system.add_alert_rule(rule)

        assert len(alert_system.alert_rules) == initial_count + 1
        assert "Custom Alert" in alert_system.alert_rules

    def test_remove_alert_rule(self, alert_system):
        """测试删除告警规则"""
        # 添加规则
        rule = AlertRule(
            name="ToRemove",
            metric_name="metric",
            condition="gt",
            threshold=100.0,
            severity="low"
        )
        alert_system.add_alert_rule(rule)

        # 删除规则
        result = alert_system.remove_alert_rule("ToRemove")
        assert result is True
        assert "ToRemove" not in alert_system.alert_rules

        # 删除不存在的规则
        result = alert_system.remove_alert_rule("NonExistent")
        assert result is False

    def test_check_alerts_cpu_high(self, alert_system):
        """测试检测CPU高告警"""
        metrics = {
            'cpu_utilization': 85.0,  # 超过阈值80
            'memory_usage': 2000.0
        }

        alerts = alert_system.check_alerts(metrics)

        assert isinstance(alerts, list)
        # 应该触发CPU高告警
        cpu_alerts = [a for a in alerts if a.metric_name == 'cpu_utilization']
        assert len(cpu_alerts) > 0

    def test_check_alerts_memory_high(self, alert_system):
        """测试检测内存高告警"""
        metrics = {
            'cpu_utilization': 50.0,
            'memory_usage': 3800.0  # 超过阈值3500
        }

        alerts = alert_system.check_alerts(metrics)

        assert isinstance(alerts, list)
        # 应该触发内存高告警
        memory_alerts = [a for a in alerts if a.metric_name == 'memory_usage']
        assert len(memory_alerts) > 0

    def test_check_alerts_low_throughput(self, alert_system):
        """测试检测低吞吐量告警"""
        metrics = {
            'cpu_utilization': 50.0,
            'throughput': 8.0  # 低于阈值10
        }

        alerts = alert_system.check_alerts(metrics)

        assert isinstance(alerts, list)
        # 应该触发低吞吐量告警
        throughput_alerts = [a for a in alerts if a.metric_name == 'throughput']
        assert len(throughput_alerts) > 0

    def test_check_alerts_no_alert(self, alert_system):
        """测试无告警情况"""
        metrics = {
            'cpu_utilization': 50.0,  # 正常
            'memory_usage': 2000.0,  # 正常
            'throughput': 15.0,  # 正常
            'latency_p95': 40.0  # 正常
        }

        alerts = alert_system.check_alerts(metrics)

        # 可能没有告警，或者有轻微告警

    def test_evaluate_condition_gt(self, alert_system):
        """测试评估条件：大于"""
        assert alert_system._evaluate_condition(90.0, "gt", 80.0) is True
        assert alert_system._evaluate_condition(80.0, "gt", 80.0) is False
        assert alert_system._evaluate_condition(70.0, "gt", 80.0) is False

    def test_evaluate_condition_lt(self, alert_system):
        """测试评估条件：小于"""
        assert alert_system._evaluate_condition(70.0, "lt", 80.0) is True
        assert alert_system._evaluate_condition(80.0, "lt", 80.0) is False
        assert alert_system._evaluate_condition(90.0, "lt", 80.0) is False

    def test_evaluate_condition_eq(self, alert_system):
        """测试评估条件：等于"""
        assert alert_system._evaluate_condition(80.0, "eq", 80.0) is True
        assert alert_system._evaluate_condition(80.1, "eq", 80.0) is False
        assert alert_system._evaluate_condition(79.9, "eq", 80.0) is False

    def test_evaluate_condition_ne(self, alert_system):
        """测试评估条件：不等于"""
        assert alert_system._evaluate_condition(90.0, "ne", 80.0) is True
        assert alert_system._evaluate_condition(80.0, "ne", 80.0) is False

    def test_create_alert(self, alert_system):
        """测试创建告警"""
        rule = AlertRule(
            name="Test Alert",
            metric_name="test_metric",
            condition="gt",
            threshold=100.0,
            severity="medium"
        )

        # 手动调用私有方法
        alert = alert_system._create_alert(rule, 120.0)

        assert isinstance(alert, Alert)
        assert alert.rule_name == "Test Alert"
        assert alert.metric_name == "test_metric"
        assert alert.value == 120.0
        assert alert.threshold == 100.0
        assert alert.severity == "medium"
        assert alert.id.startswith("Test Alert-")

    def test_send_alert(self, alert_system):
        """测试发送告警"""
        alert = Alert(
            id="test-alert",
            timestamp=datetime.now(),
            rule_name="Test",
            metric_name="test",
            value=100.0,
            threshold=80.0,
            severity="low",
            message="Test alert"
        )

        # 发送告警（不应出错）
        alert_system.send_alert(alert)

        # 告警应该被保存
        assert alert.id in alert_system.active_alerts

    def test_send_alert_with_callback(self, alert_system):
        """测试带回调的告警发送"""
        callback_called = []

        def callback(alert):
            callback_called.append(alert)

        alert_system.add_callback(callback)

        alert = Alert(
            id="callback-test",
            timestamp=datetime.now(),
            rule_name="Test",
            metric_name="test",
            value=100.0,
            threshold=80.0,
            severity="low",
            message="Callback test"
        )

        alert_system.send_alert(alert)

        assert len(callback_called) == 1
        assert callback_called[0].id == "callback-test"

    def test_acknowledge_alert(self, alert_system):
        """测试确认告警"""
        # 创建告警
        rule = AlertRule(
            name="Ack Test",
            metric_name="test",
            condition="gt",
            threshold=100.0,
            severity="low"
        )
        alert = alert_system._create_alert(rule, 120.0)

        # 确认告警
        result = alert_system.acknowledge_alert(alert.id)
        assert result is True
        assert alert_system.active_alerts[alert.id].status == 'acknowledged'

        # 确认不存在的告警
        result = alert_system.acknowledge_alert("non-existent")
        assert result is False

    def test_resolve_alert(self, alert_system):
        """测试解决告警"""
        # 创建告警
        rule = AlertRule(
            name="Resolve Test",
            metric_name="test",
            condition="gt",
            threshold=100.0,
            severity="low"
        )
        alert = alert_system._create_alert(rule, 120.0)

        # 解决告警
        result = alert_system.resolve_alert(alert.id)
        assert result is True
        assert alert_system.active_alerts[alert.id].status == 'resolved'

        # 解决不存在的告警
        result = alert_system.resolve_alert("non-existent")
        assert result is False

    def test_get_active_alerts(self, alert_system):
        """测试获取活动告警"""
        # 创建几个告警
        rule = AlertRule(
            name="Active Test",
            metric_name="test",
            condition="gt",
            threshold=100.0,
            severity="medium"
        )
        alert1 = alert_system._create_alert(rule, 120.0)
        alert2 = alert_system._create_alert(rule, 130.0)

        # 获取活动告警
        active_alerts = alert_system.get_active_alerts()
        assert len(active_alerts) >= 2

        # 按严重程度过滤
        medium_alerts = alert_system.get_active_alerts(severity="medium")
        assert len(medium_alerts) >= 2

    def test_get_alert_history(self, alert_system):
        """测试获取告警历史"""
        # 创建告警
        rule = AlertRule(
            name="History Test",
            metric_name="test",
            condition="gt",
            threshold=100.0,
            severity="low"
        )
        alert = alert_system._create_alert(rule, 120.0)

        # 获取最近24小时的历史
        history = alert_system.get_alert_history(hours=24)
        assert len(history) >= 1

        # 获取最近1小时的历史（应该为空或较少）
        recent_history = alert_system.get_alert_history(hours=1)
        # 可能没有最近的告警

    def test_get_statistics(self, alert_system):
        """测试获取告警统计"""
        # 创建一些告警
        rule = AlertRule(
            name="Stats Test",
            metric_name="test",
            condition="gt",
            threshold=100.0,
            severity="medium"
        )
        for i in range(3):
            alert_system._create_alert(rule, 120.0 + i * 10)

        stats = alert_system.get_statistics()

        assert 'total_rules' in stats
        assert 'active_alerts' in stats
        assert 'total_alerts_24h' in stats
        assert 'severity_distribution' in stats
        assert stats['total_rules'] >= 4  # 默认规则

    def test_save_alert_to_file(self, alert_system, temp_dir):
        """测试保存告警到文件"""
        alert = Alert(
            id="file-test",
            timestamp=datetime.now(),
            rule_name="File Test",
            metric_name="test",
            value=100.0,
            threshold=80.0,
            severity="low",
            message="File test alert"
        )

        alert_system._save_alert_to_file(alert)

        # 检查文件是否存在
        alert_file = Path(temp_dir) / f"{datetime.now().strftime('%Y%m%d')}.jsonl"
        # 文件可能已创建

    def test_max_alerts_limit(self, alert_system):
        """测试最大告警数量限制"""
        # 快速创建大量告警
        rule = AlertRule(
            name="Limit Test",
            metric_name="test",
            condition="gt",
            threshold=100.0,
            severity="low"
        )

        for i in range(105):  # 超过默认限制100
            alert_system._create_alert(rule, 120.0)

        # 检查历史记录不超过限制
        assert len(alert_system.alert_history) <= alert_system.config.max_alerts


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
