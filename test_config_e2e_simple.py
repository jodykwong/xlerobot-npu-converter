#!/usr/bin/env python3
"""
Simple end-to-end test for configuration management system
"""

import sys
import tempfile
import yaml
from pathlib import Path

# Add the src directory to Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from npu_converter.config import ConfigurationManager

def test_complete_workflow():
    """Test complete configuration workflow."""
    print("🔄 Testing Complete Configuration Workflow...")

    try:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            config_file = temp_path / "e2e_config.yaml"

            # Step 1: Create configuration
            config = {
                "project": {
                    "name": "e2e_test",
                    "version": "1.0.0",
                    "model_type": "sensevoice"
                },
                "hardware": {
                    "target_device": "horizon_x5",
                    "optimization_level": "O2"
                },
                "conversion_params": {
                    "input_format": "onnx",
                    "output_format": "bpu"
                },
                "model_specific": {
                    "sensevoice": {
                        "sample_rate": 16000,
                        "audio_length": 30,
                        "vocab_size": 10000
                    }
                }
            }

            with open(config_file, 'w') as f:
                yaml.dump(config, f)
            print("✅ Step 1: Configuration file created")

            # Step 2: Load configuration
            manager = ConfigurationManager(config_file)
            loaded_config = manager.load_config()
            print("✅ Step 2: Configuration loaded successfully")

            # Step 3: Validate configuration
            is_valid = manager.validate_config()
            if is_valid:
                print("✅ Step 3: Configuration validation passed")
            else:
                print("❌ Step 3: Configuration validation failed")
                return False

            # Step 4: Test configuration modification
            manager.set_config("performance.target_latency_ms", 150)
            new_value = manager.get_config("performance.target_latency_ms")
            if new_value == 150:
                print("✅ Step 4: Configuration modification successful")
            else:
                print("❌ Step 4: Configuration modification failed")
                return False

            # Step 5: Test strategy integration
            strategy = manager.get_strategy()
            if strategy and strategy.get_model_type() == "sensevoice":
                print("✅ Step 5: Strategy integration successful")
            else:
                print("❌ Step 5: Strategy integration failed")
                return False

            # Step 6: Test performance metrics
            metrics = manager.get_metrics()
            if metrics.load_time_ms < 100:
                print(f"✅ Step 6: Performance target met ({metrics.load_time_ms:.2f}ms < 100ms)")
            else:
                print(f"⚠️ Step 6: Performance target exceeded ({metrics.load_time_ms:.2f}ms > 100ms)")

            print("✅ Complete workflow test PASSED")
            return True

    except Exception as e:
        print(f"❌ Workflow test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_backup_functionality():
    """Test backup and recovery functionality."""
    print("\n💾 Testing Backup and Recovery...")

    try:
        with tempfile.TemporaryDirectory() as temp_dir:
            config_file = Path(temp_dir) / "backup_test.yaml"

            # Create initial config
            config = {
                "project": {
                    "name": "backup_test",
                    "version": "1.0.0",
                    "model_type": "sensevoice"
                },
                "hardware": {
                    "target_device": "horizon_x5",
                    "optimization_level": "O2"
                },
                "conversion_params": {
                    "input_format": "onnx",
                    "output_format": "bpu"
                },
                "model_specific": {
                    "sensevoice": {
                        "sample_rate": 16000,
                        "audio_length": 30,
                        "vocab_size": 10000
                    }
                }
            }

            with open(config_file, 'w') as f:
                yaml.dump(config, f)

            manager = ConfigurationManager(config_file)
            manager.load_config()

            # Test backup creation
            backup_path = manager.create_backup("test_backup")
            if backup_path and Path(backup_path).exists():
                print("✅ Backup created successfully")
            else:
                print("❌ Backup creation failed")
                return False

            # Test configuration modification
            manager.set_config("project.name", "modified_config")
            manager.save_config()

            # Test rollback
            rollback_success = manager.rollback_to_backup(backup_path)
            if rollback_success:
                print("✅ Rollback successful")
            else:
                print("❌ Rollback failed")
                return False

            # Verify rollback
            current_name = manager.get_config("project.name")
            if current_name == "backup_test":
                print("✅ Rollback verification successful")
            else:
                print("❌ Rollback verification failed")
                return False

            print("✅ Backup and recovery test PASSED")
            return True

    except Exception as e:
        print(f"❌ Backup test failed: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Running End-to-End Configuration Management Tests")
    print("=" * 60)

    tests = [
        ("Complete Workflow", test_complete_workflow),
        ("Backup and Recovery", test_backup_functionality)
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
    print(f"End-to-End Test Results: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 All end-to-end tests passed!")
    else:
        print(f"⚠️ {total - passed} tests failed.")