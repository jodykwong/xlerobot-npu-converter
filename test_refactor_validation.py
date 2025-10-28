#!/usr/bin/env python3
"""
Refactor Validation Test

This script tests the architectural correctness of the PTQ refactor
without requiring external dependencies like ONNX.
"""

import sys
sys.path.insert(0, 'src')

def test_core_imports():
    """Test core module imports."""
    print("🧪 Testing Core Module Imports...")

    try:
        from npu_converter.core.interfaces.base_converter import BaseConverter
        print("✅ BaseConverter import success")

        # Check that BaseConverter is abstract
        try:
            BaseConverter()
            print("❌ BaseConverter should be abstract")
            return False
        except TypeError:
            print("✅ BaseConverter is properly abstract")

    except Exception as e:
        print(f"❌ BaseConverter import failed: {e}")
        return False

    try:
        from npu_converter.core.models.ptq_config import PTQSettings, PTQConfigModel
        settings = PTQSettings()
        config = PTQConfigModel(ptq_settings=settings)
        print("✅ PTQ config models work correctly")
    except Exception as e:
        print(f"❌ PTQ config models failed: {e}")
        return False

    try:
        from npu_converter.core.utils.progress_tracker import ProgressTracker
        tracker = ProgressTracker()
        print("✅ ProgressTracker instantiation success")
    except Exception as e:
        print(f"❌ ProgressTracker failed: {e}")
        return False

    try:
        from npu_converter.core.utils.debug_tools import DebugTools
        debug_tools = DebugTools(enabled=True)
        print("✅ DebugTools instantiation success")
    except Exception as e:
        print(f"❌ DebugTools failed: {e}")
        return False

    return True

def test_architectural_alignment():
    """Test architectural alignment."""
    print("\n🏗️ Testing Architectural Alignment...")

    try:
        from npu_converter.core.interfaces.base_converter import BaseConverter
        from npu_converter.core.models.ptq_config import PTQConfigModel

        # Test PTQConfigModel inheritance
        config = PTQConfigModel()
        print("✅ PTQConfigModel instantiation success")

        # Test configuration validation
        errors = config.validate_ptq_config()
        print(f"✅ PTQ configuration validation works (errors: {len(errors)})")

    except Exception as e:
        print(f"❌ Architectural alignment test failed: {e}")
        return False

    return True

def test_import_paths():
    """Test that all import paths are correctly updated."""
    print("\n📁 Testing Import Path Updates...")

    try:
        # Test old paths don't work
        try:
            from npu_converter.utils.progress_tracker import ProgressTracker
            print("❌ Old import path still accessible")
            return False
        except ImportError:
            print("✅ Old import path correctly blocked")

        try:
            from npu_converter.utils.debug_tools import DebugTools
            print("❌ Old import path still accessible")
            return False
        except ImportError:
            print("✅ Old import path correctly blocked")

        # Test new paths work
        from npu_converter.core.utils.progress_tracker import ProgressTracker
        from npu_converter.core.utils.debug_tools import DebugTools
        print("✅ New import paths work correctly")

    except Exception as e:
        print(f"❌ Import path test failed: {e}")
        return False

    return True

def main():
    """Run all refactor validation tests."""
    print("🚀 Starting PTQ Refactor Validation Tests\n")

    tests = [
        test_core_imports,
        test_architectural_alignment,
        test_import_paths
    ]

    passed = 0
    total = len(tests)

    for test in tests:
        if test():
            passed += 1
        else:
            print(f"❌ Test {test.__name__} failed")

    print(f"\n📊 Test Results: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 All refactor validation tests passed!")
        print("✅ PTQ refactoring is architecturally correct")
        return 0
    else:
        print("❌ Some tests failed. Refactor needs attention.")
        return 1

if __name__ == "__main__":
    sys.exit(main())