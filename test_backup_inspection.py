#!/usr/bin/env python3
"""
Inspect backup files to understand recovery issues.
"""

import sys
import tempfile
import yaml
from pathlib import Path

# Add the src directory to Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from npu_converter.config import ConfigurationManager

def inspect_backup_files():
    """Inspect backup files to understand the issue."""
    print("🔍 Inspecting Backup Files")
    print("=" * 50)

    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        config_file = temp_path / "inspect_config.yaml"

        # Create initial config
        initial_config = {
            "project": {
                "name": "test_backup_inspection",
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
            }
        }

        with open(config_file, 'w') as f:
            yaml.dump(initial_config, f, default_flow_style=False, indent=2)

        print(f"📁 Created config file: {config_file}")
        print(f"   Initial optimization level: {initial_config['hardware']['optimization_level']}")

        # Load configuration
        config_manager = ConfigurationManager(config_file)
        loaded_config = config_manager.load_config()

        # Create initial backup
        print("\n🔹 Creating initial backup...")
        initial_backup = config_manager.create_backup("inspection_initial")
        print(f"   Initial backup: {initial_backup}")

        # Inspect backup file content
        backup_file = Path(initial_backup)
        if backup_file.exists():
            with open(backup_file, 'r') as f:
                backup_content = yaml.safe_load(f)
            backup_opt_level = backup_content.get("hardware", {}).get("optimization_level")
            print(f"   Backup optimization level: {backup_opt_level}")
            print(f"   Backup content keys: {list(backup_content.keys())}")
        else:
            print("   ❌ Backup file does not exist!")

        # Modify configuration
        print("\n🔹 Modifying configuration...")
        config_manager.set_config("hardware.optimization_level", "O3")
        config_manager.set_config("debug_field", "debug_value")
        config_manager.save_config()

        # Check current file content
        with open(config_file, 'r') as f:
            current_content = yaml.safe_load(f)
        current_opt_level = current_content.get("hardware", {}).get("optimization_level")
        print(f"   Current file optimization level: {current_opt_level}")

        # Get list of backups
        print("\n🔹 Listing all backups...")
        backups = config_manager.list_backups()
        print(f"   Total backups: {len(backups)}")
        for i, backup in enumerate(backups):
            print(f"   {i+1}. {backup['backup_path']} - {backup['reason']}")

        # Check backup directory
        backup_dir = temp_path / ".config_backups"
        if backup_dir.exists():
            print(f"\n🔹 Backup directory contents:")
            for backup_file in backup_dir.glob("*.yaml"):
                with open(backup_file, 'r') as f:
                    content = yaml.safe_load(f)
                opt_level = content.get("hardware", {}).get("optimization_level")
                print(f"   {backup_file.name}: optimization_level = {opt_level}")

        # Test rollback with explicit backup check
        print("\n🔹 Testing rollback with explicit checks...")
        if backups:
            # Use the first backup (should be the initial one)
            first_backup_path = backups[0]["backup_path"]
            print(f"   Using backup: {first_backup_path}")

            # Check backup content before rollback
            with open(first_backup_path, 'r') as f:
                backup_before = yaml.safe_load(f)
            backup_opt_before = backup_before.get("hardware", {}).get("optimization_level")
            print(f"   Backup content before rollback: {backup_opt_before}")

            # Perform rollback
            success = config_manager.rollback_to_backup(first_backup_path)
            print(f"   Rollback success: {success}")

            # Check file content after rollback
            with open(config_file, 'r') as f:
                content_after = yaml.safe_load(f)
            opt_level_after = content_after.get("hardware", {}).get("optimization_level")
            print(f"   File content after rollback: {opt_level_after}")

            # Check backup content after rollback (should be unchanged)
            with open(first_backup_path, 'r') as f:
                backup_after = yaml.safe_load(f)
            backup_opt_after = backup_after.get("hardware", {}).get("optimization_level")
            print(f"   Backup content after rollback: {backup_opt_after}")

if __name__ == "__main__":
    inspect_backup_files()