#!/bin/bash

# Horizon X5 BPU工具链验证脚本
# 用途: 验证工具链环境配置和组件功能

set -e  # 遇到错误立即退出

# 配置
INSTALL_PATH="${HORIZON_TOOLCHAIN_ROOT:-/opt/horizon}"
LOG_FILE="/var/log/horizon-validate.log"

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 日志函数
log() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') [$1] $2" | tee -a "$LOG_FILE"
}

log_info() {
    log "INFO" "$1"
}

log_error() {
    log "ERROR" "$1"
}

log_warning() {
    log "WARNING" "$1"
}

log_success() {
    echo -e "${GREEN}$1${NC}"
}

log_error_msg() {
    echo -e "${RED}$1${NC}"
}

log_info_msg() {
    echo -e "${BLUE}$1${NC}"
}

# 验证环境变量
validate_environment() {
    log_info "验证环境变量..."

    local errors=0

    # 检查HORIZON_TOOLCHAIN_ROOT
    if [[ -z "$HORIZON_TOOLCHAIN_ROOT" ]]; then
        log_error "HORIZON_TOOLCHAIN_ROOT未设置"
        ((errors++))
    elif [[ ! -d "$HORIZON_TOOLCHAIN_ROOT" ]]; then
        log_error "工具链安装目录不存在: $HORIZON_TOOLCHAIN_ROOT"
        ((errors++))
    else
        log_info "工具链安装目录: $HORIZON_TOOLCHAIN_ROOT"
    fi

    # 检查PATH
    if echo "$PATH" | grep -q "$HORIZON_TOOLCHAIN_ROOT/bin"; then
        log_info "PATH包含工具链bin目录"
    else
        log_warning "PATH不包含工具链bin目录"
        ((errors++))
    fi

    # 检查LD_LIBRARY_PATH
    if echo "$LD_LIBRARY_PATH" | grep -q "$HORIZON_TOOLCHAIN_ROOT/lib"; then
        log_info "LD_LIBRARY_PATH包含工具链lib目录"
    else
        log_warning "LD_LIBRARY_PATH不包含工具链lib目录"
        ((errors++))
    fi

    return $errors
}

# 验证工具链组件
validate_components() {
    log_info "验证工具链组件..."

    local errors=0
    local components=("hbdk" "hb_mapper" "hb_perf" "hb_gdb")

    for component in "${components[@]}"; do
        component_path="$HORIZON_TOOLCHAIN_ROOT/bin/$component"

        if [[ -x "$component_path" ]]; then
            log_info "✓ $component 可执行"

            # 尝试获取版本信息
            version_output=$("$component_path" --version 2>/dev/null || echo "unknown")
            if [[ "$version_output" != "unknown" ]]; then
                log_info "✓ $component 版本: $version_output"
            else
                log_warning "⚠ $component 版本未知"
                ((errors++))
            fi
        else
            log_error "✗ $component 不存在或不可执行"
            ((errors++))
        fi
    done

    return $errors
}

# 验证库文件
validate_libraries() {
    log_info "验证库文件..."

    local errors=0
    local lib_path="$HORIZON_TOOLCHAIN_ROOT/lib"

    if [[ -d "$lib_path" ]]; then
        local lib_count=$(find "$lib_path" -name "*.so*" -o -name "*.a*" | wc -l)
        log_info "找到 $lib_count 个库文件"

        if [[ $lib_count -gt 0 ]]; then
            log_info "✓ 库文件存在"
        else
            log_error "✗ 未找到库文件"
            ((errors++))
        fi
    else
        log_error "✗ 库目录不存在"
        ((errors++))
    fi

    return $errors
}

# 验证配置文件
validate_config() {
    log_info "验证配置文件..."

    local errors=0
    local config_file="$HORIZON_TOOLCHAIN_ROOT/../config/horizon-x5.yaml"

    if [[ -f "$config_file" ]]; then
        log_info "✓ 配置文件存在: $config_file"
    else
        log_warning "⚠ 配置文件不存在: $config_file"
        ((errors++))
    fi

    return $errors
}

# 功能测试
test_functionality() {
    log_info "测试工具链功能..."

    local errors=0

    # 测试hbdk帮助命令
    log_info "测试BPU编译器..."
    if "$HORIZON_TOOLCHAIN_ROOT/bin/hbdk" --help >/dev/null 2>&1; then
        log_info "✓ hbdk 帮助命令正常"
    else
        log_error "✗ hbdk 帮助命令失败"
        ((errors++))
    fi

    # 测试hb_mapper帮助命令
    log_info "测试模型转换工具..."
    if "$HORIZON_TOOLCHAIN_ROOT/bin/hb_mapper" --help >/dev/null 2>&1; then
        log_info "✓ hb_mapper 帮助命令正常"
    else
        log_error "✗ hb_mapper 帮助命令失败"
        ((errors++))
    fi

    return $errors
}

# 生成验证报告
generate_report() {
    local total_errors=$1
    local env_errors=$2
    local comp_errors=$3
    local lib_errors=$4
    local func_errors=$5

    log_info "生成验证报告..."

    cat > "$HORIZON_TOOLCHAIN_ROOT/validation_report.txt" << EOF
Horizon X5 BPU工具链验证报告
=====================================
验证时间: $(date)
安装路径: $HORIZON_TOOLCHAIN_ROOT

环境验证结果:
- 环境变量错误: $env_errors

组件验证结果:
- 组件错误: $comp_errors

库文件验证结果:
- 库文件错误: $lib_errors

功能测试结果:
- 功能错误: $func_errors

总错误数: $total_errors

状态: $([ $total_errors -eq 0 ]] && echo "通过" || echo "失败")
EOF

    if [[ $total_errors -eq 0 ]]; then
        log_success "工具链验证完成 - 所有检查通过"
        return 0
    else
        log_error_msg "工具链验证失败 - 发现 $total_errors 个问题"
        return 1
    fi
}

# 显示帮助信息
show_help() {
    echo "Horizon X5 BPU工具链验证脚本"
    echo ""
    echo "用法: $0 [选项]"
    echo ""
    echo "选项:"
    echo "  -h, --help              显示此帮助信息"
    echo "  -v, --verbose           详细输出"
    echo "  -p, --path PATH         指定工具链路径"
    echo "  -r, --report FILE      生成报告到指定文件"
    echo ""
    echo "环境变量:"
    echo "  HORIZON_TOOLCHAIN_ROOT  工具链安装路径"
    echo ""
    echo "示例:"
    echo "  $0 --path /opt/horizon"
    echo "  $0 --report /tmp/validation-report.txt"
}

# 主函数
main() {
    local env_errors=0
    local comp_errors=0
    local lib_errors=0
    local func_errors=0

    # 解析命令行参数
    while [[ $# -gt 0 ]]; do
        case $1 in
            -h|--help)
                show_help
                exit 0
                ;;
            -v|--verbose)
                set -x
                shift
                ;;
            -p|--path)
                HORIZON_TOOLCHAIN_ROOT="$2"
                shift 2
                ;;
            -r|--report)
                REPORT_FILE="$2"
                shift 2
                ;;
            *)
                log_error_msg "未知参数: $1"
                show_help
                exit 1
                ;;
        esac
    done

    log_info "开始Horizon X5 BPU工具链验证"

    # 检查工具链安装路径
    if [[ ! -d "$HORIZON_TOOLCHAIN_ROOT" ]]; then
        log_error "工具链安装目录不存在: $HORIZON_TOOLCHAIN_ROOT"
        exit 1
    fi

    # 执行验证
    env_errors=$(validate_environment)
    comp_errors=$(validate_components)
    lib_errors=$(validate_libraries)
    func_errors=$(test_functionality)
    config_errors=$(validate_config)

    # 生成验证报告
    local total_errors=$((env_errors + comp_errors + lib_errors + func_errors + config_errors))

    # 输出总结
    echo ""
    log_info "验证总结:"
    log_info "  环境错误: $env_errors"
    log_info "  组件错误: $comp_errors"
    log_info "  库文件错误: $lib_errors"
    log_info "  功能错误: $func_errors"
    log_info "  配置文件错误: $config_errors"
    log_info "  总错误数: $total_errors"

    return $(generate_report $total_errors $env_errors $comp_errors $lib_errors $func_errors)
}

# 运行主函数
main "$@"