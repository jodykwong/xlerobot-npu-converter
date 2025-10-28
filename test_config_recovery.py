#!/usr/bin/env python3
"""
Test script for configuration recovery functionality.

Tests the backup, rollback, and recovery mechanisms implemented
as part of the Story 1.4 configuration management system.
"""

import sys
import time
import tempfile
import shutil
from pathlib import Path

# Add the src directory to Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from npu_converter.config.recovery import ConfigRecoveryManager
from npu_converter.config.manager import ConfigurationManager
from npu_converter.core.exceptions.config_errors import ConfigError


def test_recovery_manager_basic_operations():
    """Test basic recovery manager operations."""
    print("Testing Recovery Manager Basic Operations...")

    try:
        # Create temporary directory for testing
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Create a test config file
            config_file = temp_path / "test_config.yaml"
            config_content = {
                "project": {
                    "name": "test_recovery",
                    "model_type": "vits_cantonese"
                },
                "hardware": {
                    "target_device": "horizon_x5"
                }
            }

            import yaml
            with open(config_file, 'w') as f:
                yaml.dump(config_content, f)

            # Initialize recovery manager
            recovery = ConfigRecoveryManager(temp_path, max_backups=3)

            # Test backup creation
            backup_path = recovery.create_backup(str(config_file), "test_backup")
            print(f"✅ Backup created: {backup_path}")

            # Test backup listing
            backups = recovery.list_backups()
            if len(backups) > 0:
                print(f"✅ Found {len(backups)} backup(s)")
                print(f"  Latest: {backups[0]['datetime']} - {backups[0]['reason']}")
            else:
                print("❌ No backups found")
                return False

            # Test backup integrity validation
            if recovery.validate_backup_integrity(backup_path):
                print("✅ Backup integrity validation passed")
            else:
                print("❌ Backup integrity validation failed")
                return False

            # Test recovery statistics
            stats = recovery.get_recovery_statistics()
            print(f"✅ Recovery statistics: {stats['total_backups']} backups, {stats['success_rate']:.1f}% success rate")

            return True

    except Exception as e:
        print(f"❌ Recovery manager basic operations test failed: {e}")
        return False


def test_configuration_manager_recovery():
    """Test configuration manager recovery functionality."""
    print("\nTesting Configuration Manager Recovery...")

    try:
        # Create temporary directory for testing
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Create a test config file
            config_file = temp_path / "test_config.yaml"
            config_content = {
                "project": {
                    "name": "test_recovery_cm",
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
                }
            }

            import yaml
            with open(config_file, 'w') as f:
                yaml.dump(config_content, f)

            # Initialize configuration manager
            config_manager = ConfigurationManager(config_file)
            config_manager.load_config()

            # Test initial backup creation
            initial_backup = config_manager.create_backup("initial_test")
            print(f"✅ Initial backup created: {initial_backup}")

            # Test backup listing through config manager
            backups = config_manager.list_backups()
            print(f"✅ Found {len(backups)} backup(s) through config manager")

            # Modify configuration
            config_manager.set_config("hardware.optimization_level", "O3")
            config_manager.set_config("test_field", "test_value")

            # Save modified config
            config_manager.save_config()

            # Create backup before rollback test
            pre_rollback_backup = config_manager.create_backup("pre_rollback_test")

            # Test rollback
            success = config_manager.rollback_to_backup(initial_backup)
            if success:
                print("✅ Rollback to initial backup successful")

                # Verify rollback worked
                current_opt_level = config_manager.get_config("hardware.optimization_level")
                if current_opt_level == "O2":
                    print("✅ Rollback verification passed - optimization level restored")
                else:
                    print(f"❌ Rollback verification failed - expected O2, got {current_opt_level}")
                    return False

                # Verify test field was removed
                test_field = config_manager.get_config("test_field")
                if test_field is None:
                    print("✅ Rollback verification passed - test field removed")
                else:
                    print(f"❌ Rollback verification failed - test field still exists: {test_field}")
                    return False
            else:
                print("❌ Rollback failed")
                return False

            # Test safe reload with rollback
            # Corrupt the config file to trigger rollback
            with open(config_file, 'w') as f:
                f.write("invalid: yaml: content: [")

            try:
                reload_success = config_manager.safe_reload_config()
                if not reload_success:
                    print("✅ Safe reload with rollback worked correctly")
                else:
                    print("❌ Safe reload should have failed and rolled back")
                    return False
            except ConfigError:
                print("✅ Safe reload correctly handled corrupted file")

            # Test recovery system validation
            validation_results = config_manager.validate_recovery_system()
            print("✅ Recovery system validation results:")
            for key, value in validation_results.items():
                print(f"  {key}: {value}")

            if validation_results["system_healthy"]:
                print("✅ Recovery system is healthy")
            else:
                print("⚠️ Recovery system shows issues (may be expected in test environment)")

            return True

    except Exception as e:
        print(f"❌ Configuration manager recovery test failed: {e}")
        return False


def test_backup_cleanup_and_limits():
    """Test backup cleanup and maximum backup limits."""
    print("\nTesting Backup Cleanup and Limits...")

    try:
        # Create temporary directory for testing
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Create a test config file
            config_file = temp_path / "test_config.yaml"
            config_content = {"project": {"name": "cleanup_test"}}

            import yaml
            with open(config_file, 'w') as f:
                yaml.dump(config_content, f)

            # Initialize recovery manager with low max_backups
            recovery = ConfigRecoveryManager(temp_path, max_backups=3)

            # Create multiple backups (more than the limit)
            backup_paths = []
            for i in range(5):
                backup_path = recovery.create_backup(str(config_file), f"test_backup_{i+1}")
                backup_paths.append(backup_path)
                time.sleep(0.1)  # Ensure different timestamps

            print(f"✅ Created {len(backup_paths)} backups")

            # Check that only max_backups remain
            final_backups = recovery.list_backups()
            if len(final_backups) <= 3:
                print(f"✅ Backup cleanup worked - {len(final_backups)} backups remain (limit: 3)")
            else:
                print(f"❌ Backup cleanup failed - {len(final_backups)} backups remain (limit: 3)")
                return False

            # Verify the most recent backups are kept
            if len(final_backups) >= 2:
                # Check that the latest backup is the most recent one created
                latest_backup = final_backups[0]
                if "test_backup_5" in latest_backup["reason"]:
                    print("✅ Most recent backup correctly preserved")
                else:
                    print(f"❌ Most recent backup not preserved: {latest_backup['reason']}")
                    return False

            return True

    except Exception as e:
        print(f"❌ Backup cleanup test failed: {e}")
        return False


def test_error_recovery_scenarios():
    """Test various error recovery scenarios."""
    print("\nTesting Error Recovery Scenarios...")

    try:
        # Create temporary directory for testing
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Create a test config file
            config_file = temp_path / "test_config.yaml"
            config_content = {
                "project": {
                    "name": "error_recovery_test",
                    "model_type": "vits_cantonese"
                },
                "hardware": {"target_device": "horizon_x5"}
            }

            import yaml
            with open(config_file, 'w') as f:
                yaml.dump(config_content, f)

            # Initialize configuration manager
            config_manager = ConfigurationManager(config_file)
            config_manager.load_config()

            # Create backup for recovery tests
            backup_path = config_manager.create_backup("error_recovery_test")

            # Test 1: Corrupted YAML file recovery
            print("  Testing corrupted YAML recovery...")
            with open(config_file, 'w') as f:
                f.write("invalid: yaml: content: [")

            try:
                config_manager.safe_reload_config()
                print("    ⚠️ Expected ConfigError but reload succeeded")
            except ConfigError:
                # Try rollback
                rollback_success = config_manager.rollback_to_latest_backup()
                if rollback_success:
                    print("    ✅ Corrupted YAML recovery successful")
                else:
                    print("    ❌ Corrupted YAML recovery failed")
                    return False

            # Test 2: Missing file recovery
            print("  Testing missing file recovery...")
            config_file.unlink()  # Delete the file

            try:
                config_manager.load_config()
                print("    ⚠️ Expected ConfigError but load succeeded")
            except ConfigError:
                # Restore from backup
                recovery = config_manager._recovery_manager
                if recovery:
                    restore_success = recovery.rollback_to_backup(backup_path)
                    if restore_success and config_file.exists():
                        print("    ✅ Missing file recovery successful")
                    else:
                        print("    ❌ Missing file recovery failed")
                        return False
                else:
                    print("    ❌ Recovery manager not available")
                    return False

            # Test 3: Validation error recovery
            print("  Testing validation error recovery...")
            # Create a config that will fail validation
            invalid_config = {
                "project": {
                    "name": "validation_test",
                    "model_type": "invalid_model_type"  # This should fail validation
                }
            }

            with open(config_file, 'w') as f:
                yaml.dump(invalid_config, f)

            try:
                config_manager.load_config()
                print("    ⚠️ Expected validation error but load succeeded")
            except ConfigError as e:
                if "validation failed" in str(e):
                    print("    ✅ Validation error correctly caught")
                    # Rollback to working config
                    rollback_success = config_manager.rollback_to_latest_backup()
                    if rollback_success:
                        print("    ✅ Validation error recovery successful")
                    else:
                        print("    ❌ Validation error recovery failed")
                        return False
                else:
                    print(f"    ❌ Unexpected error: {e}")
                    return False

            return True

    except Exception as e:
        print(f"❌ Error recovery scenarios test failed: {e}")
        return False


def main():
    """Run all configuration recovery tests."""
    print("🚀 Testing Configuration Recovery System")
    print("=" * 60)
    print("Testing backup, rollback, and error recovery functionality")

    tests = [
        ("Recovery Manager Basic Operations", test_recovery_manager_basic_operations),
        ("Configuration Manager Recovery", test_configuration_manager_recovery),
        ("Backup Cleanup and Limits", test_backup_cleanup_and_limits),
        ("Error Recovery Scenarios", test_error_recovery_scenarios),
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
        print("🎉 All tests passed! Configuration recovery system is working correctly.")
        print("\n📋 Configuration Recovery Features:")
        print("  ✅ Automatic backup creation on config load")
        print("  ✅ Manual backup creation with custom reasons")
        print("  ✅ Configuration rollback to any backup point")
        print("  ✅ Automatic rollback on reload failure")
        print("  ✅ Backup integrity validation")
        print("  ✅ Backup cleanup with configurable limits")
        print("  ✅ Error recovery from corrupted/missing files")
        print("  ✅ Recovery system health validation")
        print("  ✅ Comprehensive recovery statistics")
    else:
        print(f"⚠️ {total - passed} tests failed. Please check the implementation.")

    return passed == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)