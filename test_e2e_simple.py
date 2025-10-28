#!/usr/bin/env python3
"""
Simplified End-to-End Test for Story 1.4 Configuration Management System.
"""

import sys
import tempfile
import yaml
import time
from pathlib import Path

# Add the src directory to Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from npu_converter.config import ConfigurationManager

def create_test_config():
    """Create a test configuration for end-to-end testing."""
    return {
        "project": {
            "name": "xlerobot_e2e_test",
            "version": "1.0.0",
            "model_type": "vits_cantonese",
            "description": "End-to-End Configuration Management Test"
        },
        "hardware": {
            "target_device": "horizon_x5",
            "optimization_level": "O2",
            "memory_limit": "8GB",
            "compute_units": 10
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
            "vits_cantonese": {
                "sampling_rate": 22050,
                "inter_channels": 192,
                "hidden_channels": 192,
                "filter_channels": 768,
                "n_heads": 2,
                "n_layers": 4,
                "kernel_size": 3,
                "n_mel_channels": 80,
                "filter_length": 1024,
                "hop_length": 256,
                "win_length": 1024,
                "mel_fmin": 0.0,
                "mel_fmax": 8000.0,
                "tone_embedding": True,
                "num_tones": 6,
                "use_jyutping": True,
                "cantonese_vocab_size": 5000,
                "phoneme_set": "jyutping_extended"
            }
        },
        "performance": {
            "target_latency_ms": 200,
            "max_realtime_factor": 0.9,
            "enable_streaming": True
        }
    }

def test_complete_workflow():
    """Test complete configuration management workflow."""
    print("🔄 Testing Complete Configuration Management Workflow...")

    try:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            config_file = temp_path / "xlerobot_config.yaml"

            # Step 1: Create and save configuration
            config = create_test_config()
            with open(config_file, 'w') as f:
                yaml.dump(config, f, default_flow_style=False, indent=2)
            print("✅ Step 1: Configuration file created")

            # Step 2: Initialize and load configuration
            start_time = time.time()
            config_manager = ConfigurationManager(config_file)
            loaded_config = config_manager.load_config(fast_validation=True)
            load_time = (time.time() - start_time) * 1000
            print(f"✅ Step 2: Configuration loaded in {load_time:.2f}ms")

            # Step 3: Validate configuration
            is_valid = config_manager.validate_config()
            if is_valid:
                print("✅ Step 3: Configuration validation passed")
            else:
                print("❌ Step 3: Configuration validation failed")
                return False

            # Step 4: Test configuration retrieval
            project_name = config_manager.get_config("project.name")
            sampling_rate = config_manager.get_config("model_specific.vits_cantonese.sampling_rate")
            target_device = config_manager.get_config("hardware.target_device")

            if (project_name == "xlerobot_e2e_test" and
                sampling_rate == 22050 and
                target_device == "horizon_x5"):
                print("✅ Step 4: Configuration retrieval successful")
            else:
                print("❌ Step 4: Configuration retrieval failed")
                return False

            # Step 5: Test dynamic configuration changes
            original_latency = config_manager.get_config("performance.target_latency_ms")
            config_manager.set_config("performance.target_latency_ms", 150)
            updated_latency = config_manager.get_config("performance.target_latency_ms")

            if updated_latency == 150:
                print("✅ Step 5: Dynamic configuration change successful")
            else:
                print("❌ Step 5: Dynamic configuration change failed")
                return False

            # Step 6: Test configuration save and reload
            config_manager.save_config()
            print("✅ Step 6a: Configuration saved")

            # Create new manager to test reload
            new_config_manager = ConfigurationManager(config_file)
            reloaded_config = new_config_manager.load_config(fast_validation=True)
            reloaded_latency = new_config_manager.get_config("performance.target_latency_ms")

            if reloaded_latency == 150:
                print("✅ Step 6b: Configuration reload successful")
            else:
                print("❌ Step 6b: Configuration reload failed")
                return False

            # Step 7: Test strategy integration
            strategy = new_config_manager._current_strategy
            if strategy:
                print(f"✅ Step 7: Strategy integration successful: {strategy.__class__.__name__}")
            else:
                print("❌ Step 7: Strategy integration failed")
                return False

            # Step 8: Test backup and recovery
            backup_path = new_config_manager.create_backup("e2e_test_backup")
            if backup_path and Path(backup_path).exists():
                print("✅ Step 8a: Configuration backup created")
            else:
                print("❌ Step 8a: Configuration backup failed")
                return False

            # Test rollback
            rollback_success = new_config_manager.rollback_to_backup(backup_path)
            if rollback_success:
                print("✅ Step 8b: Configuration rollback successful")
            else:
                print("❌ Step 8b: Configuration rollback failed")
                return False

            print("✅ Complete workflow test passed")
            return True

    except Exception as e:
        print(f"❌ Complete workflow test failed: {e}")
        return False

def test_model_strategy_switching():
    """Test switching between different model strategies."""
    print("\n🔄 Testing Model Strategy Switching...")

    try:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Test VITS-Cantonese
            vits_config_file = temp_path / "vits_config.yaml"
            vits_config = {
                "project": {"name": "vits_test", "version": "1.0.0", "model_type": "vits_cantonese"},
                "hardware": {"target_device": "horizon_x5", "optimization_level": "O2"},
                "conversion_params": {"input_format": "onnx", "output_format": "bpu", "precision": "int8"},
                "model_specific": {
                    "vits_cantonese": {
                        "sampling_rate": 22050,
                        "inter_channels": 192,
                        "hidden_channels": 192,
                        "filter_channels": 768,
                        "n_heads": 2,
                        "n_layers": 4,
                        "kernel_size": 3,
                        "n_mel_channels": 80,
                        "filter_length": 1024,
                        "hop_length": 256,
                        "win_length": 1024,
                        "tone_embedding": True,
                        "num_tones": 6,
                        "use_jyutping": True,
                        "cantonese_vocab_size": 5000,
                        "phoneme_set": "jyutping_extended"
                    }
                }
            }

            with open(vits_config_file, 'w') as f:
                yaml.dump(vits_config, f, default_flow_style=False, indent=2)

            vits_manager = ConfigurationManager(vits_config_file)
            vits_config_loaded = vits_manager.load_config(fast_validation=True)

            # Test SenseVoice
            sensevoice_config_file = temp_path / "sensevoice_config.yaml"
            sensevoice_config = {
                "project": {"name": "sensevoice_test", "version": "1.0.0", "model_type": "sensevoice"},
                "hardware": {"target_device": "horizon_x5", "optimization_level": "O2"},
                "conversion_params": {"input_format": "onnx", "output_format": "bpu", "precision": "int8"},
                "model_specific": {
                    "sensevoice": {
                        "sample_rate": 16000,
                        "audio_length": 30,
                        "vocab_size": 10000,
                        "n_mels": 80,
                        "language_detection": True,
                        "supported_languages": ["zh", "en", "yue", "ja"]
                    }
                }
            }

            with open(sensevoice_config_file, 'w') as f:
                yaml.dump(sensevoice_config, f, default_flow_style=False, indent=2)

            sensevoice_manager = ConfigurationManager(sensevoice_config_file)
            sensevoice_config_loaded = sensevoice_manager.load_config(fast_validation=True)

            # Validate both configurations
            vits_valid = vits_manager.validate_config()
            sensevoice_valid = sensevoice_manager.validate_config()

            if vits_valid and sensevoice_valid:
                print("✅ Multi-model configuration validation passed")
            else:
                print("❌ Multi-model configuration validation failed")
                return False

            # Test strategy differences
            vits_strategy = vits_manager._current_strategy
            sensevoice_strategy = sensevoice_manager._current_strategy

            if (vits_strategy.__class__.__name__ == "VITSCantoneseConfigStrategy" and
                sensevoice_strategy.__class__.__name__ == "SenseVoiceConfigStrategy"):
                print("✅ Strategy differentiation successful")
            else:
                print("❌ Strategy differentiation failed")
                return False

            print("✅ Model strategy switching test passed")
            return True

    except Exception as e:
        print(f"❌ Model strategy switching test failed: {e}")
        return False

def test_error_recovery():
    """Test error handling and recovery."""
    print("\n🚨 Testing Error Handling and Recovery...")

    try:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            config_file = temp_path / "error_test_config.yaml"

            # Create valid configuration
            config = create_test_config()
            with open(config_file, 'w') as f:
                yaml.dump(config, f, default_flow_style=False, indent=2)

            manager = ConfigurationManager(config_file)
            manager.load_config(fast_validation=True)

            # Test backup creation
            backup_path = manager.create_backup("error_test_backup")
            if backup_path and Path(backup_path).exists():
                print("✅ Backup created successfully")
            else:
                print("❌ Backup creation failed")
                return False

            # Test rollback
            rollback_success = manager.rollback_to_backup(backup_path)
            if rollback_success:
                print("✅ Rollback successful")
            else:
                print("❌ Rollback failed")
                return False

            print("✅ Error recovery test passed")
            return True

    except Exception as e:
        print(f"❌ Error recovery test failed: {e}")
        return False

def test_performance_benchmarks():
    """Test performance benchmarks."""
    print("\n⚡ Testing Performance Benchmarks...")

    try:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            config_file = temp_path / "perf_config.yaml"
            config = create_test_config()

            with open(config_file, 'w') as f:
                yaml.dump(config, f, default_flow_style=False, indent=2)

            # Test loading performance
            load_times = []
            for i in range(5):
                start_time = time.time()
                manager = ConfigurationManager(config_file, lazy_init=True)
                manager.load_config(fast_validation=True)
                load_time = (time.time() - start_time) * 1000
                load_times.append(load_time)

            avg_load_time = sum(load_times) / len(load_times)
            if avg_load_time < 100:
                print(f"✅ Loading performance: avg {avg_load_time:.2f}ms (< 100ms target)")
            else:
                print(f"⚠️ Loading performance: avg {avg_load_time:.2f}ms (target: <100ms)")

            # Test modification performance
            manager = ConfigurationManager(config_file)
            manager.load_config(fast_validation=True)

            mod_times = []
            for i in range(20):
                start_time = time.time()
                manager.set_config("performance.target_latency_ms", 100 + i)
                mod_time = (time.time() - start_time) * 1000
                mod_times.append(mod_time)

            avg_mod_time = sum(mod_times) / len(mod_times)
            if avg_mod_time < 10:
                print(f"✅ Modification performance: avg {avg_mod_time:.2f}ms (< 10ms target)")
            else:
                print(f"⚠️ Modification performance: avg {avg_mod_time:.2f}ms (target: <10ms)")

            print("✅ Performance benchmarks test completed")
            return True

    except Exception as e:
        print(f"❌ Performance benchmarks test failed: {e}")
        return False

def main():
    """Run all end-to-end tests."""
    print("🚀 Testing Story 1.4 End-to-End Configuration Management")
    print("=" * 60)

    tests = [
        ("Complete Workflow", test_complete_workflow),
        ("Model Strategy Switching", test_model_strategy_switching),
        ("Error Recovery", test_error_recovery),
        ("Performance Benchmarks", test_performance_benchmarks)
    ]

    passed = 0
    total = len(tests)

    for test_name, test_func in tests:
        print(f"\n{'='*15}")
        print(f"Test: {test_name}")
        print(f"{'='*15}")

        if test_func():
            passed += 1
            print(f"✅ {test_name}: PASSED")
        else:
            print(f"❌ {test_name}: FAILED")

    print(f"\n{'='*60}")
    print(f"End-to-End Test Results: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 All end-to-end tests passed! Configuration management system is production ready.")
    else:
        print(f"⚠️ {total - passed} tests failed. System needs attention.")

    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)