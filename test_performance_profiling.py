#!/usr/bin/env python3
"""
Performance profiling to identify bottlenecks in configuration loading.
"""

import time
import tempfile
import yaml
from pathlib import Path

def create_minimal_config():
    """Create a minimal test configuration."""
    return {
        "project": {
            "name": "test",
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

def profile_individual_components():
    """Profile individual component initialization times."""
    print("🔍 Profiling Individual Component Initialization")
    print("=" * 60)

    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        config_file = temp_path / "minimal_config.yaml"

        config = create_minimal_config()
        with open(config_file, 'w', encoding='utf-8') as f:
            yaml.dump(config, f, default_flow_style=False, indent=2)

        # Test 1: Pure YAML loading
        print("\n1. Pure YAML Loading:")
        start_time = time.time()
        with open(config_file, 'r', encoding='utf-8') as f:
            loaded_config = yaml.safe_load(f)
        yaml_time = (time.time() - start_time) * 1000
        print(f"   YAML loading: {yaml_time:.2f}ms")

        # Test 2: Module import time
        print("\n2. Module Import Times:")

        import_start = time.time()
        from npu_converter.core.exceptions.config_errors import ConfigError
        config_errors_time = (time.time() - import_start) * 1000
        print(f"   ConfigError import: {config_errors_time:.2f}ms")

        import_start = time.time()
        from npu_converter.config.validator import ConfigValidator
        validator_time = (time.time() - import_start) * 1000
        print(f"   ConfigValidator import: {validator_time:.2f}ms")

        import_start = time.time()
        from npu_converter.config.templates import ConfigTemplateManager
        template_time = (time.time() - import_start) * 1000
        print(f"   ConfigTemplateManager import: {template_time:.2f}ms")

        import_start = time.time()
        from npu_converter.config.recovery import ConfigRecoveryManager
        recovery_time = (time.time() - import_start) * 1000
        print(f"   ConfigRecoveryManager import: {recovery_time:.2f}ms")

        import_start = time.time()
        from npu_converter.config.strategies.sensevoice_strategy import SenseVoiceConfigStrategy
        sensevoice_time = (time.time() - import_start) * 1000
        print(f"   SenseVoiceConfigStrategy import: {sensevoice_time:.2f}ms")

        # Test 3: Component instantiation
        print("\n3. Component Instantiation Times:")

        validator_start = time.time()
        validator = ConfigValidator()
        validator_instantiation = (time.time() - validator_start) * 1000
        print(f"   ConfigValidator instantiation: {validator_instantiation:.2f}ms")

        template_start = time.time()
        template_manager = ConfigTemplateManager()
        template_instantiation = (time.time() - template_start) * 1000
        print(f"   ConfigTemplateManager instantiation: {template_instantiation:.2f}ms")

        recovery_start = time.time()
        recovery_manager = ConfigRecoveryManager(temp_path)
        recovery_instantiation = (time.time() - recovery_start) * 1000
        print(f"   ConfigRecoveryManager instantiation: {recovery_instantiation:.2f}ms")

        # Test 4: Validation time
        print("\n4. Validation Times:")

        validation_start = time.time()
        is_valid = validator.validate(loaded_config)
        validation_time = (time.time() - validation_start) * 1000
        print(f"   Basic validation: {validation_time:.2f}ms")
        print(f"   Validation result: {is_valid}")

        detailed_validation_start = time.time()
        validation_result = validator.validate_detailed(loaded_config)
        detailed_validation_time = (time.time() - detailed_validation_start) * 1000
        print(f"   Detailed validation: {detailed_validation_time:.2f}ms")
        print(f"   Detailed validation result: {validation_result.is_valid}")

        # Test 5: Strategy initialization
        print("\n5. Strategy Initialization:")

        strategy_start = time.time()
        strategy = SenseVoiceConfigStrategy(loaded_config)
        strategy_instantiation = (time.time() - strategy_start) * 1000
        print(f"   SenseVoiceConfigStrategy instantiation: {strategy_instantiation:.2f}ms")

        # Summary
        print("\n" + "=" * 60)
        print("Performance Bottleneck Analysis")
        print("=" * 60)

        total_components = (
            yaml_time + config_errors_time + validator_time + template_time +
            recovery_time + sensevoice_time + validator_instantiation +
            template_instantiation + recovery_instantiation + validation_time +
            strategy_instantiation
        )

        print(f"YAML loading: {yaml_time:.2f}ms ({yaml_time/total_components*100:.1f}%)")
        print(f"Module imports: {config_errors_time + validator_time + template_time + recovery_time + sensevoice_time:.2f}ms ({(config_errors_time + validator_time + template_time + recovery_time + sensevoice_time)/total_components*100:.1f}%)")
        print(f"Component instantiation: {validator_instantiation + template_instantiation + recovery_instantiation:.2f}ms ({(validator_instantiation + template_instantiation + recovery_instantiation)/total_components*100:.1f}%)")
        print(f"Validation: {validation_time:.2f}ms ({validation_time/total_components*100:.1f}%)")
        print(f"Strategy: {strategy_instantiation:.2f}ms ({strategy_instantiation/total_components*100:.1f}%)")
        print(f"Total estimated: {total_components:.2f}ms")

        # Identify bottlenecks
        times = [
            ("YAML Loading", yaml_time),
            ("ConfigValidator Import", validator_time),
            ("ConfigTemplateManager Import", template_time),
            ("ConfigRecoveryManager Import", recovery_time),
            ("SenseVoiceConfigStrategy Import", sensevoice_time),
            ("ConfigValidator Instantiation", validator_instantiation),
            ("ConfigTemplateManager Instantiation", template_instantiation),
            ("ConfigRecoveryManager Instantiation", recovery_instantiation),
            ("Validation", validation_time),
            ("Strategy Instantiation", strategy_instantiation)
        ]

        times.sort(key=lambda x: x[1], reverse=True)

        print(f"\nTop 3 bottlenecks:")
        for i, (name, time_ms) in enumerate(times[:3]):
            print(f"  {i+1}. {name}: {time_ms:.2f}ms")

if __name__ == "__main__":
    profile_individual_components()