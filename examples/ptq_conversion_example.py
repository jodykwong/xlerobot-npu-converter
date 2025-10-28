#!/usr/bin/env python3
"""
PTQ Conversion Example

Demonstrates the complete PTQ conversion workflow with official Horizon X5 tools.
This example shows how to use the PTQ converter to convert models and generate reports.
"""

import sys
import os
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from npu_converter.ptq.converter import PTQConverter
from npu_converter.models.calibration import CalibrationConfig
from npu_converter.reports.report_generator import PTQReportGenerator


def main():
    """Main example function."""
    print("🚀 Horizon X5 PTQ Conversion Example")
    print("=" * 50)

    # Example model path (replace with actual model)
    model_path = "examples/test_model.onnx"

    # Example calibration data path
    calibration_data_path = "examples/calibration_data"

    # Create output directory
    output_dir = "ptq_output"
    os.makedirs(output_dir, exist_ok=True)

    # Initialize PTQ converter
    print(f"\n📁 Initializing PTQ Converter...")
    converter = PTQConverter(output_dir=output_dir, debug_mode=True)

    # Create calibration configuration
    print(f"📊 Creating calibration configuration...")
    calib_config = CalibrationConfig(
        data_path=calibration_data_path,
        batch_size=16,
        num_samples=100,
        input_shape=(1, 224, 224, 3)
    )

    try:
        # Step 1: Model Preparation
        print(f"\n🔧 Step 1: Model Preparation")
        print(f"   Loading model: {model_path}")

        # Create a mock model file for demonstration
        mock_model_path = Path(output_dir) / "test_model.onnx"
        with open(mock_model_path, 'w') as f:
            f.write("mock_onnx_model_data")

        model_info = converter.prepare_model(str(mock_model_path))
        print(f"   ✅ Model prepared: {model_info.model_size_mb:.2f}MB")

        # Step 2: Model Validation
        print(f"\n🔍 Step 2: Model Validation")
        validation_result = converter.validate_model(model_info)
        print(f"   ✅ Validation completed: {validation_result.compatibility_score:.2f} compatibility")

        # Step 3: Calibration Data Preparation
        print(f"\n📊 Step 3: Calibration Data Preparation")

        # Create mock calibration data directory
        calib_dir = Path(calibration_data_path)
        calib_dir.mkdir(parents=True, exist_ok=True)

        calib_data = converter.prepare_calibration_data(calib_config)
        print(f"   ✅ Calibration data prepared: {calib_data.data.shape}")

        # Step 4: Model Quantization
        print(f"\n⚡ Step 4: Model Quantization")
        quantized_model = converter.quantize_model(model_info, calib_data)
        print(f"   ✅ Model quantized: {quantized_model.get_compression_ratio():.2f}x compression")

        # Step 5: Model Compilation
        print(f"\n⚙️  Step 5: Model Compilation")
        compiled_model = converter.compile_model(quantized_model)
        print(f"   ✅ Model compiled for {compiled_model.target_device}")

        # Step 6: Performance Analysis
        print(f"\n📈 Step 6: Performance Analysis")
        performance_result = converter.analyze_performance(compiled_model)
        print(f"   ✅ Performance: {performance_result.throughput_fps:.1f} FPS")

        # Step 7: Accuracy Analysis
        print(f"\n🎯 Step 7: Accuracy Analysis")
        accuracy_result = converter.analyze_accuracy(compiled_model)
        print(f"   ✅ Accuracy: {accuracy_result.accuracy_after_quantization:.1f}%")

        # Generate comprehensive report
        print(f"\n📄 Generating Conversion Report...")
        report_generator = PTQReportGenerator(output_dir=output_dir)

        report = report_generator.generate_comprehensive_report(
            converter=converter,
            model_info=model_info,
            validation_result=validation_result,
            calib_data=calib_data,
            quantized_model=quantized_model,
            compiled_model=compiled_model,
            performance_result=performance_result,
            accuracy_result=accuracy_result,
            format_type="json"
        )

        # Save reports in multiple formats
        json_path = report_generator.save_report(report, format_type="json")
        html_path = report_generator.save_report(report, format_type="html")
        md_path = report_generator.save_report(report, format_type="markdown")

        # Save converter's built-in report
        converter.save_report()

        print(f"\n🎉 PTQ Conversion Complete!")
        print(f"📊 Performance: {performance_result.throughput_fps:.1f} FPS ({performance_result.comparison_with_baseline['speedup_ratio']:.2f}x speedup)")
        print(f"🎯 Accuracy: {accuracy_result.accuracy_after_quantization:.1f}% (Target: >98%)")
        print(f"💾 Compression: {quantized_model.get_compression_ratio():.2f}x reduction")
        print(f"📁 Output: {output_dir}")
        print(f"\n📄 Reports Generated:")
        print(f"   • JSON: {json_path}")
        print(f"   • HTML: {html_path}")
        print(f"   • Markdown: {md_path}")
        print(f"   • Converter Report: {output_dir}/ptq_conversion_report.json")

        # Check if targets are met
        meets_accuracy = accuracy_result.meets_accuracy_target()
        meets_performance = performance_result.meets_performance_target()

        if meets_accuracy and meets_performance:
            print(f"\n✅ All targets met! Model ready for deployment.")
        else:
            print(f"\n⚠️  Some targets not met. Review the detailed reports.")

    except Exception as e:
        print(f"\n❌ PTQ conversion failed: {str(e)}")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())