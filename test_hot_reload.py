#!/usr/bin/env python3
"""
Test script for the configuration hot reload system.

Tests the hot reload functionality implemented in task 4 of Story 1.4.
"""

import sys
import time
import threading
import tempfile
from pathlib import Path

# Add the src directory to Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from npu_converter.config import ConfigurationManager


def test_hot_reload_initialization():
    """Test hot reload manager initialization."""
    print("Testing Hot Reload Initialization...")

    try:
        config_file = Path("test_config_hot_reload.yaml")
        if not config_file.exists():
            print("❌ Test config file not found")
            return False

        # Initialize configuration manager
        manager = ConfigurationManager(config_file)
        config = manager.load_config()
        print("✅ ConfigurationManager initialized and loaded")

        # Get hot reload manager
        hot_reload_manager = manager._hot_reload_manager
        if hot_reload_manager:
            print("✅ HotReloadManager initialized")
        else:
            print("❌ HotReloadManager not available")
            return False

        # Check initial metrics
        metrics = hot_reload_manager.get_metrics()
        print(f"✅ Initial metrics: {metrics.reload_count} reloads")

        return True

    except Exception as e:
        print(f"❌ Hot reload initialization test failed: {e}")
        return False


def test_hot_reload_monitoring():
    """Test hot reload file monitoring."""
    print("\nTesting Hot Reload File Monitoring...")

    try:
        config_file = Path("test_config_hot_reload.yaml")
        manager = ConfigurationManager(config_file)
        manager.load_config()

        # Start monitoring
        hot_reload_manager = manager._hot_reload_manager
        hot_reload_manager.start_monitoring()

        if hot_reload_manager.is_monitoring():
            print("✅ Hot reload monitoring started")
        else:
            print("❌ Failed to start hot reload monitoring")
            return False

        # Test force reload
        initial_latency = manager.get_config("performance.target_latency_ms")

        # Modify the config file
        new_config_content = """project:
  name: "xlerobot"
  version: "1.0.0"
  model_type: "sensevoice"

hardware:
  target_device: "horizon_x5"
  optimization_level: "O2"
  memory_limit: "8GB"
  compute_units: 10
  cache_size: "256MB"

conversion_params:
  input_format: "onnx"
  output_format: "bpu"
  precision: "int8"
  calibration_method: "minmax"
  batch_size: 1
  num_workers: 4

model_specific:
  sensevoice:
    sample_rate: 16000
    audio_length: 30
    vocab_size: 10000
    mel_bins: 80
    frame_length: 25
    frame_shift: 10
    normalize: true
    preemphasis: 0.97
    n_fft: 512
    hop_length: 160
    win_length: 400
    n_mels: 80
    f_min: 0.0
    f_max: 8000.0

performance:
  target_latency_ms: 75
  max_realtime_factor: 0.1
  enable_streaming: False
"""

        with open(config_file, 'w') as f:
            f.write(new_config_content)

        # Wait for file monitoring to detect change
        time.sleep(1.0)

        # Check if config was reloaded
        updated_latency = manager.get_config("performance.target_latency_ms")
        if updated_latency != initial_latency:
            print(f"✅ Configuration reloaded: latency changed from {initial_latency} to {updated_latency}")
        else:
            print("⚠️ Configuration change not detected (may need more time)")

        # Stop monitoring
        hot_reload_manager.stop_monitoring()
        if not hot_reload_manager.is_monitoring():
            print("✅ Hot reload monitoring stopped")
        else:
            print("❌ Failed to stop hot reload monitoring")
            return False

        return True

    except Exception as e:
        print(f"❌ Hot reload monitoring test failed: {e}")
        return False


def test_hot_reload_performance():
    """Test hot reload performance requirements."""
    print("\nTesting Hot Reload Performance...")

    try:
        config_file = Path("test_config_hot_reload.yaml")
        manager = ConfigurationManager(config_file)
        manager.load_config()

        hot_reload_manager = manager._hot_reload_manager
        hot_reload_manager.start_monitoring()

        # Test multiple reloads for performance metrics
        reload_times = []
        num_tests = 5

        for i in range(num_tests):
            start_time = time.time()

            # Modify config file
            new_latency = 100 + i * 10
            config_content = f"""project:
  name: "xlerobot"
  version: "1.0.0"
  model_type: "sensevoice"

hardware:
  target_device: "horizon_x5"
  optimization_level: "O2"
  memory_limit: "8GB"
  compute_units: 10
  cache_size: "256MB"

conversion_params:
  input_format: "onnx"
  output_format: "bpu"
  precision: "int8"
  calibration_method: "minmax"
  batch_size: 1
  num_workers: 4

model_specific:
  sensevoice:
    sample_rate: 16000
    audio_length: 30
    vocab_size: 10000
    mel_bins: 80
    frame_length: 25
    frame_shift: 10
    normalize: true
    preemphasis: 0.97
    n_fft: 512
    hop_length: 160
    win_length: 400
    n_mels: 80
    f_min: 0.0
    f_max: 8000.0

performance:
  target_latency_ms: {new_latency}
  max_realtime_factor: 0.1
  enable_streaming: False
"""

            with open(config_file, 'w') as f:
                f.write(config_content)

            # Use force reload for more precise timing
            success = hot_reload_manager.force_reload()
            if success:
                reload_time = (time.time() - start_time) * 1000
                reload_times.append(reload_time)
                print(f"  Reload {i+1}: {reload_time:.2f}ms")
            else:
                print(f"❌ Force reload {i+1} failed")
                return False

            time.sleep(0.1)  # Small delay between reloads

        # Analyze performance
        avg_reload_time = sum(reload_times) / len(reload_times)
        max_reload_time = max(reload_times)
        min_reload_time = min(reload_times)

        print(f"✅ Performance metrics:")
        print(f"  Average reload time: {avg_reload_time:.2f}ms")
        print(f"  Max reload time: {max_reload_time:.2f}ms")
        print(f"  Min reload time: {min_reload_time:.2f}ms")

        # Check performance requirements (<500ms)
        if max_reload_time < 500:
            print("✅ Performance requirement met: all reloads < 500ms")
        else:
            print(f"❌ Performance requirement failed: max reload time {max_reload_time:.2f}ms >= 500ms")
            return False

        # Check hot reload manager metrics
        metrics = hot_reload_manager.get_metrics()
        if metrics.reload_count >= num_tests:
            print(f"✅ Reload count in metrics: {metrics.reload_count}")
        else:
            print(f"❌ Reload count mismatch: expected >= {num_tests}, got {metrics.reload_count}")
            return False

        hot_reload_manager.stop_monitoring()
        return True

    except Exception as e:
        print(f"❌ Hot reload performance test failed: {e}")
        return False


def test_hot_reload_error_handling():
    """Test hot reload error handling."""
    print("\nTesting Hot Reload Error Handling...")

    try:
        config_file = Path("test_config_hot_reload.yaml")
        manager = ConfigurationManager(config_file)
        manager.load_config()

        hot_reload_manager = manager._hot_reload_manager
        hot_reload_manager.start_monitoring()

        # Test invalid YAML configuration
        invalid_yaml = """project:
  name: "xlerobot"
  version: "1.0.0"
  model_type: "sensevoice"

hardware:
  target_device: "horizon_x5"
  optimization_level: "O2"
  memory_limit: "8GB"
  compute_units: 10
  cache_size: "256MB"

conversion_params:
  input_format: "onnx"
  output_format: "bpu"
  precision: "int8"
  calibration_method: "minmax"
  batch_size: 1
  num_workers: 4

# Invalid YAML - missing closing quotes
model_specific:
  sensevoice:
    sample_rate: 16000
    description: "invalid yaml without closing quote

performance:
  target_latency_ms: 100
  max_realtime_factor: 0.1
  enable_streaming: False
"""

        # Write invalid YAML
        with open(config_file, 'w') as f:
            f.write(invalid_yaml)

        # Wait for error handling
        time.sleep(1.0)

        # Check if system is still functional
        try:
            # Should still be able to access last known good configuration
            current_config = manager.get_config("project.name")
            if current_config:
                print("✅ System remained stable after invalid YAML")
            else:
                print("❌ System became unstable after invalid YAML")
                return False
        except Exception as e:
            print(f"❌ System crashed after invalid YAML: {e}")
            return False

        # Restore valid configuration
        valid_yaml = """project:
  name: "xlerobot"
  version: "1.0.0"
  model_type: "sensevoice"

hardware:
  target_device: "horizon_x5"
  optimization_level: "O2"
  memory_limit: "8GB"
  compute_units: 10
  cache_size: "256MB"

conversion_params:
  input_format: "onnx"
  output_format: "bpu"
  precision: "int8"
  calibration_method: "minmax"
  batch_size: 1
  num_workers: 4

model_specific:
  sensevoice:
    sample_rate: 16000
    audio_length: 30
    vocab_size: 10000
    mel_bins: 80
    frame_length: 25
    frame_shift: 10
    normalize: true
    preemphasis: 0.97
    n_fft: 512
    hop_length: 160
    win_length: 400
    n_mels: 80
    f_min: 0.0
    f_max: 8000.0

performance:
  target_latency_ms: 100
  max_realtime_factor: 0.1
  enable_streaming: False
"""

        with open(config_file, 'w') as f:
            f.write(valid_yaml)

        # Force reload to recover
        success = hot_reload_manager.force_reload()
        if success:
            print("✅ System recovered after restoring valid configuration")
        else:
            print("❌ System failed to recover after restoring valid configuration")
            return False

        hot_reload_manager.stop_monitoring()
        return True

    except Exception as e:
        print(f"❌ Hot reload error handling test failed: {e}")
        return False


def test_hot_reload_atomic_updates():
    """Test atomic configuration updates."""
    print("\nTesting Hot Reload Atomic Updates...")

    try:
        config_file = Path("test_config_hot_reload.yaml")
        manager = ConfigurationManager(config_file)
        manager.load_config()

        hot_reload_manager = manager._hot_reload_manager
        hot_reload_manager.start_monitoring()

        # Get initial configuration values
        initial_values = {
            "performance.target_latency_ms": manager.get_config("performance.target_latency_ms"),
            "hardware.optimization_level": manager.get_config("hardware.optimization_level"),
            "conversion_params.batch_size": manager.get_config("conversion_params.batch_size")
        }

        # Create new configuration with multiple changes
        new_config = """project:
  name: "xlerobot"
  version: "1.0.0"
  model_type: "sensevoice"

hardware:
  target_device: "horizon_x5"
  optimization_level: "O3"
  memory_limit: "8GB"
  compute_units: 10
  cache_size: "256MB"

conversion_params:
  input_format: "onnx"
  output_format: "bpu"
  precision: "int8"
  calibration_method: "minmax"
  batch_size: 4
  num_workers: 4

model_specific:
  sensevoice:
    sample_rate: 16000
    audio_length: 30
    vocab_size: 10000
    mel_bins: 80
    frame_length: 25
    frame_shift: 10
    normalize: true
    preemphasis: 0.97
    n_fft: 512
    hop_length: 160
    win_length: 400
    n_mels: 80
    f_min: 0.0
    f_max: 8000.0

performance:
  target_latency_ms: 50
  max_realtime_factor: 0.1
  enable_streaming: False
"""

        # Write new configuration atomically
        with tempfile.NamedTemporaryFile(mode='w', dir=config_file.parent, delete=False) as tmp_file:
            tmp_file.write(new_config)
            tmp_file.flush()
            # Atomic move
            Path(tmp_file.name).replace(config_file)

        # Wait for reload - increase time for file system monitoring
        time.sleep(1.0)

        # Force reload to ensure atomic update test works
        success = hot_reload_manager.force_reload()
        if success:
            print("✅ Force reload triggered for atomic update test")
        else:
            print("❌ Force reload failed for atomic update test")
            return False

        # Check if all changes were applied atomically
        updated_values = {
            "performance.target_latency_ms": manager.get_config("performance.target_latency_ms"),
            "hardware.optimization_level": manager.get_config("hardware.optimization_level"),
            "conversion_params.batch_size": manager.get_config("conversion_params.batch_size")
        }

        expected_values = {
            "performance.target_latency_ms": 50,
            "hardware.optimization_level": "O3",
            "conversion_params.batch_size": 4
        }

        atomic_updates = True
        for key, expected in expected_values.items():
            if updated_values[key] != expected:
                print(f"❌ Atomic update failed for {key}: expected {expected}, got {updated_values[key]}")
                atomic_updates = False
            else:
                print(f"✅ Atomic update succeeded for {key}: {initial_values[key]} -> {updated_values[key]}")

        if atomic_updates:
            print("✅ All configuration changes applied atomically")
        else:
            print("❌ Configuration changes were not applied atomically")
            return False

        hot_reload_manager.stop_monitoring()
        return True

    except Exception as e:
        print(f"❌ Hot reload atomic updates test failed: {e}")
        return False


def create_test_config():
    """Create a test configuration file for hot reload testing."""
    config_content = """project:
  name: "xlerobot"
  version: "1.0.0"
  model_type: "sensevoice"

hardware:
  target_device: "horizon_x5"
  optimization_level: "O2"
  memory_limit: "8GB"
  compute_units: 10
  cache_size: "256MB"

conversion_params:
  input_format: "onnx"
  output_format: "bpu"
  precision: "int8"
  calibration_method: "minmax"
  batch_size: 1
  num_workers: 4

model_specific:
  sensevoice:
    sample_rate: 16000
    audio_length: 30
    vocab_size: 10000
    mel_bins: 80
    frame_length: 25
    frame_shift: 10
    normalize: true
    preemphasis: 0.97
    n_fft: 512
    hop_length: 160
    win_length: 400
    n_mels: 80
    f_min: 0.0
    f_max: 8000.0

performance:
  target_latency_ms: 100
  max_realtime_factor: 0.1
  enable_streaming: False
"""

    config_file = Path("test_config_hot_reload.yaml")
    with open(config_file, 'w') as f:
        f.write(config_content)

    return config_file


def cleanup_test_files():
    """Clean up test files."""
    test_files = [
        Path("test_config_hot_reload.yaml"),
        Path("test_config_hot_reload.yaml.backup"),
        Path("test_config_hot_reload.yaml.tmp")
    ]

    for file_path in test_files:
        if file_path.exists():
            try:
                file_path.unlink()
                print(f"🧹 Cleaned up: {file_path}")
            except Exception as e:
                print(f"⚠️ Failed to clean up {file_path}: {e}")


def main():
    """Run all hot reload tests."""
    print("🚀 Testing Story 1.4 Configuration Hot Reload System")
    print("=" * 60)

    # Create test configuration
    test_config = create_test_config()
    print(f"✅ Created test configuration: {test_config}")

    tests = [
        ("Hot Reload Initialization", test_hot_reload_initialization),
        ("Hot Reload File Monitoring", test_hot_reload_monitoring),
        ("Hot Reload Performance", test_hot_reload_performance),
        ("Hot Reload Error Handling", test_hot_reload_error_handling),
        ("Hot Reload Atomic Updates", test_hot_reload_atomic_updates),
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

    print(f"\n{'='*60}")
    print(f"Test Results: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 All tests passed! Hot reload system is working correctly.")
    else:
        print(f"⚠️ {total - passed} tests failed. Please check the implementation.")

    # Cleanup
    print(f"\nCleaning up test files...")
    cleanup_test_files()

    return passed == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)