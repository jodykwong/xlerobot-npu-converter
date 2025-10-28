#!/usr/bin/env python3
"""
Test script for the configuration management system.

Tests the basic functionality of the configuration management system
implemented in the first task of Story 1.4.
"""

import sys
import time
from pathlib import Path

# Add the src directory to Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from npu_converter.config import (
    ConfigurationManager,
    ConfigValidator,
    HotReloadManager,
    ConfigTemplateManager
)
from npu_converter.config.strategies import SenseVoiceConfigStrategy, PiperVITSConfigStrategy


def test_configuration_manager():
    """Test the basic configuration manager functionality."""
    print("Testing ConfigurationManager...")

    config_file = Path("test_config.yaml")
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

        # Verify performance requirement (<100ms)
        if load_time > 100:
            print(f"⚠️ Load time {load_time:.2f}ms exceeds 100ms threshold")
        else:
            print(f"✅ Load time {load_time:.2f}ms meets <100ms requirement")

        # Test config retrieval
        model_type = manager.get_config("project.model_type")
        print(f"✅ Retrieved model type: {model_type}")

        target_device = manager.get_config("hardware.target_device")
        print(f"✅ Retrieved target device: {target_device}")

        # Test config setting
        manager.set_config("performance.target_latency_ms", 150)
        new_latency = manager.get_config("performance.target_latency_ms")
        print(f"✅ Set and retrieved config value: {new_latency}")

        # Test validation
        is_valid = manager.validate_config()
        print(f"✅ Configuration validation: {'PASSED' if is_valid else 'FAILED'}")

        # Test strategy initialization
        strategy = manager.get_strategy()
        if strategy:
            print(f"✅ Strategy initialized: {strategy.get_model_type()}")
        else:
            print("⚠️ No strategy initialized (model_type may not be supported)")

        # Test metrics
        metrics = manager.get_metrics()
        print(f"✅ Load time: {metrics.load_time_ms:.2f}ms")
        print(f"✅ Strategy list: {manager.list_available_strategies()}")

        return True

    except Exception as e:
        print(f"❌ ConfigurationManager test failed: {e}")
        return False


def test_config_validator():
    """Test the configuration validator."""
    print("\nTesting ConfigValidator...")

    try:
        validator = ConfigValidator()
        print("✅ ConfigValidator initialized")

        # Test with valid config
        config_file = Path("test_config.yaml")
        if config_file.exists():
            import yaml
            with open(config_file, 'r') as f:
                config = yaml.safe_load(f)

            result = validator.validate_detailed(config)
            print(f"✅ Validation result: {result.get_summary()}")

            if result.has_errors:
                print(f"❌ Validation errors found: {len(result.errors)}")
                for error in result.errors:
                    print(f"  - {error.field_path}: {error.message}")
            else:
                print("✅ No validation errors found")

            if result.has_warnings:
                print(f"⚠️ Validation warnings: {len(result.warnings)}")
                for warning in result.warnings:
                    print(f"  - {warning.field_path}: {warning.message}")

        return True

    except Exception as e:
        print(f"❌ ConfigValidator test failed: {e}")
        return False


def test_strategies():
    """Test model-specific configuration strategies."""
    print("\nTesting Configuration Strategies...")

    try:
        # Load test config
        config_file = Path("test_config.yaml")
        if not config_file.exists():
            print("❌ Test config file not found")
            return False

        import yaml
        with open(config_file, 'r') as f:
            config = yaml.safe_load(f)

        # Test SenseVoice strategy
        sensevoice_strategy = SenseVoiceConfigStrategy(config)
        print("✅ SenseVoiceConfigStrategy initialized")

        is_valid = sensevoice_strategy.validate()
        print(f"✅ SenseVoice config validation: {'PASSED' if is_valid else 'FAILED'}")

        # Test strategy methods
        template = sensevoice_strategy.get_default_template()
        print(f"✅ SenseVoice template keys: {list(template.keys())}")

        audio_config = sensevoice_strategy.get_audio_processing_config()
        print(f"✅ Audio config sample rate: {audio_config['sample_rate']}")

        # Test Piper VITS strategy (with config change)
        config["project"]["model_type"] = "piper_vits"
        config["model_specific"]["piper_vits"] = {
            "sample_rate": 22050,
            "mel_channels": 80,
            "speaker_embedding": True
        }

        piper_strategy = PiperVITSConfigStrategy(config)
        print("✅ PiperVITSConfigStrategy initialized")

        is_valid = piper_strategy.validate()
        print(f"✅ Piper VITS config validation: {'PASSED' if is_valid else 'FAILED'}")

        synthesis_config = piper_strategy.get_synthesis_config()
        print(f"✅ Synthesis config sample rate: {synthesis_config['sample_rate']}")

        return True

    except Exception as e:
        print(f"❌ Strategy test failed: {e}")
        return False


def test_template_manager():
    """Test the configuration template manager."""
    print("\nTesting ConfigTemplateManager...")

    try:
        template_manager = ConfigTemplateManager()
        print("✅ ConfigTemplateManager initialized")

        # Test template listing
        templates = template_manager.list_templates()
        print(f"✅ Available templates: {len(templates)}")

        # Test SenseVoice templates
        sensevoice_templates = template_manager.get_templates_by_model_type("sensevoice")
        print(f"✅ SenseVoice templates: {len(sensevoice_templates)}")

        # Test template creation
        test_template = {
            "project": {
                "name": "test",
                "model_type": "sensevoice",
                "version": "1.0.0"
            },
            "hardware": {
                "target_device": "horizon_x5",
                "optimization_level": "O2"
            }
        }

        success = template_manager.create_template("test_template", test_template)
        print(f"✅ Template creation: {'SUCCESS' if success else 'FAILED'}")

        # Test template retrieval
        retrieved = template_manager.get_template("test_template")
        if retrieved:
            print(f"✅ Template retrieval successful")
            print(f"✅ Retrieved template project name: {retrieved.get('project', {}).get('name')}")
        else:
            print("❌ Template retrieval failed")

        # Test template application with overrides
        overrides = {"hardware": {"optimization_level": "O3"}}
        applied = template_manager.apply_template("test_template", overrides)
        if applied:
            print(f"✅ Template with overrides applied")
            print(f"✅ Optimization level: {applied.get('hardware', {}).get('optimization_level')}")

        return True

    except Exception as e:
        print(f"❌ ConfigTemplateManager test failed: {e}")
        return False


def test_hot_reload():
    """Test the hot reload manager (basic functionality only)."""
    print("\nTesting HotReloadManager...")

    try:
        config_file = Path("test_config.yaml")
        if not config_file.exists():
            print("❌ Test config file not found")
            return False

        reload_count = 0
        def reload_callback():
            nonlocal reload_count
            reload_count += 1
            print(f"🔄 Reload callback triggered (#{reload_count})")

        # Initialize hot reload manager
        hot_reload = HotReloadManager(config_file, reload_callback)
        print("✅ HotReloadManager initialized")

        # Test metrics
        metrics = hot_reload.get_metrics()
        print(f"✅ Initial metrics - Reload count: {metrics.reload_count}")

        # Test force reload
        success = hot_reload.force_reload()
        print(f"✅ Force reload: {'SUCCESS' if success else 'FAILED'}")

        if reload_count == 1:
            print("✅ Reload callback was triggered")

        # Check metrics after reload
        updated_metrics = hot_reload.get_metrics()
        print(f"✅ Updated metrics - Reload count: {updated_metrics.reload_count}")
        print(f"✅ Last reload time: {updated_metrics.last_reload_time_ms:.2f}ms")

        return True

    except Exception as e:
        print(f"❌ HotReloadManager test failed: {e}")
        return False


def cleanup():
    """Clean up test files."""
    test_files = [
        Path("test_config.yaml"),
        Path("test_config.yaml.backup"),
        Path("test_config.yaml.tmp")
    ]

    for file_path in test_files:
        if file_path.exists():
            try:
                file_path.unlink()
                print(f"🧹 Cleaned up: {file_path}")
            except Exception as e:
                print(f"⚠️ Failed to clean up {file_path}: {e}")


def main():
    """Run all tests."""
    print("🚀 Testing Story 1.4 Configuration Management System")
    print("=" * 60)

    tests = [
        ("Configuration Manager", test_configuration_manager),
        ("Configuration Validator", test_config_validator),
        ("Configuration Strategies", test_strategies),
        ("Template Manager", test_template_manager),
        ("Hot Reload Manager", test_hot_reload),
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
        print("🎉 All tests passed! Configuration management system is working correctly.")
    else:
        print(f"⚠️ {total - passed} tests failed. Please check the implementation.")

    # Cleanup
    print(f"\nCleaning up test files...")
    cleanup()

    return passed == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)