"""
测试用例套件单元测试

测试BenchmarkSuite类的所有功能，包括测试用例管理、
参数化测试、套件创建等功能。

作者: BMAD Method
创建日期: 2025-10-29
版本: v1.0
"""

import pytest
import tempfile
import shutil
from datetime import datetime
from pathlib import Path
import sys
import yaml

# 添加源码路径
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / 'src'))

from npu_converter.performance.benchmark_suite import (
    BenchmarkSuite,
    SuiteConfig,
    TestCase,
    TestSuite,
    ValidationResult
)


class TestSuiteConfig:
    """测试SuiteConfig配置类"""

    def test_default_config(self):
        """测试默认配置"""
        config = SuiteConfig()
        assert config.test_data_dir == "data/benchmarks"
        assert config.test_cases_file == "test_cases.yaml"
        assert config.default_timeout == 3600
        assert config.max_retries == 3
        assert config.parallel_execution is True
        assert config.enable_validation is True
        assert config.auto_cleanup is True

    def test_custom_config(self):
        """测试自定义配置"""
        config = SuiteConfig(
            test_data_dir="/tmp/test",
            test_cases_file="custom.yaml",
            default_timeout=1800,
            parallel_execution=False
        )
        assert config.test_data_dir == "/tmp/test"
        assert config.test_cases_file == "custom.yaml"
        assert config.default_timeout == 1800
        assert config.parallel_execution is False


class TestTestCase:
    """测试TestCase测试用例类"""

    def test_create_test_case(self):
        """测试创建测试用例"""
        test_case = TestCase(
            id="TC-001",
            name="测试用例1",
            description="测试描述",
            category="single_model",
            model_type="asr",
            model_name="SenseVoice",
            parameters={"batch_size": 4},
            expected_results={"throughput": "> 10"}
        )

        assert test_case.id == "TC-001"
        assert test_case.name == "测试用例1"
        assert test_case.category == "single_model"
        assert test_case.model_type == "asr"
        assert test_case.timeout == 3600  # 默认超时
        assert test_case.tags == []
        assert test_case.dependencies == []

    def test_create_test_case_with_optional(self):
        """测试创建带可选字段的测试用例"""
        test_case = TestCase(
            id="TC-002",
            name="测试用例2",
            description="测试描述",
            category="concurrent",
            model_type="mixed",
            model_name="Mixed",
            parameters={"batch_size": 8},
            expected_results={"throughput": "> 20"},
            timeout=1800,
            priority="high",
            tags=["performance", "concurrent"],
            dependencies=["TC-001"],
            setup_script="setup.sh",
            cleanup_script="cleanup.sh"
        )

        assert test_case.timeout == 1800
        assert test_case.priority == "high"
        assert test_case.tags == ["performance", "concurrent"]
        assert test_case.dependencies == ["TC-001"]
        assert test_case.setup_script == "setup.sh"
        assert test_case.cleanup_script == "cleanup.sh"

    def test_test_case_to_dict(self):
        """测试测试用例转换为字典"""
        test_case = TestCase(
            id="TC-003",
            name="测试用例3",
            description="测试描述",
            category="single_model",
            model_type="asr",
            model_name="SenseVoice",
            parameters={"batch_size": 4},
            expected_results={"throughput": "> 10"}
        )

        result = test_case.to_dict()
        assert result['id'] == "TC-003"
        assert result['name'] == "测试用例3"
        assert result['category'] == "single_model"
        assert result['timeout'] == 3600

    def test_test_case_validate(self):
        """测试测试用例验证"""
        # 有效的测试用例
        valid_case = TestCase(
            id="TC-VALID",
            name="有效测试用例",
            description="测试描述",
            category="single_model",
            model_type="asr",
            model_name="SenseVoice",
            parameters={"batch_size": 4},
            expected_results={"throughput": "> 10"}
        )
        assert valid_case.validate() is True

        # 无效的测试用例 - 缺少必填字段
        invalid_case = TestCase(
            id="",  # 缺少ID
            name="",  # 缺少名称
            description="测试描述",
            category="single_model",
            model_type="asr",
            model_name="SenseVoice",
            parameters={"batch_size": 4},
            expected_results={"throughput": "> 10"}
        )
        assert invalid_case.validate() is False


class TestBenchmarkSuite:
    """测试BenchmarkSuite套件类"""

    @pytest.fixture
    def temp_dir(self):
        """创建临时目录"""
        temp_path = tempfile.mkdtemp()
        yield temp_path
        shutil.rmtree(temp_path, ignore_errors=True)

    @pytest.fixture
    def suite(self, temp_dir):
        """创建BenchmarkSuite实例"""
        config = SuiteConfig(
            test_data_dir=temp_dir,
            test_cases_file="test_cases.yaml"
        )
        return BenchmarkSuite(config)

    def test_initialize_suite(self, temp_dir):
        """测试初始化套件"""
        config = SuiteConfig(test_data_dir=temp_dir)
        suite = BenchmarkSuite(config)

        assert config.test_data_dir == temp_dir
        assert len(suite.test_cases) > 0  # 应该加载了内置测试用例
        assert len(suite.test_suites) == 0

    def test_load_builtin_test_cases(self, temp_dir):
        """测试加载内置测试用例"""
        config = SuiteConfig(test_data_dir=temp_dir)
        suite = BenchmarkSuite(config)

        # 应该加载了8个内置测试用例
        assert len(suite.test_cases) >= 8

        # 检查内置测试用例
        assert "TC-001" in suite.test_cases
        assert "TC-002" in suite.test_cases
        assert "TC-003" in suite.test_cases
        assert "TC-004" in suite.test_cases

        # 验证测试用例
        tc = suite.test_cases["TC-001"]
        assert tc.name == "SenseVoice ASR模型转换性能测试"
        assert tc.category == "single_model"
        assert tc.model_type == "asr"

    def test_add_test_case(self, suite):
        """测试添加测试用例"""
        initial_count = len(suite.test_cases)

        test_case = TestCase(
            id="TC-NEW",
            name="新测试用例",
            description="新测试描述",
            category="single_model",
            model_type="asr",
            model_name="Custom",
            parameters={"batch_size": 4},
            expected_results={"throughput": "> 10"}
        )

        suite.add_test_case(test_case)

        assert len(suite.test_cases) == initial_count + 1
        assert "TC-NEW" in suite.test_cases
        assert suite.test_cases["TC-NEW"].name == "新测试用例"

    def test_add_invalid_test_case(self, suite):
        """测试添加无效测试用例"""
        initial_count = len(suite.test_cases)

        # 无效的测试用例（缺少必填字段）
        test_case = TestCase(
            id="",  # 缺少ID
            name="无效测试用例",
            description="无效描述",
            category="",
            model_type="asr",
            model_name="Custom",
            parameters={},
            expected_results={}
        )

        suite.add_test_case(test_case)

        # 不应该添加
        assert len(suite.test_cases) == initial_count
        assert "TC-NEW" not in suite.test_cases

    def test_remove_test_case(self, suite):
        """测试删除测试用例"""
        # 添加测试用例
        test_case = TestCase(
            id="TC-REMOVE",
            name="删除测试",
            description="删除测试描述",
            category="single_model",
            model_type="asr",
            model_name="Custom",
            parameters={"batch_size": 4},
            expected_results={"throughput": "> 10"}
        )

        suite.add_test_case(test_case)
        assert "TC-REMOVE" in suite.test_cases

        # 删除测试用例
        result = suite.remove_test_case("TC-REMOVE")
        assert result is True
        assert "TC-REMOVE" not in suite.test_cases

        # 删除不存在的测试用例
        result = suite.remove_test_case("TC-NONEXISTENT")
        assert result is False

    def test_get_test_case(self, suite):
        """测试获取测试用例"""
        # 获取存在的测试用例
        tc = suite.get_test_case("TC-001")
        assert tc is not None
        assert tc.id == "TC-001"

        # 获取不存在的测试用例
        tc = suite.get_test_case("TC-NONEXISTENT")
        assert tc is None

    def test_list_test_cases_no_filter(self, suite):
        """测试列出所有测试用例"""
        test_cases = suite.list_test_cases()

        assert isinstance(test_cases, list)
        assert len(test_cases) >= 8

        # 所有测试用例都应该是TestCase实例
        for tc in test_cases:
            assert isinstance(tc, TestCase)

    def test_list_test_cases_by_category(self, suite):
        """测试按分类列出测试用例"""
        single_model_tests = suite.list_test_cases(category="single_model")

        assert isinstance(single_model_tests, list)
        assert len(single_model_tests) >= 3  # 至少3个单模型测试

        for tc in single_model_tests:
            assert tc.category == "single_model"

        # 不存在的分类
        nonexistent_tests = suite.list_test_cases(category="nonexistent")
        assert len(nonexistent_tests) == 0

    def test_list_test_cases_by_tags(self, suite):
        """测试按标签列出测试用例"""
        performance_tests = suite.list_test_cases(tags=["performance"])

        assert isinstance(performance_tests, list)
        assert len(performance_tests) > 0

        for tc in performance_tests:
            assert "performance" in tc.tags

    def test_list_categories(self, suite):
        """测试列出所有分类"""
        categories = suite.list_categories()

        assert isinstance(categories, list)
        assert "single_model" in categories
        assert "concurrent" in categories
        assert "stress_test" in categories
        assert "stability_test" in categories

    def test_list_model_types(self, suite):
        """测试列出所有模型类型"""
        model_types = suite.list_model_types()

        assert isinstance(model_types, list)
        assert "asr" in model_types
        assert "tts" in model_types

    def test_validate_test_case(self, suite):
        """测试验证测试用例"""
        # 有效的测试用例
        valid_case = TestCase(
            id="TC-VALID",
            name="有效测试",
            description="测试描述",
            category="single_model",
            model_type="asr",
            model_name="Custom",
            parameters={"batch_size": 4},
            expected_results={"throughput": "> 10"}
        )

        result = suite.validate_test_case(valid_case)
        assert isinstance(result, ValidationResult)
        assert result.is_valid is True
        assert len(result.errors) == 0

        # 无效的测试用例
        invalid_case = TestCase(
            id="",  # 缺少ID
            name="",  # 缺少名称
            description="测试描述",
            category="invalid",  # 不存在的分类
            model_type="asr",
            model_name="Custom",
            parameters={},
            expected_results={}
        )

        result = suite.validate_test_case(invalid_case)
        assert result.is_valid is False
        assert len(result.errors) > 0

        # 警告情况
        warning_case = TestCase(
            id="TC-WARNING",
            name="警告测试",
            description="测试描述",
            category="single_model",
            model_type="asr",
            model_name="Custom",
            parameters={},
            expected_results={},
            timeout=90000  # 超时时间过长
        )

        result = suite.validate_test_case(warning_case)
        assert result.is_valid is True
        assert len(result.warnings) > 0

    def test_create_test_suite(self, suite):
        """测试创建测试套件"""
        test_case_ids = ["TC-001", "TC-002", "TC-003"]

        test_suite = suite.create_test_suite(
            name="测试套件1",
            description="这是一个测试套件",
            test_case_ids=test_case_ids
        )

        assert isinstance(test_suite, TestSuite)
        assert test_suite.name == "测试套件1"
        assert test_suite.description == "这是一个测试套件"
        assert len(test_suite.test_cases) == 3

        # 检查测试套件是否已保存
        assert "测试套件1" in suite.test_suites

    def test_get_test_suite(self, suite):
        """测试获取测试套件"""
        # 创建测试套件
        suite.create_test_suite(
            name="获取测试套件",
            description="测试获取功能",
            test_case_ids=["TC-001"]
        )

        # 获取测试套件
        result = suite.get_test_suite("获取测试套件")
        assert result is not None
        assert result.name == "获取测试套件"

        # 获取不存在的测试套件
        result = suite.get_test_suite("不存在")
        assert result is None

    def test_list_test_suites(self, suite):
        """测试列出测试套件"""
        # 创建测试套件
        suite.create_test_suite(
            name="套件1",
            description="描述1",
            test_case_ids=["TC-001"]
        )
        suite.create_test_suite(
            name="套件2",
            description="描述2",
            test_case_ids=["TC-002"]
        )

        suites = suite.list_test_suites()
        assert len(suites) == 2

    def test_generate_parameterized_tests(self, suite):
        """测试生成参数化测试用例"""
        base_test_id = "TC-001"
        parameter_combinations = [
            {"batch_size": 4, "precision": "fp16"},
            {"batch_size": 8, "precision": "fp16"},
            {"batch_size": 16, "precision": "fp16"}
        ]

        parameterized_tests = suite.generate_parameterized_tests(
            base_test_id,
            parameter_combinations
        )

        assert len(parameterized_tests) == 3

        # 检查参数化测试
        for i, test in enumerate(parameterized_tests, 1):
            assert test.id == f"TC-001-P{i}"
            assert "parameterized" in test.tags
            assert test.parameters["batch_size"] in [4, 8, 16]
            assert test.parameters["precision"] == "fp16"

    def test_generate_parameterized_tests_nonexistent(self, suite):
        """测试为不存在的测试用例生成参数化测试"""
        parameter_combinations = [{"batch_size": 4}]
        result = suite.generate_parameterized_tests("TC-NONEXISTENT", parameter_combinations)
        assert len(result) == 0

    def test_export_test_cases_yaml(self, temp_dir):
        """测试导出测试用例为YAML"""
        config = SuiteConfig(test_data_dir=temp_dir)
        suite = BenchmarkSuite(config)

        output_file = Path(temp_dir) / "exported_test_cases.yaml"
        suite.export_test_cases(str(output_file), format="yaml")

        assert output_file.exists()

        # 验证文件内容
        with open(output_file, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
            assert 'test_cases' in data
            assert 'metadata' in data
            assert data['metadata']['total'] >= 8

    def test_export_test_cases_json(self, temp_dir):
        """测试导出测试用例为JSON"""
        config = SuiteConfig(test_data_dir=temp_dir)
        suite = BenchmarkSuite(config)

        output_file = Path(temp_dir) / "exported_test_cases.json"
        suite.export_test_cases(str(output_file), format="json")

        assert output_file.exists()

    def test_get_statistics(self, suite):
        """测试获取统计信息"""
        stats = suite.get_statistics()

        assert 'total_test_cases' in stats
        assert 'total_test_suites' in stats
        assert 'categories' in stats
        assert 'model_types' in stats
        assert 'priorities' in stats
        assert 'average_timeout' in stats

        assert stats['total_test_cases'] >= 8
        assert stats['total_test_suites'] == 0
        assert 'single_model' in stats['categories']

    def test_builtin_models(self, suite):
        """测试内置模型"""
        assert "SenseVoice" in suite.BUILTIN_MODELS
        assert "VITS-Cantonese" in suite.BUILTIN_MODELS
        assert "Piper-VITS" in suite.BUILTIN_MODELS

        # 验证模型信息
        sensevoice = suite.BUILTIN_MODELS["SenseVoice"]
        assert sensevoice['type'] == 'asr'
        assert sensevoice['description'] == 'SenseVoice ASR模型'

    def test_file_loading(self, temp_dir):
        """测试从文件加载测试用例"""
        # 创建测试用例文件
        test_cases_file = Path(temp_dir) / "custom_test_cases.yaml"
        with open(test_cases_file, 'w', encoding='utf-8') as f:
            yaml.dump({
                'test_cases': [
                    {
                        'id': 'TC-FILE-001',
                        'name': '文件测试用例',
                        'description': '从文件加载的测试用例',
                        'category': 'single_model',
                        'model_type': 'asr',
                        'model_name': 'FileTest',
                        'parameters': {'batch_size': 4},
                        'expected_results': {'throughput': '> 10'}
                    }
                ]
            }, f, default_flow_style=False, allow_unicode=True)

        # 重新初始化套件（会加载文件）
        config = SuiteConfig(
            test_data_dir=temp_dir,
            test_cases_file="custom_test_cases.yaml"
        )
        suite = BenchmarkSuite(config)

        # 检查是否加载了文件中的测试用例
        assert "TC-FILE-001" in suite.test_cases


class TestTestSuite:
    """测试TestSuite测试套件类"""

    def test_create_test_suite(self):
        """测试创建测试套件"""
        test_cases = [
            TestCase(
                id="TC-001",
                name="测试1",
                description="描述1",
                category="single_model",
                model_type="asr",
                model_name="Test",
                parameters={},
                expected_results={}
            ),
            TestCase(
                id="TC-002",
                name="测试2",
                description="描述2",
                category="single_model",
                model_type="asr",
                model_name="Test",
                parameters={},
                expected_results={}
            )
        ]

        suite = TestSuite(
            name="测试套件",
            description="测试套件描述",
            version="1.0.0",
            test_cases=test_cases,
            metadata={'author': 'test'},
            created_date=datetime.now(),
            modified_date=datetime.now()
        )

        assert suite.name == "测试套件"
        assert len(suite.test_cases) == 2
        assert suite.metadata['author'] == 'test'

    def test_test_suite_to_dict(self):
        """测试测试套件转换为字典"""
        test_cases = [
            TestCase(
                id="TC-001",
                name="测试1",
                description="描述1",
                category="single_model",
                model_type="asr",
                model_name="Test",
                parameters={},
                expected_results={}
            )
        ]

        now = datetime.now()
        suite = TestSuite(
            name="测试套件",
            description="测试套件描述",
            version="1.0.0",
            test_cases=test_cases,
            metadata={'author': 'test'},
            created_date=now,
            modified_date=now
        )

        result = suite.to_dict()
        assert result['name'] == "测试套件"
        assert result['version'] == "1.0.0"
        assert len(result['test_cases']) == 1


class TestValidationResult:
    """测试ValidationResult验证结果类"""

    def test_create_validation_result(self):
        """测试创建验证结果"""
        result = ValidationResult(
            is_valid=True,
            errors=[],
            warnings=["这是一个警告"]
        )

        assert result.is_valid is True
        assert len(result.errors) == 0
        assert len(result.warnings) == 1

    def test_validation_result_to_dict(self):
        """测试验证结果转换为字典"""
        result = ValidationResult(
            is_valid=False,
            errors=["错误1", "错误2"],
            warnings=["警告1"]
        )

        result_dict = result.to_dict()
        assert result_dict['is_valid'] is False
        assert len(result_dict['errors']) == 2
        assert len(result_dict['warnings']) == 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
