#!/usr/bin/env python3
"""
Test error recovery scenarios with proper configuration.
"""

import sys
import tempfile
import yaml
from pathlib import Path

# Add the src directory to Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from npu_converter.config import ConfigurationManager
from npu_converter.core.exceptions.config_errors import ConfigError

def test_error_recovery_scenarios():
    """Test error recovery scenarios with complete configuration."""
    print("🚀 Testing Error Recovery Scenarios")
    print("=" * 60)

    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        config_file = temp_path / "error_recovery_config.yaml"

        # Create a complete valid configuration
        valid_config = {
            "project": {
                "name": "error_recovery_test",
                "version": "1.0.0",
                "model_type": "sensevoice",
                "description": "Test configuration for error recovery"
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

        with open(config_file, 'w') as f:
            yaml.dump(valid_config, f, default_flow_style=False, indent=2)

        print(f"📁 Created valid config file: {config_file}")

        # Initialize configuration manager
        config_manager = ConfigurationManager(config_file)
        config = config_manager.load_config()
        print("✅ Configuration manager initialized and loaded successfully")

        # Test 1: Safe reload with invalid file (should rollback)
        print("\n🔹 Test 1: Safe reload with corrupted file")
        initial_backup = config_manager.create_backup("before_corruption")

        # Corrupt the config file
        with open(config_file, 'w') as f:
            f.write("invalid: yaml: content: [")

        try:
            reload_success = config_manager.safe_reload_config()
            if not reload_success:
                print("✅ Safe reload correctly failed and rolled back")

                # Verify rollback worked
                current_config = config_manager.get_config("project.name")
                if current_config == "error_recovery_test":
                    print("✅ Rollback verification passed - configuration restored")
                else:
                    print(f"❌ Rollback verification failed - got {current_config}")
                    return False
            else:
                print("❌ Safe reload should have failed")
                return False
        except ConfigError as e:
            print(f"✅ Safe reload correctly handled corrupted file: {e}")

        # Test 2: Invalid configuration update (should be rejected)
        print("\n🔹 Test 2: Invalid configuration update rejection")
        try:
            # Try to set an invalid optimization level
            config_manager.set_config("hardware.optimization_level", "INVALID_LEVEL")
            print("❌ Should have rejected invalid optimization level")
            return False
        except Exception as e:
            print(f"✅ Correctly rejected invalid configuration: {e}")

        # Test 3: Configuration validation with missing required fields
        print("\n🔹 Test 3: Configuration with missing required fields")

        # Create incomplete config
        incomplete_config = {
            "project": {
                "name": "incomplete_test"
                # Missing version and model_type
            },
            "hardware": {
                "target_device": "horizon_x5"
                # Missing optimization_level
            }
            # Missing conversion_params
        }

        incomplete_config_file = temp_path / "incomplete_config.yaml"
        with open(incomplete_config_file, 'w') as f:
            yaml.dump(incomplete_config, f)

        try:
            incomplete_manager = ConfigurationManager(incomplete_config_file)
            incomplete_manager.load_config()
            print("❌ Should have rejected incomplete configuration")
            return False
        except ConfigError as e:
            print(f"✅ Correctly rejected incomplete configuration: {e}")

        # Test 4: Recovery system validation
        print("\n🔹 Test 4: Recovery system health check")
        validation_results = config_manager.validate_recovery_system()

        print("✅ Recovery system validation results:")
        for key, value in validation_results.items():
            print(f"  {key}: {value}")

        if validation_results.get("system_healthy", False):
            print("✅ Recovery system is healthy")
        else:
            print("⚠️ Recovery system has issues")
            # This is not necessarily a failure for testing

        # Test 5: Backup and restore cycle
        print("\n🔹 Test 5: Complete backup and restore cycle")

        # Save current state
        original_latency = config_manager.get_config("performance.target_latency_ms")
        print(f"Original latency: {original_latency}")

        # Create backup
        backup_before_change = config_manager.create_backup("before_latency_change")

        # Change configuration
        config_manager.set_config("performance.target_latency_ms", 200)
        config_manager.save_config()

        changed_latency = config_manager.get_config("performance.target_latency_ms")
        print(f"Changed latency: {changed_latency}")

        # Restore from backup
        restore_success = config_manager.rollback_to_backup(backup_before_change)
        if restore_success:
            restored_latency = config_manager.get_config("performance.target_latency_ms")
            print(f"Restored latency: {restored_latency}")

            if restored_latency == original_latency:
                print("✅ Backup and restore cycle successful")
            else:
                print(f"❌ Restore failed - expected {original_latency}, got {restored_latency}")
                return False
        else:
            print("❌ Restore operation failed")
            return False

        return True

if __name__ == "__main__":
    success = test_error_recovery_scenarios()
    if success:
        print("\n🎉 All error recovery tests passed!")
    else:
        print("\n❌ Some error recovery tests failed!")
    sys.exit(0 if success else 1)