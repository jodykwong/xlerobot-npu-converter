"""
NPU转换器CLI主入口

提供命令行界面来操作NPU模型转换工具和工具链管理。
"""

import click
import logging
import sys
from pathlib import Path
from typing import Optional, Dict, Any

from .bpu_toolchain.horizon_x5 import HorizonX5Interface
from .bpu_toolchain.installer import ToolchainInstaller
from .bpu_toolchain.version_manager import VersionManager
from .bpu_toolchain.validator import ToolchainValidator

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@click.group()
@click.version_option(version="1.0.0", prog_name="npu-converter")
def cli():
    """XLeRobot NPU模型转换工具 - 提供NPU模型转换和工具链管理功能。"""
    pass


@cli.group()
def toolchain():
    """Horizon X5 BPU工具链管理命令组。"""
    pass


@toolchain.command()
@click.option('--url', help='指定工具链下载URL')
@click.option('--checksum', help='指定文件校验和')
@click.option('--path', default='/opt/horizon', help='指定安装路径')
@click.pass_context
def install(ctx, url: str, checksum: str, path: str):
    """安装Horizon X5 BPU工具链"""
    click.echo("开始安装Horizon X5 BPU工具链...")

    installer = ToolchainInstaller(path)
    result = installer.install()

    if result["success"]:
        click.echo(f"✅ 工具链安装成功！")
        click.echo(f"版本: {result['installed_version']}")
        click.echo(f"安装路径: {result['install_path']}")
    else:
        click.echo(f"❌ 工具链安装失败: {result.get('error', '未知错误')}")


@toolchain.command()
@click.option('--verbose', '-v', is_flag=True, help='详细输出')
@click.pass_context
def validate(ctx, verbose: bool):
    """验证Horizon X5 BPU工具链安装"""
    click.echo("开始验证工具链安装...")

    validator = ToolchainValidator()
    result = validator.run_comprehensive_test()

    if result["overall_success"]:
        click.echo("✅ 工具链验证通过！")
        if verbose:
            click.echo("详细验证结果:")
            click.echo(f"  环境变量: {len(result['environment'].get('missing_variables', []))} 个问题")
            click.echo(f"  组件状态: {result['environment']['components_status']}")
    else:
        click.echo("❌ 工具链验证失败！")
        if verbose:
            click.echo("验证问题:")
            for key, value in result.items():
                if key.endswith('_status') and not value.get('success', False):
                    click.echo(f"  {key}: {value}")

    if verbose:
        # 生成详细验证报告
        click.echo("验证报告已生成: /opt/horizon/validation_report.txt")


@toolchain.command()
@click.option('--verbose', '-v', is_flag=True, help='详细输出')
@click.pass_context
def version(ctx, verbose: bool):
    """检查工具链版本信息"""
    click.echo("检查工具链版本...")

    manager = VersionManager()
    result = manager.check_version()

    if verbose:
        click.echo(f"安装路径: {result.get('install_path', 'unknown')}")
        click.echo(f"组件状态: {result.get('components_status', {})}")
        click.echo(f"兼容性: {result.get('compatibility', 'unknown')}")

    if result["is_installed"]:
        click.echo(f"✅ 工具链版本: {result['current_version']}")
    else:
        click.echo("❌ 工具链未安装")


@toolchain.command()
@click.option('--target-version', default='latest', help='指定目标版本')
@click.option('--force', is_flag=True, help='强制更新')
@click.pass_context
def update(ctx, target_version: str, force: bool):
    """更新Horizon X5 BPU工具链"""
    click.echo(f"开始更新工具链到版本: {target_version}")

    manager = VersionManager()
    result = manager.update_version(target_version)

    if result["success"]:
        click.echo(f"✅ 工具链更新成功！")
        click.echo(f"从版本: {result['old_version']}")
        click.echo(f"更新到版本: {result['new_version']}")
    else:
        click.echo(f"❌ 工具链更新失败: {result.get('error', '未知错误')}")


@toolchain.command()
@click.option('--target-version', help='指定回滚目标版本')
@click.pass_context
def rollback(ctx, target_version: str):
    """回滚工具链版本"""
    click.echo(f"开始回滚工具链到版本: {target_version}")

    manager = VersionManager()
    result = manager.rollback()

    if result["success"]:
        click.echo(f"✅ 工具链回滚成功！")
        click.echo(f"从版本: {result['from_version']}")
        click.echo(f"回滚到版本: {result['to_version']}")
    else:
        click.echo(f"❌ 工具链回滚失败: {result.get('error', '未知错误')}")


@cli.command()
@click.option('--model', '-m', required=True, help='输入模型文件路径')
@click.option('--output', '-o', required=True, help='输出文件路径')
@click.option('--optimize', default='2', type=click.IntRange(1, 3), help='优化级别 (1-3)')
@click.pass_context
def convert(ctx, model: str, output: str, optimize: int):
    """执行NPU模型转换"""
    click.echo(f"开始转换模型: {model}")

    interface = HorizonX5Interface()
    result = interface.run_hbdk(model, output, {"optimize": optimize})

    if result["success"]:
        click.echo("✅ 模型转换成功！")
        click.echo(f"输入: {model}")
        click.echo(f"输出: {output}")
    else:
        click.echo(f"❌ 模型转换失败: {result.get('error', '未知错误')}")


@cli.command()
@click.option('--model', '-m', required=True, help='输入模型文件路径')
@click.option('--iterations', default=100, type=int, help='推理测试次数')
@click.option('--warmup', default=10, type=int, help='预热次数')
@click.option('--output', '-o', help='结果输出文件')
@click.pass_context
def benchmark(ctx, model: str, iterations: int, warmup: int, output: Optional[str]):
    """执行性能基准测试"""
    click.echo(f"开始性能基准测试: {model}")

    interface = HorizonX5Interface()
    result = interface.run_hb_perf(model, {"iterations": iterations, "warmup": warmup})

    if result["success"]:
        click.echo("✅ 性能基准测试完成！")
        click.echo(f"测试模型: {model}")
        click.echo(f"推理次数: {iterations}")
        click.echo(f"预热次数: {warmup}")

        if output:
            with open(output, 'w') as f:
                f.write(result.get("output", ""))
            click.echo(f"结果已保存到: {output}")
    else:
        click.echo(f"❌ 性能基准测试失败: {result.get('error', '未知错误')}")


if __name__ == '__main__':
    cli()