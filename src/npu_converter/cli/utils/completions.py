"""
CLI Auto-completion Utilities

This module provides auto-completion script generation for bash and zsh.
"""

import os
from pathlib import Path
from typing import List, Dict, Optional


def generate_bash_completion(command_name: str = "xlerobot") -> str:
    """
    Generate bash completion script.

    Args:
        command_name: Name of the command

    Returns:
        str: Bash completion script
    """
    script = f'''# Bash completion for {command_name}

_{command_name}_completion() {{
    local cur prev opts
    COMPREPLY=()
    cur="${{COMP_WORDS[COMP_CWORD]}}"
    prev="${{COMP_WORDS[COMP_CWORD-1]}}"
    opts="convert config info --version --help --quiet"

    if [[ ${{cur}} == -* ]] ; then
        COMPREPLY=( $(compgen -W "${{opts}}" -- ${{cur}}) )
        return 0
    fi

    case "${{prev}}" in
        convert)
            COMPREPLY=( $(compgen -W "-i --input -o --output -t --type -c --config --device --quantize --optimize --verbose --quiet --json --progress -h --help" -- ${{cur}}) )
            ;;
        config)
            COMPREPLY=( $(compgen -W "create validate watch --help" -- ${{cur}}) )
            ;;
        -i|--input|-c|--config)
            COMPREPLY=( $(compgen -A file -X "!*.onnx" -X "!*.yaml" -X "!*.yml" -- ${{cur}}) )
            ;;
        -o|--output)
            COMPREPLY=( $(compgen -A file -X "!*.bpu" -- ${{cur}}) )
            ;;
        -t|--type)
            COMPREPLY=( $(compgen -W "sensevoice vits_cantonese piper_vits" -- ${{cur}}) )
            ;;
        --device)
            COMPREPLY=( $(compgen -W "npu cpu gpu" -- ${{cur}}) )
            ;;
        *)
            COMPREPLY=( $(compgen -W "${{opts}}" -- ${{cur}}) )
            ;;
    esac
}}

complete -F _{command_name}_completion {command_name}
'''
    return script


def generate_zsh_completion(command_name: str = "xlerobot") -> str:
    """
    Generate zsh completion script.

    Args:
        command_name: Name of the command

    Returns:
        str: Zsh completion script
    """
    script = f'''#compdef {command_name}

_{command_name}() {{
    local -a commands
    commands=(
        'convert:转换AI模型到NPU格式'
        'config:配置管理工具'
        'info:显示项目信息'
        '--version:显示版本信息'
        '--help:显示帮助信息'
    )

    local -a convert_options
    convert_options=(
        '(-i --input)'{{-i,--input}}'[输入模型文件路径]:file:_files -g "*.onnx"'
        '(-o --output)'{{-o,--output}}'[输出模型文件路径或目录]:file:_files'
        '(-t --type)'{{-t,--type}}'[模型类型]:model_type:(sensevoice vits_cantonese piper_vits)'
        '(-c --config)'{{-c,--config}}'[配置文件路径]:file:_files -g "*.yaml(-.)"'
        '(--device)--device[目标设备类型]:device:(npu cpu gpu)'
        '(--quantize)--quantize[启用模型量化]'
        '(--optimize)--optimize[启用模型优化]'
        '(--verbose)--verbose[详细输出模式]'
        '(--quiet)--quiet[静默模式]'
        '(--json)--json[JSON格式输出]'
        '(--progress)--progress[显示详细进度信息]'
        '(-h --help)'{{-h,--help}}'[显示帮助信息]'
    )

    local -a config_options
    config_options=(
        'create:创建配置文件'
        'validate:验证配置文件'
        'watch:监控配置文件变化'
        '--help:显示帮助信息'
    )

    case $state in
        command)
            _describe 'command' commands
            ;;
        convert)
            _describe 'options' convert_options
            ;;
        config)
            _describe 'options' config_options
            ;;
        *)
            case $words[1] in
                convert)
                    _arguments -s -S $convert_options && ret=0
                    ;;
                config)
                    _arguments -s -S $config_options && ret=0
                    ;;
                *)
                    _arguments -s -S \\
                        '(--version)--version[显示版本信息]' \\
                        '(--help)--help[显示帮助信息]' \\
                        '1: :_guard "^-*" "command"' \\
                        '*:: :->command' && ret=0
                    ;;
            esac
            ;;
    esac

    return ret
}}

_{command_name} "$@"
'''
    return script


def install_bash_completion(script: str, command_name: str = "xlerobot") -> bool:
    """
    Install bash completion script.

    Args:
        script: Bash completion script content
        command_name: Name of the command

    Returns:
        bool: True if installation successful
    """
    try:
        # Get user's home directory
        home_dir = Path.home()
        completion_dir = home_dir / ".bash_completion.d"

        # Create completion directory if it doesn't exist
        completion_dir.mkdir(exist_ok=True)

        # Write completion script
        completion_file = completion_dir / f"{command_name}.bash"
        with open(completion_file, 'w') as f:
            f.write(script)

        # Add to .bashrc if not already present
        bashrc = home_dir / ".bashrc"
        if bashrc.exists():
            bashrc_content = bashrc.read_text()
            source_line = f'source "{completion_file}"'
            if source_line not in bashrc_content:
                with open(bashrc, 'a') as f:
                    f.write(f'\n# {command_name} completion\n{source_line}\n')

        return True

    except Exception:
        return False


def install_zsh_completion(script: str, command_name: str = "xlerobot") -> bool:
    """
    Install zsh completion script.

    Args:
        script: Zsh completion script content
        command_name: Name of the command

    Returns:
        bool: True if installation successful
    """
    try:
        # Get user's home directory
        home_dir = Path.home()
        completion_dir = home_dir / ".zsh/completions"

        # Create completion directory if it doesn't exist
        completion_dir.mkdir(parents=True, exist_ok=True)

        # Write completion script
        completion_file = completion_dir / f"_{command_name}"
        with open(completion_file, 'w') as f:
            f.write(script)

        return True

    except Exception:
        return False


def generate_completion_install_script(command_name: str = "xlerobot") -> str:
    """
    Generate script to install completions.

    Args:
        command_name: Name of the command

    Returns:
        str: Installation script
    """
    script = f'''#!/bin/bash
# {command_name} 自动补全安装脚本

set -e

COMMAND_NAME="{command_name}"
INSTALL_DIR="$HOME/.local/share/{command_name}"

echo "🚀 安装 {command_name} 自动补全..."

# 创建安装目录
mkdir -p "$INSTALL_DIR"

# 生成补全脚本
echo "📝 生成 bash 补全脚本..."
cat > "$INSTALL_DIR/bash-completion.sh" << 'EOF'
{bash_script}
EOF

echo "📝 生成 zsh 补全脚本..."
cat > "$INSTALL_DIR/zsh-completion.sh" << 'EOF'
{zsh_script}
EOF

# 检测 shell 并安装
if [[ -n "$BASH_VERSION" ]]; then
    echo "🐚 检测到 Bash shell"
    if install_bash_completion "$(cat "$INSTALL_DIR/bash-completion.sh")" "$COMMAND_NAME"; then
        echo "✅ Bash 补全安装成功"
        echo "💡 请运行: source ~/.bashrc 或重新打开终端"
    else
        echo "❌ Bash 补全安装失败"
    fi
elif [[ -n "$ZSH_VERSION" ]]; then
    echo "🐚 检测到 Zsh shell"
    if install_zsh_completion "$(cat "$INSTALL_DIR/zsh-completion.sh")" "$COMMAND_NAME"; then
        echo "✅ Zsh 补全安装成功"
        echo "💡 请运行: source ~/.zshrc 或重新打开终端"
    else
        echo "❌ Zsh 补全安装失败"
    fi
else
    echo "⚠️  未检测到支持的 shell (bash/zsh)"
    echo "💡 手动安装说明:"
    echo "   Bash: 将 $INSTALL_DIR/bash-completion.sh 内容添加到 ~/.bash_completion.d/"
    echo "   Zsh: 将 $INSTALL_DIR/zsh-completion.sh 复制到 ~/.zsh/completions/_{command_name}"
fi

echo "🎉 安装完成！"
echo "💡 使用 {command_name} --help 查看帮助信息"
echo "💡 输入 {command_name} 然后按 TAB 键测试自动补全"
'''.format(
        bash_script=generate_bash_completion(command_name),
        zsh_script=generate_zsh_completion(command_name)
    )

    return script


def get_completion_files() -> List[str]:
    """
    Get list of common completion file locations.

    Returns:
        List[str]: List of completion file paths
    """
    home = Path.home()
    return [
        str(home / ".bash_completion"),
        str(home / ".bash_completion.d" / "xlerobot.bash"),
        str(home / ".zsh" / "completions" / "_xlerobot"),
        str(home / ".local" / "share" / "bash-completion" / "completions" / "xlerobot"),
        "/etc/bash_completion.d/xlerobot",
        "/usr/share/bash-completion/completions/xlerobot",
        "/usr/share/zsh/site-functions/_xlerobot",
    ]


def is_completion_installed(command_name: str = "xlerobot") -> bool:
    """
    Check if completion is installed for the command.

    Args:
        command_name: Name of the command

    Returns:
        bool: True if completion is installed
    """
    completion_files = get_completion_files()

    for file_path in completion_files:
        if os.path.exists(file_path):
            try:
                content = Path(file_path).read_text()
                if command_name in content:
                    return True
            except Exception:
                continue

    return False