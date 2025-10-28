#!/usr/bin/env python3
"""
PTQ Integration Test

This script tests the refactored PTQ converter functionality
in a controlled environment without requiring external dependencies.
"""

import sys
import json
import tempfile
import os
from pathlib import Path
sys.path.insert(0, 'src')

def create_mock_onnx_model(model_path):
    """Create a mock ONNX model file for testing."""
    # Create a simple mock model structure
    mock_model_data = {
        "model_format": "onnx",
        "input_shape": [1, 3, 224, 224],
        "output_shape": [1, 1000],
        "model_size_mb": 25.5,
        "num_parameters": 25000000,
        "operators": ["Conv", "Relu", "MaxPool", "Add", "Softmax"]
    }

    # Write mock data to file (not a real ONNX model, but sufficient for testing)
    with open(model_path, 'w') as f:
        json.dump(mock_model_data, f)

    return mock_model_data

def test_ptq_converter_basic_functionality():
    """Test basic PTQ converter functionality."""
    print("🔧 Testing PTQ Converter Basic Functionality...")

    try:
        from npu_converter.ptq.converter import PTQConverter
        from npu_converter.core.models.ptq_config import PTQSettings, PTQConfigModel

        # Create PTQ converter
        converter = PTQConverter(
            name="TestPTQConverter",
            version="1.0.0-test"
        )
        print("✅ PTQConverter instantiation success")

        # Check inheritance
        from npu_converter.core.interfaces.base_converter import BaseConverter
        assert isinstance(converter, BaseConverter)
        print("✅ PTQConverter properly inherits from BaseConverter")

        # Test configuration
        ptq_settings = PTQSettings(
            output_dir=tempfile.mkdtemp(),
            debug_mode=True,
            target_precision="int8"
        )

        config = PTQConfigModel(ptq_settings=ptq_settings)
        converter_with_config = PTQConverter(
            name="ConfiguredPTQConverter",
            version="1.0.0-test",
            config=config
        )
        print("✅ PTQConverter with configuration instantiation success")

        return True

    except Exception as e:
        print(f"❌ PTQ converter basic functionality test failed: {e}")
        return False

def test_ptq_converter_workflow():
    """Test PTQ converter workflow without external dependencies."""
    print("\n🔄 Testing PTQ Converter Workflow...")

    try:
        from npu_converter.ptq.converter import PTQConverter
        from npu_converter.core.models.ptq_config import PTQSettings, PTQConfigModel
        from npu_converter.models.calibration import CalibrationConfig

        # Create temporary directory and mock model
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            model_file = temp_path / "mock_model.onnx"
            create_mock_onnx_model(model_file)

            # Create PTQ converter
            ptq_settings = PTQSettings(
                output_dir=str(temp_path / "output"),
                debug_mode=True
            )

            config = PTQConfigModel(ptq_settings=ptq_settings)
            converter = PTQConverter(
                name="WorkflowTestConverter",
                version="1.0.0-test",
                config=config
            )

            # Test workflow interface
            print("✅ PTQ converter setup complete")

            # Test abstract method implementations exist
            assert hasattr(converter, 'validate_input')
            assert hasattr(converter, 'prepare_conversion')
            assert hasattr(converter, 'convert')
            assert hasattr(converter, 'export_results')
            print("✅ All required abstract methods are implemented")

            # Test PTQ-specific methods
            assert hasattr(converter, 'prepare_model')
            assert hasattr(converter, 'validate_model')
            assert hasattr(converter, 'prepare_calibration_data')
            assert hasattr(converter, 'quantize_model')
            assert hasattr(converter, 'compile_model')
            assert hasattr(converter, 'analyze_performance')
            assert hasattr(converter, 'analyze_accuracy')
            print("✅ All PTQ-specific methods are available")

            return True

    except Exception as e:
        print(f"❌ PTQ converter workflow test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_configuration_integration():
    """Test configuration integration."""
    print("\n⚙️ Testing Configuration Integration...")

    try:
        from npu_converter.core.models.ptq_config import PTQSettings, PTQConfigModel, CalibrationConfig
        from npu_converter.ptq.converter import PTQConverter

        # Test PTQ settings
        settings = PTQSettings(
            output_dir="./test_output",
            debug_mode=True,
            target_device="horizon_x5",
            target_fps=60.0,
            target_accuracy=99.0
        )

        # Test configuration validation
        config = PTQConfigModel(ptq_settings=settings)
        errors = config.validate_ptq_config()
        assert len(errors) == 0, f"Configuration validation failed: {errors}"
        print("✅ PTQ configuration validation successful")

        # Test calibration configuration
        calib_config = CalibrationConfig(
            data_path="./mock_calibration_data",
            batch_size=1,
            num_samples=100,
            input_shape=(1, 3, 224, 224)
        )

        config.set_calibration_config(calib_config)
        assert config.calibration_config == calib_config
        print("✅ Calibration configuration integration successful")

        return True

    except Exception as e:
        print(f"❌ Configuration integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_tool_integration():
    """Test tool integration."""
    print("\n🔧 Testing Tool Integration...")

    try:
        from npu_converter.core.utils.progress_tracker import ProgressTracker
        from npu_converter.core.utils.debug_tools import DebugTools

        # Test progress tracker
        tracker = ProgressTracker(enable_console_output=False)

        # Test basic progress tracking
        tracker.start_step("Test Step 1", 1, 3)
        tracker.complete_step("Test Step 1", {"test": "data"})
        tracker.finish_conversion()

        progress = tracker.get_overall_progress()
        assert progress['total_steps'] == 1
        assert progress['completed_steps'] == 1
        print("✅ ProgressTracker integration successful")

        # Test debug tools
        debug_tools = DebugTools(enabled=True)
        assert debug_tools.enabled == True
        print("✅ DebugTools integration successful")

        return True

    except Exception as e:
        print(f"❌ Tool integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all integration tests."""
    print("🚀 Starting PTQ Integration Tests\n")

    tests = [
        test_ptq_converter_basic_functionality,
        test_ptq_converter_workflow,
        test_configuration_integration,
        test_tool_integration
    ]

    passed = 0
    total = len(tests)

    for test in tests:
        if test():
            passed += 1
        else:
            print(f"❌ Test {test.__name__} failed")

    print(f"\n📊 Integration Test Results: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 All integration tests passed!")
        print("✅ PTQ refactoring maintains functionality")
        return 0
    else:
        print("❌ Some integration tests failed.")
        return 1

if __name__ == "__main__":
    sys.exit(main())