#!/usr/bin/env python3
"""
XLeRobot配置管理CLI工具

提供命令行界面用于配置文件管理，包括：
- 配置文件创建、验证、修改
- 模型配置模板生成
- 配置文件备份和恢复
- 配置热加载监控
"""

import sys
import os
import json
import yaml
import argparse
from pathlib import Path
from typing import Dict, Any, Optional, List

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from npu_converter.config import ConfigurationManager
from npu_converter.config.strategies import (
    VITSCantoneseConfigStrategy,
    SenseVoiceConfigStrategy,
    PiperVITSConfigStrategy
)
from npu_converter.core.exceptions.config_errors import (
    ConfigError,
    ConfigNotFoundError,
    ConfigLoadError,
    ConfigValidationError
)

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

def color_print(message: str, color: str = Colors.ENDC):
    """打印彩色消息"""
    print(f"{color}{message}{Colors.ENDC}")

def print_success(message: str):
    """打印成功消息"""
    color_print(f"✅ {message}", Colors.GREEN)

def print_error(message: str):
    """打印错误消息"""
    color_print(f"❌ {message}", Colors.FAIL)

def print_warning(message: str):
    """打印警告消息"""
    color_print(f"⚠️  {message}", Colors.WARNING)

def print_info(message: str):
    """打印信息消息"""
    color_print(f"ℹ️  {message}", Colors.BLUE)

def print_header(message: str):
    """打印标题消息"""
    color_print(f"\n🔧 {message}", Colors.HEADER + Colors.BOLD)

def create_config_command(args):
    """创建配置文件命令"""
    print_header("创建配置文件")

    model_type = args.model_type
    output_file = Path(args.output)

    if output_file.exists() and not args.force:
        print_error(f"配置文件 {output_file} 已存在，使用 --force 强制覆盖")
        return False

    # 选择配置策略
    strategy_map = {
        "vits_cantonese": VITSCantoneseConfigStrategy,
        "sensevoice": SenseVoiceConfigStrategy,
        "piper_vits": PiperVITSConfigStrategy
    }

    if model_type not in strategy_map:
        print_error(f"不支持的模型类型: {model_type}")
        print_info(f"支持的模型类型: {', '.join(strategy_map.keys())}")
        return False

    try:
        # 获取配置模板
        strategy = strategy_map[model_type]({})
        template = strategy.get_default_template()

        # 应用自定义参数
        if args.name:
            template["project"]["name"] = args.name
        if args.description:
            template["project"]["description"] = args.description
        if args.device:
            template["hardware"]["target_device"] = args.device
        if args.optimization:
            template["hardware"]["optimization_level"] = args.optimization
        if args.memory:
            template["hardware"]["memory_limit"] = args.memory

        # 直接保存YAML文件
        with open(output_file, 'w', encoding='utf-8') as f:
            yaml.dump(template, f, default_flow_style=False, indent=2, allow_unicode=True)

        print_success(f"配置文件已创建: {output_file}")
        print_info(f"模型类型: {model_type}")

        if args.show:
            show_config_content(output_file)

        return True

    except Exception as e:
        print_error(f"创建配置文件失败: {e}")
        return False

def validate_config_command(args):
    """验证配置文件命令"""
    print_header("验证配置文件")

    config_file = Path(args.config)

    if not config_file.exists():
        print_error(f"配置文件不存在: {config_file}")
        return False

    try:
        manager = ConfigurationManager(config_file)

        # 加载配置
        print_info("正在加载配置...")
        config = manager.load_config(fast_validation=False)

        # 验证配置
        print_info("正在验证配置...")
        is_valid = manager.validate_config()

        if is_valid:
            print_success("配置验证通过")

            # 显示配置摘要
            show_config_summary(manager)
        else:
            print_error("配置验证失败")

            # 显示详细错误
            errors = manager.get_validation_errors()
            if errors:
                print_header("验证错误详情")
                for error in errors:
                    print_error(f"{error.field_path}: {error.message}")
                    if error.suggestion:
                        print_warning(f"建议: {error.suggestion}")

        return is_valid

    except ConfigNotFoundError:
        print_error(f"配置文件未找到: {config_file}")
        return False
    except ConfigValidationError as e:
        print_error(f"配置验证失败: {e}")
        if hasattr(e, 'errors') and e.errors:
            for error in e.errors:
                print_error(f"  - {error}")
        return False
    except Exception as e:
        print_error(f"验证过程异常: {e}")
        return False

def show_config_command(args):
    """显示配置内容命令"""
    print_header("显示配置内容")

    config_file = Path(args.config)

    if not config_file.exists():
        print_error(f"配置文件不存在: {config_file}")
        return False

    try:
        manager = ConfigurationManager(config_file)
        config = manager.load_config()

        if args.format == "yaml":
            print(yaml.dump(config, default_flow_style=False, indent=2))
        elif args.format == "json":
            print(json.dumps(config, indent=2, ensure_ascii=False))
        else:
            # 显示摘要
            show_config_summary(manager)

        return True

    except Exception as e:
        print_error(f"显示配置失败: {e}")
        return False

def modify_config_command(args):
    """修改配置命令"""
    print_header("修改配置")

    config_file = Path(args.config)

    if not config_file.exists():
        print_error(f"配置文件不存在: {config_file}")
        return False

    try:
        manager = ConfigurationManager(config_file)
        manager.load_config()

        # 解析键值对
        modifications = {}
        for kv in args.set:
            if '=' not in kv:
                print_error(f"无效的键值对格式: {kv}")
                return False

            key, value = kv.split('=', 1)

            # 尝试解析值类型
            try:
                # 尝试解析为JSON
                parsed_value = json.loads(value)
            except json.JSONDecodeError:
                # 如果不是JSON，直接使用字符串
                parsed_value = value

            modifications[key] = parsed_value

        # 应用修改
        for key, value in modifications.items():
            manager.set_config(key, value)
            print_success(f"已设置 {key} = {value}")

        # 保存配置
        if args.save:
            manager.save_config()
            print_success("配置已保存")

        # 显示修改后的配置摘要
        if args.show:
            show_config_summary(manager)

        return True

    except Exception as e:
        print_error(f"修改配置失败: {e}")
        return False

def backup_config_command(args):
    """备份配置命令"""
    print_header("备份配置")

    config_file = Path(args.config)

    if not config_file.exists():
        print_error(f"配置文件不存在: {config_file}")
        return False

    try:
        manager = ConfigurationManager(config_file)
        manager.load_config()

        # 创建备份
        backup_name = args.name if args.name else None
        backup_path = manager.create_backup(backup_name)

        print_success(f"配置已备份到: {backup_path}")

        # 列出所有备份
        if args.list:
            list_backups_command(args)

        return True

    except Exception as e:
        print_error(f"备份配置失败: {e}")
        return False

def restore_config_command(args):
    """恢复配置命令"""
    print_header("恢复配置")

    backup_file = Path(args.backup)
    config_file = Path(args.config) if args.config else None

    if not backup_file.exists():
        print_error(f"备份文件不存在: {backup_file}")
        return False

    try:
        # 如果指定了目标配置文件，先备份当前配置
        if config_file and config_file.exists():
            manager = ConfigurationManager(config_file)
            manager.load_config()
            current_backup = manager.create_backup("before_restore")
            print_info(f"当前配置已备份到: {current_backup}")

        # 恢复配置
        manager = ConfigurationManager(config_file) if config_file else ConfigurationManager()
        success = manager.rollback_to_backup(str(backup_file))

        if success:
            print_success("配置恢复成功")

            if config_file:
                print_info(f"配置已恢复到: {config_file}")
        else:
            print_error("配置恢复失败")

        return success

    except Exception as e:
        print_error(f"恢复配置失败: {e}")
        return False

def list_backups_command(args):
    """列出备份命令"""
    print_header("配置备份列表")

    try:
        # 查找备份目录
        backup_dir = Path(".config_backups")
        if not backup_dir.exists():
            print_info("没有找到备份目录")
            return True

        # 查找备份文件
        config_name = Path(args.config).stem if args.config else None
        backup_files = []

        for backup_file in backup_dir.glob("*.yaml"):
            if config_name and config_name not in backup_file.stem:
                continue
            backup_files.append(backup_file)

        if not backup_files:
            print_info("没有找到备份文件")
            return True

        # 按修改时间排序
        backup_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)

        print(f"找到 {len(backup_files)} 个备份:")
        print()

        for i, backup_file in enumerate(backup_files, 1):
            file_size = backup_file.stat().st_size
            mtime = backup_file.stat().st_mtime

            import time
            time_str = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(mtime))

            print(f"{i:2d}. {backup_file.name}")
            print(f"    路径: {backup_file}")
            print(f"    时间: {time_str}")
            print(f"    大小: {file_size} 字节")
            print()

        return True

    except Exception as e:
        print_error(f"列出备份失败: {e}")
        return False

def watch_config_command(args):
    """监控配置文件变更命令"""
    print_header("监控配置文件变更")

    config_file = Path(args.config)

    if not config_file.exists():
        print_error(f"配置文件不存在: {config_file}")
        return False

    try:
        manager = ConfigurationManager(config_file)
        manager.load_config()

        # 设置变更回调
        def on_config_change(config_path, changes):
            print_info(f"检测到配置文件变更: {config_path}")
            print_info(f"变更内容: {changes}")

            # 验证新配置
            if manager.validate_config():
                print_success("新配置验证通过")
            else:
                print_warning("新配置验证失败")
                if args.auto_rollback:
                    print_info("正在自动回滚...")
                    manager.rollback()
                    print_success("已回滚到上一个有效配置")

        # 启用热加载
        manager.enable_hot_reload()
        manager.add_change_callback(on_config_change)

        print_success(f"开始监控配置文件: {config_file}")
        print_info("按 Ctrl+C 停止监控")

        # 保持运行
        try:
            import time
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print_info("\n正在停止监控...")
            manager.disable_hot_reload()
            print_success("监控已停止")

        return True

    except Exception as e:
        print_error(f"监控配置失败: {e}")
        return False

def show_config_summary(manager: ConfigurationManager):
    """显示配置摘要"""
    config = manager._config

    print_header("配置摘要")

    # 项目信息
    project = config.get("project", {})
    print(f"📋 项目名称: {project.get('name', 'Unknown')}")
    print(f"🤖 模型类型: {project.get('model_type', 'Unknown')}")
    print(f"🔢 版本: {project.get('version', 'Unknown')}")

    # 硬件配置
    hardware = config.get("hardware", {})
    print(f"🖥️  目标设备: {hardware.get('target_device', 'Unknown')}")
    print(f"⚡ 优化级别: {hardware.get('optimization_level', 'Unknown')}")
    print(f"💾 内存限制: {hardware.get('memory_limit', 'Unknown')}")

    # 转换参数
    conversion = config.get("conversion_params", {})
    print(f"📥 输入格式: {conversion.get('input_format', 'Unknown')}")
    print(f"📤 输出格式: {conversion.get('output_format', 'Unknown')}")
    print(f"🎯 精度: {conversion.get('precision', 'Unknown')}")

    # 性能配置
    performance = config.get("performance", {})
    if performance:
        print(f"⏱️  目标延迟: {performance.get('target_latency_ms', 'Unknown')}ms")
        print(f"🔄 实时因子: {performance.get('max_realtime_factor', 'Unknown')}")

def show_config_content(config_file: Path):
    """显示配置文件内容"""
    print_header("配置文件内容")

    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            content = f.read()
            print(content)
    except Exception as e:
        print_error(f"读取配置文件失败: {e}")

def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        prog="xlerobot-config",
        description="XLeRobot配置管理CLI工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例用法:
  %(prog)s create vits_cantonese -o config.yaml
  %(prog)s validate config.yaml
  %(prog)s show config.yaml --format json
  %(prog)s modify config.yaml --set hardware.optimization_level=O3
  %(prog)s backup config.yaml --name pre_optimization
  %(prog)s restore backup_config.yaml
  %(prog)s watch config.yaml
        """
    )

    subparsers = parser.add_subparsers(dest='command', help='可用命令')

    # 创建配置命令
    create_parser = subparsers.add_parser('create', help='创建配置文件')
    create_parser.add_argument('model_type', choices=['vits_cantonese', 'sensevoice', 'piper_vits'],
                              help='模型类型')
    create_parser.add_argument('-o', '--output', required=True, help='输出配置文件路径')
    create_parser.add_argument('--name', help='项目名称')
    create_parser.add_argument('--description', help='项目描述')
    create_parser.add_argument('--device', help='目标设备')
    create_parser.add_argument('--optimization', help='优化级别')
    create_parser.add_argument('--memory', help='内存限制')
    create_parser.add_argument('--force', action='store_true', help='强制覆盖已存在的文件')
    create_parser.add_argument('--show', action='store_true', help='显示创建的配置内容')
    create_parser.set_defaults(func=create_config_command)

    # 验证配置命令
    validate_parser = subparsers.add_parser('validate', help='验证配置文件')
    validate_parser.add_argument('config', help='配置文件路径')
    validate_parser.set_defaults(func=validate_config_command)

    # 显示配置命令
    show_parser = subparsers.add_parser('show', help='显示配置内容')
    show_parser.add_argument('config', help='配置文件路径')
    show_parser.add_argument('--format', choices=['yaml', 'json', 'summary'], default='summary',
                             help='显示格式')
    show_parser.set_defaults(func=show_config_command)

    # 修改配置命令
    modify_parser = subparsers.add_parser('modify', help='修改配置参数')
    modify_parser.add_argument('config', help='配置文件路径')
    modify_parser.add_argument('--set', action='append', required=True,
                              help='设置键值对 (key=value)', metavar='KEY=VALUE')
    modify_parser.add_argument('--save', action='store_true', help='保存修改到文件')
    modify_parser.add_argument('--show', action='store_true', help='显示修改后的配置摘要')
    modify_parser.set_defaults(func=modify_config_command)

    # 备份配置命令
    backup_parser = subparsers.add_parser('backup', help='备份配置文件')
    backup_parser.add_argument('config', help='配置文件路径')
    backup_parser.add_argument('--name', help='备份名称')
    backup_parser.add_argument('--list', action='store_true', help='列出所有备份')
    backup_parser.set_defaults(func=backup_config_command)

    # 恢复配置命令
    restore_parser = subparsers.add_parser('restore', help='恢复配置文件')
    restore_parser.add_argument('backup', help='备份文件路径')
    restore_parser.add_argument('--config', help='目标配置文件路径')
    restore_parser.set_defaults(func=restore_config_command)

    # 列出备份命令
    list_parser = subparsers.add_parser('list-backups', help='列出配置备份')
    list_parser.add_argument('--config', help='配置文件路径')
    list_parser.set_defaults(func=list_backups_command)

    # 监控配置命令
    watch_parser = subparsers.add_parser('watch', help='监控配置文件变更')
    watch_parser.add_argument('config', help='配置文件路径')
    watch_parser.add_argument('--auto-rollback', action='store_true', help='自动回滚无效配置')
    watch_parser.set_defaults(func=watch_config_command)

    # 解析参数
    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 1

    # 执行命令
    try:
        success = args.func(args)
        return 0 if success else 1
    except KeyboardInterrupt:
        print_info("\n操作已取消")
        return 130
    except Exception as e:
        print_error(f"命令执行异常: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())