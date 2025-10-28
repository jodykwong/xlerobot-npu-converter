#!/usr/bin/env python3
"""
Test script for the configuration template system.

Tests the template management functionality implemented in task 2 of Story 1.4.
"""

import sys
import time
import tempfile
from pathlib import Path

# Add the src directory to Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from npu_converter.config.templates.manager import ConfigTemplateManager


def test_template_discovery():
    """Test automatic template discovery."""
    print("Testing Template Discovery...")

    try:
        # Initialize template manager
        template_manager = ConfigTemplateManager()
        print("✅ ConfigTemplateManager initialized")

        # List all available templates
        templates = template_manager.list_templates()
        print(f"✅ Found {len(templates)} templates")

        for template in templates:
            print(f"  - {template.name} ({template.model_type}): {template.description}")

        # Test filtering by model type
        sensevoice_templates = template_manager.get_templates_by_model_type("sensevoice")
        print(f"✅ Found {len(sensevoice_templates)} SenseVoice templates")

        piper_templates = template_manager.get_templates_by_model_type("piper_vits")
        print(f"✅ Found {len(piper_templates)} Piper VITS templates")

        return True

    except Exception as e:
        print(f"❌ Template discovery test failed: {e}")
        return False


def test_template_retrieval():
    """Test template retrieval functionality."""
    print("\nTesting Template Retrieval...")

    try:
        template_manager = ConfigTemplateManager()

        # Test retrieving SenseVoice default template
        sensevoice_template = template_manager.get_template("sensevoice_default")
        if sensevoice_template:
            print("✅ Retrieved sensevoice_default template")

            # Verify template structure
            required_sections = ["project", "hardware", "conversion_params", "model_specific"]
            for section in required_sections:
                if section in sensevoice_template:
                    print(f"✅ Template contains '{section}' section")
                else:
                    print(f"❌ Template missing '{section}' section")
                    return False

            # Verify SenseVoice specific configuration
            sensevoice_config = sensevoice_template.get("model_specific", {}).get("sensevoice", {})
            if sensevoice_config:
                print(f"✅ SenseVoice config found with sample_rate: {sensevoice_config.get('sample_rate')}")
            else:
                print("❌ SenseVoice specific configuration not found")
                return False

        else:
            print("❌ Failed to retrieve sensevoice_default template")
            return False

        # Test retrieving Piper VITS default template
        piper_template = template_manager.get_template("piper_vits_default")
        if piper_template:
            print("✅ Retrieved piper_vits_default template")

            # Verify Piper VITS specific configuration
            piper_config = piper_template.get("model_specific", {}).get("piper_vits", {})
            if piper_config:
                print(f"✅ Piper VITS config found with sample_rate: {piper_config.get('sample_rate')}")
            else:
                print("❌ Piper VITS specific configuration not found")
                return False

        else:
            print("❌ Failed to retrieve piper_vits_default template")
            return False

        return True

    except Exception as e:
        print(f"❌ Template retrieval test failed: {e}")
        return False


def test_template_application():
    """Test template application with overrides."""
    print("\nTesting Template Application...")

    try:
        template_manager = ConfigTemplateManager()

        # Test applying template without overrides
        base_config = template_manager.apply_template("sensevoice_default")
        if base_config:
            print("✅ Applied sensevoice_default template without overrides")
            print(f"✅ Model type: {base_config.get('project', {}).get('model_type')}")
            print(f"✅ Target device: {base_config.get('hardware', {}).get('target_device')}")
        else:
            print("❌ Failed to apply sensevoice_default template")
            return False

        # Test applying template with overrides
        overrides = {
            "hardware": {
                "optimization_level": "O3",
                "cache_size": "512MB"
            },
            "performance": {
                "target_latency_ms": 50
            }
        }

        overridden_config = template_manager.apply_template("sensevoice_default", overrides)
        if overridden_config:
            print("✅ Applied sensevoice_default template with overrides")
            print(f"✅ Override optimization level: {overridden_config.get('hardware', {}).get('optimization_level')}")
            print(f"✅ Override cache size: {overridden_config.get('hardware', {}).get('cache_size')}")
            print(f"✅ Override target latency: {overridden_config.get('performance', {}).get('target_latency_ms')}")
        else:
            print("❌ Failed to apply sensevoice_default template with overrides")
            return False

        # Test applying performance template
        perf_config = template_manager.apply_template("sensevoice_performance")
        if perf_config:
            print("✅ Applied sensevoice_performance template")
            print(f"✅ Performance optimization level: {perf_config.get('hardware', {}).get('optimization_level')}")
            print(f"✅ Performance batch size: {perf_config.get('conversion_params', {}).get('batch_size')}")
        else:
            print("❌ Failed to apply sensevoice_performance template")
            return False

        return True

    except Exception as e:
        print(f"❌ Template application test failed: {e}")
        return False


def test_template_creation():
    """Test dynamic template creation."""
    print("\nTesting Template Creation...")

    try:
        template_manager = ConfigTemplateManager()

        # Create a custom template
        custom_template = {
            "_metadata": {
                "name": "custom_test",
                "description": "Custom test template",
                "model_type": "sensevoice",
                "version": "1.0.0",
                "author": "Test Suite",
                "created_at": "2024-01-01",
                "tags": ["test", "custom"]
            },
            "project": {
                "name": "custom_sensevoice",
                "version": "1.0.0",
                "model_type": "sensevoice"
            },
            "hardware": {
                "target_device": "horizon_x5",
                "optimization_level": "O1"
            },
            "conversion_params": {
                "input_format": "onnx",
                "output_format": "bpu",
                "precision": "int8"
            },
            "model_specific": {
                "sensevoice": {
                    "sample_rate": 16000,
                    "vocab_size": 5000
                }
            }
        }

        # Create template
        success = template_manager.create_template("custom_test", custom_template)
        if success:
            print("✅ Successfully created custom_test template")
        else:
            print("❌ Failed to create custom_test template")
            return False

        # Verify template can be retrieved
        retrieved_template = template_manager.get_template("custom_test")
        if retrieved_template:
            print("✅ Successfully retrieved custom_test template")
            print(f"✅ Custom template name: {retrieved_template.get('project', {}).get('name')}")
        else:
            print("❌ Failed to retrieve custom_test template")
            return False

        # Clean up - delete the custom template
        delete_success = template_manager.delete_template("custom_test")
        if delete_success:
            print("✅ Successfully deleted custom_test template")
        else:
            print("⚠️ Failed to delete custom_test template (may need manual cleanup)")

        return True

    except Exception as e:
        print(f"❌ Template creation test failed: {e}")
        return False


def test_template_validation():
    """Test template validation."""
    print("\nTesting Template Validation...")

    try:
        template_manager = ConfigTemplateManager()

        # Get a valid template
        valid_template = template_manager.get_template("sensevoice_default")
        if valid_template:
            # Validate the template
            errors = template_manager.validate_template(valid_template)
            if not errors:
                print("✅ Valid template passed validation")
            else:
                print(f"❌ Valid template failed validation: {errors}")
                return False
        else:
            print("❌ Could not retrieve valid template for testing")
            return False

        # Test invalid template
        invalid_template = {
            "project": {
                # Missing required fields
                "name": "invalid_test"
                # Missing version and model_type
            },
            # Missing required sections: hardware, conversion_params
        }

        errors = template_manager.validate_template(invalid_template)
        if errors:
            print(f"✅ Invalid template correctly failed validation with {len(errors)} errors")
            for error in errors[:3]:  # Show first 3 errors
                print(f"  - {error}")
        else:
            print("❌ Invalid template incorrectly passed validation")
            return False

        return True

    except Exception as e:
        print(f"❌ Template validation test failed: {e}")
        return False


def test_default_template_selection():
    """Test default template selection for model types."""
    print("\nTesting Default Template Selection...")

    try:
        template_manager = ConfigTemplateManager()

        # Test getting default template for SenseVoice
        sensevoice_default = template_manager.get_default_template_for_model("sensevoice")
        if sensevoice_default:
            print("✅ Found default template for SenseVoice")
            print(f"✅ Default template model type: {sensevoice_default.get('project', {}).get('model_type')}")
        else:
            print("❌ No default template found for SenseVoice")
            return False

        # Test getting default template for Piper VITS
        piper_default = template_manager.get_default_template_for_model("piper_vits")
        if piper_default:
            print("✅ Found default template for Piper VITS")
            print(f"✅ Default template model type: {piper_default.get('project', {}).get('model_type')}")
        else:
            print("❌ No default template found for Piper VITS")
            return False

        # Test with unsupported model type
        unsupported_default = template_manager.get_default_template_for_model("unsupported_model")
        if unsupported_default is None:
            print("✅ Correctly returned None for unsupported model type")
        else:
            print("❌ Should have returned None for unsupported model type")
            return False

        return True

    except Exception as e:
        print(f"❌ Default template selection test failed: {e}")
        return False


def main():
    """Run all template system tests."""
    print("🚀 Testing Story 1.4 Configuration Template System")
    print("=" * 60)

    tests = [
        ("Template Discovery", test_template_discovery),
        ("Template Retrieval", test_template_retrieval),
        ("Template Application", test_template_application),
        ("Template Creation", test_template_creation),
        ("Template Validation", test_template_validation),
        ("Default Template Selection", test_default_template_selection),
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
        print("🎉 All tests passed! Configuration template system is working correctly.")
    else:
        print(f"⚠️ {total - passed} tests failed. Please check the implementation.")

    return passed == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)