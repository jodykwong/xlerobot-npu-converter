#!/usr/bin/env python3
"""
XLeRobot NPU转换器主CLI工具

提供统一的命令行入口，整合配置管理、模型转换等功能。
Story 1.6 - 命令行界面开发的完整实现。
"""

import sys
import argparse
from pathlib import Path
from typing import List

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from npu_converter.cli.config_cli import main as config_main
from npu_converter.cli.commands.convert import ConvertCommand
from npu_converter.cli.commands.config import ConfigCommand
from npu_converter.cli.commands.status import StatusCommand

# ANSI颜色代码
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def print_banner():
    """打印程序横幅"""
    banner = f"""
{Colors.CYAN}{Colors.BOLD}
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║                    XLeRobot NPU转换器                        ║
║                  Configuration Management CLI                ║
║                                                              ║
║  版本: 1.0.0                                                ║
║  作者: XLeRobot Team                                        ║
║  支持: VITS-Cantonese, SenseVoice, Piper VITS               ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
{Colors.ENDC}
"""
    print(banner)

def print_version():
    """打印版本信息"""
    version_info = f"""
{Colors.GREEN}XLeRobot NPU转换器 CLI工具{Colors.ENDC}
{Colors.BLUE}版本: 1.0.0{Colors.ENDC}
{Colors.BLUE}Python版本: {sys.version}{Colors.ENDC}
{Colors.BLUE}支持平台: Linux, macOS, Windows{Colors.ENDC}
"""
    print(version_info)

def config_command(args):
    """配置管理命令"""
    # 转发到配置CLI工具
    sys.argv = ['xlerobot-config'] + args.args
    return config_main()

def convert_command(args):
    """模型转换命令 - Story 1.6 完整实现"""
    # 使用新的 ConvertCommand 实现
    convert_cmd = ConvertCommand()

    # 传递剩余参数给 convert 命令
    # 获取原始的 sys.argv 并过滤出 xlerobot convert 后的参数
    try:
        # 找到 'convert' 在 argv 中的位置
        convert_index = sys.argv.index('convert')
        # 获取 convert 后的所有参数
        convert_args = sys.argv[convert_index + 1:]

        return convert_cmd.run(convert_args)
    except ValueError:
        # 如果没有找到 'convert'，使用默认行为
        return convert_cmd.run()

def info_command(args):
    """显示项目信息"""
    print("📋 XLeRobot项目信息")
    print("=" * 50)

    print("\n🤖 支持的模型类型:")
    print("   • VITS-Cantonese: 粤语语音合成 (主要)")
    print("   • SenseVoice: 多语言语音识别")
    print("   • Piper VITS: 通用语音合成")

    print("\n🖥️  支持的硬件平台:")
    print("   • Horizon X5 NPU")
    print("   • NVIDIA GPU (计划支持)")
    print("   • 通用 CPU (开发模式)")

    print("\n📦 支持的格式:")
    print("   • 输入: ONNX")
    print("   • 输出: BPU (地平线NPU格式)")

    print("\n⚡ 优化功能:")
    print("   • INT8量化")
    print("   • 模型剪枝")
    print("   • 算子融合")
    print("   • 内存优化")

    print("\n📚 相关文档:")
    print("   • 配置管理指南: docs/configuration-management-guide.md")
    print("   • API参考文档: docs/api-reference.md")
    print("   • 使用示例: docs/examples/")

    print("\n🔗 GitHub: https://github.com/xlerobot/npu-converter")
    print("📧 联系: xlerobot@example.com")

def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        prog="xlerobot",
        description="XLeRobot NPU转换器 CLI工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  xlerobot config create vits_cantonese -o config.yaml
  xlerobot config validate config.yaml
  xlerobot config watch config.yaml
  xlerobot convert --input model.onnx --output model.bpu
  xlerobot info
        """
    )

    parser.add_argument('--version', action='store_true', help='显示版本信息')
    parser.add_argument('--quiet', '-q', action='store_true', help='静默模式')

    subparsers = parser.add_subparsers(dest='command', help='可用命令')

    # 配置管理命令
    config_parser = subparsers.add_parser('config', help='配置管理工具')
    config_parser.add_argument('args', nargs=argparse.REMAINDER,
                              help='配置管理命令参数')
    config_parser.set_defaults(func=config_command)

    # 模型转换命令
    convert_parser = subparsers.add_parser('convert', help='模型转换工具')
    convert_parser.add_argument('--input', '-i', help='输入模型文件')
    convert_parser.add_argument('--output', '-o', help='输出模型文件')
    convert_parser.add_argument('--config', '-c', help='配置文件路径')
    convert_parser.add_argument('--device', '-d', help='目标设备')
    convert_parser.set_defaults(func=convert_command)

    # 项目信息命令
    info_parser = subparsers.add_parser('info', help='显示项目信息')
    info_parser.set_defaults(func=info_command)

    # 解析参数
    args = parser.parse_args()

    # 显示横幅（除非在静默模式或显示版本）
    if not args.quiet and not args.version:
        print_banner()

    # 处理版本信息
    if args.version:
        print_version()
        return 0

    # 如果没有指定命令，显示帮助
    if not args.command:
        parser.print_help()
        return 0

    # 执行命令
    try:
        return args.func(args)
    except KeyboardInterrupt:
        if not args.quiet:
            print("\n👋 操作已取消")
        return 130
    except Exception as e:
        if not args.quiet:
            print(f"❌ 命令执行异常: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())