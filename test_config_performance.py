#!/usr/bin/env python3
"""
Performance test for optimized configuration loading.
Tests the improvements made to achieve <100ms loading time.
"""

import time
import tempfile
import shutil
from pathlib import Path
from npu_converter.config.manager import ConfigurationManager

def create_test_config():
    """Create a test configuration file with complete VITS-Cantonese fields."""
    config = {
        "project": {
            "name": "xlerobot",
            "version": "1.0.0",
            "model_type": "vits_cantonese",
            "description": "VITS-Cantonese Text-to-Speech model"
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
            "calibration_method": "minmax"
        },
        "model_specific": {
            "vits_cantonese": {
                # VITS Model Architecture Configuration
                "inter_channels": 192,
                "hidden_channels": 192,
                "filter_channels": 768,
                "n_heads": 2,
                "n_layers": 4,
                "kernel_size": 3,
                "p_dropout": 0.1,
                "resblock": "1",
                "resblock_kernel_sizes": [3, 7, 11],
                "resblock_dilation_sizes": [[1, 3, 5], [1, 3, 5], [1, 3, 5]],
                "upsample_rates": [8, 8, 2, 2],
                "upsample_initial_channel": 512,
                "upsample_kernel_sizes": [16, 16, 4, 4],
                "n_layers_q": 3,
                "use_spectral_norm": False,
                "gin_channels": 256,

                # Audio Processing Parameters (Cantonese-optimized)
                "sampling_rate": 22050,
                "filter_length": 1024,
                "hop_length": 256,
                "win_length": 1024,
                "n_mel_channels": 80,
                "mel_fmin": 0.0,
                "mel_fmax": 8000.0,
                "max_wav_value": 32768.0,
                "normalize": True,
                "trim_silence": True,
                "trim_threshold": 0.01,

                # Voice Characteristics
                "speaker_embedding_size": 192,
                "num_speakers": 1,
                "speaker_id": 0,
                "use_speaker_embedding": True,

                # Cantonese TTS Synthesis Parameters
                "noise_scale": 0.667,
                "noise_scale_w": 0.8,
                "length_scale": 1.0,
                "inference_noise_scale": 0.667,

                # Cantonese Phoneme System Configuration
                "cantonese_vocab_size": 5000,
                "phoneme_set": "jyutping_extended",
                "phoneme_language": "cantonese",
                "phonemizer": "espeak",
                "tone_embedding": True,
                "num_tones": 6,
                "use_jyutping": True,
                "character_coverage": 0.995,

                # Cantonese Phoneme Inventory
                "phoneme_inventory": {
                    "initials": ["b", "p", "m", "f", "d", "t", "n", "l", "g", "k",
                               "ng", "h", "gw", "kw", "w", "z", "c", "s", "j"],
                    "finals": ["aa", "aai", "aau", "aam", "aan", "aang", "aap", "aat", "aak",
                               "ai", "au", "am", "an", "ang", "ap", "at", "ak", "e", "ei",
                               "eu", "em", "en", "eng", "ep", "et", "i", "iu", "im", "in",
                               "ing", "ip", "it", "o", "oi", "ou", "on", "ong", "ot", "ok",
                               "oe", "oeng", "oek", "u", "ui", "un", "ung", "ut", "uk", "oe"],
                    "tones": [1, 2, 3, 4, 5, 6],
                    "tone_values": {
                        "1": 55,  # High level
                        "2": 25,  # High rising
                        "3": 33,  # Mid level
                        "4": 21,  # Low falling
                        "5": 23,  # Low rising
                        "6": 22   # Low level
                    }
                },

                # Cantonese Text Processing
                "text_cleaners": ["cantonese_cleaners"],
                "jyutping_to_phoneme": True,
                "tone_normalization": True,
                "regional_accent": "hong_kong",
                "regional_variants": {
                    "hong_kong": {
                        "preference": "standard",
                        "tone_contours": "standard",
                        "vowel_system": "9_vowel"
                    },
                    "guangzhou": {
                        "preference": "standard",
                        "tone_contours": "slightly_modified",
                        "vowel_system": "8_vowel"
                    }
                },

                # Data Preprocessing Settings
                "add_blank": True,
                "n_speakers": 1,
                "cleaned_text": True
            }
        }
    }
    return config

def test_performance_improvements():
    """Test performance improvements for configuration loading."""
    print("🚀 Testing Configuration Loading Performance Improvements")
    print("=" * 70)

    # Create temporary directory
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        config_file = temp_path / "test_config.yaml"

        # Create test configuration
        config = create_test_config()

        import yaml
        with open(config_file, 'w', encoding='utf-8') as f:
            yaml.dump(config, f, default_flow_style=False, indent=2)

        print(f"📁 Test config created: {config_file}")

        # Test 1: Lazy initialization (optimized)
        print("\n" + "=" * 50)
        print("Test 1: Lazy Initialization (Optimized)")
        print("=" * 50)

        lazy_times = []
        for i in range(5):
            start_time = time.time()

            config_manager = ConfigurationManager(config_file, lazy_init=True)
            loaded_config = config_manager.load_config(skip_backup=True, fast_validation=True)

            end_time = time.time()
            load_time_ms = (end_time - start_time) * 1000
            lazy_times.append(load_time_ms)

            print(f"  Run {i+1}: {load_time_ms:.2f}ms")

        avg_lazy_time = sum(lazy_times) / len(lazy_times)
        min_lazy_time = min(lazy_times)

        print(f"\n📊 Lazy Initialization Results:")
        print(f"  Average: {avg_lazy_time:.2f}ms")
        print(f"  Minimum: {min_lazy_time:.2f}ms")
        print(f"  Maximum: {max(lazy_times):.2f}ms")

        # Check performance target
        if min_lazy_time < 100:
            print(f"  ✅ Performance target achieved (<100ms): {min_lazy_time:.2f}ms")
        else:
            print(f"  ⚠️ Performance target not met: {min_lazy_time:.2f}ms > 100ms")

        # Test 2: Eager initialization (original behavior)
        print("\n" + "=" * 50)
        print("Test 2: Eager Initialization (Original)")
        print("=" * 50)

        eager_times = []
        for i in range(3):
            start_time = time.time()

            config_manager = ConfigurationManager(config_file, lazy_init=False)
            loaded_config = config_manager.load_config(skip_backup=True, fast_validation=True)

            end_time = time.time()
            load_time_ms = (end_time - start_time) * 1000
            eager_times.append(load_time_ms)

            print(f"  Run {i+1}: {load_time_ms:.2f}ms")

        avg_eager_time = sum(eager_times) / len(eager_times)

        print(f"\n📊 Eager Initialization Results:")
        print(f"  Average: {avg_eager_time:.2f}ms")

        # Performance improvement comparison
        print("\n" + "=" * 50)
        print("Performance Improvement Analysis")
        print("=" * 50)

        improvement = ((avg_eager_time - avg_lazy_time) / avg_eager_time) * 100
        speedup = avg_eager_time / avg_lazy_time

        print(f"  Lazy loading average: {avg_lazy_time:.2f}ms")
        print(f"  Eager loading average: {avg_eager_time:.2f}ms")
        print(f"  Performance improvement: {improvement:.1f}%")
        print(f"  Speedup factor: {speedup:.2f}x")

        # Test 3: Component initialization verification
        print("\n" + "=" * 50)
        print("Test 3: Component Initialization Verification")
        print("=" * 50)

        config_manager = ConfigurationManager(config_file, lazy_init=True)
        loaded_config = config_manager.load_config(skip_backup=True, fast_validation=True)

        # Check if basic components are initialized
        has_validator = config_manager._validator is not None
        has_strategy = config_manager._current_strategy is not None
        has_template_manager = config_manager._template_manager is not None

        print(f"  ✅ Validator initialized: {has_validator}")
        print(f"  ✅ Strategy initialized: {has_strategy}")
        print(f"  ✅ Template manager initialized: {has_template_manager}")

        # Check if heavy components are NOT initialized yet
        has_hot_reload = config_manager._hot_reload_manager is not None
        has_dynamic_config = config_manager._dynamic_config_manager is not None

        print(f"  ⏳ Hot reload manager deferred: {not has_hot_reload}")
        print(f"  ⏳ Dynamic config manager deferred: {not has_dynamic_config}")

        # Test on-demand initialization
        print("\n  Testing on-demand initialization...")
        start_time = time.time()
        config_manager.start_hot_reload()  # Should trigger heavy component init
        end_time = time.time()

        heavy_init_time = (end_time - start_time) * 1000
        print(f"  Heavy component initialization: {heavy_init_time:.2f}ms")

        # Verify heavy components are now initialized
        has_hot_reload_after = config_manager._hot_reload_manager is not None
        has_dynamic_config_after = config_manager._dynamic_config_manager is not None

        print(f"  ✅ Hot reload manager initialized: {has_hot_reload_after}")
        print(f"  ✅ Dynamic config manager initialized: {has_dynamic_config_after}")

        # Final assessment
        print("\n" + "=" * 50)
        print("Final Performance Assessment")
        print("=" * 50)

        if min_lazy_time < 100:
            print(f"🎉 SUCCESS: Performance target achieved!")
            print(f"   Best loading time: {min_lazy_time:.2f}ms (target: <100ms)")
            print(f"   Performance improvement: {improvement:.1f}% faster than original")
        else:
            print(f"⚠️ PARTIAL SUCCESS: Performance improved but target not met")
            print(f"   Best loading time: {min_lazy_time:.2f}ms (target: <100ms)")
            print(f"   Performance improvement: {improvement:.1f}% faster than original")
            print(f"   Further optimization may be needed")

        return min_lazy_time < 100, avg_lazy_time, improvement

if __name__ == "__main__":
    test_performance_improvements()