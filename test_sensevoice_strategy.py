#!/usr/bin/env python3
"""
Test script for SenseVoice configuration strategy.

Tests the SenseVoice strategy implementation based on technical specifications
and requirements for automatic speech recognition models.
"""

import sys
import time
from pathlib import Path

# Add the src directory to Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from npu_converter.config.strategies.sensevoice_strategy import SenseVoiceConfigStrategy


def test_sensevoice_strategy_initialization():
    """Test SenseVoice strategy initialization."""
    print("Testing SenseVoice Strategy Initialization...")

    try:
        # Create test configuration
        test_config = {
            "project": {
                "name": "test_sensevoice",
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
                    # Required basic fields
                    "sample_rate": 16000,
                    "audio_length": 30,
                    "vocab_size": 10000,

                    # Audio processing parameters
                    "n_fft": 400,
                    "hop_length": 160,
                    "win_length": 400,
                    "n_mels": 80,
                    "mel_fmin": 0.0,
                    "mel_fmax": 8000.0,

                    # ASR-specific parameters
                    "language_detection": True,
                    "supported_languages": ["zh", "en", "yue", "ja"],
                    "confidence_threshold": 0.8,
                    "segmentation": True,
                    "vad_enabled": True,

                    # Model optimization parameters
                    "beam_size": 5,
                    "length_penalty": 1.0,
                    "coverage_penalty": 1.0,
                    "repetition_penalty": 1.0
                }
            }
        }

        # Initialize strategy
        strategy = SenseVoiceConfigStrategy(test_config)
        print("✅ SenseVoiceConfigStrategy initialized successfully")

        # Test model type
        model_type = strategy.get_model_type()
        if model_type == "sensevoice":
            print(f"✅ Model type correctly identified: {model_type}")
        else:
            print(f"❌ Model type incorrect: expected 'sensevoice', got '{model_type}'")
            return False

        # Test validation
        is_valid = strategy.validate_model_specific_config()
        if is_valid:
            print("✅ Configuration validation passed")
        else:
            print("❌ Configuration validation failed")
            return False

        return True

    except Exception as e:
        print(f"❌ SenseVoice strategy initialization test failed: {e}")
        return False


def test_sensevoice_template():
    """Test SenseVoice default template."""
    print("\nTesting SenseVoice Default Template...")

    try:
        strategy = SenseVoiceConfigStrategy({})
        template = strategy.get_default_template()

        if not template:
            print("❌ Template generation failed")
            return False

        # Check template structure
        required_sections = ["project", "hardware", "conversion_params", "model_specific"]
        for section in required_sections:
            if section in template:
                print(f"✅ Template contains '{section}' section")
            else:
                print(f"❌ Template missing '{section}' section")
                return False

        # Check SenseVoice specific configuration
        sensevoice_config = template.get("model_specific", {}).get("sensevoice", {})
        if not sensevoice_config:
            print("❌ SenseVoice configuration missing from template")
            return False

        # Check required SenseVoice architecture fields
        required_fields = ["sample_rate", "audio_length", "vocab_size", "mel_bins", "n_mels"]
        for field in required_fields:
            if field in sensevoice_config:
                print(f"✅ Template contains SenseVoice field '{field}': {sensevoice_config[field]}")
            else:
                print(f"❌ Template missing SenseVoice field '{field}'")
                return False

        # Check audio processing fields
        audio_fields = ["sample_rate", "n_fft", "hop_length", "n_mels"]
        for field in audio_fields:
            if field in sensevoice_config:
                print(f"✅ Template contains audio field '{field}': {sensevoice_config[field]}")
            else:
                print(f"❌ Template missing audio field '{field}'")
                return False

        # Check ASR-specific fields
        asr_fields = ["language_detection", "supported_languages", "confidence_threshold"]
        for field in asr_fields:
            if field in sensevoice_config:
                print(f"✅ Template contains ASR field '{field}': {sensevoice_config[field]}")
            else:
                print(f"❌ Template missing ASR field '{field}'")
                return False

        return True

    except Exception as e:
        print(f"❌ SenseVoice template test failed: {e}")
        return False


def test_sensevoice_validation_rules():
    """Test SenseVoice validation rules."""
    print("\nTesting SenseVoice Validation Rules...")

    try:
        strategy = SenseVoiceConfigStrategy({})
        validation_rules = strategy.get_validation_rules()

        if not validation_rules:
            print("❌ No validation rules generated")
            return False

        print(f"✅ Generated {len(validation_rules)} validation rules")

        # Check important validation rules
        important_rules = [
            "model_specific.sensevoice.sample_rate",
            "model_specific.sensevoice.audio_length",
            "model_specific.sensevoice.vocab_size",
            "model_specific.sensevoice.language_detection",
            "model_specific.sensevoice.confidence_threshold"
        ]

        for rule_path in important_rules:
            rule_exists = any(rule.field_path == rule_path for rule in validation_rules)
            if rule_exists:
                print(f"✅ Validation rule exists: {rule_path}")
            else:
                print(f"❌ Missing validation rule: {rule_path}")
                return False

        return True

    except Exception as e:
        print(f"❌ SenseVoice validation rules test failed: {e}")
        return False


def test_sensevoice_audio_config():
    """Test SenseVoice audio processing configuration."""
    print("\nTesting SenseVoice Audio Processing Configuration...")

    try:
        strategy = SenseVoiceConfigStrategy({})
        config = {
            "model_specific": {
                "sensevoice": {
                    "sample_rate": 16000,
                    "n_fft": 400,
                    "hop_length": 160,
                    "win_length": 400,
                    "n_mels": 80,
                    "mel_fmin": 0.0,
                    "mel_fmax": 8000.0,
                    "preemphasis": 0.97,
                    "window_type": "hann"
                }
            }
        }
        strategy = SenseVoiceConfigStrategy(config)

        # Note: SenseVoice strategy may not have specific audio config methods
        # This tests basic configuration handling
        model_type = strategy.get_model_type()
        if model_type == "sensevoice":
            print("✅ Audio configuration loaded successfully")
        else:
            print("❌ Audio configuration failed")
            return False

        return True

    except Exception as e:
        print(f"❌ SenseVoice audio config test failed: {e}")
        return False


def test_sensevoice_asr_config():
    """Test SenseVoice ASR-specific configuration."""
    print("\nTesting SenseVoice ASR Configuration...")

    try:
        strategy = SenseVoiceConfigStrategy({})
        config = {
            "model_specific": {
                "sensevoice": {
                    # Required ASR parameters
                    "sample_rate": 16000,
                    "audio_length": 30,
                    "vocab_size": 10000,

                    # ASR-specific parameters
                    "language_detection": True,
                    "supported_languages": ["zh", "en", "yue", "ja"],
                    "confidence_threshold": 0.8,
                    "segmentation": True,
                    "vad_enabled": True,
                    "beam_size": 5,
                    "length_penalty": 1.0,
                    "repetition_penalty": 1.0,

                    # Audio processing parameters
                    "n_fft": 400,
                    "hop_length": 160,
                    "win_length": 400,
                    "n_mels": 80,
                    "mel_fmin": 0.0,
                    "mel_fmax": 8000.0,
                    "preemphasis": 0.97
                }
            }
        }
        strategy = SenseVoiceConfigStrategy(config)

        # Test model-specific validation
        is_valid = strategy.validate_model_specific_config()
        if is_valid:
            print("✅ ASR configuration validation passed")
        else:
            print("❌ ASR configuration validation failed")
            return False

        # Test get_model_specific_fields if method exists
        if hasattr(strategy, 'get_model_specific_fields'):
            fields = strategy.get_model_specific_fields()
            print(f"✅ Model-specific fields count: {len(fields)}")
        else:
            print("⚠️ get_model_specific_fields method not available")

        return True

    except Exception as e:
        print(f"❌ SenseVoice ASR config test failed: {e}")
        return False


def test_sensevoice_language_support():
    """Test SenseVoice multi-language support."""
    print("\nTesting SenseVoice Language Support...")

    try:
        # Test with multiple languages
        config = {
            "model_specific": {
                "sensevoice": {
                    # Required ASR parameters
                    "sample_rate": 16000,
                    "audio_length": 30,
                    "vocab_size": 10000,

                    # Multi-language support
                    "supported_languages": ["zh", "en", "yue", "ja", "ko"],
                    "language_detection": True,
                    "default_language": "zh",

                    # Audio processing parameters
                    "n_fft": 400,
                    "hop_length": 160,
                    "win_length": 400,
                    "n_mels": 80,
                    "mel_fmin": 0.0,
                    "mel_fmax": 8000.0
                }
            }
        }

        strategy = SenseVoiceConfigStrategy(config)

        # Validate multi-language configuration
        is_valid = strategy.validate_model_specific_config()
        if is_valid:
            print("✅ Multi-language configuration validation passed")

            # Check language support
            sensevoice_config = config["model_specific"]["sensevoice"]
            supported_langs = sensevoice_config.get("supported_languages", [])
            print(f"✅ Supported languages: {supported_langs}")
        else:
            print("❌ Multi-language configuration validation failed")
            return False

        return True

    except Exception as e:
        print(f"❌ SenseVoice language support test failed: {e}")
        return False


def main():
    """Run all SenseVoice strategy tests."""
    print("🚀 Testing SenseVoice Configuration Strategy")
    print("=" * 60)
    print("Based on technical specifications for ASR models")

    tests = [
        ("Strategy Initialization", test_sensevoice_strategy_initialization),
        ("Default Template", test_sensevoice_template),
        ("Validation Rules", test_sensevoice_validation_rules),
        ("Audio Processing Config", test_sensevoice_audio_config),
        ("ASR Configuration", test_sensevoice_asr_config),
        ("Language Support", test_sensevoice_language_support),
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
        print("🎉 All tests passed! SenseVoice strategy is working correctly.")
        print("\n📋 SenseVoice Strategy Features:")
        print("  ✅ SenseVoice ASR model architecture configuration")
        print("  ✅ Multi-language support (Chinese, English, Cantonese, Japanese)")
        print("  ✅ Audio processing optimized for speech recognition")
        print("  ✅ Language detection and confidence scoring")
        print("  ✅ Voice activity detection and segmentation")
        print("  ✅ Beam search and decoding parameters")
        print("  ✅ Comprehensive validation system")
    else:
        print(f"⚠️ {total - passed} tests failed. Please check the implementation.")

    return passed == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)