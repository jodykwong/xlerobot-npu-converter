#!/usr/bin/env python3
"""
Test script for the dynamic configuration system.

Tests the dynamic configuration adjustment functionality implemented in task 3 of Story 1.4.
"""

import sys
import time
import threading
import tempfile
import yaml
from pathlib import Path

# Add the src directory to Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from npu_converter.config import ConfigurationManager


def create_test_config():
    """Create a test configuration file for dynamic testing."""
    config = {
        "project": {
            "name": "xlerobot",
            "version": "1.0.0",
            "model_type": "sensevoice",
            "description": "Test configuration for dynamic config"
        },
        "hardware": {
            "target_device": "horizon_x5",
            "optimization_level": "O2",
            "memory_limit": "8GB",
            "compute_units": 10,
            "cache_size": "256MB"
        },
        "conversion_params": {
            "input_format": "onnx",
            "output_format": "bpu",
            "precision": "int8",
            "calibration_method": "minmax",
            "batch_size": 1,
            "num_workers": 4
        },
        "model_specific": {
            "sensevoice": {
                "sample_rate": 16000,
                "audio_length": 30,
                "vocab_size": 10000,
                "mel_bins": 80,
                "frame_length": 25,
                "frame_shift": 10,
                "normalize": True,
                "preemphasis": 0.97,
                "n_fft": 512,
                "hop_length": 160,
                "win_length": 400,
                "n_mels": 80,
                "f_min": 0.0,
                "f_max": 8000.0
            }
        },
        "performance": {
            "target_latency_ms": 100,
            "max_realtime_factor": 0.1,
            "enable_streaming": False,
            "batch_size": 1,
            "num_workers": 4
        }
    }
    return config


def setup_test_environment():
    """Setup test environment with configuration file."""
    import tempfile
    import shutil

    # Create temporary config file
    config_data = create_test_config()
    config_file = Path("test_config.yaml")

    with open(config_file, 'w', encoding='utf-8') as f:
        yaml.dump(config_data, f, default_flow_style=False, indent=2)

    return config_file


def cleanup_test_environment():
    """Cleanup test environment."""
    config_file = Path("test_config.yaml")
    if config_file.exists():
        config_file.unlink()


def test_dynamic_config_initialization():
    """Test dynamic configuration manager initialization."""
    print("Testing Dynamic Configuration Initialization...")

    try:
        # Setup test environment
        config_file = setup_test_environment()

        # Initialize configuration manager
        manager = ConfigurationManager(config_file)
        config = manager.load_config()
        print("✅ ConfigurationManager initialized and loaded")

        # Get dynamic manager
        dynamic_manager = manager.get_dynamic_manager()
        if dynamic_manager:
            print("✅ DynamicConfigManager initialized")
        else:
            print("❌ DynamicConfigManager not available")
            return False

        # Check initial metrics
        metrics = dynamic_manager.get_metrics()
        print(f"✅ Initial metrics: {metrics.total_changes} changes, {metrics.successful_changes} successful")

        return True

    except Exception as e:
        print(f"❌ Dynamic config initialization test failed: {e}")
        return False


def test_single_config_change():
    """Test single configuration value changes."""
    print("\nTesting Single Configuration Changes...")

    try:
        config_file = Path("test_config.yaml")
        manager = ConfigurationManager(config_file)
        manager.load_config()
        dynamic_manager = manager.get_dynamic_manager()

        # Test changing a simple value
        original_latency = manager.get_config("performance.target_latency_ms")
        new_latency = 150

        success = dynamic_manager.set_config("performance.target_latency_ms", new_latency, source="test")
        if success:
            updated_latency = manager.get_config("performance.target_latency_ms")
            if updated_latency == new_latency:
                print(f"✅ Successfully changed latency from {original_latency} to {updated_latency}")
            else:
                print(f"❌ Value not updated correctly: expected {new_latency}, got {updated_latency}")
                return False
        else:
            print("❌ Failed to set configuration value")
            return False

        # Test changing a different type of value
        original_optimization = manager.get_config("hardware.optimization_level")
        new_optimization = "O3"

        success = dynamic_manager.set_config("hardware.optimization_level", new_optimization, source="test")
        if success:
            updated_optimization = manager.get_config("hardware.optimization_level")
            if updated_optimization == new_optimization:
                print(f"✅ Successfully changed optimization level from {original_optimization} to {updated_optimization}")
            else:
                print(f"❌ Value not updated correctly: expected {new_optimization}, got {updated_optimization}")
                return False
        else:
            print("❌ Failed to set optimization level")
            return False

        return True

    except Exception as e:
        print(f"❌ Single config change test failed: {e}")
        return False


def test_batch_config_update():
    """Test batch configuration updates."""
    print("\nTesting Batch Configuration Updates...")

    try:
        config_file = Path("test_config.yaml")
        manager = ConfigurationManager(config_file)
        manager.load_config()
        dynamic_manager = manager.get_dynamic_manager()

        # Prepare batch changes
        batch_changes = {
            "performance.target_latency_ms": 80,
            "hardware.cache_size": "512MB",
            "conversion_params.batch_size": 4
        }

        # Get original values
        original_values = {}
        for field_path in batch_changes.keys():
            original_values[field_path] = manager.get_config(field_path)

        # Apply batch changes
        success = manager.batch_update_dynamic(batch_changes, source="batch_test")
        if success:
            print("✅ Batch update completed successfully")

            # Verify all changes were applied
            all_applied = True
            for field_path, expected_value in batch_changes.items():
                actual_value = manager.get_config(field_path)
                if actual_value != expected_value:
                    print(f"❌ Batch update failed for {field_path}: expected {expected_value}, got {actual_value}")
                    all_applied = False

            if all_applied:
                print("✅ All batch changes applied correctly")
            else:
                return False
        else:
            print("❌ Batch update failed")
            return False

        return True

    except Exception as e:
        print(f"❌ Batch config update test failed: {e}")
        return False


def test_config_validation():
    """Test configuration validation during dynamic changes."""
    print("\nTesting Configuration Validation...")

    try:
        config_file = Path("test_config.yaml")
        manager = ConfigurationManager(config_file)
        manager.load_config()
        dynamic_manager = manager.get_dynamic_manager()

        # Test valid change
        try:
            success = dynamic_manager.set_config("performance.target_latency_ms", 120, source="validation_test")
            if success:
                print("✅ Valid configuration change accepted")
            else:
                print("❌ Valid configuration change rejected")
                return False
        except Exception as e:
            print(f"❌ Valid change unexpectedly failed: {e}")
            return False

        # Test invalid type change
        try:
            dynamic_manager.set_config("performance.target_latency_ms", "invalid_string", source="validation_test")
            print("❌ Invalid type change was accepted (should have been rejected)")
            return False
        except Exception:
            print("✅ Invalid type change correctly rejected")

        # Test invalid enum value
        try:
            dynamic_manager.set_config("hardware.optimization_level", "INVALID_LEVEL", source="validation_test")
            print("❌ Invalid enum change was accepted (should have been rejected)")
            return False
        except Exception:
            print("✅ Invalid enum change correctly rejected")

        # Test out-of-range value
        try:
            dynamic_manager.set_config("conversion_params.batch_size", 100, source="validation_test")
            print("❌ Out-of-range change was accepted (should have been rejected)")
            return False
        except Exception:
            print("✅ Out-of-range change correctly rejected")

        return True

    except Exception as e:
        print(f"❌ Config validation test failed: {e}")
        return False


def test_config_reset():
    """Test configuration reset functionality."""
    print("\nTesting Configuration Reset...")

    try:
        config_file = Path("test_config.yaml")
        manager = ConfigurationManager(config_file)
        manager.load_config()
        dynamic_manager = manager.get_dynamic_manager()

        # Change a value
        original_batch_size = manager.get_config("conversion_params.batch_size")
        new_batch_size = 8
        dynamic_manager.set_config("conversion_params.batch_size", new_batch_size)

        # Verify the change
        current_batch_size = manager.get_config("conversion_params.batch_size")
        if current_batch_size != new_batch_size:
            print("❌ Failed to change batch size before reset test")
            return False

        # Reset the value
        success = manager.reset_config_dynamic("conversion_params.batch_size", source="reset_test")
        if success:
            reset_batch_size = manager.get_config("conversion_params.batch_size")
            if reset_batch_size == original_batch_size:
                print(f"✅ Successfully reset batch size to original value: {original_batch_size}")
            else:
                print(f"❌ Reset failed: expected {original_batch_size}, got {reset_batch_size}")
                return False
        else:
            print("❌ Reset operation failed")
            return False

        return True

    except Exception as e:
        print(f"❌ Config reset test failed: {e}")
        return False


def test_template_reload():
    """Test template reload functionality."""
    print("\nTesting Template Reload...")

    try:
        config_file = Path("test_config.yaml")
        manager = ConfigurationManager(config_file)
        manager.load_config()
        dynamic_manager = manager.get_dynamic_manager()

        # Change some values
        dynamic_manager.set_config("hardware.optimization_level", "O3")
        dynamic_manager.set_config("performance.target_latency_ms", 50)

        # Reload from performance template
        success = manager.reload_from_template_dynamic("sensevoice_performance", preserve_overrides=False)
        if success:
            print("✅ Successfully reloaded from performance template")

            # Check if values were updated
            opt_level = manager.get_config("hardware.optimization_level")
            batch_size = manager.get_config("conversion_params.batch_size")

            if opt_level == "O3" and batch_size == 8:
                print("✅ Template values correctly applied")
            else:
                print(f"❌ Template reload failed: opt_level={opt_level}, batch_size={batch_size}")
                return False
        else:
            print("❌ Template reload failed")
            return False

        return True

    except Exception as e:
        print(f"❌ Template reload test failed: {e}")
        return False


def test_change_callbacks():
    """Test configuration change callbacks."""
    print("\nTesting Configuration Change Callbacks...")

    try:
        config_file = Path("test_config.yaml")
        manager = ConfigurationManager(config_file)
        manager.load_config()
        dynamic_manager = manager.get_dynamic_manager()

        # Track callback invocations
        callback_calls = []

        def test_callback(change):
            callback_calls.append(change)
            print(f"📞 Callback invoked: {change.field_path} changed from {change.old_value} to {change.new_value}")

        # Add callback
        manager.add_config_change_callback(test_callback)

        # Make a configuration change
        dynamic_manager.set_config("performance.target_latency_ms", 200, source="callback_test")

        # Check if callback was invoked
        if len(callback_calls) == 1:
            change = callback_calls[0]
            if change.field_path == "performance.target_latency_ms" and change.new_value == 200:
                print("✅ Callback correctly invoked with expected parameters")
            else:
                print(f"❌ Callback parameters incorrect: {change}")
                return False
        else:
            print(f"❌ Expected 1 callback call, got {len(callback_calls)}")
            return False

        # Remove callback
        manager.remove_config_change_callback(test_callback)

        # Make another change
        dynamic_manager.set_config("performance.target_latency_ms", 180, source="callback_test")

        # Check if callback was not invoked
        if len(callback_calls) == 1:
            print("✅ Callback correctly removed")
        else:
            print(f"❌ Callback still invoked after removal: {len(callback_calls)} calls")
            return False

        return True

    except Exception as e:
        print(f"❌ Change callbacks test failed: {e}")
        return False


def test_concurrent_changes():
    """Test thread-safe concurrent configuration changes."""
    print("\nTesting Concurrent Configuration Changes...")

    try:
        config_file = Path("test_config.yaml")
        manager = ConfigurationManager(config_file)
        manager.load_config()
        dynamic_manager = manager.get_dynamic_manager()

        # Track results from multiple threads
        results = []
        errors = []

        def worker_thread(thread_id):
            try:
                for i in range(5):
                    field_path = f"performance.target_latency_ms"
                    value = 100 + thread_id * 10 + i
                    success = dynamic_manager.set_config(field_path, value, source=f"thread_{thread_id}")
                    results.append((thread_id, i, success))

                    # Small delay to increase chance of race conditions
                    time.sleep(0.001)

            except Exception as e:
                errors.append((thread_id, str(e)))

        # Create and start multiple threads
        threads = []
        for thread_id in range(3):
            thread = threading.Thread(target=worker_thread, args=(thread_id,))
            threads.append(thread)
            thread.start()

        # Wait for all threads to complete
        for thread in threads:
            thread.join()

        # Check results
        if errors:
            print(f"❌ Thread errors occurred: {errors}")
            return False

        expected_operations = 3 * 5  # 3 threads * 5 operations each
        if len(results) == expected_operations:
            print(f"✅ All {expected_operations} concurrent operations completed successfully")
        else:
            print(f"❌ Expected {expected_operations} operations, got {len(results)}")
            return False

        # Verify final state is consistent
        final_value = manager.get_config("performance.target_latency_ms")
        if isinstance(final_value, int) and 100 <= final_value <= 200:
            print(f"✅ Final configuration state is consistent: {final_value}")
        else:
            print(f"❌ Final configuration state is inconsistent: {final_value}")
            return False

        return True

    except Exception as e:
        print(f"❌ Concurrent changes test failed: {e}")
        return False


def test_metrics_and_history():
    """Test metrics tracking and change history."""
    print("\nTesting Metrics and Change History...")

    try:
        config_file = Path("test_config.yaml")
        manager = ConfigurationManager(config_file)
        manager.load_config()
        dynamic_manager = manager.get_dynamic_manager()

        # Get initial metrics
        initial_metrics = dynamic_manager.get_metrics()
        initial_changes = initial_metrics.total_changes

        # Make some changes
        dynamic_manager.set_config("performance.target_latency_ms", 150, source="metrics_test")
        dynamic_manager.set_config("hardware.optimization_level", "O1", source="metrics_test")

        # Check updated metrics
        updated_metrics = dynamic_manager.get_metrics()
        if updated_metrics.total_changes == initial_changes + 2:
            print("✅ Change count metrics updated correctly")
        else:
            print(f"❌ Change count incorrect: expected {initial_changes + 2}, got {updated_metrics.total_changes}")
            return False

        if updated_metrics.successful_changes == initial_changes + 2:
            print("✅ Successful changes metrics updated correctly")
        else:
            print(f"❌ Successful changes incorrect: expected {initial_changes + 2}, got {updated_metrics.successful_changes}")
            return False

        # Check change history
        history = dynamic_manager.get_change_history(limit=5)
        if len(history) >= 2:
            print(f"✅ Change history contains {len(history)} recent changes")

            # Verify last change
            last_change = history[-1]
            if last_change.field_path == "hardware.optimization_level" and last_change.new_value == "O1":
                print("✅ Last change in history is correct")
            else:
                print(f"❌ Last change incorrect: {last_change}")
                return False
        else:
            print(f"❌ Change history too short: {len(history)} changes")
            return False

        return True

    except Exception as e:
        print(f"❌ Metrics and history test failed: {e}")
        return False


def main():
    """Run all dynamic configuration tests."""
    print("🚀 Testing Story 1.4 Dynamic Configuration System")
    print("=" * 60)

    try:
        # Setup test environment
        setup_test_environment()

        tests = [
            ("Dynamic Config Initialization", test_dynamic_config_initialization),
            ("Single Config Change", test_single_config_change),
            ("Batch Config Update", test_batch_config_update),
            ("Config Validation", test_config_validation),
            ("Config Reset", test_config_reset),
            ("Template Reload", test_template_reload),
            ("Change Callbacks", test_change_callbacks),
            ("Concurrent Changes", test_concurrent_changes),
            ("Metrics and History", test_metrics_and_history),
        ]

        passed = 0
        total = len(tests)

        for test_name, test_func in tests:
            print(f"\n{'='*20}")
            print(f"Test: {test_name}")
            print(f"{'='*20}")

            if test_func():
                passed += 1
                print(f"✅ {test_name}: PASSED")
            else:
                print(f"❌ {test_name}: FAILED")

        print(f"\n{'='*60}")
        print(f"Test Results: {passed}/{total} tests passed")

        if passed == total:
            print("🎉 All tests passed! Dynamic configuration system is working correctly.")
        else:
            print(f"⚠️ {total - passed} tests failed. Please check the implementation.")

        return passed == total

    finally:
        # Cleanup test environment
        cleanup_test_environment()
        print("\n🧹 Cleaned up test files")


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)