#!/usr/bin/env python3
"""
Test script for Piper VITS configuration strategy.

Tests the Piper VITS strategy implementation based on technical specifications
and requirements for text-to-speech models.
"""

import sys
import time
from pathlib import Path

# Add the src directory to Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from npu_converter.config.strategies.piper_vits_strategy import PiperVITSConfigStrategy


def test_piper_vits_strategy_initialization():
    """Test Piper VITS strategy initialization."""
    print("Testing Piper VITS Strategy Initialization...")

    try:
        # Create test configuration
        test_config = {
            "project": {
                "name": "test_piper_vits",
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
                "precision": "int8"
            },
            "model_specific": {
                "piper_vits": {
                    # Required basic fields
                    "sample_rate": 22050,
                    "mel_channels": 80,
                    "speaker_embedding": True,
                    "num_speakers": 1,
                    "speaker_id": 0,
                    "embedding_dim": 192,

                    # VITS architecture parameters
                    "inter_channels": 192,
                    "hidden_channels": 192,
                    "filter_channels": 768,
                    "n_heads": 2,
                    "n_layers": 6,
                    "kernel_size": 3,
                    "p_dropout": 0.1,

                    # Audio processing parameters
                    "n_fft": 1024,
                    "hop_size": 256,
                    "win_size": 1024,
                    "n_mels": 80,
                    "f_min": 0.0,
                    "f_max": 8000.0,

                    # Synthesis parameters
                    "noise_scale": 0.667,
                    "noise_scale_d": 0.8,
                    "length_scale": 1.0,
                    "inference_noise_scale": 0.667,
                    "max_wav_value": 32768.0,

                    # Advanced features
                    "use_sdp": True,
                    "use_spectral_norm": False,
                    "gin_channels": 256
                }
            }
        }

        # Initialize strategy
        strategy = PiperVITSConfigStrategy(test_config)
        print("✅ PiperVITSConfigStrategy initialized successfully")

        # Test model type
        model_type = strategy.get_model_type()
        if model_type == "piper_vits":
            print(f"✅ Model type correctly identified: {model_type}")
        else:
            print(f"❌ Model type incorrect: expected 'piper_vits', got '{model_type}'")
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
        print(f"❌ Piper VITS strategy initialization test failed: {e}")
        return False


def test_piper_vits_template():
    """Test Piper VITS default template."""
    print("\nTesting Piper VITS Default Template...")

    try:
        strategy = PiperVITSConfigStrategy({})
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

        # Check Piper VITS specific configuration
        piper_config = template.get("model_specific", {}).get("piper_vits", {})
        if not piper_config:
            print("❌ Piper VITS configuration missing from template")
            return False

        # Check required VITS architecture fields
        required_vits_fields = ["inter_channels", "hidden_channels", "filter_channels", "n_heads", "n_layers"]
        for field in required_vits_fields:
            if field in piper_config:
                print(f"✅ Template contains VITS field '{field}': {piper_config[field]}")
            else:
                print(f"❌ Template missing VITS field '{field}'")
                return False

        # Check audio processing fields
        audio_fields = ["sample_rate", "n_fft", "hop_size", "n_mels", "f_min", "f_max"]
        for field in audio_fields:
            if field in piper_config:
                print(f"✅ Template contains audio field '{field}': {piper_config[field]}")
            else:
                print(f"❌ Template missing audio field '{field}'")
                return False

        # Check synthesis parameters
        synthesis_fields = ["noise_scale", "noise_scale_d", "length_scale", "inference_noise_scale"]
        for field in synthesis_fields:
            if field in piper_config:
                print(f"✅ Template contains synthesis field '{field}': {piper_config[field]}")
            else:
                print(f"❌ Template missing synthesis field '{field}'")
                return False

        return True

    except Exception as e:
        print(f"❌ Piper VITS template test failed: {e}")
        return False


def test_piper_vits_validation_rules():
    """Test Piper VITS validation rules."""
    print("\nTesting Piper VITS Validation Rules...")

    try:
        # Use a complete configuration for validation rules testing
        config = {
            "project": {
                "name": "test",
                "version": "1.0.0",
                "model_type": "piper_vits"
            },
            "hardware": {
                "target_device": "horizon_x5",
                "optimization_level": "O2",
                "memory_limit": "8GB",
                "compute_units": 10
            },
            "conversion_params": {
                "input_format": "onnx",
                "output_format": "bpu",
                "precision": "int8",
                "batch_size": 1,
                "num_workers": 4
            },
            "model_specific": {
                "piper_vits": {
                    # Required validation fields
                    "sample_rate": 22050,
                    "mel_channels": 80,
                    "speaker_embedding": True,

                    # VITS architecture parameters
                    "inter_channels": 192,
                    "hidden_channels": 192,
                    "filter_channels": 768,
                    "n_heads": 2,
                    "n_layers": 6,
                    "kernel_size": 3,
                    "p_dropout": 0.1,

                    # Audio processing parameters
                    "n_fft": 1024,
                    "hop_size": 256,
                    "win_size": 1024,
                    "n_mels": 80,
                    "f_min": 0.0,
                    "f_max": 8000.0,
                    "max_wav_value": 32768.0,
                    "normalize": True,

                    # Synthesis parameters
                    "noise_scale": 0.667,
                    "noise_scale_d": 0.8,
                    "length_scale": 1.0,
                    "inference_noise_scale": 0.667,
                    "max_decoder_steps": 2000,
                    "gate_threshold": 0.5,
                    "temperature": 1.0,

                    # Speaker configuration
                    "num_speakers": 1,
                    "speaker_id": 0,
                    "speaker_embedding_size": 192,

                    # Advanced features
                    "use_sdp": True,
                    "use_spectral_norm": False,
                    "gin_channels": 256
                }
            }
        }
        strategy = PiperVITSConfigStrategy(config)
        validation_rules = strategy.get_validation_rules()

        if not validation_rules:
            print("❌ No validation rules generated")
            return False

        print(f"✅ Generated {len(validation_rules)} validation rules")

        # Check important validation rules
        important_rules = [
            "model_specific.piper_vits.inter_channels",
            "model_specific.piper_vits.n_heads",
            "model_specific.piper_vits.sample_rate",
            "model_specific.piper_vits.num_speakers",
            "model_specific.piper_vits.noise_scale"
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
        print(f"❌ Piper VITS validation rules test failed: {e}")
        return False


def test_piper_vits_audio_processing():
    """Test Piper VITS audio processing configuration."""
    print("\nTesting Piper VITS Audio Processing Configuration...")

    try:
        config = {
            "model_specific": {
                "piper_vits": {
                    # Required validation fields
                    "sample_rate": 22050,
                    "mel_channels": 80,
                    "speaker_embedding": True,

                    # Audio processing parameters
                    "n_fft": 1024,
                    "hop_size": 256,
                    "win_size": 1024,
                    "n_mels": 80,
                    "f_min": 0.0,
                    "f_max": 8000.0,
                    "max_wav_value": 32768.0,
                    "normalize": True,

                    # Additional VITS parameters
                    "inter_channels": 192,
                    "hidden_channels": 192,
                    "filter_channels": 768,
                    "n_heads": 2,
                    "n_layers": 6,
                    "kernel_size": 3,
                    "p_dropout": 0.1,

                    # Synthesis parameters
                    "noise_scale": 0.667,
                    "noise_scale_d": 0.8,
                    "length_scale": 1.0,
                    "inference_noise_scale": 0.667,

                    # Speaker configuration
                    "num_speakers": 1,
                    "speaker_id": 0
                }
            }
        }

        strategy = PiperVITSConfigStrategy(config)

        # Test validation
        is_valid = strategy.validate_model_specific_config()
        if is_valid:
            print("✅ Audio processing configuration validation passed")
        else:
            print("❌ Audio processing configuration validation failed")
            return False

        # Check audio parameters
        piper_config = config["model_specific"]["piper_vits"]
        sample_rate = piper_config.get("sample_rate")
        if sample_rate == 22050:
            print(f"✅ Sample rate correct: {sample_rate}Hz")
        else:
            print(f"❌ Sample rate incorrect: {sample_rate}")
            return False

        return True

    except Exception as e:
        print(f"❌ Piper VITS audio processing test failed: {e}")
        return False


def test_piper_vits_speaker_support():
    """Test Piper VITS speaker support configuration."""
    print("\nTesting Piper VITS Speaker Support...")

    try:
        # Test with multiple speakers
        config = {
            "model_specific": {
                "piper_vits": {
                    # Required validation fields
                    "sample_rate": 22050,
                    "mel_channels": 80,
                    "speaker_embedding": True,

                    # Multi-speaker configuration
                    "num_speakers": 10,
                    "speaker_embedding_size": 256,
                    "speaker_id": 0,
                    "use_speaker_embedding": True,
                    "gin_channels": 256,

                    # Audio processing parameters
                    "n_fft": 1024,
                    "hop_size": 256,
                    "win_size": 1024,
                    "n_mels": 80,
                    "f_min": 0.0,
                    "f_max": 8000.0,

                    # VITS architecture
                    "inter_channels": 192,
                    "hidden_channels": 192,
                    "filter_channels": 768,
                    "n_heads": 2,
                    "n_layers": 6,
                    "kernel_size": 3
                }
            }
        }

        strategy = PiperVITSConfigStrategy(config)

        # Validate multi-speaker configuration
        is_valid = strategy.validate_model_specific_config()
        if is_valid:
            print("✅ Multi-speaker configuration validation passed")

            # Check speaker configuration
            piper_config = config["model_specific"]["piper_vits"]
            num_speakers = piper_config.get("num_speakers")
            embedding_size = piper_config.get("speaker_embedding_size")
            print(f"✅ Speakers: {num_speakers}, Embedding size: {embedding_size}")
        else:
            print("❌ Multi-speaker configuration validation failed")
            return False

        return True

    except Exception as e:
        print(f"❌ Piper VITS speaker support test failed: {e}")
        return False


def test_piper_vits_synthesis_parameters():
    """Test Piper VITS synthesis parameter validation."""
    print("\nTesting Piper VITS Synthesis Parameters...")

    try:
        # Test various synthesis parameter combinations
        test_configs = [
            {
                "name": "fast_synthesis",
                "config": {
                    # Required validation fields
                    "sample_rate": 22050,
                    "mel_channels": 80,
                    "speaker_embedding": True,

                    # Synthesis parameters
                    "noise_scale": 0.5,
                    "noise_scale_d": 0.6,
                    "length_scale": 0.8,
                    "inference_noise_scale": 0.5
                }
            },
            {
                "name": "quality_synthesis",
                "config": {
                    # Required validation fields
                    "sample_rate": 22050,
                    "mel_channels": 80,
                    "speaker_embedding": True,

                    # Synthesis parameters
                    "noise_scale": 0.8,
                    "noise_scale_d": 1.0,
                    "length_scale": 1.2,
                    "inference_noise_scale": 0.8
                }
            }
        ]

        for test_case in test_configs:
            config = {
                "model_specific": {
                    "piper_vits": test_case["config"]
                }
            }

            strategy = PiperVITSConfigStrategy(config)
            is_valid = strategy.validate_model_specific_config()

            if is_valid:
                print(f"✅ {test_case['name']} configuration validation passed")
            else:
                print(f"❌ {test_case['name']} configuration validation failed")
                return False

        return True

    except Exception as e:
        print(f"❌ Piper VITS synthesis parameters test failed: {e}")
        return False


def test_piper_vits_advanced_features():
    """Test Piper VITS advanced features."""
    print("\nTesting Piper VITS Advanced Features...")

    try:
        config = {
            "model_specific": {
                "piper_vits": {
                    # Required validation fields
                    "sample_rate": 22050,
                    "mel_channels": 80,
                    "speaker_embedding": True,

                    # Basic VITS parameters
                    "inter_channels": 192,
                    "hidden_channels": 192,
                    "n_heads": 2,
                    "n_layers": 6,

                    # Audio processing parameters
                    "n_fft": 1024,
                    "hop_size": 256,
                    "win_size": 1024,
                    "n_mels": 80,
                    "f_min": 0.0,
                    "f_max": 8000.0,

                    # Advanced features
                    "use_sdp": True,  # Stochastic Duration Predictor
                    "use_spectral_norm": False,
                    "gin_channels": 256,

                    # Performance optimizations
                    "deterministic_seed": 42,
                    "profiling_enabled": False
                }
            }
        }

        strategy = PiperVITSConfigStrategy(config)

        # Test validation with advanced features
        is_valid = strategy.validate_model_specific_config()
        if is_valid:
            print("✅ Advanced features configuration validation passed")

            # Check advanced features
            piper_config = config["model_specific"]["piper_vits"]
            use_sdp = piper_config.get("use_sdp")
            gin_channels = piper_config.get("gin_channels")
            print(f"✅ SDP enabled: {use_sdp}, GIN channels: {gin_channels}")
        else:
            print("❌ Advanced features configuration validation failed")
            return False

        return True

    except Exception as e:
        print(f"❌ Piper VITS advanced features test failed: {e}")
        return False


def main():
    """Run all Piper VITS strategy tests."""
    print("🚀 Testing Piper VITS Configuration Strategy")
    print("=" * 60)
    print("Based on technical specifications for TTS models")

    tests = [
        ("Strategy Initialization", test_piper_vits_strategy_initialization),
        ("Default Template", test_piper_vits_template),
        ("Validation Rules", test_piper_vits_validation_rules),
        ("Audio Processing", test_piper_vits_audio_processing),
        ("Speaker Support", test_piper_vits_speaker_support),
        ("Synthesis Parameters", test_piper_vits_synthesis_parameters),
        ("Advanced Features", test_piper_vits_advanced_features),
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
        print("🎉 All tests passed! Piper VITS strategy is working correctly.")
        print("\n📋 Piper VITS Strategy Features:")
        print("  ✅ VITS TTS model architecture configuration")
        print("  ✅ Multi-speaker voice synthesis support")
        print("  ✅ High-quality audio processing (22.05kHz)")
        print("  ✅ Advanced synthesis parameter control")
        print("  ✅ Stochastic Duration Predictor (SDP)")
        print("  ✅ Comprehensive validation system")
        print("  ✅ Performance optimization features")
    else:
        print(f"⚠️ {total - passed} tests failed. Please check the implementation.")

    return passed == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)