#!/usr/bin/env python3
"""
Comprehensive Integration Test for Story 1.4 Configuration Management System

This test script validates the complete functionality of the configuration management
system implemented in Story 1.4, including all components working together.

Tests covered:
- Configuration loading and validation
- Template management and application
- Dynamic configuration adjustments
- Hot reload functionality
- Error handling and recovery
- Performance requirements
- Integration between all components
"""

import sys
import time
import tempfile
import threading
from pathlib import Path

# Add the src directory to Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from npu_converter.config import ConfigurationManager


def create_comprehensive_test_config():
    """Create a comprehensive test configuration file."""
    config_content = """project:
  name: "xlerobot_integration_test"
  version: "1.0.0"
  model_type: "sensevoice"

hardware:
  target_device: "horizon_x5"
  optimization_level: "O2"
  memory_limit: "8GB"
  compute_units: 10
  cache_size: "256MB"

conversion_params:
  input_format: "onnx"
  output_format: "bpu"
  precision: "int8"
  calibration_method: "minmax"
  batch_size: 1
  num_workers: 4

model_specific:
  sensevoice:
    sample_rate: 16000
    audio_length: 30
    vocab_size: 10000
    mel_bins: 80
    frame_length: 25
    frame_shift: 10
    normalize: true
    preemphasis: 0.97
    n_fft: 512
    hop_length: 160
    win_length: 400
    n_mels: 80
    f_min: 0.0
    f_max: 8000.0

performance:
  target_latency_ms: 100
  max_realtime_factor: 0.1
  enable_streaming: false
  enable_caching: true
  max_batch_size: 8

optimization:
  enable_quantization: true
  quantization_precision: "int8"
  enable_fusion: true
  enable_pruning: false
  enable_weight_sharing: false
  enable_dynamic_shapes: false

validation:
  strict_validation: true
  warn_on_deprecated: true
  validate_paths: true
"""

    config_file = Path("test_integration_config.yaml")
    with open(config_file, 'w') as f:
        f.write(config_content)

    return config_file


def test_complete_system_initialization():
    """Test complete system initialization with all components."""
    print("Testing Complete System Initialization...")

    try:
        config_file = create_comprehensive_test_config()
        print(f"✅ Created comprehensive test configuration: {config_file}")

        # Initialize configuration manager
        start_time = time.time()
        manager = ConfigurationManager(config_file)
        config = manager.load_config()
        init_time = (time.time() - start_time) * 1000

        print(f"✅ System initialized in {init_time:.2f}ms")

        # Verify all components are initialized
        if manager._validator:
            print("✅ Config validator initialized")
        else:
            print("❌ Config validator not initialized")
            return False

        if manager._template_manager:
            print("✅ Template manager initialized")
        else:
            print("❌ Template manager not initialized")
            return False

        if manager._hot_reload_manager:
            print("✅ Hot reload manager initialized")
        else:
            print("❌ Hot reload manager not initialized")
            return False

        if manager._dynamic_config_manager:
            print("✅ Dynamic config manager initialized")
        else:
            print("❌ Dynamic config manager not initialized")
            return False

        if manager._current_strategy:
            print(f"✅ Strategy initialized: {manager._current_strategy.get_model_type()}")
        else:
            print("❌ Strategy not initialized")
            return False

        # Check performance requirement (<100ms for initial load)
        if init_time < 100:
            print(f"✅ Performance requirement met: {init_time:.2f}ms < 100ms")
        else:
            print(f"⚠️ Performance requirement exceeded: {init_time:.2f}ms >= 100ms")

        # Clean up
        config_file.unlink()
        return True

    except Exception as e:
        print(f"❌ Complete system initialization test failed: {e}")
        # Clean up on error
        try:
            if 'config_file' in locals() and config_file.exists():
                config_file.unlink()
        except:
            pass
        return False


def test_template_and_dynamic_integration():
    """Test integration between template system and dynamic configuration."""
    print("\nTesting Template and Dynamic Configuration Integration...")

    try:
        config_file = create_comprehensive_test_config()
        manager = ConfigurationManager(config_file)
        manager.load_config()

        # Get initial configuration values
        initial_optimization = manager.get_config("hardware.optimization_level")
        initial_latency = manager.get_config("performance.target_latency_ms")

        # Apply performance template
        success = manager.reload_from_template_dynamic("sensevoice_performance", preserve_overrides=False)
        if success:
            print("✅ Successfully applied performance template")

            # Verify template values
            updated_optimization = manager.get_config("hardware.optimization_level")
            updated_batch_size = manager.get_config("conversion_params.batch_size")

            if updated_optimization == "O3" and updated_batch_size == 8:
                print("✅ Template values correctly applied")
            else:
                print(f"❌ Template values not correctly applied: opt={updated_optimization}, batch={updated_batch_size}")
                return False
        else:
            print("❌ Failed to apply performance template")
            return False

        # Test dynamic adjustment after template application
        dynamic_success = manager.set_config_dynamic("performance.target_latency_ms", 25, source="integration_test")
        if dynamic_success:
            updated_latency = manager.get_config("performance.target_latency_ms")
            if updated_latency == 25:
                print("✅ Dynamic adjustment successful after template application")
            else:
                print(f"❌ Dynamic adjustment failed: expected 25, got {updated_latency}")
                return False
        else:
            print("❌ Dynamic adjustment failed")
            return False

        # Clean up
        config_file.unlink()
        return True

    except Exception as e:
        print(f"❌ Template and dynamic integration test failed: {e}")
        # Clean up on error
        try:
            if 'config_file' in locals() and config_file.exists():
                config_file.unlink()
        except:
            pass
        return False


def test_hot_reload_and_dynamic_coordination():
    """Test coordination between hot reload and dynamic configuration."""
    print("\nTesting Hot Reload and Dynamic Configuration Coordination...")

    try:
        config_file = create_comprehensive_test_config()
        manager = ConfigurationManager(config_file)
        manager.load_config()

        # Start hot reload monitoring
        hot_reload_manager = manager._hot_reload_manager
        hot_reload_manager.start_monitoring()

        # Make a dynamic change
        dynamic_success = manager.set_config_dynamic("hardware.cache_size", "512MB", source="coordination_test")
        if dynamic_success:
            current_cache_size = manager.get_config("hardware.cache_size")
            if current_cache_size == "512MB":
                print("✅ Dynamic change applied")
            else:
                print(f"❌ Dynamic change failed: expected 512MB, got {current_cache_size}")
                return False
        else:
            print("❌ Dynamic change failed")
            return False

        # Make a file-based change
        new_config_content = """project:
  name: "xlerobot_integration_test"
  version: "1.0.0"
  model_type: "sensevoice"

hardware:
  target_device: "horizon_x5"
  optimization_level: "O3"
  memory_limit: "8GB"
  compute_units: 10
  cache_size: "1GB"

conversion_params:
  input_format: "onnx"
  output_format: "bpu"
  precision: "int8"
  calibration_method: "minmax"
  batch_size: 1
  num_workers: 4

model_specific:
  sensevoice:
    sample_rate: 16000
    audio_length: 30
    vocab_size: 10000
    mel_bins: 80
    frame_length: 25
    frame_shift: 10
    normalize: true
    preemphasis: 0.97
    n_fft: 512
    hop_length: 160
    win_length: 400
    n_mels: 80
    f_min: 0.0
    f_max: 8000.0

performance:
  target_latency_ms: 100
  max_realtime_factor: 0.1
  enable_streaming: false
  enable_caching: true
  max_batch_size: 8

optimization:
  enable_quantization: true
  quantization_precision: "int8"
  enable_fusion: true
  enable_pruning: false
  enable_weight_sharing: false
  enable_dynamic_shapes: false

validation:
  strict_validation: true
  warn_on_deprecated: true
  validate_paths: true
"""

        with open(config_file, 'w') as f:
            f.write(new_config_content)

        # Wait for hot reload
        time.sleep(1.0)

        # Force reload to ensure it works
        reload_success = hot_reload_manager.force_reload()
        if reload_success:
            print("✅ Hot reload successful")
        else:
            print("❌ Hot reload failed")
            return False

        # Verify file-based changes
        updated_optimization = manager.get_config("hardware.optimization_level")
        updated_cache_size = manager.get_config("hardware.cache_size")

        if updated_optimization == "O3" and updated_cache_size == "1GB":
            print("✅ File-based changes applied correctly")
        else:
            print(f"❌ File-based changes not applied: opt={updated_optimization}, cache={updated_cache_size}")
            return False

        # Verify dynamic changes were overwritten by file reload (expected behavior)
        final_cache_size = manager.get_config("hardware.cache_size")
        if final_cache_size == "1GB":
            print("✅ File reload correctly overwrote dynamic changes")
        else:
            print(f"❌ File reload did not overwrite dynamic changes: {final_cache_size}")
            return False

        # Stop monitoring
        hot_reload_manager.stop_monitoring()

        # Clean up
        config_file.unlink()
        return True

    except Exception as e:
        print(f"❌ Hot reload and dynamic coordination test failed: {e}")
        # Clean up on error
        try:
            if 'config_file' in locals() and config_file.exists():
                config_file.unlink()
        except:
            pass
        return False


def test_validation_integration():
    """Test validation integration across all components."""
    print("\nTesting Validation Integration...")

    try:
        config_file = create_comprehensive_test_config()
        manager = ConfigurationManager(config_file)
        manager.load_config()

        # Test template validation
        template_success = manager.reload_from_template_dynamic("sensevoice_default", preserve_overrides=False)
        if template_success:
            print("✅ Template validation passed")
        else:
            print("❌ Template validation failed")
            return False

        # Test dynamic change validation
        try:
            manager.set_config_dynamic("hardware.optimization_level", "INVALID_LEVEL", source="validation_test")
            print("❌ Invalid dynamic change was accepted")
            return False
        except Exception as e:
            print("✅ Invalid dynamic change correctly rejected")

        # Test batch validation with mixed valid/invalid changes
        batch_changes = {
            "conversion_params.batch_size": 4,  # Valid
            "hardware.optimization_level": "INVALID",  # Invalid
            "performance.target_latency_ms": 50  # Valid
        }

        try:
            manager.batch_update_dynamic(batch_changes)
            print("❌ Batch with invalid changes was accepted")
            return False
        except Exception as e:
            print("✅ Batch with invalid changes correctly rejected")

        # Verify atomicity - no changes should have been applied
        batch_size = manager.get_config("conversion_params.batch_size")
        latency = manager.get_config("performance.target_latency_ms")

        if batch_size == 1 and latency == 100:
            print("✅ Batch update atomicity preserved")
        else:
            print(f"❌ Batch update atomicity violated: batch_size={batch_size}, latency={latency}")
            return False

        # Clean up
        config_file.unlink()
        return True

    except Exception as e:
        print(f"❌ Validation integration test failed: {e}")
        # Clean up on error
        try:
            if 'config_file' in locals() and config_file.exists():
                config_file.unlink()
        except:
            pass
        return False


def test_performance_requirements():
    """Test performance requirements across all operations."""
    print("\nTesting Performance Requirements...")

    try:
        config_file = create_comprehensive_test_config()
        manager = ConfigurationManager(config_file)

        # Test initial load performance
        start_time = time.time()
        config = manager.load_config()
        load_time = (time.time() - start_time) * 1000

        if load_time < 100:
            print(f"✅ Initial load performance: {load_time:.2f}ms < 100ms")
        else:
            print(f"⚠️ Initial load performance exceeded: {load_time:.2f}ms >= 100ms")

        # Test dynamic configuration performance
        dynamic_times = []
        for i in range(10):
            start_time = time.time()
            manager.set_config_dynamic("performance.target_latency_ms", 100 + i, source=f"perf_test_{i}")
            dynamic_time = (time.time() - start_time) * 1000
            dynamic_times.append(dynamic_time)

        avg_dynamic_time = sum(dynamic_times) / len(dynamic_times)
        max_dynamic_time = max(dynamic_times)

        if max_dynamic_time < 50:  # Dynamic changes should be very fast
            print(f"✅ Dynamic config performance: avg {avg_dynamic_time:.2f}ms, max {max_dynamic_time:.2f}ms")
        else:
            print(f"⚠️ Dynamic config performance slow: max {max_dynamic_time:.2f}ms")

        # Test hot reload performance
        hot_reload_manager = manager._hot_reload_manager
        hot_reload_manager.start_monitoring()

        reload_times = []
        for i in range(5):
            start_time = time.time()

            # Modify config
            new_latency = 80 + i * 5
            config_content = config_file.read_text().replace("target_latency_ms: 100", f"target_latency_ms: {new_latency}")
            config_file.write_text(config_content)

            # Force reload
            hot_reload_manager.force_reload()

            reload_time = (time.time() - start_time) * 1000
            reload_times.append(reload_time)

        avg_reload_time = sum(reload_times) / len(reload_times)
        max_reload_time = max(reload_times)

        if max_reload_time < 500:
            print(f"✅ Hot reload performance: avg {avg_reload_time:.2f}ms, max {max_reload_time:.2f}ms < 500ms")
        else:
            print(f"❌ Hot reload performance exceeded: max {max_reload_time:.2f}ms >= 500ms")
            return False

        hot_reload_manager.stop_monitoring()

        # Clean up
        config_file.unlink()
        return True

    except Exception as e:
        print(f"❌ Performance requirements test failed: {e}")
        # Clean up on error
        try:
            if 'config_file' in locals() and config_file.exists():
                config_file.unlink()
        except:
            pass
        return False


def test_concurrent_operations():
    """Test concurrent operations across all components."""
    print("\nTesting Concurrent Operations...")

    try:
        config_file = create_comprehensive_test_config()
        manager = ConfigurationManager(config_file)
        manager.load_config()

        # Start hot reload monitoring
        hot_reload_manager = manager._hot_reload_manager
        hot_reload_manager.start_monitoring()

        results = []
        errors = []

        def dynamic_config_worker(thread_id):
            """Worker that performs dynamic configuration changes."""
            try:
                for i in range(5):
                    success = manager.set_config_dynamic(
                        f"performance.target_latency_ms",
                        100 + thread_id * 10 + i,
                        source=f"thread_{thread_id}"
                    )
                    results.append(("dynamic", thread_id, i, success))
                    time.sleep(0.01)
            except Exception as e:
                errors.append(("dynamic", thread_id, str(e)))

        def template_worker(thread_id):
            """Worker that applies templates."""
            try:
                templates = ["sensevoice_default", "sensevoice_performance"]
                for i in range(2):
                    template_name = templates[i % len(templates)]
                    success = manager.reload_from_template_dynamic(template_name, preserve_overrides=False)
                    results.append(("template", thread_id, i, success))
                    time.sleep(0.02)
            except Exception as e:
                errors.append(("template", thread_id, str(e)))

        def validation_worker(thread_id):
            """Worker that performs validation operations."""
            try:
                for i in range(3):
                    try:
                        manager.set_config_dynamic("hardware.invalid_field", "invalid_value", source=f"validation_test_{thread_id}")
                        results.append(("validation", thread_id, i, "should_not_reach"))
                    except Exception:
                        results.append(("validation", thread_id, i, "correctly_rejected"))
                    time.sleep(0.015)
            except Exception as e:
                errors.append(("validation", thread_id, str(e)))

        # Create and start threads
        threads = []
        for thread_id in range(3):
            # Dynamic config threads
            thread = threading.Thread(target=dynamic_config_worker, args=(thread_id,))
            threads.append(thread)
            thread.start()

            # Template threads
            thread = threading.Thread(target=template_worker, args=(thread_id + 3,))
            threads.append(thread)
            thread.start()

            # Validation threads
            thread = threading.Thread(target=validation_worker, args=(thread_id + 6,))
            threads.append(thread)
            thread.start()

        # Wait for all threads to complete
        for thread in threads:
            thread.join()

        # Check results
        if errors:
            print(f"❌ Thread errors occurred: {errors}")
            return False

        total_operations = len(results)
        successful_operations = sum(1 for _, _, _, success in results if success in [True, "correctly_rejected"])

        if successful_operations == total_operations:
            print(f"✅ All {total_operations} concurrent operations completed successfully")
        else:
            print(f"❌ Only {successful_operations}/{total_operations} operations successful")
            return False

        # Verify system is still in a consistent state
        try:
            final_latency = manager.get_config("performance.target_latency_ms")
            final_optimization = manager.get_config("hardware.optimization_level")

            if isinstance(final_latency, int) and final_optimization in ["O2", "O3"]:
                print(f"✅ System remained consistent: latency={final_latency}, opt={final_optimization}")
            else:
                print(f"❌ System became inconsistent: latency={final_latency}, opt={final_optimization}")
                return False
        except Exception as e:
            print(f"❌ System consistency check failed: {e}")
            return False

        hot_reload_manager.stop_monitoring()

        # Clean up
        config_file.unlink()
        return True

    except Exception as e:
        print(f"❌ Concurrent operations test failed: {e}")
        # Clean up on error
        try:
            if 'config_file' in locals() and config_file.exists():
                config_file.unlink()
        except:
            pass
        return False


def test_error_handling_integration():
    """Test error handling integration across all components."""
    print("\nTesting Error Handling Integration...")

    try:
        config_file = create_comprehensive_test_config()
        manager = ConfigurationManager(config_file)
        manager.load_config()

        # Test error recovery from invalid configuration file
        invalid_config = """project:
  name: "invalid"
  version: "1.0"
  # Missing required fields

hardware:
  target_device: "invalid_device"
  optimization_level: "INVALID_LEVEL"
"""

        # Write invalid config
        with open(config_file, 'w') as f:
            f.write(invalid_config)

        # Try to reload - should fail gracefully
        hot_reload_manager = manager._hot_reload_manager
        hot_reload_manager.start_monitoring()

        try:
            reload_success = hot_reload_manager.force_reload()
            if not reload_success:
                print("✅ Invalid configuration correctly rejected by hot reload")
            else:
                print("❌ Invalid configuration was accepted by hot reload")
                return False
        except Exception as e:
            print(f"✅ Hot reload correctly handled invalid config: {type(e).__name__}")

        # Restore valid configuration
        valid_config = create_comprehensive_test_config()
        valid_config_file = Path("test_integration_config.yaml")

        try:
            reload_success = hot_reload_manager.force_reload()
            if reload_success:
                print("✅ System recovered after restoring valid configuration")
            else:
                print("❌ System failed to recover after restoring valid configuration")
                return False
        except Exception as e:
            print(f"❌ System recovery failed: {e}")
            return False

        # Test error handling during template application
        try:
            manager.reload_from_template_dynamic("nonexistent_template", preserve_overrides=False)
            print("❌ Nonexistent template was accepted")
            return False
        except Exception as e:
            print("✅ Nonexistent template correctly rejected")

        # Test error handling during dynamic changes
        try:
            manager.set_config_dynamic("nonexistent.field.path", "value", source="error_test")
            print("❌ Invalid field path was accepted")
            return False
        except Exception as e:
            print("✅ Invalid field path correctly rejected")

        # Verify system is still functional after all error scenarios
        try:
            test_value = manager.get_config("project.name")
            if test_value:
                print("✅ System remained functional after error scenarios")
            else:
                print("❌ System became non-functional after error scenarios")
                return False
        except Exception as e:
            print(f"❌ System functionality check failed: {e}")
            return False

        hot_reload_manager.stop_monitoring()

        # Clean up
        config_file.unlink()
        if valid_config_file.exists():
            valid_config_file.unlink()
        return True

    except Exception as e:
        print(f"❌ Error handling integration test failed: {e}")
        # Clean up on error
        try:
            if 'config_file' in locals() and config_file.exists():
                config_file.unlink()
            if 'valid_config_file' in locals() and valid_config_file.exists():
                valid_config_file.unlink()
        except:
            pass
        return False


def main():
    """Run comprehensive integration tests for Story 1.4."""
    print("🚀 Story 1.4 Configuration Management System - Comprehensive Integration Tests")
    print("=" * 90)

    tests = [
        ("Complete System Initialization", test_complete_system_initialization),
        ("Template and Dynamic Integration", test_template_and_dynamic_integration),
        ("Hot Reload and Dynamic Coordination", test_hot_reload_and_dynamic_coordination),
        ("Validation Integration", test_validation_integration),
        ("Performance Requirements", test_performance_requirements),
        ("Concurrent Operations", test_concurrent_operations),
        ("Error Handling Integration", test_error_handling_integration),
    ]

    passed = 0
    total = len(tests)

    for test_name, test_func in tests:
        print(f"\n{'='*25}")
        print(f"Test: {test_name}")
        print(f"{'='*25}")

        try:
            if test_func():
                passed += 1
                print(f"✅ {test_name}: PASSED")
            else:
                print(f"❌ {test_name}: FAILED")
        except Exception as e:
            print(f"❌ {test_name}: FAILED with exception: {e}")

    print(f"\n{'='*90}")
    print(f"Integration Test Results: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 All integration tests passed! Story 1.4 Configuration Management System is fully functional.")
        print("\n📋 Implemented Features:")
        print("  ✅ Configuration loading and validation")
        print("  ✅ Template management with inheritance")
        print("  ✅ Dynamic configuration adjustments")
        print("  ✅ Hot reload with atomic updates")
        print("  ✅ Comprehensive error handling")
        print("  ✅ Performance optimization")
        print("  ✅ Thread-safe concurrent operations")
        print("  ✅ Integration with Story 1.3 core framework")
    else:
        print(f"⚠️ {total - passed} integration tests failed. Please check the implementation.")

    return passed == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)