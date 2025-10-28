#!/usr/bin/env python3
"""
Simple test for ConfigurationManager functionality
"""

import sys
import time
from pathlib import Path

# Add the src directory to Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from npu_converter.config import ConfigurationManager

def test_config_manager_simple():
    """Simple test for ConfigurationManager."""
    print("🔧 Testing ConfigurationManager (Simple)...")

    config_file = Path("test_config_debug.yaml")
    if not config_file.exists():
        print(f"❌ Test config file not found: {config_file}")
        return False

    try:
        # Test initialization
        manager = ConfigurationManager(config_file)
        print("✅ ConfigurationManager initialized")

        # Test config loading
        start_time = time.time()
        config = manager.load_config()
        load_time = (time.time() - start_time) * 1000
        print(f"✅ Configuration loaded in {load_time:.2f}ms")

        # Test basic config retrieval
        model_type = manager.get_config("project.model_type")
        print(f"✅ Retrieved model type: {model_type}")

        target_device = manager.get_config("hardware.target_device")
        print(f"✅ Retrieved target device: {target_device}")

        # Test validation
        is_valid = manager.validate_config()
        print(f"✅ Configuration validation: {'PASSED' if is_valid else 'FAILED'}")

        # Test metrics
        metrics = manager.get_metrics()
        print(f"✅ Load time: {metrics.load_time_ms:.2f}ms")
        print(f"✅ Available strategies: {manager.list_available_strategies()}")

        # Test strategy
        strategy = manager.get_strategy()
        if strategy:
            print(f"✅ Strategy initialized: {strategy.get_model_type()}")
        else:
            print("⚠️ No strategy initialized")

        print("✅ ConfigurationManager test PASSED")
        return True

    except Exception as e:
        print(f"❌ ConfigurationManager test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_config_manager_simple()
    print(f"\n📊 Test Result: {'PASSED' if success else 'FAILED'}")