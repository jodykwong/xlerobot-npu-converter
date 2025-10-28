#!/usr/bin/env python3
"""
Architectural Integration Test

This script tests the architectural integration of the refactored PTQ system
without importing modules that have external dependencies.
"""

import sys
import inspect
sys.path.insert(0, 'src')

def test_core_architecture():
    """Test core architecture components."""
    print("🏗️ Testing Core Architecture Components...")

    try:
        # Test BaseConverter abstract base class
        from npu_converter.core.interfaces.base_converter import BaseConverter

        # Check abstract methods
        abstract_methods = BaseConverter.__abstractmethods__
        required_methods = {'validate_input', 'prepare_conversion', 'convert', 'export_results'}

        assert required_methods.issubset(abstract_methods), f"Missing abstract methods: {required_methods - abstract_methods}"
        print("✅ BaseConverter has all required abstract methods")

        # Check it's actually abstract
        try:
            BaseConverter("test", "1.0")
            assert False, "BaseConverter should be abstract"
        except TypeError:
            print("✅ BaseConverter is properly abstract")

        return True

    except Exception as e:
        print(f"❌ Core architecture test failed: {e}")
        return False

def test_configuration_architecture():
    """Test configuration architecture."""
    print("\n⚙️ Testing Configuration Architecture...")

    try:
        from npu_converter.core.models.ptq_config import PTQSettings, PTQConfigModel, CalibrationConfig
        from npu_converter.core.models.config_model import ConfigModel

        # Test PTQSettings
        settings = PTQSettings()
        assert hasattr(settings, 'output_dir')
        assert hasattr(settings, 'debug_mode')
        assert hasattr(settings, 'target_device')
        print("✅ PTQSettings has required attributes")

        # Test PTQConfigModel inheritance
        config = PTQConfigModel()
        assert isinstance(config, ConfigModel)
        print("✅ PTQConfigModel properly inherits from ConfigModel")

        # Test CalibrationConfig
        calib_config = CalibrationConfig(
            data_path="./test",
            batch_size=1,
            num_samples=10,
            input_shape=(1, 3, 224, 224)
        )
        assert calib_config.batch_size == 1
        assert calib_config.num_samples == 10
        print("✅ CalibrationConfig works correctly")

        # Test configuration validation
        errors = config.validate_ptq_config()
        print(f"✅ Configuration validation works (errors: {len(errors)})")

        return True

    except Exception as e:
        print(f"❌ Configuration architecture test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_utils_architecture():
    """Test utilities architecture."""
    print("\n🔧 Testing Utilities Architecture...")

    try:
        from npu_converter.core.utils.progress_tracker import ProgressTracker
        from npu_converter.core.utils.debug_tools import DebugTools

        # Test ProgressTracker
        tracker = ProgressTracker()
        assert hasattr(tracker, 'start_step')
        assert hasattr(tracker, 'complete_step')
        assert hasattr(tracker, 'get_overall_progress')
        print("✅ ProgressTracker has required methods")

        # Test ProgressTracker functionality
        tracker.start_step("Test", 1, 1)
        tracker.complete_step("Test")
        progress = tracker.get_overall_progress()
        assert progress['completed_steps'] == 1
        print("✅ ProgressTracker functionality works")

        # Test DebugTools
        debug_tools = DebugTools()
        assert hasattr(debug_tools, 'enabled')
        print("✅ DebugTools has required attributes")

        return True

    except Exception as e:
        print(f"❌ Utils architecture test failed: {e}")
        return False

def test_import_structure():
    """Test import structure and module organization."""
    print("\n📁 Testing Import Structure...")

    try:
        # Test core imports
        from npu_converter.core.interfaces.base_converter import BaseConverter
        from npu_converter.core.models.ptq_config import PTQSettings
        from npu_converter.core.utils.progress_tracker import ProgressTracker
        print("✅ Core module imports work")

        # Test that old paths are blocked
        try:
            from npu_converter.utils.progress_tracker import ProgressTracker
            assert False, "Old import path should not work"
        except ImportError:
            print("✅ Old import paths correctly blocked")

        # Test PTQ models re-export
        from npu_converter.models.calibration import CalibrationConfig
        assert CalibrationConfig is not None
        print("✅ PTQ models re-export works")

        return True

    except Exception as e:
        print(f"❌ Import structure test failed: {e}")
        return False

def test_interface_compliance():
    """Test interface compliance."""
    print("\n🔍 Testing Interface Compliance...")

    try:
        from npu_converter.core.interfaces.base_converter import BaseConverter
        from npu_converter.core.models.ptq_config import PTQSettings
        from npu_converter.core.models.config_model import ConfigModel

        # Check BaseConverter interface
        base_methods = dir(BaseConverter)
        required_methods = ['validate_input', 'prepare_conversion', 'convert', 'export_results']

        for method in required_methods:
            assert method in base_methods, f"Missing method: {method}"
        print("✅ BaseConverter interface is complete")

        # Check PTQSettings interface
        settings_methods = dir(PTQSettings())
        assert 'to_dict' in settings_methods, "PTQSettings missing to_dict method"
        assert 'from_dict' in dir(PTQSettings), "PTQSettings missing from_dict method"
        print("✅ PTQSettings interface is complete")

        return True

    except Exception as e:
        print(f"❌ Interface compliance test failed: {e}")
        return False

def main():
    """Run all architectural integration tests."""
    print("🚀 Starting Architectural Integration Tests\n")

    tests = [
        test_core_architecture,
        test_configuration_architecture,
        test_utils_architecture,
        test_import_structure,
        test_interface_compliance
    ]

    passed = 0
    total = len(tests)

    for test in tests:
        if test():
            passed += 1
        else:
            print(f"❌ Test {test.__name__} failed")

    print(f"\n📊 Architectural Integration Test Results: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 All architectural integration tests passed!")
        print("✅ PTQ refactoring maintains proper architecture")
        return 0
    else:
        print("❌ Some architectural integration tests failed.")
        return 1

if __name__ == "__main__":
    sys.exit(main())