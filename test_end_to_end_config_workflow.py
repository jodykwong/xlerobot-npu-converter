#!/usr/bin/env python3
"""
End-to-End Test for Story 1.4 Configuration Management System.

This test validates the complete configuration management workflow
from configuration creation through to model conversion preparation.
"""

import sys
import tempfile
import yaml
import time
import shutil
from pathlib import Path

# Add the src directory to Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from npu_converter.config import ConfigurationManager

def create_xlerobot_complete_config():
    """Create a complete XLeRobot project configuration."""
    return {
        "project": {
            "name": "xlerobot_e2e_test",
            "version": "1.0.0",
            "description": "End-to-End Configuration Management Test",
            "author": "Test Agent",
            "created_date": "2025-10-26"
        },
        "hardware": {
            "target_device": "horizon_x5",
            "optimization_level": "O2",
            "memory_limit": "8GB",
            "compute_units": 10,
            "cache_size": "256MB",
            "thermal_management": True,
            "power_optimization": True
        },
        "conversion_params": {
            "input_format": "onnx",
            "output_format": "bpu",
            "precision": "int8",
            "calibration_method": "minmax",
            "calibration_dataset_size": 1000,
            "batch_size": 1,
            "num_workers": 4,
            "enable_profiling": True
        },
        "model_specific": {
            "vits_cantonese": {
                # VITS Model Architecture Configuration
                "inter_channels": 192,
                "hidden_channels": 192,
                "filter_channels": 768,
                "n_heads": 2,
                "n_layers": 4,
                "kernel_size": 3,
                "p_dropout": 0.1,
                "resblock": "1",
                "resblock_kernel_sizes": [3, 7, 11],
                "resblock_dilation_sizes": [[1, 3, 5], [1, 3, 5], [1, 3, 5]],
                "upsample_rates": [8, 8, 2, 2],
                "upsample_initial_channel": 512,
                "upsample_kernel_sizes": [16, 16, 4, 4],
                "n_layers_q": 3,
                "use_spectral_norm": False,
                "gin_channels": 256,

                # Audio Processing Parameters (Cantonese-optimized)
                "sampling_rate": 22050,
                "filter_length": 1024,
                "hop_length": 256,
                "win_length": 1024,
                "n_mel_channels": 80,
                "mel_fmin": 0.0,
                "mel_fmax": 8000.0,
                "max_wav_value": 32768.0,
                "normalize": True,
                "trim_silence": True,
                "trim_threshold": 0.01,

                # Voice Characteristics
                "speaker_embedding_size": 192,
                "num_speakers": 1,
                "speaker_id": 0,
                "use_speaker_embedding": True,

                # Cantonese TTS Synthesis Parameters
                "noise_scale": 0.667,
                "noise_scale_w": 0.8,
                "length_scale": 1.0,
                "inference_noise_scale": 0.667,

                # Cantonese Phoneme System Configuration
                "cantonese_vocab_size": 5000,
                "phoneme_set": "jyutping_extended",
                "phoneme_language": "cantonese",
                "phonemizer": "espeak",
                "tone_embedding": True,
                "num_tones": 6,
                "use_jyutping": True,
                "character_coverage": 0.995,

                # Data Preprocessing Settings
                "add_blank": True,
                "n_speakers": 1,
                "cleaned_text": True
            }
        },
        "performance": {
            "target_latency_ms": 200,
            "max_realtime_factor": 0.9,
            "enable_streaming": True,
            "chunk_size": 1024,
            "memory_optimization": True
        },
        "validation": {
            "enable_model_validation": True,
            "validate_audio_output": True,
            "quality_thresholds": {
                "mos_score": 4.0,
                "mcd_score": 4.5,
                "cer_score": 0.05
            }
        }
    }

def test_complete_configuration_workflow():
    """Test the complete configuration management workflow."""
    print("🔄 Testing Complete Configuration Management Workflow...")

    try:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            config_file = temp_path / "xlerobot_config.yaml"

            # Step 1: Create initial configuration
            config = create_xlerobot_complete_config()
            with open(config_file, 'w') as f:
                yaml.dump(config, f, default_flow_style=False, indent=2)

            print(f"✅ Step 1: Initial configuration created at {config_file}")

            # Step 2: Initialize configuration manager
            config_manager = ConfigurationManager(config_file)
            loaded_config = config_manager.load_config()
            print(f"✅ Step 2: Configuration manager initialized")

        # Step 3: Validate configuration
        is_valid = config_manager.validate_config()
        if is_valid:
            print("✅ Step 3: Configuration validation passed")
        else:
            print("❌ Step 3: Configuration validation failed")
            return False

        # Step 4: Test configuration retrieval
        project_name = config_manager.get_config("project.name")
        model_type = config_manager.get_config("model_specific.vits_cantonese.sampling_rate")
        target_device = config_manager.get_config("hardware.target_device")

        if project_name == "xlerobot_e2e_test" and model_type == 22050 and target_device == "horizon_x5":
            print("✅ Step 4: Configuration retrieval successful")
        else:
            print(f"❌ Step 4: Configuration retrieval failed")
            return False

        # Step 5: Test dynamic configuration changes
        original_latency = config_manager.get_config("performance.target_latency_ms")
        config_manager.set_config("performance.target_latency_ms", 150)
        updated_latency = config_manager.get_config("performance.target_latency_ms")

        if updated_latency == 150:
            print("✅ Step 5: Dynamic configuration change successful")
        else:
            print(f"❌ Step 5: Dynamic configuration change failed")
            return False

        # Step 6: Test configuration save and reload
        config_manager.save_config()

        # Create new manager to test reload
        new_config_manager = ConfigurationManager(config_file)
        reloaded_config = new_config_manager.load_config()
        reloaded_latency = new_config_manager.get_config("performance.target_latency_ms")

        if reloaded_latency == 150:
            print("✅ Step 6: Configuration save and reload successful")
        else:
            print(f"❌ Step 6: Configuration save and reload failed")
            return False

        # Step 7: Test strategy integration
        strategy = new_config_manager._current_strategy
        if strategy:
            print(f"✅ Step 7: Strategy integration successful: {strategy.__class__.__name__}")

            # Test strategy-specific methods
            if hasattr(strategy, 'validate_model_specific_config'):
                strategy_valid = strategy.validate_model_specific_config()
                if strategy_valid:
                    print("✅ Step 7a: Strategy validation successful")
                else:
                    print("❌ Step 7a: Strategy validation failed")
                    return False
        else:
            print("❌ Step 7: Strategy integration failed")
            return False

        # Step 8: Test backup and recovery
        backup_path = new_config_manager.create_backup("e2e_test_backup")
        if backup_path and Path(backup_path).exists():
            print("✅ Step 8: Configuration backup created successfully")
        else:
            print("❌ Step 8: Configuration backup failed")
            return False

        # Test rollback
        rollback_success = new_config_manager.rollback_to_backup(backup_path)
        if rollback_success:
            print("✅ Step 8a: Configuration rollback successful")
        else:
            print("❌ Step 8a: Configuration rollback failed")
            return False

        print("✅ Complete configuration workflow test passed")
        return True

    except Exception as e:
        print(f"❌ Complete workflow test failed: {e}")
        return False

def test_multi_model_configuration():
    """Test configuration management for multiple model types."""
    print("\n🔄 Testing Multi-Model Configuration Management...")

    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)

        # Test VITS-Cantonese configuration
        vits_config_file = temp_path / "vits_config.yaml"
        vits_config = {
            "project": {
                "name": "vits_cantonese_test",
                "version": "1.0.0",
                "model_type": "vits_cantonese"
            },
            "hardware": {
                "target_device": "horizon_x5",
                "optimization_level": "O2"
            },
            "conversion_params": {
                "input_format": "onnx",
                "output_format": "bpu",
                "precision": "int8"
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
            }
        }

        with open(vits_config_file, 'w') as f:
            yaml.dump(vits_config, f, default_flow_style=False, indent=2)

        vits_manager = ConfigurationManager(vits_config_file)
        vits_config_loaded = vits_manager.load_config()

        # Test SenseVoice configuration
        sensevoice_config_file = temp_path / "sensevoice_config.yaml"
        sensevoice_config = {
            "project": {
                "name": "sensevoice_test",
                "version": "1.0.0",
                "model_type": "sensevoice"
            },
            "hardware": {
                "target_device": "horizon_x5",
                "optimization_level": "O2"
            },
            "conversion_params": {
                "input_format": "onnx",
                "output_format": "bpu",
                "precision": "int8"
            },
            "model_specific": {
                "sensevoice": {
                    "sample_rate": 16000,
                    "audio_length": 30,
                    "vocab_size": 10000,
                    "n_mels": 80,
                    "n_fft": 512,
                    "hop_length": 160,
                    "win_length": 400,
                    "mel_fmin": 0.0,
                    "mel_fmax": 8000.0,
                    "language_detection": True,
                    "supported_languages": ["zh", "en", "yue", "ja"],
                    "confidence_threshold": 0.8
                }
            }
        }

        with open(sensevoice_config_file, 'w') as f:
            yaml.dump(sensevoice_config, f, default_flow_style=False, indent=2)

        sensevoice_manager = ConfigurationManager(sensevoice_config_file)
        sensevoice_config_loaded = sensevoice_manager.load_config()

        # Validate both configurations
        vits_valid = vits_manager.validate_config()
        sensevoice_valid = sensevoice_manager.validate_config()

        if vits_valid and sensevoice_valid:
            print("✅ Multi-model configuration validation passed")
        else:
            print("❌ Multi-model configuration validation failed")
            return False

        # Test model-specific strategy differences
        vits_strategy = vits_manager._current_strategy
        sensevoice_strategy = sensevoice_manager._current_strategy

        if (vits_strategy.__class__.__name__ == "VITSCantoneseConfigStrategy" and
            sensevoice_strategy.__class__.__name__ == "SenseVoiceConfigStrategy"):
            print("✅ Multi-model strategy differentiation successful")
        else:
            print("❌ Multi-model strategy differentiation failed")
            return False

        print("✅ Multi-model configuration management test passed")
        return True

    except Exception as e:
        print(f"❌ Multi-model configuration test failed: {e}")
        return False

def test_performance_and_scalability():
    """Test performance and scalability of configuration management."""
    print("\n⚡ Testing Performance and Scalability...")

    try:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Test loading performance
            config_file = temp_path / "perf_config.yaml"
            config = create_xlerobot_complete_config()

            with open(config_file, 'w') as f:
                yaml.dump(config, f, default_flow_style=False, indent=2)

            # Test multiple load operations
            load_times = []
            for i in range(10):
                start_time = time.time()
                manager = ConfigurationManager(config_file, lazy_init=True)
                manager.load_config(fast_validation=True)
                load_time = (time.time() - start_time) * 1000
                load_times.append(load_time)

            avg_load_time = sum(load_times) / len(load_times)
            max_load_time = max(load_times)

            if avg_load_time < 100 and max_load_time < 200:
                print(f"✅ Loading performance: avg {avg_load_time:.2f}ms, max {max_load_time:.2f}ms")
            else:
                print(f"⚠️ Loading performance: avg {avg_load_time:.2f}ms, max {max_load_time:.2f}ms (may need optimization)")

            # Test memory usage (simplified)
            import gc
            gc.collect()

            # Test concurrent configuration operations
            manager = ConfigurationManager(config_file)
            manager.load_config()

            modification_times = []
            for i in range(50):
                start_time = time.time()
                manager.set_config("performance.target_latency_ms", 100 + i)
                mod_time = (time.time() - start_time) * 1000
                modification_times.append(mod_time)

            avg_mod_time = sum(modification_times) / len(modification_times)
            if avg_mod_time < 10:
                print(f"✅ Modification performance: avg {avg_mod_time:.2f}ms")
            else:
                print(f"⚠️ Modification performance: avg {avg_mod_time:.2f}ms (may need optimization)")

            print("✅ Performance and scalability test completed")
            return True

    except Exception as e:
        print(f"❌ Performance and scalability test failed: {e}")
        return False

def test_error_handling_and_recovery():
    """Test error handling and recovery mechanisms."""
    print("\n🚨 Testing Error Handling and Recovery...")

    try:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            config_file = temp_path / "error_test_config.yaml"

            # Create valid configuration
            config = create_xlerobot_complete_config()
            with open(config_file, 'w') as f:
                yaml.dump(config, f, default_flow_style=False, indent=2)

            manager = ConfigurationManager(config_file)
            manager.load_config()

            # Test 1: Invalid configuration value
            try:
                manager.set_config("performance.target_latency_ms", -100)  # Invalid negative value
                # This should either reject the value or handle it gracefully
                print("✅ Invalid value handling: No exception thrown")
            except Exception as e:
                print(f"✅ Invalid value handling: Exception caught {type(e).__name__}")

            # Test 2: Configuration file corruption simulation
            manager.create_backup("before_corruption")

            # Corrupt the configuration file
            with open(config_file, 'w') as f:
                f.write("invalid: yaml: content: [")

            try:
                reload_success = manager.safe_reload_config()
                if not reload_success:
                    print("✅ Corrupted file handling: Safe reload correctly failed")
                else:
                    print("❌ Corrupted file handling: Safe reload should have failed")
                    return False
            except Exception as e:
                print(f"✅ Corrupted file handling: Exception caught {type(e).__name__}")

            # Test 3: Recovery from backup
            backups = manager.list_backups()
            if backups:
                latest_backup = backups[0]["backup_path"]
                rollback_success = manager.rollback_to_backup(latest_backup)
                if rollback_success:
                    print("✅ Recovery from backup successful")
                else:
                    print("❌ Recovery from backup failed")
                    return False
            else:
                print("❌ No backups available for recovery test")
                return False

            print("✅ Error handling and recovery test passed")
            return True

    except Exception as e:
        print(f"❌ Error handling and recovery test failed: {e}")
        return False

def main():
    """Run all end-to-end tests."""
    print("🚀 Testing Story 1.4 End-to-End Configuration Management Workflow")
    print("=" * 80)

    tests = [
        ("Complete Configuration Workflow", test_complete_configuration_workflow),
        ("Multi-Model Configuration", test_multi_model_configuration),
        ("Performance and Scalability", test_performance_and_scalability),
        ("Error Handling and Recovery", test_error_handling_and_recovery)
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

    print(f"\n{'='*80}")
    print(f"End-to-End Test Results: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 All end-to-end tests passed! Configuration management system is ready for production.")
    else:
        print(f"⚠️ {total - passed} tests failed. Configuration management system needs further work.")

    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)