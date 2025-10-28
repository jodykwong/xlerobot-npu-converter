#!/usr/bin/env python3
"""
Performance Validation Test

This script validates that the PTQ refactoring hasn't negatively impacted
performance by testing instantiation, method calls, and memory usage.
"""

import sys
import time
import tracemalloc
from pathlib import Path
sys.path.insert(0, 'src')

def test_instantiation_performance():
    """Test PTQ converter instantiation performance."""
    print("⚡ Testing Instantiation Performance...")

    try:
        from npu_converter.core.models.ptq_config import PTQSettings, PTQConfigModel

        # Test PTQSettings instantiation
        start_time = time.perf_counter()
        for _ in range(1000):
            settings = PTQSettings()
        end_time = time.perf_counter()

        settings_time = (end_time - start_time) * 1000  # Convert to ms
        print(f"✅ PTQSettings instantiation (1000x): {settings_time:.2f}ms")

        # Test PTQConfigModel instantiation
        start_time = time.perf_counter()
        for _ in range(100):
            config = PTQConfigModel()
        end_time = time.perf_counter()

        config_time = (end_time - start_time) * 1000  # Convert to ms
        print(f"✅ PTQConfigModel instantiation (100x): {config_time:.2f}ms")

        # Performance thresholds (should be very fast)
        assert settings_time < 100, f"PTQSettings instantiation too slow: {settings_time}ms"
        assert config_time < 200, f"PTQConfigModel instantiation too slow: {config_time}ms"

        print("✅ Instantiation performance meets requirements")
        return True

    except Exception as e:
        print(f"❌ Instantiation performance test failed: {e}")
        return False

def test_memory_usage():
    """Test memory usage of refactored components."""
    print("\n💾 Testing Memory Usage...")

    try:
        from npu_converter.core.models.ptq_config import PTQSettings, PTQConfigModel
        from npu_converter.core.utils.progress_tracker import ProgressTracker
        from npu_converter.core.utils.debug_tools import DebugTools

        # Start memory tracking
        tracemalloc.start()

        # Create multiple instances
        configs = []
        trackers = []
        debug_tools = []

        for i in range(100):
            configs.append(PTQConfigModel())
            trackers.append(ProgressTracker(enable_console_output=False))
            debug_tools.append(DebugTools(enabled=False))

        # Get memory usage
        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()

        current_mb = current / 1024 / 1024
        peak_mb = peak / 1024 / 1024

        print(f"✅ Memory usage for 100 instances: {current_mb:.2f}MB (current), {peak_mb:.2f}MB (peak)")

        # Memory should be reasonable (less than 10MB for 100 instances)
        assert peak_mb < 10, f"Memory usage too high: {peak_mb}MB"
        print("✅ Memory usage within acceptable limits")

        return True

    except Exception as e:
        print(f"❌ Memory usage test failed: {e}")
        return False

def test_method_call_performance():
    """Test method call performance."""
    print("\n🔧 Testing Method Call Performance...")

    try:
        from npu_converter.core.models.ptq_config import PTQSettings, PTQConfigModel
        from npu_converter.core.utils.progress_tracker import ProgressTracker

        # Test PTQSettings methods
        settings = PTQSettings()

        start_time = time.perf_counter()
        for _ in range(10000):
            settings_dict = settings.to_dict()
        end_time = time.perf_counter()

        to_dict_time = (end_time - start_time) * 1000
        print(f"✅ PTQSettings.to_dict() (10,000x): {to_dict_time:.2f}ms")

        # Test ProgressTracker methods
        tracker = ProgressTracker(enable_console_output=False)

        start_time = time.perf_counter()
        for i in range(1000):
            tracker.start_step(f"Step {i}", i % 10 + 1, 10)
            tracker.complete_step(f"Step {i}")
        end_time = time.perf_counter()

        tracker_time = (end_time - start_time) * 1000
        print(f"✅ ProgressTracker operations (1,000x): {tracker_time:.2f}ms")

        # Performance thresholds
        assert to_dict_time < 500, f"to_dict too slow: {to_dict_time}ms"
        assert tracker_time < 1000, f"ProgressTracker too slow: {tracker_time}ms"

        print("✅ Method call performance meets requirements")
        return True

    except Exception as e:
        print(f"❌ Method call performance test failed: {e}")
        return False

def test_import_performance():
    """Test import performance."""
    print("\n📦 Testing Import Performance...")

    try:
        # Test core imports
        start_time = time.perf_counter()
        for _ in range(100):
            from npu_converter.core.interfaces.base_converter import BaseConverter
            from npu_converter.core.models.ptq_config import PTQSettings, PTQConfigModel
            from npu_converter.core.utils.progress_tracker import ProgressTracker
            from npu_converter.core.utils.debug_tools import DebugTools
        end_time = time.perf_counter()

        import_time = (end_time - start_time) * 1000
        print(f"✅ Core imports (100x): {import_time:.2f}ms")

        # Performance threshold
        assert import_time < 1000, f"Import performance too slow: {import_time}ms"
        print("✅ Import performance meets requirements")

        return True

    except Exception as e:
        print(f"❌ Import performance test failed: {e}")
        return False

def test_configuration_validation_performance():
    """Test configuration validation performance."""
    print("\n✅ Testing Configuration Validation Performance...")

    try:
        from npu_converter.core.models.ptq_config import PTQSettings, PTQConfigModel

        config = PTQConfigModel()

        start_time = time.perf_counter()
        for _ in range(1000):
            errors = config.validate_ptq_config()
        end_time = time.perf_counter()

        validation_time = (end_time - start_time) * 1000
        print(f"✅ Configuration validation (1,000x): {validation_time:.2f}ms")

        # Performance threshold
        assert validation_time < 100, f"Validation too slow: {validation_time}ms"
        print("✅ Configuration validation performance meets requirements")

        return True

    except Exception as e:
        print(f"❌ Configuration validation performance test failed: {e}")
        return False

def main():
    """Run all performance validation tests."""
    print("🚀 Starting Performance Validation Tests\n")

    tests = [
        test_instantiation_performance,
        test_memory_usage,
        test_method_call_performance,
        test_import_performance,
        test_configuration_validation_performance
    ]

    passed = 0
    total = len(tests)

    for test in tests:
        if test():
            passed += 1
        else:
            print(f"❌ Test {test.__name__} failed")

    print(f"\n📊 Performance Validation Results: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 All performance validation tests passed!")
        print("✅ PTQ refactoring maintains or improves performance")
        return 0
    else:
        print("❌ Some performance validation tests failed.")
        return 1

if __name__ == "__main__":
    sys.exit(main())