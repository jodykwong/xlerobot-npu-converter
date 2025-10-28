#!/usr/bin/env python3
"""
XLeRobot NPU Converter - 性能趋势分析器

分析性能测试结果的历史趋势，识别性能变化模式和提供优化建议。
"""

import json
import sys
import os
import statistics
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict
from collections import defaultdict


@dataclass
class PerformanceDataPoint:
    """性能数据点"""
    timestamp: datetime
    operation: str
    value: float
    unit: str
    baseline: Optional[float] = None
    improvement: Optional[float] = None
    metadata: Optional[Dict] = None


@dataclass
class TrendAnalysis:
    """趋势分析结果"""
    operation: str
    trend_direction: str  # improving, deteriorating, stable
    trend_strength: float  # 0-1, 趋势强度
    avg_value: float
    std_deviation: float
    min_value: float
    max_value: float
    change_rate: float  # 变化率(每单位时间)
    volatility: float  # 波动性
    outlier_count: int
    recommendations: List[str]


class PerformanceTrendAnalyzer:
    """性能趋势分析器"""

    def __init__(self, project_root: str = None):
        """初始化趋势分析器

        Args:
            project_root: 项目根目录
        """
        self.project_root = Path(project_root) if project_root else Path.cwd()
        self.reports_dir = self.project_root / "reports"
        self.trend_data_file = self.reports_dir / "performance_trends.json"
        self.analysis_file = self.reports_dir / "trend_analysis.json"

        # 确保目录存在
        self.reports_dir.mkdir(parents=True, exist_ok=True)

    def load_historical_performance_data(self) -> List[PerformanceDataPoint]:
        """加载历史性能数据

        Returns:
            历史性能数据列表
        """
        data_points = []

        # 从测试报告中提取性能数据
        test_report_file = self.reports_dir / "test_report.json"
        if test_report_file.exists():
            data_points.extend(self._extract_from_test_report(test_report_file))

        # 从专门的性能历史文件中加载数据
        performance_history_file = self.reports_dir / "performance_history.json"
        if performance_history_file.exists():
            data_points.extend(self._extract_from_performance_history(performance_history_file))

        # 按时间排序
        data_points.sort(key=lambda x: x.timestamp)

        return data_points

    def _extract_from_test_report(self, report_file: Path) -> List[PerformanceDataPoint]:
        """从测试报告中提取性能数据

        Args:
            report_file: 测试报告文件

        Returns:
            性能数据点列表
        """
        data_points = []

        try:
            with open(report_file, 'r', encoding='utf-8') as f:
                report = json.load(f)

            metadata = report.get("metadata", {})
            timestamp_str = metadata.get("generated_at", "")
            timestamp = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))

            performance_metrics = report.get("performance_metrics", [])
            for metric in performance_metrics:
                data_point = PerformanceDataPoint(
                    timestamp=timestamp,
                    operation=metric.get("name", ""),
                    value=metric.get("value", 0),
                    unit=metric.get("unit", ""),
                    baseline=metric.get("baseline"),
                    improvement=metric.get("improvement"),
                    metadata={"source": "test_report"}
                )
                data_points.append(data_point)

        except Exception as e:
            print(f"⚠️ 从测试报告提取性能数据失败: {e}")

        return data_points

    def _extract_from_performance_history(self, history_file: Path) -> List[PerformanceDataPoint]:
        """从性能历史文件中提取数据

        Args:
            history_file: 性能历史文件

        Returns:
            性能数据点列表
        """
        data_points = []

        try:
            with open(history_file, 'r') as f:
                history_data = json.load(f)

            for record in history_data:
                timestamp_str = record.get("timestamp", "")
                timestamp = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))

                # 假设历史数据包含性能指标
                metrics = record.get("performance_metrics", {})
                for operation, metric_data in metrics.items():
                    data_point = PerformanceDataPoint(
                        timestamp=timestamp,
                        operation=operation,
                        value=metric_data.get("value", 0),
                        unit=metric_data.get("unit", ""),
                        baseline=metric_data.get("baseline"),
                        improvement=metric_data.get("improvement"),
                        metadata={"source": "performance_history"}
                    )
                    data_points.append(data_point)

        except Exception as e:
            print(f"⚠️ 从性能历史文件提取数据失败: {e}")

        return data_points

    def group_data_by_operation(self, data_points: List[PerformanceDataPoint]) -> Dict[str, List[PerformanceDataPoint]]:
        """按操作类型分组数据

        Args:
            data_points: 性能数据点列表

        Returns:
            按操作分组的数据字典
        """
        grouped = defaultdict(list)
        for data_point in data_points:
            grouped[data_point.operation].append(data_point)
        return dict(grouped)

    def analyze_trend(self, operation_data: List[PerformanceDataPoint]) -> TrendAnalysis:
        """分析单个操作的性能趋势

        Args:
            operation_data: 单个操作的性能数据

        Returns:
            趋势分析结果
        """
        if not operation_data:
            raise ValueError("没有可分析的数据")

        operation_name = operation_data[0].operation
        values = [point.value for point in operation_data]
        timestamps = [point.timestamp for point in operation_data]

        # 基本统计
        avg_value = statistics.mean(values)
        std_deviation = statistics.stdev(values) if len(values) > 1 else 0
        min_value = min(values)
        max_value = max(values)

        # 计算趋势（线性回归）
        trend_strength, change_rate = self._calculate_linear_trend(timestamps, values)

        # 确定趋势方向
        if abs(change_rate) < 0.01:  # 变化率阈值
            trend_direction = "stable"
        elif change_rate > 0:
            # 对于时间类指标，值越小越好（如响应时间）
            if "time" in operation_name.lower() or "duration" in operation_name.lower():
                trend_direction = "deteriorating"  # 时间增加是恶化
            else:
                trend_direction = "improving"  # 吞吐量等增加是改进
        else:
            if "time" in operation_name.lower() or "duration" in operation_name.lower():
                trend_direction = "improving"  # 时间减少是改进
            else:
                trend_direction = "deteriorating"  # 吞吐量等减少是恶化

        # 计算波动性
        volatility = std_deviation / avg_value if avg_value > 0 else 0

        # 检测异常值
        outlier_count = self._detect_outliers(values)

        # 生成建议
        recommendations = self._generate_recommendations(
            operation_name, trend_direction, trend_strength,
            volatility, outlier_count, avg_value
        )

        return TrendAnalysis(
            operation=operation_name,
            trend_direction=trend_direction,
            trend_strength=trend_strength,
            avg_value=avg_value,
            std_deviation=std_deviation,
            min_value=min_value,
            max_value=max_value,
            change_rate=change_rate,
            volatility=volatility,
            outlier_count=outlier_count,
            recommendations=recommendations
        )

    def _calculate_linear_trend(self, timestamps: List[datetime], values: List[float]) -> Tuple[float, float]:
        """计算线性趋势

        Args:
            timestamps: 时间戳列表
            values: 数值列表

        Returns:
            (趋势强度, 变化率)
        """
        if len(timestamps) < 2:
            return 0.0, 0.0

        # 转换时间戳为数值（秒）
        base_time = timestamps[0]
        x_values = [(ts - base_time).total_seconds() for ts in timestamps]
        y_values = values

        n = len(x_values)
        if n == 0:
            return 0.0, 0.0

        # 计算线性回归参数
        sum_x = sum(x_values)
        sum_y = sum(y_values)
        sum_xy = sum(x * y for x, y in zip(x_values, y_values))
        sum_x2 = sum(x * x for x in x_values)

        denominator = n * sum_x2 - sum_x * sum_x
        if denominator == 0:
            return 0.0, 0.0

        slope = (n * sum_xy - sum_x * sum_y) / denominator
        intercept = (sum_y - slope * sum_x) / n

        # 计算R²作为趋势强度
        y_mean = sum_y / n
        ss_total = sum((y - y_mean) ** 2 for y in y_values)

        if ss_total == 0:
            trend_strength = 1.0
        else:
            y_predicted = [slope * x + intercept for x in x_values]
            ss_residual = sum((y_actual - y_pred) ** 2 for y_actual, y_pred in zip(y_values, y_predicted))
            trend_strength = 1 - (ss_residual / ss_total)

        return max(0, min(1, trend_strength)), slope

    def _detect_outliers(self, values: List[float]) -> int:
        """检测异常值

        Args:
            values: 数值列表

        Returns:
            异常值数量
        """
        if len(values) < 4:
            return 0

        # 使用IQR方法检测异常值
        sorted_values = sorted(values)
        n = len(sorted_values)

        q1_index = n // 4
        q3_index = 3 * n // 4

        q1 = sorted_values[q1_index]
        q3 = sorted_values[q3_index]
        iqr = q3 - q1

        lower_bound = q1 - 1.5 * iqr
        upper_bound = q3 + 1.5 * iqr

        outlier_count = sum(1 for v in values if v < lower_bound or v > upper_bound)

        return outlier_count

    def _generate_recommendations(self, operation: str, trend_direction: str,
                                trend_strength: float, volatility: float,
                                outlier_count: int, avg_value: float) -> List[str]:
        """生成改进建议

        Args:
            operation: 操作名称
            trend_direction: 趋势方向
            trend_strength: 趋势强度
            volatility: 波动性
            outlier_count: 异常值数量
            avg_value: 平均值

        Returns:
            建议列表
        """
        recommendations = []

        # 基于趋势方向的建议
        if trend_direction == "deteriorating" and trend_strength > 0.5:
            recommendations.append(f"⚠️ {operation}性能持续恶化，需要立即优化")
        elif trend_direction == "improving" and trend_strength > 0.5:
            recommendations.append(f"✅ {operation}性能持续改进，保持当前优化策略")
        elif trend_direction == "stable":
            recommendations.append(f"➡️ {operation}性能稳定，可考虑进一步优化")

        # 基于波动性的建议
        if volatility > 0.3:
            recommendations.append(f"📊 {operation}性能波动较大({volatility:.1%})，需要提高稳定性")
        elif volatility < 0.05:
            recommendations.append(f"🎯 {operation}性能表现非常稳定")

        # 基于异常值的建议
        if outlier_count > 0:
            recommendations.append(f"🔍 {operation}存在{outlier_count}个异常值，需要调查原因")

        # 基于具体操作类型的建议
        operation_lower = operation.lower()
        if "time" in operation_lower or "duration" in operation_lower:
            if avg_value > 10:  # 假设10秒为阈值
                recommendations.append(f"⏱️ {operation}平均耗时较长({avg_value:.2f}s)，建议优化算法")
            else:
                recommendations.append(f"⚡ {operation}响应时间良好({avg_value:.2f}s)")
        elif "memory" in operation_lower:
            if avg_value > 1000:  # 假设1GB为阈值
                recommendations.append(f"💾 {operation}内存使用较高({avg_value:.1f}MB)，需要优化内存管理")
        elif "throughput" in operation_lower or "ops" in operation_lower:
            if avg_value < 100:  # 假设100 ops/sec为阈值
                recommendations.append(f"📈 {operation}吞吐量偏低({avg_value:.1f})，需要提升处理效率")

        # 如果没有特殊情况
        if not recommendations:
            recommendations.append(f"📊 {operation}性能指标正常，继续监控")

        return recommendations

    def analyze_all_trends(self) -> Dict[str, TrendAnalysis]:
        """分析所有操作的性能趋势

        Returns:
            所有操作的趋势分析结果
        """
        print("📈 分析性能趋势...")

        # 加载数据
        data_points = self.load_historical_performance_data()
        if not data_points:
            print("⚠️ 没有找到历史性能数据")
            return {}

        # 按操作分组
        grouped_data = self.group_data_by_operation(data_points)

        # 分析每个操作的趋势
        all_trends = {}
        for operation, operation_data in grouped_data.items():
            if len(operation_data) >= 2:  # 至少需要2个数据点
                try:
                    trend_analysis = self.analyze_trend(operation_data)
                    all_trends[operation] = trend_analysis
                    print(f"  ✅ 分析完成: {operation}")
                except Exception as e:
                    print(f"  ❌ 分析失败: {operation} - {e}")

        return all_trends

    def generate_trend_summary(self, trends: Dict[str, TrendAnalysis]) -> Dict:
        """生成趋势摘要

        Args:
            trends: 趋势分析结果

        Returns:
            趋势摘要
        """
        if not trends:
            return {"error": "没有趋势数据"}

        # 统计趋势分布
        improving_count = sum(1 for t in trends.values() if t.trend_direction == "improving")
        deteriorating_count = sum(1 for t in trends.values() if t.trend_direction == "deteriorating")
        stable_count = sum(1 for t in trends.values() if t.trend_direction == "stable")

        # 计算整体健康度
        health_score = 100.0
        if deteriorating_count > 0:
            health_score -= (deteriorating_count / len(trends)) * 50
        if improving_count > 0:
            health_score += (improving_count / len(trends)) * 25

        health_score = max(0, min(100, health_score))

        # 识别关键问题
        critical_issues = []
        for operation, trend in trends.items():
            if trend.trend_direction == "deteriorating" and trend.trend_strength > 0.7:
                critical_issues.append({
                    "operation": operation,
                    "severity": "high",
                    "description": f"{operation}性能严重恶化，趋势强度{trend.trend_strength:.2f}"
                })
            elif trend.volatility > 0.4:
                critical_issues.append({
                    "operation": operation,
                    "severity": "medium",
                    "description": f"{operation}性能波动过大，波动性{trend.volatility:.1%}"
                })

        # 生成总体建议
        overall_recommendations = []
        if deteriorating_count > 0:
            overall_recommendations.append(f"🔴 {deteriorating_count}个操作性能恶化，需要优先处理")
        if improving_count > len(trends) * 0.5:
            overall_recommendations.append("🟢 大部分操作性能在改进，整体趋势良好")
        if len(critical_issues) == 0:
            overall_recommendations.append("✅ 所有性能指标表现良好")

        return {
            "summary": {
                "total_operations": len(trends),
                "improving": improving_count,
                "deteriorating": deteriorating_count,
                "stable": stable_count,
                "health_score": health_score
            },
            "critical_issues": critical_issues,
            "overall_recommendations": overall_recommendations,
            "detailed_trends": {op: asdict(trend) for op, trend in trends.items()}
        }

    def save_analysis(self, analysis: Dict) -> None:
        """保存趋势分析结果

        Args:
            analysis: 分析结果
        """
        try:
            with open(self.analysis_file, 'w', encoding='utf-8') as f:
                json.dump(analysis, f, indent=2, ensure_ascii=False, default=str)
            print(f"✅ 趋势分析结果已保存: {self.analysis_file}")
        except Exception as e:
            print(f"❌ 保存分析结果失败: {e}")

    def generate_trend_report(self) -> str:
        """生成趋势分析报告

        Returns:
            格式化的报告文本
        """
        trends = self.analyze_all_trends()
        if not trends:
            return "没有可用的趋势分析数据"

        summary = self.generate_trend_summary(trends)

        report = f"""
# XLeRobot NPU Converter - 性能趋势分析报告

生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 📊 总体概况

- **总操作数**: {summary['summary']['total_operations']}
- **性能改进**: {summary['summary']['improving']} 个
- **性能恶化**: {summary['summary']['deteriorating']} 个
- **性能稳定**: {summary['summary']['stable']} 个
- **健康评分**: {summary['summary']['health_score']:.1f}/100

## 🔴 关键问题

"""

        for issue in summary.get("critical_issues", []):
            severity_icon = "🔴" if issue["severity"] == "high" else "🟡"
            report += f"- {severity_icon} **{issue['operation']}**: {issue['description']}\n"

        report += "\n## 💡 总体建议\n\n"
        for rec in summary.get("overall_recommendations", []):
            report += f"- {rec}\n"

        report += "\n## 📈 详细趋势分析\n\n"

        for operation, trend in trends.items():
            trend_icon = {"improving": "📈", "deteriorating": "📉", "stable": "➡️"}[trend.trend_direction]

            report += f"""
### {trend_icon} {operation}

- **趋势方向**: {trend.trend_direction}
- **趋势强度**: {trend.trend_strength:.2f}
- **平均值**: {trend.avg_value:.2f} {trends[operation].metadata.get('unit', '') if trends[operation].metadata else ''}
- **标准差**: {trend.std_deviation:.2f}
- **变化率**: {trend.change_rate:.6f}/秒
- **波动性**: {trend.volatility:.1%}
- **异常值**: {trend.outlier_count} 个

**建议**:
"""
            for rec in trend.recommendations:
                report += f"- {rec}\n"

            report += "\n"

        return report

    def analyze_and_save(self) -> Dict:
        """执行完整分析并保存结果

        Returns:
            分析结果
        """
        # 执行趋势分析
        trends = self.analyze_all_trends()

        # 生成摘要
        summary = self.generate_trend_summary(trends)

        # 保存分析结果
        self.save_analysis(summary)

        # 生成文本报告
        report = self.generate_trend_report()
        report_file = self.reports_dir / "trend_report.md"
        try:
            with open(report_file, 'w', encoding='utf-8') as f:
                f.write(report)
            print(f"✅ 趋势报告已保存: {report_file}")
        except Exception as e:
            print(f"❌ 保存趋势报告失败: {e}")

        # 打印摘要
        self._print_summary(summary)

        return summary

    def _print_summary(self, summary: Dict) -> None:
        """打印分析摘要

        Args:
            summary: 分析摘要
        """
        print("\n" + "="*60)
        print("📈 性能趋势分析摘要")
        print("="*60)

        summary_data = summary.get("summary", {})
        print(f"📊 总操作数: {summary_data.get('total_operations', 0)}")
        print(f"📈 性能改进: {summary_data.get('improving', 0)} 个")
        print(f"📉 性能恶化: {summary_data.get('deteriorating', 0)} 个")
        print(f"➡️ 性能稳定: {summary_data.get('stable', 0)} 个")
        print(f"💚 健康评分: {summary_data.get('health_score', 0):.1f}/100")

        critical_issues = summary.get("critical_issues", [])
        if critical_issues:
            print(f"\n🔴 关键问题 ({len(critical_issues)}个):")
            for issue in critical_issues:
                severity_icon = "🔴" if issue["severity"] == "high" else "🟡"
                print(f"  {severity_icon} {issue['operation']}: {issue['description']}")

        recommendations = summary.get("overall_recommendations", [])
        if recommendations:
            print(f"\n💡 总体建议:")
            for rec in recommendations:
                print(f"  {rec}")

        print("="*60)


def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(description="性能趋势分析")
    parser.add_argument("--project-root", default=".", help="项目根目录")
    parser.add_argument("--output", help="输出目录")

    args = parser.parse_args()

    analyzer = PerformanceTrendAnalyzer(args.project_root)

    if args.output:
        analyzer.reports_dir = Path(args.output)
        analyzer.trend_data_file = analyzer.reports_dir / "performance_trends.json"
        analyzer.analysis_file = analyzer.reports_dir / "trend_analysis.json"

    result = analyzer.analyze_and_save()

    print(f"\n📈 性能趋势分析完成!")
    print(f"📊 分析结果: {analyzer.analysis_file}")
    print(f"📄 趋势报告: {analyzer.reports_dir / 'trend_report.md'}")


if __name__ == "__main__":
    main()