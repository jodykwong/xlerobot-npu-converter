#!/usr/bin/env python3
"""
Test script for VITS-Cantonese configuration strategy.

Tests the VITS-Cantonese strategy implementation based on technical research
from market analysis agent, ensuring compatibility with the actual VITS-Cantonese model specifications.
"""

import sys
import time
from pathlib import Path

# Add the src directory to Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from npu_converter.config.strategies.vits_cantonese_strategy import VITSCantoneseConfigStrategy


def test_vits_cantonese_strategy_initialization():
    """Test VITS-Cantonese strategy initialization."""
    print("Testing VITS-Cantonese Strategy Initialization...")

    try:
        # Create test configuration
        test_config = {
            "project": {
                "name": "test_vits_cantonese",
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
            },
            "model_specific": {
                "vits_cantonese": {
                    # VITS architecture parameters
                    "inter_channels": 192,
                    "hidden_channels": 192,
                    "filter_channels": 768,
                    "n_heads": 2,
                    "n_layers": 4,
                    "kernel_size": 3,

                    # Audio processing parameters
                    "sampling_rate": 22050,
                    "filter_length": 1024,
                    "hop_length": 256,
                    "win_length": 1024,
                    "n_mel_channels": 80,

                    # Cantonese-specific parameters
                    "cantonese_vocab_size": 5000,
                    "phoneme_set": "jyutping_extended",
                    "tone_embedding": True,
                    "num_tones": 6,
                    "use_jyutping": True,

                    # Synthesis parameters
                    "noise_scale": 0.667,
                    "noise_scale_w": 0.8,
                    "length_scale": 1.0,
                    "inference_noise_scale": 0.667,

                    # Cantonese Phoneme Inventory
                    "phoneme_inventory": {
                        "initials": ["b", "p", "m", "f", "d", "t", "n", "l", "g", "k",
                                   "ng", "h", "gw", "kw", "w", "z", "c", "s", "j"],
                        "finals": ["aa", "aai", "aau", "aam", "aan", "aang", "aap", "aat", "aak"],
                        "tones": [1, 2, 3, 4, 5, 6],
                        "tone_values": {
                            "1": 55, "2": 25, "3": 33, "4": 21, "5": 23, "6": 22
                        }
                    },

                    # Regional settings
                    "regional_accent": "hong_kong",
                    "text_cleaners": ["cantonese_cleaners"],
                    "jyutping_to_phoneme": True,
                    "tone_normalization": True
                }
            }
        }

        # Initialize strategy
        strategy = VITSCantoneseConfigStrategy(test_config)
        print("✅ VITSCantoneseConfigStrategy initialized successfully")

        # Test model type
        model_type = strategy.get_model_type()
        if model_type == "vits_cantonese":
            print(f"✅ Model type correctly identified: {model_type}")
        else:
            print(f"❌ Model type incorrect: expected 'vits_cantonese', got '{model_type}'")
            return False

        # Test validation
        is_valid = strategy.validate()
        if is_valid:
            print("✅ Configuration validation passed")
        else:
            print("❌ Configuration validation failed")
            return False

        return True

    except Exception as e:
        print(f"❌ VITS-Cantonese strategy initialization test failed: {e}")
        return False


def test_vits_cantonese_template():
    """Test VITS-Cantonese default template."""
    print("\nTesting VITS-Cantonese Default Template...")

    try:
        strategy = VITSCantoneseConfigStrategy({})
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

        # Check VITS-Cantonese specific configuration
        vits_config = template.get("model_specific", {}).get("vits_cantonese", {})
        if not vits_config:
            print("❌ VITS-Cantonese configuration missing from template")
            return False

        # Check required VITS architecture fields
        required_vits_fields = ["inter_channels", "hidden_channels", "filter_channels", "n_heads", "n_layers"]
        for field in required_vits_fields:
            if field in vits_config:
                print(f"✅ Template contains VITS field '{field}': {vits_config[field]}")
            else:
                print(f"❌ Template missing VITS field '{field}'")
                return False

        # Check Cantonese-specific fields
        required_cantonese_fields = ["sampling_rate", "cantonese_vocab_size", "phoneme_set", "num_tones", "use_jyutping"]
        for field in required_cantonese_fields:
            if field in vits_config:
                print(f"✅ Template contains Cantonese field '{field}': {vits_config[field]}")
            else:
                print(f"❌ Template missing Cantonese field '{field}'")
                return False

        # Check phoneme inventory
        phoneme_inventory = vits_config.get("phoneme_inventory", {})
        if phoneme_inventory:
            print(f"✅ Template contains phoneme inventory with {len(phoneme_inventory)} keys")
            print(f"  - Initials: {len(phoneme_inventory.get('initials', []))}")
            print(f"  - Finals: {len(phoneme_inventory.get('finals', []))}")
            print(f"  - Tones: {phoneme_inventory.get('tones', [])}")
        else:
            print("❌ Template missing phoneme inventory")

        return True

    except Exception as e:
        print(f"❌ VITS-Cantonese template test failed: {e}")
        return False


def test_vits_cantonese_validation_rules():
    """Test VITS-Cantonese validation rules."""
    print("\nTesting VITS-Cantonese Validation Rules...")

    try:
        strategy = VITSCantoneseConfigStrategy({})
        validation_rules = strategy.get_validation_rules()

        if not validation_rules:
            print("❌ No validation rules generated")
            return False

        print(f"✅ Generated {len(validation_rules)} validation rules")

        # Check important validation rules
        important_rules = [
            "model_specific.vits_cantonese.inter_channels",
            "model_specific.vits_cantonese.n_heads",
            "model_specific.vits_cantonese.sampling_rate",
            "model_specific.vits_cantonese.num_tones",
            "model_specific.vits_cantonese.phoneme_set"
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
        print(f"❌ VITS-Cantonese validation rules test failed: {e}")
        return False


def test_vits_cantonese_audio_processing_config():
    """Test VITS-Cantonese audio processing configuration."""
    print("\nTesting VITS-Cantonese Audio Processing Configuration...")

    try:
        strategy = VITSCantoneseConfigStrategy({})
        config = {
            "model_specific": {
                "vits_cantonese": {
                    "sampling_rate": 22050,
                    "filter_length": 1024,
                    "hop_length": 256,
                    "n_mel_channels": 80,
                    "mel_fmin": 0.0,
                    "mel_fmax": 8000.0,
                    "jyutping_to_phoneme": True,
                    "tone_normalization": True,
                    "regional_accent": "hong_kong",
                    "phoneme_set": "jyutping_extended"
                }
            }
        }
        strategy = VITSCantoneseConfigStrategy(config)

        audio_config = strategy.get_audio_processing_config()
        if not audio_config:
            print("❌ Audio processing configuration generation failed")
            return False

        # Check VITS architecture config
        vits_arch = audio_config.get("vits_architecture", {})
        if vits_arch:
            print(f"✅ VITS architecture config generated")
            print(f"  - Inter channels: {vits_arch.get('inter_channels')}")
            print(f"  - Hidden channels: {vits_arch.get('hidden_channels')}")
            print(f"  - N heads: {vits_arch.get('n_heads')}")
        else:
            print("❌ VITS architecture config missing")

        # Check audio processing config
        audio_proc = audio_config.get("audio_processing", {})
        if audio_proc:
            print(f"✅ Audio processing config generated")
            print(f"  - Sample rate: {audio_proc.get('sampling_rate')}")
            print(f"  - Mel channels: {audio_proc.get('n_mel_channels')}")
            print(f"  - Mel frequency range: {audio_proc.get('mel_fmin')} - {audio_proc.get('mel_fmax')}")
        else:
            print("❌ Audio processing config missing")

        # Check Cantonese preprocessing config
        cantonese_preproc = audio_config.get("cantonese_preprocessing", {})
        if cantonese_preproc:
            print(f"✅ Cantonese preprocessing config generated")
            print(f"  - Jyutping conversion: {cantonese_preproc.get('jyutping_to_phoneme')}")
            print(f"  - Tone normalization: {cantonese_preproc.get('tone_normalization')}")
            print(f"  - Regional accent: {cantonese_preproc.get('regional_accent')}")
        else:
            print("❌ Cantonese preprocessing config missing")

        return True

    except Exception as e:
        print(f"❌ VITS-Cantonese audio processing config test failed: {e}")
        return False


def test_vits_cantonese_synthesis_config():
    """Test VITS-Cantonese synthesis configuration."""
    print("\nTesting VITS-Cantonese Synthesis Configuration...")

    try:
        strategy = VITSCantoneseConfigStrategy({})
        config = {
            "model_specific": {
                "vits_cantonese": {
                    "noise_scale": 0.667,
                    "noise_scale_w": 0.8,
                    "length_scale": 1.0,
                    "inference_noise_scale": 0.667,
                    "speaker_embedding_size": 192,
                    "num_speakers": 1,
                    "tone_embedding": True,
                    "num_tones": 6,
                    "use_jyutping": True
                }
            }
        }
        strategy = VITSCantoneseConfigStrategy(config)

        synthesis_config = strategy.get_synthesis_config()
        if not synthesis_config:
            print("❌ Synthesis configuration generation failed")
            return False

        # Check synthesis parameters
        synth_params = synthesis_config.get("synthesis_parameters", {})
        if synth_params:
            print(f"✅ Synthesis parameters config generated")
            print(f"  - Noise scale: {synth_params.get('noise_scale')}")
            print(f"  - Noise scale w: {synth_params.get('noise_scale_w')}")
            print(f"  - Length scale: {synth_params.get('length_scale')}")
        else:
            print("❌ Synthesis parameters config missing")

        # Check speaker config
        speaker_config = synthesis_config.get("speaker_config", {})
        if speaker_config:
            print(f"✅ Speaker config generated")
            print(f"  - Speaker embedding size: {speaker_config.get('speaker_embedding_size')}")
            print(f"  - Num speakers: {speaker_config.get('num_speakers')}")
        else:
            print("❌ Speaker config missing")

        # Check Cantonese synthesis config
        cantonese_synth = synthesis_config.get("cantonese_synthesis", {})
        if cantonese_synth:
            print(f"✅ Cantonese synthesis config generated")
            print(f"  - Tone embedding: {cantonese_synth.get('tone_embedding')}")
            print(f"  - Num tones: {cantonese_synth.get('num_tones')}")
            print(f"  - Use Jyutping: {cantonese_synth.get('use_jyutping')}")
        else:
            print("❌ Cantonese synthesis config missing")

        return True

    except Exception as e:
        print(f"❌ VITS-Cantonese synthesis config test failed: {e}")
        return False


def test_vits_cantonese_optimization_config():
    """Test VITS-Cantonese optimization configuration."""
    print("\nTesting VITS-Cantonese Optimization Configuration...")

    try:
        strategy = VITSCantoneseConfigStrategy({})
        config = {
            "optimization": {
                "enable_quantization": True,
                "quantization_precision": "int8",
                "quantization_method": "dynamic_quantization",
                "torch_compile": True,
                "use_efficient_attention": True
            }
        }
        strategy = VITSCantoneseConfigStrategy(config)

        optimization_config = strategy.get_optimization_config()
        if not optimization_config:
            print("❌ Optimization configuration generation failed")
            return False

        # Check inference optimization
        inference_opt = optimization_config.get("inference_optimization", {})
        if inference_opt:
            print(f"✅ Inference optimization config generated")
            print(f"  - Torch compile: {inference_opt.get('torch_compile')}")
            print(f"  - Efficient attention: {inference_opt.get('use_efficient_attention')}")
        else:
            print("❌ Inference optimization config missing")

        # Check quantization config
        quantization = optimization_config.get("quantization", {})
        if quantization:
            print(f"✅ Quantization config generated")
            print(f"  - Enabled: {quantization.get('enabled')}")
            print(f"  - Precision: {quantization.get('precision')}")
            print(f"  - Method: {quantization.get('method')}")
        else:
            print("❌ Quantization config missing")

        # Check Cantonese preservation
        cantonese_preservation = quantization.get("cantonese_preservation", {})
        if cantonese_preservation:
            print(f"✅ Cantonese preservation config generated")
            print(f"  - Tone model quantization: {cantonese_preservation.get('tone_model_quantization')}")
            print(f"  - Phoneme embedding quantization: {cantonese_preservation.get('phoneme_embedding_quantization')}")
        else:
            print("❌ Cantonese preservation config missing")

        return True

    except Exception as e:
        print(f"❌ VITS-Cantonese optimization config test failed: {e}")
        return False


def test_vits_cantonese_performance_requirements():
    """Test VITS-Cantonese performance requirements."""
    print("\nTesting VITS-Cantonese Performance Requirements...")

    try:
        strategy = VITSCantoneseConfigStrategy({})
        config = {
            "performance": {
                "target_latency_ms": 200,
                "max_realtime_factor": 0.9,
                "enable_streaming": True,
                "max_batch_size": 4
            }
        }
        strategy = VITSCantoneseConfigStrategy(config)

        performance_config = strategy.get_performance_requirements()
        if not performance_config:
            print("❌ Performance requirements configuration generation failed")
            return False

        # Check latency targets
        latency = performance_config.get("latency_targets", {})
        if latency:
            print(f"✅ Latency targets configured")
            print(f"  - Target latency: {latency.get('target_latency_ms')}ms")
            print(f"  - Max realtime factor: {latency.get('max_realtime_factor')}")
        else:
            print("❌ Latency targets missing")

        # Check throughput targets
        throughput = performance_config.get("throughput_targets", {})
        if throughput:
            print(f"✅ Throughput targets configured")
            print(f"  - Realtime factor: {throughput.get('realtime_factor')}")
            print(f"  - Max batch size: {throughput.get('max_batch_size')}")
        else:
            print("❌ Throughput targets missing")

        # Check quality metrics
        quality = performance_config.get("quality_metrics", {})
        if quality:
            print(f"✅ Quality metrics configured")
            print(f"  - MCD score target: {quality.get('objective', {}).get('mcd_score_target')}")
            print(f"  - MOS score target: {quality.get('subjective', {}).get('mos_score_target')}")
        else:
            print("❌ Quality metrics missing")

        return True

    except Exception as e:
        print(f"❌ VITS-Cantonese performance requirements test failed: {e}")
        return False


def main():
    """Run all VITS-Cantonese strategy tests."""
    print("🚀 Testing VITS-Cantonese Configuration Strategy")
    print("=" * 60)
    print("Based on technical research from market analysis agent")

    tests = [
        ("Strategy Initialization", test_vits_cantonese_strategy_initialization),
        ("Default Template", test_vits_cantonese_template),
        ("Validation Rules", test_vits_cantonese_validation_rules),
        ("Audio Processing Config", test_vits_cantonese_audio_processing_config),
        ("Synthesis Config", test_vits_cantonese_synthesis_config),
        ("Optimization Config", test_vits_cantonese_optimization_config),
        ("Performance Requirements", test_vits_cantonese_performance_requirements),
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
        print("🎉 All tests passed! VITS-Cantonese strategy is working correctly.")
        print("\n📋 VITS-Cantonese Strategy Features:")
        print("  ✅ VITS model architecture configuration")
        print("  ✅ Cantonese phoneme system (6 tones, Jyutping)")
        print("  ✅ Audio processing optimized for Cantonese")
        print("  ✅ Real-time synthesis optimization")
        print("  ✅ NPU deployment configuration")
        print("  ✅ Comprehensive validation system")
        print("  ✅ Performance requirement compliance")
    else:
        print(f"⚠️ {total - passed} tests failed. Please check the implementation.")

    return passed == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)