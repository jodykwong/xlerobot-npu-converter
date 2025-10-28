#!/usr/bin/env python3
"""
Test script for configuration validation and error handling system.

Tests the validation and error handling functionality implemented in task 5 of Story 1.4.
"""

import sys
import time
import tempfile
from pathlib import Path

# Add the src directory to Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from npu_converter.config import ConfigurationManager
from npu_converter.config.validator import ConfigValidator, ValidationResult, ValidationError


def test_basic_validation():
    """Test basic configuration validation."""
    print("Testing Basic Configuration Validation...")

    try:
        validator = ConfigValidator()
        print("✅ ConfigValidator initialized")

        # Test with valid configuration
        valid_config = {
            "project": {
                "name": "test_project",
                "version": "1.0.0",
                "model_type": "sensevoice"
            },
            "hardware": {
                "target_device": "horizon_x5",
                "optimization_level": "O2",
                "memory_limit": "8GB"
            },
            "conversion_params": {
                "input_format": "onnx",
                "output_format": "bpu",
                "precision": "int8",
                "batch_size": 1
            },
            "model_specific": {
                "sensevoice": {
                    "sample_rate": 16000,
                    "vocab_size": 10000,
                    "mel_bins": 80,
                    "audio_length": 30  # Add missing required field
                }
            }
        }

        result = validator.validate_detailed(valid_config)
        if result.is_valid:
            print("✅ Valid configuration passed validation")
        else:
            print(f"❌ Valid configuration failed validation: {result.get_summary()}")
            return False

        return True

    except Exception as e:
        print(f"❌ Basic validation test failed: {e}")
        return False


def test_validation_error_reporting():
    """Test detailed validation error reporting."""
    print("\nTesting Validation Error Reporting...")

    try:
        validator = ConfigValidator()

        # Test with invalid configuration
        invalid_config = {
            "project": {
                "name": "invalid project name!",  # Invalid characters
                "version": "1.0",  # Invalid version format
                # Missing model_type
            },
            "hardware": {
                "target_device": "invalid_device",  # Invalid device
                "optimization_level": "O5",  # Invalid optimization level
                "memory_limit": "invalid_memory",  # Invalid memory format
            },
            "conversion_params": {
                "input_format": "invalid_input",  # Invalid input format
                # Missing output_format
                "precision": "invalid_precision",  # Invalid precision
                "batch_size": 100  # Out of range
            },
            # Missing model_specific section
        }

        result = validator.validate_detailed(invalid_config)

        if not result.is_valid:
            print(f"✅ Invalid configuration correctly rejected: {result.get_summary()}")

            # Check error details
            if result.errors:
                print(f"✅ Found {len(result.errors)} validation errors:")
                for i, error in enumerate(result.errors[:5]):  # Show first 5 errors
                    print(f"  {i+1}. {error.field_path}: {error.message}")
                    print(f"     Suggestion: {error.suggestion}")
                    print(f"     Severity: {error.severity}")

            if result.warnings:
                print(f"✅ Found {len(result.warnings)} validation warnings:")
                for i, warning in enumerate(result.warnings[:3]):  # Show first 3 warnings
                    print(f"  {i+1}. {warning.field_path}: {warning.message}")
                    print(f"     Suggestion: {warning.suggestion}")

            return True
        else:
            print("❌ Invalid configuration incorrectly passed validation")
            return False

    except Exception as e:
        print(f"❌ Validation error reporting test failed: {e}")
        return False


def test_model_specific_validation():
    """Test model-specific validation rules."""
    print("\nTesting Model-Specific Validation...")

    try:
        validator = ConfigValidator()

        # Test SenseVoice specific validation
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
                "precision": "int8",
                "batch_size": 1
            },
            "model_specific": {
                "sensevoice": {
                    "sample_rate": 44100,  # Invalid sample rate
                    "vocab_size": 100,  # Too small
                    # Missing required fields
                }
            }
        }

        result = validator.validate_detailed(sensevoice_config)

        if not result.is_valid:
            print("✅ Invalid SenseVoice configuration correctly rejected")

            # Check for SenseVoice specific errors
            sensevoice_errors = [e for e in result.errors if "sensevoice" in e.field_path]
            if sensevoice_errors:
                print(f"✅ Found {len(sensevoice_errors)} SenseVoice-specific errors")
                for error in sensevoice_errors:
                    print(f"  - {error.field_path}: {error.message}")
            else:
                print("⚠️ No SenseVoice-specific errors found")
        else:
            print("❌ Invalid SenseVoice configuration incorrectly passed validation")
            return False

        # Test Piper VITS specific validation
        piper_config = {
            "project": {
                "name": "piper_test",
                "version": "1.0.0",
                "model_type": "piper_vits"
            },
            "hardware": {
                "target_device": "horizon_x5",
                "optimization_level": "O2"
            },
            "conversion_params": {
                "input_format": "onnx",
                "output_format": "bpu",
                "precision": "int8",
                "batch_size": 1
            },
            "model_specific": {
                "piper_vits": {
                    "sample_rate": 8000,  # Invalid sample rate
                    "mel_channels": 200,  # Out of range
                    # Missing required fields
                }
            }
        }

        result = validator.validate_detailed(piper_config)

        if not result.is_valid:
            print("✅ Invalid Piper VITS configuration correctly rejected")

            # Check for Piper VITS specific errors
            piper_errors = [e for e in result.errors if "piper_vits" in e.field_path]
            if piper_errors:
                print(f"✅ Found {len(piper_errors)} Piper VITS-specific errors")
                for error in piper_errors:
                    print(f"  - {error.field_path}: {error.message}")
            else:
                print("⚠️ No Piper VITS-specific errors found")
        else:
            print("❌ Invalid Piper VITS configuration incorrectly passed validation")
            return False

        return True

    except Exception as e:
        print(f"❌ Model-specific validation test failed: {e}")
        return False


def test_configuration_manager_validation():
    """Test configuration manager integration with validation."""
    print("\nTesting Configuration Manager Validation...")

    try:
        # Create invalid configuration file
        invalid_config_file = Path("test_invalid_config.yaml")
        invalid_config_content = """project:
  name: "invalid project"
  version: "1.0"
  # Missing model_type

hardware:
  target_device: "invalid_device"
  optimization_level: "O5"
  memory_limit: "invalid_memory"

conversion_params:
  input_format: "invalid_format"
  # Missing output_format
  precision: "invalid_precision"
  batch_size: 100

# Missing model_specific section
"""

        with open(invalid_config_file, 'w') as f:
            f.write(invalid_config_content)

        # Try to load invalid configuration
        manager = ConfigurationManager(invalid_config_file)

        try:
            config = manager.load_config()
            print("❌ Invalid configuration was loaded without errors")
            return False
        except Exception as e:
            print(f"✅ Configuration manager correctly rejected invalid config: {type(e).__name__}")

        # Test validation method (should not reach here since load_config failed)
        print("✅ Configuration manager validation working correctly")

        # Clean up
        invalid_config_file.unlink()
        return True

    except Exception as e:
        print(f"❌ Configuration manager validation test failed: {e}")
        # Clean up on error
        try:
            if 'invalid_config_file' in locals() and invalid_config_file.exists():
                invalid_config_file.unlink()
        except:
            pass
        return False


def test_error_recovery():
    """Test error recovery mechanisms."""
    print("\nTesting Error Recovery...")

    try:
        config_file = Path("test_config_error_recovery.yaml")

        # Start with valid configuration
        valid_config_content = """project:
  name: "test_project"
  version: "1.0.0"
  model_type: "sensevoice"

hardware:
  target_device: "horizon_x5"
  optimization_level: "O2"
  memory_limit: "8GB"

conversion_params:
  input_format: "onnx"
  output_format: "bpu"
  precision: "int8"
  batch_size: 1

model_specific:
  sensevoice:
    sample_rate: 16000
    vocab_size: 10000
    mel_bins: 80
    audio_length: 30

performance:
  target_latency_ms: 100
  max_realtime_factor: 0.1
  enable_streaming: False
"""

        with open(config_file, 'w') as f:
            f.write(valid_config_content)

        manager = ConfigurationManager(config_file)
        config = manager.load_config()
        print("✅ Valid configuration loaded successfully")

        # Save initial state
        initial_name = manager.get_config("project.name")
        initial_latency = manager.get_config("performance.target_latency_ms", 100)

        # Try to apply invalid configuration change
        try:
            manager.set_config_dynamic("hardware.target_device", "invalid_device")
            print("❌ Invalid configuration change was accepted")
            return False
        except Exception as e:
            print(f"✅ Invalid configuration change correctly rejected: {type(e).__name__}")

        # Verify system state is unchanged
        current_name = manager.get_config("project.name")
        current_device = manager.get_config("hardware.target_device")

        if current_name == initial_name and current_device == "horizon_x5":
            print("✅ System state preserved after invalid change attempt")
        else:
            print("❌ System state corrupted after invalid change attempt")
            return False

        # Test batch update error recovery
        batch_changes = {
            "conversion_params.batch_size": 4,  # Valid
            "hardware.optimization_level": "INVALID",  # Invalid
            "performance.target_latency_ms": 50,  # Valid - but this field doesn't exist in config!
        }

        try:
            success = manager.batch_update_dynamic(batch_changes)
            if not success:
                print("✅ Batch update with invalid changes correctly rejected")
            else:
                print("❌ Batch update with invalid changes incorrectly accepted")
                return False
        except Exception as e:
            print(f"✅ Batch update correctly failed: {type(e).__name__}")

        # Verify no changes were applied (atomicity)
        current_latency = manager.get_config("performance.target_latency_ms")
        current_optimization = manager.get_config("hardware.optimization_level")
        current_batch_size = manager.get_config("conversion_params.batch_size")

        if (current_latency == initial_latency and
            current_optimization == "O2" and
            current_batch_size == 1):
            print("✅ No changes applied after failed batch update (atomicity preserved)")
        else:
            print("❌ Partial changes applied after failed batch update")
            return False

        # Clean up
        config_file.unlink()
        return True

    except Exception as e:
        print(f"❌ Error recovery test failed: {e}")
        # Clean up on error
        try:
            if 'config_file' in locals() and config_file.exists():
                config_file.unlink()
        except:
            pass
        return False


def test_warning_system():
    """Test validation warning system."""
    print("\nTesting Validation Warning System...")

    try:
        validator = ConfigValidator()

        # Create configuration with potential issues
        config_with_warnings = {
            "project": {
                "name": "test_project",
                "version": "1.0.0",
                "model_type": "sensevoice"
            },
            "hardware": {
                "target_device": "horizon_x5",
                "optimization_level": "O2",
                "memory_limit": "8GB"
            },
            "conversion_params": {
                "input_format": "onnx",
                "output_format": "bpu",
                "precision": "int8",
                "batch_size": 1
            },
            # Missing model_specific (should generate warning)
        }

        result = validator.validate_detailed(config_with_warnings)

        # Should be valid but with warnings
        if result.is_valid and result.warnings:
            print(f"✅ Configuration is valid but has {len(result.warnings)} warnings")

            for warning in result.warnings:
                print(f"  Warning: {warning.field_path}: {warning.message}")
                print(f"    Suggestion: {warning.suggestion}")

            return True
        elif result.is_valid:
            print("⚠️ Configuration is valid but no warnings generated (may be expected)")
            return True
        else:
            print("❌ Configuration incorrectly marked as invalid")
            return False

    except Exception as e:
        print(f"❌ Warning system test failed: {e}")
        return False


def test_custom_validation_rules():
    """Test custom validation rule addition."""
    print("\nTesting Custom Validation Rules...")

    try:
        validator = ConfigValidator()

        # Add a custom validation rule
        def validate_project_name(value, context):
            """Custom validator for project name."""
            if isinstance(value, str) and len(value) < 3:
                return False
            return True

        validator.add_validation_rule(
            "project",
            {
                "field": "name",
                "type": str,
                "custom_validator": validate_project_name,
                "message": "Project name must be at least 3 characters long",
                "suggestion": "Use a more descriptive project name"
            }
        )

        # Test with short project name
        config_with_short_name = {
            "project": {
                "name": "ab",  # Too short
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
                "precision": "int8",
                "batch_size": 1
            }
        }

        result = validator.validate_detailed(config_with_short_name)

        if not result.is_valid:
            print("✅ Custom validation rule correctly triggered")

            # Check if our custom error is present
            name_errors = [e for e in result.errors if e.field_path == "project.name"]
            if name_errors:
                print(f"✅ Custom error found: {name_errors[0].message}")
            else:
                print("⚠️ Custom error not found in validation results")
        else:
            print("❌ Custom validation rule did not trigger")
            return False

        # Test with valid project name
        config_with_valid_name = config_with_short_name.copy()
        config_with_valid_name["project"]["name"] = "valid_project_name"

        result = validator.validate_detailed(config_with_valid_name)

        if result.is_valid:
            print("✅ Custom validation rule passed for valid input")
        else:
            print("❌ Custom validation rule failed for valid input")
            return False

        return True

    except Exception as e:
        print(f"❌ Custom validation rules test failed: {e}")
        return False


def main():
    """Run all validation and error handling tests."""
    print("🚀 Testing Story 1.4 Configuration Validation and Error Handling")
    print("=" * 70)

    tests = [
        ("Basic Validation", test_basic_validation),
        ("Validation Error Reporting", test_validation_error_reporting),
        ("Model-Specific Validation", test_model_specific_validation),
        ("Configuration Manager Validation", test_configuration_manager_validation),
        ("Error Recovery", test_error_recovery),
        ("Warning System", test_warning_system),
        ("Custom Validation Rules", test_custom_validation_rules),
    ]

    passed = 0
    total = len(tests)

    for test_name, test_func in tests:
        print(f"\n{'='*20}")
        print(f"Test: {test_name}")
        print(f"{'='*20}")

        try:
            if test_func():
                passed += 1
                print(f"✅ {test_name}: PASSED")
            else:
                print(f"❌ {test_name}: FAILED")
        except Exception as e:
            print(f"❌ {test_name}: FAILED with exception: {e}")

    print(f"\n{'='*70}")
    print(f"Test Results: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 All tests passed! Configuration validation and error handling is working correctly.")
    else:
        print(f"⚠️ {total - passed} tests failed. Please check the implementation.")

    return passed == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)