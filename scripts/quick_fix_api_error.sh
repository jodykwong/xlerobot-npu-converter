#!/bin/bash

# =============================================================================
# BMM工作流程API Error快速修复脚本
# 用途: 防止 "Cannot read properties of undefined (reading 'map')" 错误
# =============================================================================

set -e  # 出错时退出

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 打印标题
print_header() {
    echo -e "${BLUE}=================================================================${NC}"
    echo -e "${BLUE}  BMM工作流程 API Error 快速修复工具${NC}"
    echo -e "${BLUE}=================================================================${NC}"
    echo ""
}

# 打印错误信息
print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# 打印成功信息
print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

# 打印警告信息
print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

# 打印信息
print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# 检查依赖
check_dependencies() {
    print_info "检查依赖..."

    if ! command -v python3 &> /dev/null; then
        print_error "Python3 未安装"
        exit 1
    fi

    if [ ! -f "scripts/safe_bmm_file_handler.py" ]; then
        print_error "安全文件处理器不存在: scripts/safe_bmm_file_handler.py"
        exit 1
    fi

    print_success "依赖检查通过"
    echo ""
}

# 备份文件
backup_file() {
    local file_path=$1
    local timestamp=$(date +%Y%m%d_%H%M%S)
    local backup_path="${file_path}.backup.${timestamp}"

    if [ -f "$file_path" ]; then
        cp "$file_path" "$backup_path"
        print_success "文件已备份到: $backup_path"
        echo "$backup_path"
    else
        print_warning "文件不存在: $file_path"
        echo ""
    fi
}

# 更新故事状态
update_story_status() {
    local story_id=$1
    local file_path="docs/stories/${story_id}.md"

    print_info "更新故事状态: $story_id"

    # 检查文件是否存在
    if [ ! -f "$file_path" ]; then
        print_error "文件不存在: $file_path"
        return 1
    fi

    # 备份文件
    backup_path=$(backup_file "$file_path")
    echo ""

    # 使用Python安全工具更新
    print_info "使用安全文件处理器更新..."
    python3 scripts/safe_bmm_file_handler.py

    # 验证更新
    echo ""
    print_info "验证更新结果..."
    if grep -q "Phase 2.*完成" "$file_path"; then
        print_success "更新验证成功！"
        return 0
    else
        print_warning "更新可能未完全成功，请检查文件内容"
        return 1
    fi
}

# 显示使用说明
show_usage() {
    echo "用法:"
    echo "  $0 [选项]"
    echo ""
    echo "选项:"
    echo "  -h, --help          显示帮助信息"
    echo "  -u, --update <id>   更新指定故事ID的状态 (例如: story-3.1)"
    echo "  -b, --backup <file> 备份指定文件"
    echo "  -c, --check         仅检查依赖，不执行操作"
    echo ""
    echo "示例:"
    echo "  $0 --update story-3.1      # 更新story-3.1的状态"
    echo "  $0 --backup docs/stories/story-3.1.md  # 备份文件"
    echo "  $0 --check                 # 仅检查依赖"
    echo ""
}

# 交互式模式
interactive_mode() {
    print_info "启动交互式模式..."
    echo ""

    PS3="请选择操作: "
    options=("更新故事状态" "备份文件" "检查依赖" "查看FAQ" "退出")

    select opt in "${options[@]}"
    do
        case $opt in
            "更新故事状态")
                read -p "请输入故事ID (例如: story-3.1): " story_id
                update_story_status "$story_id"
                break
                ;;
            "备份文件")
                read -p "请输入文件路径: " file_path
                backup_file "$file_path"
                break
                ;;
            "检查依赖")
                check_dependencies
                break
                ;;
            "查看FAQ")
                if [ -f "scripts/API_ERROR_FAQ.md" ]; then
                    cat scripts/API_ERROR_FAQ.md
                else
                    print_error "FAQ文件不存在"
                fi
                break
                ;;
            "退出")
                print_info "退出"
                exit 0
                ;;
            *)
                print_warning "无效选择"
                ;;
        esac
    done
}

# 主函数
main() {
    print_header

    # 检查是否在正确目录
    if [ ! -f "README.md" ] || [ ! -d "docs" ]; then
        print_error "请在项目根目录 (/home/sunrise/xlerobot) 运行此脚本"
        exit 1
    fi

    # 解析命令行参数
    case "${1:-}" in
        -h|--help)
            show_usage
            exit 0
            ;;
        -u|--update)
            if [ -z "$2" ]; then
                print_error "请提供故事ID"
                show_usage
                exit 1
            fi
            check_dependencies
            update_story_status "$2"
            ;;
        -b|--backup)
            if [ -z "$2" ]; then
                print_error "请提供文件路径"
                show_usage
                exit 1
            fi
            check_dependencies
            backup_file "$2"
            ;;
        -c|--check)
            check_dependencies
            ;;
        "")
            # 无参数，启动交互式模式
            interactive_mode
            ;;
        *)
            print_error "未知选项: $1"
            show_usage
            exit 1
            ;;
    esac

    echo ""
    print_success "操作完成！"
}

# 执行主函数
main "$@"
