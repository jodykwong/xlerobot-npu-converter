#!/usr/bin/env python3
"""
Simple test script for configuration recovery functionality.
Tests core backup and rollback mechanisms.
"""

import sys
import time
import tempfile
from pathlib import Path

# Add the src directory to Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from npu_converter.config.recovery import ConfigRecoveryManager


def test_basic_recovery():
    """Test basic backup and recovery functionality."""
    print("🚀 Testing Basic Configuration Recovery")

    try:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Create a test config file
            config_file = temp_path / "test_config.yaml"
            original_content = {
                "project": {
                    "name": "recovery_test",
                    "model_type": "vits_cantonese",
                    "version": "1.0.0"
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
                yaml.dump(original_content, f)

            print("✅ Created test configuration file")

            # Initialize recovery manager
            recovery = ConfigRecoveryManager(temp_path, max_backups=5)

            # Test backup creation
            backup1 = recovery.create_backup(str(config_file), "original_config")
            print(f"✅ Created backup 1: {backup1}")

            # Modify config
            modified_content = original_content.copy()
            modified_content["hardware"]["optimization_level"] = "O3"
            modified_content["test_field"] = "test_value"

            with open(config_file, 'w') as f:
                yaml.dump(modified_content, f)

            backup2 = recovery.create_backup(str(config_file), "modified_config")
            print(f"✅ Created backup 2: {backup2}")

            # List backups
            backups = recovery.list_backups()
            print(f"✅ Found {len(backups)} backups:")
            for i, backup in enumerate(backups):
                print(f"  {i+1}. {backup['datetime']} - {backup['reason']}")

            # Test rollback to original
            success = recovery.rollback_to_backup(backup1)
            if success:
                print("✅ Rollback to original backup successful")

                # Verify rollback worked by reading file directly
                with open(config_file, 'r') as f:
                    restored_content = yaml.safe_load(f)

                if restored_content["hardware"]["optimization_level"] == "O2":
                    print("✅ Rollback verification passed - optimization level restored")
                else:
                    print(f"❌ Rollback verification failed")
                    return False

                if "test_field" not in restored_content:
                    print("✅ Rollback verification passed - test field removed")
                else:
                    print(f"❌ Rollback verification failed - test field still exists")
                    return False
            else:
                print("❌ Rollback failed")
                return False

            # Test backup integrity
            if recovery.validate_backup_integrity(backup1):
                print("✅ Backup integrity validation passed")
            else:
                print("❌ Backup integrity validation failed")
                return False

            # Test recovery statistics
            stats = recovery.get_recovery_statistics()
            print(f"✅ Recovery statistics:")
            print(f"  Total backups: {stats['total_backups']}")
            print(f"  Recovery attempts: {stats['recovery_attempts']}")
            print(f"  Successful recoveries: {stats['successful_recoveries']}")
            print(f"  Success rate: {stats['success_rate']:.1f}%")

            return True

    except Exception as e:
        print(f"❌ Basic recovery test failed: {e}")
        return False


def test_multiple_backups_and_cleanup():
    """Test multiple backup creation and cleanup."""
    print("\n🔄 Testing Multiple Backups and Cleanup")

    try:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Create a test config file
            config_file = temp_path / "test_config.yaml"
            base_content = {"project": {"name": "cleanup_test"}}

            import yaml
            with open(config_file, 'w') as f:
                yaml.dump(base_content, f)

            # Initialize recovery manager with low limit
            recovery = ConfigRecoveryManager(temp_path, max_backups=3)

            # Create multiple backups
            backup_paths = []
            for i in range(6):
                # Modify content slightly
                content = base_content.copy()
                content["iteration"] = i + 1

                with open(config_file, 'w') as f:
                    yaml.dump(content, f)

                backup_path = recovery.create_backup(str(config_file), f"iteration_{i+1}")
                backup_paths.append(backup_path)
                time.sleep(0.01)  # Ensure different timestamps

            print(f"✅ Created {len(backup_paths)} backups")

            # Check cleanup
            final_backups = recovery.list_backups()
            print(f"✅ After cleanup: {len(final_backups)} backups remain (limit: 3)")

            if len(final_backups) <= 3:
                print("✅ Backup cleanup worked correctly")
            else:
                print("❌ Backup cleanup failed")
                return False

            return True

    except Exception as e:
        print(f"❌ Multiple backups test failed: {e}")
        return False


def main():
    """Run simple recovery tests."""
    print("=" * 60)
    print("Configuration Recovery System - Simple Tests")
    print("=" * 60)

    tests = [
        ("Basic Recovery", test_basic_recovery),
        ("Multiple Backups and Cleanup", test_multiple_backups_and_cleanup),
    ]

    passed = 0
    total = len(tests)

    for test_name, test_func in tests:
        if test_func():
            passed += 1
            print(f"✅ {test_name}: PASSED")
        else:
            print(f"❌ {test_name}: FAILED")

    print(f"\n{'='*60}")
    print(f"Test Results: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 All recovery tests passed!")
        print("\n📋 Core Recovery Features Verified:")
        print("  ✅ Configuration backup creation")
        print("  ✅ Configuration rollback functionality")
        print("  ✅ Backup integrity validation")
        print("  ✅ Multiple backup management")
        print("  ✅ Automatic backup cleanup")
        print("  ✅ Recovery statistics tracking")
    else:
        print(f"⚠️ {total - passed} tests failed.")

    return passed == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)