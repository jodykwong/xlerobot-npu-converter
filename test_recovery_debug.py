#!/usr/bin/env python3
"""
Debug configuration recovery issues.
"""

import sys
import tempfile
import yaml
from pathlib import Path

# Add the src directory to Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from npu_converter.config import ConfigurationManager

def debug_recovery_issue():
    """Debug the recovery issue step by step."""
    print("🔍 Debugging Configuration Recovery Issue")
    print("=" * 50)

    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        config_file = temp_path / "debug_config.yaml"

        # Create initial config
        initial_config = {
            "project": {
                "name": "test_recovery_debug",
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
            }
        }

        with open(config_file, 'w') as f:
            yaml.dump(initial_config, f, default_flow_style=False, indent=2)

        print(f"📁 Created config file: {config_file}")
        print(f"   Initial optimization level: {initial_config['hardware']['optimization_level']}")

        # Step 1: Load configuration
        print("\n🔹 Step 1: Loading configuration...")
        config_manager = ConfigurationManager(config_file)
        loaded_config = config_manager.load_config()
        current_opt_level = config_manager.get_config("hardware.optimization_level")
        print(f"   Loaded optimization level: {current_opt_level}")

        # Step 2: Create initial backup
        print("\n🔹 Step 2: Creating initial backup...")
        initial_backup = config_manager.create_backup("debug_initial")
        print(f"   Initial backup: {initial_backup}")

        # Step 3: Modify configuration
        print("\n🔹 Step 3: Modifying configuration...")
        config_manager.set_config("hardware.optimization_level", "O3")
        config_manager.set_config("debug_field", "debug_value")

        # Check in-memory config
        modified_opt_level = config_manager.get_config("hardware.optimization_level")
        debug_field = config_manager.get_config("debug_field")
        print(f"   Modified optimization level: {modified_opt_level}")
        print(f"   Debug field: {debug_field}")

        # Step 4: Save to file
        print("\n🔹 Step 4: Saving to file...")
        config_manager.save_config()

        # Read file directly to verify
        with open(config_file, 'r') as f:
            file_config = yaml.safe_load(f)
        file_opt_level = file_config.get("hardware", {}).get("optimization_level")
        file_debug_field = file_config.get("debug_field")
        print(f"   File optimization level: {file_opt_level}")
        print(f"   File debug field: {file_debug_field}")

        # Step 5: Rollback
        print("\n🔹 Step 5: Rolling back to initial backup...")
        rollback_success = config_manager.rollback_to_backup(initial_backup)
        print(f"   Rollback success: {rollback_success}")

        # Step 6: Verify rollback
        print("\n🔹 Step 6: Verifying rollback...")

        # Check in-memory config
        rollback_opt_level = config_manager.get_config("hardware.optimization_level")
        rollback_debug_field = config_manager.get_config("debug_field")
        print(f"   Rollback optimization level: {rollback_opt_level}")
        print(f"   Rollback debug field: {rollback_debug_field}")

        # Check file directly
        with open(config_file, 'r') as f:
            file_config_after = yaml.safe_load(f)
        file_opt_level_after = file_config_after.get("hardware", {}).get("optimization_level")
        file_debug_field_after = file_config_after.get("debug_field")
        print(f"   File optimization level after rollback: {file_opt_level_after}")
        print(f"   File debug field after rollback: {file_debug_field_after}")

        # Analysis
        print("\n" + "=" * 50)
        print("🔍 Analysis:")
        print(f"   Expected optimization level: O2")
        print(f"   Actual optimization level: {rollback_opt_level}")
        print(f"   File optimization level: {file_opt_level_after}")

        if rollback_opt_level == "O2" and file_opt_level_after == "O2":
            print("   ✅ Rollback worked correctly!")
        else:
            print("   ❌ Rollback failed!")
            print(f"   In-memory vs File mismatch: {rollback_opt_level} vs {file_opt_level_after}")

if __name__ == "__main__":
    debug_recovery_issue()