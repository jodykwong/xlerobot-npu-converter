"""
测试用例套件 (Benchmark Suite)

定义标准测试用例，管理测试用例的生命周期，
支持测试用例参数化，提供测试用例执行接口。

作者: BMAD Method
创建日期: 2025-10-29
版本: v1.0
"""

import yaml
import json
import logging
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, asdict
from pathlib import Path
from datetime import datetime

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class SuiteConfig:
    """测试套件配置"""
    test_data_dir: str = "data/benchmarks"
    test_cases_file: str = "test_cases.yaml"
    default_timeout: int = 3600
    max_retries: int = 3
    parallel_execution: bool = True
    enable_validation: bool = True
    auto_cleanup: bool = True


@dataclass
class TestCase:
    """测试用例"""
    id: str
    name: str
    description: str
    category: str
    model_type: str
    model_name: str
    parameters: Dict[str, Any]
    expected_results: Dict[str, Any]
    timeout: Optional[int] = None
    priority: str = "medium"  # low, medium, high, critical
    tags: Optional[List[str]] = None
    dependencies: Optional[List[str]] = None
    setup_script: Optional[str] = None
    cleanup_script: Optional[str] = None

    def __post_init__(self):
        if self.timeout is None:
            self.timeout = 3600
        if self.tags is None:
            self.tags = []
        if self.dependencies is None:
            self.dependencies = []

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    def validate(self) -> bool:
        """验证测试用例的完整性"""
        required_fields = ['id', 'name', 'category', 'model_type', 'parameters', 'expected_results']
        for field in required_fields:
            if not hasattr(self, field) or getattr(self, field) is None or getattr(self, field) == "":
                return False
        return True


@dataclass
class TestSuite:
    """测试套件"""
    name: str
    description: str
    version: str
    test_cases: List[TestCase]
    metadata: Dict[str, Any]
    created_date: datetime
    modified_date: datetime

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}

    def to_dict(self) -> Dict[str, Any]:
        return {
            'name': self.name,
            'description': self.description,
            'version': self.version,
            'test_cases': [tc.to_dict() for tc in self.test_cases],
            'metadata': self.metadata,
            'created_date': self.created_date.isoformat(),
            'modified_date': self.modified_date.isoformat()
        }


@dataclass
class ValidationResult:
    """验证结果"""
    is_valid: bool
    errors: List[str]
    warnings: List[str]

    def to_dict(self) -> Dict[str, Any]:
        return {
            'is_valid': self.is_valid,
            'errors': self.errors,
            'warnings': self.warnings
        }


class BenchmarkSuite:
    """
    测试用例套件

    定义标准测试用例，管理测试用例的生命周期，
    支持测试用例参数化，提供测试用例执行接口。
    """

    # 内置测试用例类别
    CATEGORIES = {
        'single_model': '单模型转换测试',
        'concurrent': '多模型并发测试',
        'stress_test': '压力测试',
        'stability_test': '稳定性测试',
        'regression_test': '回归测试',
        'integration_test': '集成测试'
    }

    # 内置模型类型
    MODEL_TYPES = {
        'asr': 'Automatic Speech Recognition',
        'tts': 'Text-to-Speech',
        'cv': 'Computer Vision',
        'nlp': 'Natural Language Processing'
    }

    # 内置模型名称
    BUILTIN_MODELS = {
        'SenseVoice': {
            'type': 'asr',
            'description': 'SenseVoice ASR模型'
        },
        'VITS-Cantonese': {
            'type': 'tts',
            'description': 'VITS-Cantonese TTS模型'
        },
        'Piper-VITS': {
            'type': 'tts',
            'description': 'Piper VITS TTS模型'
        }
    }

    def __init__(self, config: SuiteConfig):
        """
        初始化测试用例套件

        Args:
            config: 测试套件配置
        """
        self.config = config
        self.test_cases: Dict[str, TestCase] = {}
        self.test_suites: Dict[str, TestSuite] = {}

        # 创建测试数据目录
        Path(config.test_data_dir).mkdir(parents=True, exist_ok=True)

        # 加载内置测试用例
        self._load_builtin_test_cases()

        # 尝试从文件加载测试用例
        self._load_test_cases_from_file()

        logger.info(f"Benchmark Suite initialized with {len(self.test_cases)} test cases")

    def _load_builtin_test_cases(self):
        """加载内置测试用例"""
        logger.info("Loading built-in test cases...")

        # TC-001: SenseVoice ASR单模型转换性能测试
        tc_001 = TestCase(
            id="TC-001",
            name="SenseVoice ASR模型转换性能测试",
            description="测试SenseVoice ASR模型的转换性能",
            category="single_model",
            model_type="asr",
            model_name="SenseVoice",
            parameters={
                "model_path": "/models/sensevoice",
                "input_format": "onnx",
                "output_format": "npu",
                "batch_size": [1, 4, 8, 16],
                "precision": ["fp32", "fp16", "int8"],
                "concurrency": 1,
                "test_duration": 300  # 5分钟
            },
            expected_results={
                "throughput": {
                    "fp32": "> 12 models/minute",
                    "fp16": "> 15 models/minute",
                    "int8": "> 18 models/minute"
                },
                "latency_p95": {
                    "fp32": "< 60 seconds",
                    "fp16": "< 45 seconds",
                    "int8": "< 30 seconds"
                },
                "resource_usage": {
                    "cpu": "< 70%",
                    "memory": "< 3GB",
                    "gpu": "< 80%",
                    "npu": "< 80%"
                },
                "success_rate": "> 99.9%"
            },
            priority="high",
            tags=["performance", "asr", "single-model"],
            timeout=1800
        )
        self.add_test_case(tc_001)

        # TC-002: VITS-Cantonese TTS单模型转换性能测试
        tc_002 = TestCase(
            id="TC-002",
            name="VITS-Cantonese TTS模型转换性能测试",
            description="测试VITS-Cantonese TTS模型的转换性能",
            category="single_model",
            model_type="tts",
            model_name="VITS-Cantonese",
            parameters={
                "model_path": "/models/vits-cantonese",
                "input_format": "pytorch",
                "output_format": "npu",
                "batch_size": [1, 2, 4, 8],
                "precision": ["fp32", "fp16"],
                "concurrency": 1,
                "test_duration": 300
            },
            expected_results={
                "throughput": {
                    "fp32": "> 10 models/minute",
                    "fp16": "> 14 models/minute"
                },
                "latency_p95": {
                    "fp32": "< 80 seconds",
                    "fp16": "< 60 seconds"
                },
                "resource_usage": {
                    "cpu": "< 70%",
                    "memory": "< 3.5GB",
                    "gpu": "< 80%",
                    "npu": "< 80%"
                },
                "success_rate": "> 99.9%"
            },
            priority="high",
            tags=["performance", "tts", "single-model"],
            timeout=1800
        )
        self.add_test_case(tc_002)

        # TC-003: Piper VITS TTS单模型转换性能测试
        tc_003 = TestCase(
            id="TC-003",
            name="Piper VITS TTS模型转换性能测试",
            description="测试Piper VITS TTS模型的转换性能",
            category="single_model",
            model_type="tts",
            model_name="Piper-VITS",
            parameters={
                "model_path": "/models/piper-vits",
                "input_format": "pytorch",
                "output_format": "npu",
                "batch_size": [1, 2, 4, 8],
                "precision": ["fp32", "fp16"],
                "concurrency": 1,
                "test_duration": 300
            },
            expected_results={
                "throughput": {
                    "fp32": "> 11 models/minute",
                    "fp16": "> 15 models/minute"
                },
                "latency_p95": {
                    "fp32": "< 75 seconds",
                    "fp16": "< 55 seconds"
                },
                "resource_usage": {
                    "cpu": "< 70%",
                    "memory": "< 3.5GB",
                    "gpu": "< 80%",
                    "npu": "< 80%"
                },
                "success_rate": "> 99.9%"
            },
            priority="high",
            tags=["performance", "tts", "single-model"],
            timeout=1800
        )
        self.add_test_case(tc_003)

        # TC-004: 多模型并发转换性能测试
        tc_004 = TestCase(
            id="TC-004",
            name="多模型并发转换性能测试",
            description="测试多模型并发转换的系统性能",
            category="concurrent",
            model_type="mixed",
            model_name="Mixed Models",
            parameters={
                "concurrent_models": [2, 5, 10, 20],
                "model_mix_ratio": {
                    "asr": 0.4,
                    "tts": 0.6
                },
                "batch_size": 4,
                "precision": "fp16",
                "test_duration": 600
            },
            expected_results={
                "throughput_per_model": "> 8 models/minute",
                "total_throughput": "> 40 models/minute",
                "latency_p95": "< 90 seconds",
                "resource_usage": {
                    "cpu": "< 85%",
                    "memory": "< 4GB",
                    "gpu": "< 90%",
                    "npu": "< 90%"
                },
                "success_rate": "> 99.5%"
            },
            priority="critical",
            tags=["performance", "concurrent", "multi-model"],
            timeout=3600
        )
        self.add_test_case(tc_004)

        # TC-005: 高压力转换性能测试
        tc_005 = TestCase(
            id="TC-005",
            name="高压力转换性能测试",
            description="测试系统在高压下的性能表现",
            category="stress_test",
            model_type="mixed",
            model_name="Stress Test Models",
            parameters={
                "target_throughput": 20,
                "ramp_up_time": 600,  # 10分钟
                "steady_state_time": 3600,  # 1小时
                "ramp_down_time": 600,  # 10分钟
                "batch_size": 8,
                "precision": "fp16",
                "monitor_interval": 60
            },
            expected_results={
                "no_errors": True,
                "no_performance_degradation": True,
                "resource_usage_stable": True,
                "throughput_maintained": "> 90% of target",
                "error_rate": "< 0.1%"
            },
            priority="critical",
            tags=["stress", "performance", "stability"],
            timeout=7200
        )
        self.add_test_case(tc_005)

        # TC-006: 24小时长期稳定性测试
        tc_006 = TestCase(
            id="TC-006",
            name="24小时长期稳定性测试",
            description="测试系统长期运行的稳定性",
            category="stability_test",
            model_type="mixed",
            model_name="Stability Test Models",
            parameters={
                "average_throughput": 10,
                "batch_size": 4,
                "precision": "fp16",
                "monitoring_interval": 300,  # 5分钟
                "total_duration": 86400,  # 24小时
                "model_rotation": True
            },
            expected_results={
                "no_memory_leaks": True,
                "no_performance_degradation": True,
                "error_rate": "< 0.1%",
                "resource_usage_stable": True,
                "availability": "> 99.9%"
            },
            priority="critical",
            tags=["stability", "long-term", "reliability"],
            timeout=90000
        )
        self.add_test_case(tc_006)

        # TC-007: 内存泄漏测试
        tc_007 = TestCase(
            id="TC-007",
            name="内存泄漏测试",
            description="检测系统是否存在内存泄漏",
            category="stability_test",
            model_type="mixed",
            model_name="Memory Leak Test Models",
            parameters={
                "test_duration": 3600,  # 1小时
                "conversion_frequency": 60,  # 每60秒一次转换
                "batch_size": 4,
                "precision": "fp16",
                "memory_threshold": "5GB"
            },
            expected_results={
                "memory_growth_rate": "< 1% per hour",
                "no_memory_leaks": True,
                "gc_effective": True,
                "max_memory_usage": "< 4GB"
            },
            priority="high",
            tags=["memory", "leak", "stability"],
            timeout=4500
        )
        self.add_test_case(tc_007)

        # TC-008: 性能回归测试
        tc_008 = TestCase(
            id="TC-008",
            name="性能回归测试",
            description="对比历史性能数据，检测性能回归",
            category="regression_test",
            model_type="mixed",
            model_name="Regression Test Models",
            parameters={
                "baseline_version": "previous",
                "current_version": "current",
                "test_models": ["SenseVoice", "VITS-Cantonese", "Piper-VITS"],
                "batch_size": 4,
                "precision": "fp16",
                "iterations": 10
            },
            expected_results={
                "throughput_regression": "< 5%",
                "latency_regression": "< 5%",
                "resource_usage_regression": "< 10%",
                "no_critical_issues": True
            },
            priority="high",
            tags=["regression", "performance", "comparison"],
            timeout=3600
        )
        self.add_test_case(tc_008)

        logger.info(f"Loaded {len(self.test_cases)} built-in test cases")

    def _load_test_cases_from_file(self):
        """从文件加载测试用例"""
        test_cases_file = Path(self.config.test_data_dir) / self.config.test_cases_file

        if not test_cases_file.exists():
            logger.info(f"Test cases file not found: {test_cases_file}")
            # 创建示例文件
            self._create_example_test_cases_file(test_cases_file)
            return

        try:
            with open(test_cases_file, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)

            if 'test_cases' in data:
                for item in data['test_cases']:
                    test_case = TestCase(
                        id=item['id'],
                        name=item['name'],
                        description=item.get('description', ''),
                        category=item.get('category', ''),
                        model_type=item.get('model_type', ''),
                        model_name=item.get('model_name', ''),
                        parameters=item.get('parameters', {}),
                        expected_results=item.get('expected_results', {}),
                        timeout=item.get('timeout'),
                        priority=item.get('priority', 'medium'),
                        tags=item.get('tags', []),
                        dependencies=item.get('dependencies', []),
                        setup_script=item.get('setup_script'),
                        cleanup_script=item.get('cleanup_script')
                    )

                    # 如果ID不存在则添加
                    if test_case.id not in self.test_cases:
                        self.add_test_case(test_case)

            logger.info(f"Loaded test cases from file: {test_cases_file}")

        except Exception as e:
            logger.error(f"Error loading test cases from file: {e}")

    def _create_example_test_cases_file(self, file_path: Path):
        """创建示例测试用例文件"""
        example_data = {
            'test_cases': [
                {
                    'id': 'TC-009',
                    'name': '自定义测试用例',
                    'description': '用户自定义的测试用例示例',
                    'category': 'single_model',
                    'model_type': 'asr',
                    'model_name': 'CustomASR',
                    'parameters': {
                        'model_path': '/models/custom',
                        'batch_size': 4,
                        'precision': 'fp16'
                    },
                    'expected_results': {
                        'throughput': '> 10 models/minute',
                        'latency_p95': '< 60 seconds'
                    },
                    'timeout': 1800,
                    'priority': 'medium',
                    'tags': ['custom', 'example']
                }
            ]
        }

        with open(file_path, 'w', encoding='utf-8') as f:
            yaml.dump(example_data, f, default_flow_style=False, allow_unicode=True)

        logger.info(f"Created example test cases file: {file_path}")

    def add_test_case(self, test_case: TestCase):
        """
        添加测试用例

        Args:
            test_case: 测试用例
        """
        if test_case.validate():
            self.test_cases[test_case.id] = test_case
            logger.info(f"Added test case: {test_case.id}")
        else:
            logger.error(f"Invalid test case: {test_case.id}")

    def remove_test_case(self, test_id: str) -> bool:
        """
        删除测试用例

        Args:
            test_id: 测试用例ID

        Returns:
            bool: 是否成功删除
        """
        if test_id in self.test_cases:
            del self.test_cases[test_id]
            logger.info(f"Removed test case: {test_id}")
            return True
        return False

    def get_test_case(self, test_id: str) -> Optional[TestCase]:
        """
        获取指定测试用例

        Args:
            test_id: 测试用例ID

        Returns:
            Optional[TestCase]: 测试用例
        """
        return self.test_cases.get(test_id)

    def list_test_cases(self, category: Optional[str] = None,
                       tags: Optional[List[str]] = None) -> List[TestCase]:
        """
        列出测试用例

        Args:
            category: 分类过滤
            tags: 标签过滤

        Returns:
            List[TestCase]: 测试用例列表
        """
        test_cases = list(self.test_cases.values())

        # 按分类过滤
        if category:
            test_cases = [tc for tc in test_cases if tc.category == category]

        # 按标签过滤
        if tags:
            test_cases = [tc for tc in test_cases
                         if any(tag in tc.tags for tag in tags)]

        return test_cases

    def list_categories(self) -> List[str]:
        """列出所有分类"""
        return list(self.CATEGORIES.keys())

    def list_model_types(self) -> List[str]:
        """列出所有模型类型"""
        return list(self.MODEL_TYPES.keys())

    def validate_test_case(self, test_case: TestCase) -> ValidationResult:
        """
        验证测试用例

        Args:
            test_case: 测试用例

        Returns:
            ValidationResult: 验证结果
        """
        errors = []
        warnings = []

        # 检查必填字段
        if not test_case.id:
            errors.append("Test case ID is required")
        elif test_case.id in self.test_cases:
            warnings.append(f"Test case ID {test_case.id} already exists")

        if not test_case.name:
            errors.append("Test case name is required")

        if not test_case.category:
            errors.append("Test case category is required")
        elif test_case.category not in self.CATEGORIES:
            warnings.append(f"Unknown category: {test_case.category}")

        if not test_case.model_type:
            errors.append("Model type is required")
        elif test_case.model_type not in self.MODEL_TYPES:
            warnings.append(f"Unknown model type: {test_case.model_type}")

        if not test_case.parameters:
            warnings.append("No parameters defined")

        if not test_case.expected_results:
            warnings.append("No expected results defined")

        # 检查超时时间
        if test_case.timeout and test_case.timeout > 86400:  # 24小时
            warnings.append("Timeout is very long (> 24 hours)")

        # 检查优先级
        if test_case.priority not in ['low', 'medium', 'high', 'critical']:
            warnings.append(f"Invalid priority: {test_case.priority}")

        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings
        )

    def create_test_suite(self, name: str, description: str,
                          test_case_ids: List[str]) -> TestSuite:
        """
        创建测试套件

        Args:
            name: 套件名称
            description: 套件描述
            test_case_ids: 测试用例ID列表

        Returns:
            TestSuite: 测试套件
        """
        test_cases = []
        for tc_id in test_case_ids:
            tc = self.get_test_case(tc_id)
            if tc:
                test_cases.append(tc)
            else:
                logger.warning(f"Test case not found: {tc_id}")

        suite = TestSuite(
            name=name,
            description=description,
            version="1.0.0",
            test_cases=test_cases,
            metadata={'created_by': 'BenchmarkSuite'},
            created_date=datetime.now(),
            modified_date=datetime.now()
        )

        self.test_suites[name] = suite
        logger.info(f"Created test suite: {name} with {len(test_cases)} test cases")

        return suite

    def get_test_suite(self, name: str) -> Optional[TestSuite]:
        """
        获取测试套件

        Args:
            name: 套件名称

        Returns:
            Optional[TestSuite]: 测试套件
        """
        return self.test_suites.get(name)

    def list_test_suites(self) -> List[TestSuite]:
        """列出所有测试套件"""
        return list(self.test_suites.values())

    def generate_parameterized_tests(self, base_test_id: str,
                                    parameter_combinations: List[Dict[str, Any]]) -> List[TestCase]:
        """
        生成参数化测试用例

        Args:
            base_test_id: 基础测试用例ID
            parameter_combinations: 参数组合列表

        Returns:
            List[TestCase]: 参数化测试用例列表
        """
        base_test = self.get_test_case(base_test_id)
        if not base_test:
            logger.error(f"Base test case not found: {base_test_id}")
            return []

        parameterized_tests = []

        for i, params in enumerate(parameter_combinations, 1):
            # 合并参数
            combined_params = base_test.parameters.copy()
            combined_params.update(params)

            # 创建新测试用例
            test_id = f"{base_test.id}-P{i}"
            test_case = TestCase(
                id=test_id,
                name=f"{base_test.name} (Params {i})",
                description=base_test.description,
                category=base_test.category,
                model_type=base_test.model_type,
                model_name=base_test.model_name,
                parameters=combined_params,
                expected_results=base_test.expected_results,
                timeout=base_test.timeout,
                priority=base_test.priority,
                tags=base_test.tags + ['parameterized'],
                dependencies=base_test.dependencies
            )

            parameterized_tests.append(test_case)

        logger.info(f"Generated {len(parameterized_tests)} parameterized tests from {base_test_id}")

        return parameterized_tests

    def export_test_cases(self, output_file: str, format: str = "yaml"):
        """
        导出测试用例

        Args:
            output_file: 输出文件路径
            format: 格式 (yaml, json)
        """
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        data = {
            'test_cases': [tc.to_dict() for tc in self.test_cases.values()],
            'metadata': {
                'total': len(self.test_cases),
                'exported_at': datetime.now().isoformat()
            }
        }

        if format.lower() == "json":
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        else:  # yaml
            with open(output_path, 'w', encoding='utf-8') as f:
                yaml.dump(data, f, default_flow_style=False, allow_unicode=True)

        logger.info(f"Exported {len(self.test_cases)} test cases to {output_file}")

    def get_statistics(self) -> Dict[str, Any]:
        """
        获取测试用例统计信息

        Returns:
            Dict: 统计信息
        """
        categories = {}
        model_types = {}
        priorities = {}

        for tc in self.test_cases.values():
            # 分类统计
            categories[tc.category] = categories.get(tc.category, 0) + 1

            # 模型类型统计
            model_types[tc.model_type] = model_types.get(tc.model_type, 0) + 1

            # 优先级统计
            priorities[tc.priority] = priorities.get(tc.priority, 0) + 1

        return {
            'total_test_cases': len(self.test_cases),
            'total_test_suites': len(self.test_suites),
            'categories': categories,
            'model_types': model_types,
            'priorities': priorities,
            'average_timeout': sum(tc.timeout for tc in self.test_cases.values()) / len(self.test_cases) if self.test_cases else 0
        }


if __name__ == "__main__":
    # 示例使用
    config = SuiteConfig(
        test_data_dir="data/benchmarks",
        test_cases_file="test_cases.yaml",
        default_timeout=3600
    )

    suite = BenchmarkSuite(config)

    # 获取统计信息
    stats = suite.get_statistics()
    print(f"Test suite statistics: {stats}")

    # 列出所有测试用例
    test_cases = suite.list_test_cases()
    print(f"Total test cases: {len(test_cases)}")

    # 获取特定测试用例
    tc = suite.get_test_case("TC-001")
    if tc:
        print(f"Test case: {tc.name}")
        print(f"Parameters: {tc.parameters}")

    # 创建测试套件
    test_suite = suite.create_test_suite(
        name="Performance Test Suite",
        description="Performance and stress test suite",
        test_case_ids=["TC-001", "TC-002", "TC-003"]
    )

    # 生成参数化测试
    param_combinations = [
        {"batch_size": 4, "precision": "fp16"},
        {"batch_size": 8, "precision": "fp16"},
        {"batch_size": 16, "precision": "fp16"}
    ]
    parameterized_tests = suite.generate_parameterized_tests("TC-001", param_combinations)
    print(f"Generated {len(parameterized_tests)} parameterized tests")
