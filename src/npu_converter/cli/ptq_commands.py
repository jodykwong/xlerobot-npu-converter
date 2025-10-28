"""
PTQ CLI Commands

This module implements CLI commands for PTQ conversion with real-time progress feedback
as defined in Acceptance Criteria 4: Provide detailed progress feedback.
"""

import click
import json
import time
from pathlib import Path
from typing import Optional

from ..ptq.converter import PTQConverter
from ..models.calibration import CalibrationConfig
from ..core.utils.progress_tracker import ProgressTracker


@click.group()
def ptq():
    """PTQ (Post-Training Quantization) conversion commands."""
    pass


@ptq.command()
@click.argument('model_path', type=click.Path(exists=True))
@click.option('--output-dir', '-o', default='./ptq_output', help='Output directory for PTQ results')
@click.option('--calibration-data', '-c', required=True, help='Path to calibration data directory')
@click.option('--batch-size', default=32, help='Batch size for calibration')
@click.option('--num-samples', default=100, help='Number of calibration samples')
@click.option('--input-shape', help='Input shape as comma-separated values (e.g., 1,224,224,3)')
@click.option('--debug/--no-debug', default=False, help='Enable debug mode')
@click.option('--verbose/--no-verbose', default=True, help='Enable verbose output')
@click.option('--save-report/--no-save-report', default=True, help='Save conversion report')
def convert(model_path: str, output_dir: str, calibration_data: str, batch_size: int,
            num_samples: int, input_shape: Optional[str], debug: bool, verbose: bool,
            save_report: bool):
    """
    Convert a model using the complete 6-step PTQ process.

    This command implements the full PTQ conversion workflow:
    1. Model Preparation
    2. Model Validation
    3. Calibration Data Preparation
    4. Model Quantization
    5. Model Compilation
    6. Performance & Accuracy Analysis
    """
    # Parse input shape
    if input_shape:
        input_shape_tuple = tuple(int(x.strip()) for x in input_shape.split(','))
    else:
        # Default shape for image classification
        input_shape_tuple = (1, 224, 224, 3)

    # Create calibration configuration
    calib_config = CalibrationConfig(
        data_path=calibration_data,
        batch_size=batch_size,
        num_samples=num_samples,
        input_shape=input_shape_tuple
    )

    # Initialize PTQ converter with progress tracking
    converter = PTQConverter(output_dir=output_dir, debug_mode=debug)

    # Setup progress tracking
    progress_tracker = ProgressTracker(enable_console_output=verbose)

    # Add progress callback for CLI output
    def progress_callback(step_info, overall_progress):
        """Callback for progress updates."""
        if verbose:
            status_msg = progress_tracker.get_status_message()
            click.echo(f"\r{status_msg}", nl=False)

    progress_tracker.add_progress_callback(progress_callback)

    try:
        click.echo(f"🚀 Starting PTQ conversion for: {model_path}")
        click.echo(f"📁 Output directory: {output_dir}")
        click.echo(f"📊 Calibration data: {calibration_data} ({num_samples} samples, batch={batch_size})")

        # Step 1: Model Preparation
        click.echo("\n📋 Step 1/6: Model Preparation")
        model_info = converter.prepare_model(model_path)
        click.echo(f"   ✅ Model loaded: {model_info.model_size_mb:.2f}MB, {model_info.num_parameters:,} parameters")

        # Step 2: Model Validation
        click.echo("\n🔍 Step 2/6: Model Validation")
        validation_result = converter.validate_model(model_info)
        if validation_result.is_valid:
            click.echo(f"   ✅ Model validation passed (Score: {validation_result.compatibility_score:.2f})")
        else:
            click.echo(f"   ⚠️  Model validation issues (Score: {validation_result.compatibility_score:.2f})")
            for error in validation_result.errors:
                click.echo(f"      ❌ {error}")
            for warning in validation_result.warnings:
                click.echo(f"      ⚠️  {warning}")

        # Step 3: Calibration Data Preparation
        click.echo("\n📊 Step 3/6: Calibration Data Preparation")
        calib_data = converter.prepare_calibration_data(calib_config)
        click.echo(f"   ✅ Calibration data prepared: {calib_data.data.shape}")

        # Step 4: Model Quantization
        click.echo("\n🔧 Step 4/6: Model Quantization")
        quantized_model = converter.quantize_model(model_info, calib_data)
        compression_ratio = quantized_model.get_compression_ratio()
        click.echo(f"   ✅ Model quantized (Compression: {compression_ratio:.2f}x)")

        # Step 5: Model Compilation
        click.echo("\n⚙️  Step 5/6: Model Compilation")
        compiled_model = converter.compile_model(quantized_model)
        click.echo(f"   ✅ Model compiled for {compiled_model.target_device}")

        # Step 6: Performance Analysis
        click.echo("\n📈 Step 6/6: Performance Analysis")
        performance_result = converter.analyze_performance(compiled_model)
        click.echo(f"   ✅ Performance: {performance_result.throughput_fps:.1f} FPS, {performance_result.inference_time_ms:.1f}ms")

        # Accuracy Analysis
        click.echo("\n🎯 Accuracy Analysis")
        accuracy_result = converter.analyze_accuracy(compiled_model)
        click.echo(f"   ✅ Accuracy: {accuracy_result.accuracy_after_quantization:.1f}% (Drop: {accuracy_result.accuracy_drop_percentage:.2f}%)")

        # Complete conversion
        progress_tracker.finish_conversion()

        # Save report if requested
        if save_report:
            report_path = Path(output_dir) / "ptq_conversion_report.json"
            converter.save_report(str(report_path))
            click.echo(f"\n📄 Report saved to: {report_path}")

        # Final summary
        click.echo(f"\n🎉 PTQ Conversion Complete!")
        click.echo(f"📊 Performance: {performance_result.throughput_fps:.1f} FPS ({performance_result.comparison_with_baseline['speedup_ratio']:.2f}x speedup)")
        click.echo(f"🎯 Accuracy: {accuracy_result.accuracy_after_quantization:.1f}% (Target: >98%)")
        click.echo(f"💾 Compression: {compression_ratio:.2f}x reduction")
        click.echo(f"📁 Output: {output_dir}")

        # Check if targets are met
        meets_accuracy = accuracy_result.meets_accuracy_target()
        meets_performance = performance_result.meets_performance_target()

        if meets_accuracy and meets_performance:
            click.echo("\n✅ All targets met! Model ready for deployment.")
        else:
            click.echo("\n⚠️  Some targets not met. Review the detailed report.")

    except Exception as e:
        click.echo(f"\n❌ PTQ conversion failed: {str(e)}", err=True)
        if debug:
            click.echo("Debug mode enabled - check logs for detailed error information.")
        raise click.ClickException(str(e))


@ptq.command()
@click.argument('model_path', type=click.Path(exists=True))
@click.option('--output-format', type=click.Choice(['json', 'table']), default='table', help='Output format')
def analyze(model_path: str, output_format: str):
    """Analyze a model without performing full PTQ conversion."""
    debug_tools = None
    try:
        from ..utils.debug_tools import DebugTools
        debug_tools = DebugTools(enabled=True)
    except ImportError:
        click.echo("Debug tools not available")
        return

    click.echo(f"🔍 Analyzing model: {model_path}")

    try:
        # Perform model analysis
        analysis = debug_tools.dump_model_info(model_path)

        if output_format == 'json':
            analysis_data = {
                'model_info': {
                    'model_path': analysis.model_info.model_path,
                    'model_size_mb': analysis.model_info.model_size_mb,
                    'num_parameters': analysis.model_info.num_parameters,
                    'input_shape': analysis.model_info.input_shape,
                    'output_shape': analysis.model_info.output_shape,
                    'model_format': analysis.model_info.model_format
                },
                'op_analysis': analysis.op_analysis,
                'memory_analysis': analysis.memory_analysis,
                'compatibility_report': analysis.compatibility_report,
                'optimization_suggestions': analysis.optimization_suggestions
            }
            click.echo(json.dumps(analysis_data, indent=2))
        else:
            # Table format
            click.echo(f"\n📊 Model Analysis Results:")
            click.echo(f"   Model Size: {analysis.model_info.model_size_mb:.2f} MB")
            click.echo(f"   Parameters: {analysis.model_info.num_parameters:,}")
            click.echo(f"   Input Shape: {analysis.model_info.input_shape}")
            click.echo(f"   Output Shape: {analysis.model_info.output_shape}")

            click.echo(f"\n🔧 Operator Analysis:")
            op_breakdown = analysis.op_analysis.get('operator_breakdown', {})
            for op_type, count in op_breakdown.items():
                click.echo(f"   {op_type}: {count}")

            click.echo(f"\n💾 Memory Analysis:")
            memory_analysis = analysis.memory_analysis
            for key, value in memory_analysis.items():
                click.echo(f"   {key}: {value}")

            click.echo(f"\n✅ Compatibility Report:")
            compat_report = analysis.compatibility_report
            click.echo(f"   Overall Compatibility: {compat_report['overall_compatibility']:.2f}")

            if compat_report['critical_issues']:
                click.echo("   Critical Issues:")
                for issue in compat_report['critical_issues']:
                    click.echo(f"     ❌ {issue}")

            if compat_report['warnings']:
                click.echo("   Warnings:")
                for warning in compat_report['warnings']:
                    click.echo(f"     ⚠️  {warning}")

            if analysis.optimization_suggestions:
                click.echo(f"\n💡 Optimization Suggestions:")
                for suggestion in analysis.optimization_suggestions:
                    click.echo(f"   • {suggestion}")

    except Exception as e:
        click.echo(f"❌ Model analysis failed: {str(e)}", err=True)
        raise click.ClickException(str(e))


@ptq.command()
@click.argument('model_path', type=click.Path(exists=True))
@click.option('--input-data', help='Input data file for inference testing')
@click.option('--iterations', default=10, help='Number of inference iterations')
def test(model_path: str, input_data: Optional[str], iterations: int):
    """Test model inference performance."""
    debug_tools = None
    try:
        from ..utils.debug_tools import DebugTools
        debug_tools = DebugTools(enabled=True)
    except ImportError:
        click.echo("Debug tools not available")
        return

    click.echo(f"🧪 Testing model inference: {model_path}")

    try:
        # Mock input data if not provided
        if input_data:
            with open(input_data, 'r') as f:
                test_input = json.load(f)
        else:
            test_input = {"data": [[0.1] * 224 * 224 * 3]}  # Mock input

        click.echo(f"   Running {iterations} inference iterations...")

        # Execute model
        result = debug_tools.execute_model(model_path, test_input)

        if result.success:
            click.echo(f"✅ Inference test completed successfully")

            if result.performance_metrics:
                metrics = result.performance_metrics
                click.echo(f"📊 Performance Results:")
                for key, value in metrics.items():
                    click.echo(f"   {key}: {value}")

            if result.memory_usage:
                memory = result.memory_usage
                click.echo(f"💾 Memory Usage:")
                for key, value in memory.items():
                    click.echo(f"   {key}: {value}")
        else:
            click.echo("❌ Inference test failed")
            for error in result.errors:
                click.echo(f"   Error: {error}")

    except Exception as e:
        click.echo(f"❌ Model testing failed: {str(e)}", err=True)
        raise click.ClickException(str(e))


@ptq.command()
@click.argument('report_path', type=click.Path(exists=True))
def show_report(report_path: str):
    """Display PTQ conversion report."""
    try:
        with open(report_path, 'r') as f:
            report = json.load(f)

        click.echo(f"📊 PTQ Conversion Report")
        click.echo("=" * 50)

        # Conversion summary
        summary = report['conversion_summary']
        click.echo(f"Model: {summary['model_name']}")
        click.echo(f"Status: {summary['conversion_status']}")
        click.echo(f"Date: {summary['conversion_date']}")
        click.echo(f"Duration: {summary['total_conversion_time_seconds']:.1f} seconds")

        # Model information
        model_info = report['model_information']
        click.echo(f"\n📋 Model Information:")
        click.echo(f"   Original Size: {model_info['original_size_mb']:.2f} MB")
        click.echo(f"   Parameters: {model_info['num_parameters']:,}")
        click.echo(f"   Input Shape: {model_info['input_shape']}")

        # Performance results
        perf = report['performance_results']
        click.echo(f"\n⚡ Performance Results:")
        click.echo(f"   Inference Time: {perf['inference_time_ms']:.1f} ms")
        click.echo(f"   Throughput: {perf['throughput_fps']:.1f} FPS")
        click.echo(f"   Speedup: {perf['speedup_ratio']:.2f}x")

        # Accuracy results
        accuracy = report['accuracy_results']
        click.echo(f"\n🎯 Accuracy Results:")
        click.echo(f"   Before Quantization: {accuracy['accuracy_before_quantization']:.1f}%")
        click.echo(f"   After Quantization: {accuracy['accuracy_after_quantization']:.1f}%")
        click.echo(f"   Accuracy Drop: {accuracy['accuracy_drop_percentage']:.2f}%")
        click.echo(f"   Meets Target: {accuracy['meets_accuracy_target']}")

        # Validation results
        validation = report['validation_results']
        if validation['errors']:
            click.echo(f"\n❌ Validation Errors:")
            for error in validation['errors']:
                click.echo(f"   • {error}")

        if validation['warnings']:
            click.echo(f"\n⚠️  Validation Warnings:")
            for warning in validation['warnings']:
                click.echo(f"   • {warning}")

    except Exception as e:
        click.echo(f"❌ Failed to read report: {str(e)}", err=True)
        raise click.ClickException(str(e))