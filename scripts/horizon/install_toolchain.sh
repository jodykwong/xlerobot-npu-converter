#!/bin/bash

# Horizon X5 BPU工具链自动安装脚本
# 用途: 在Docker环境中自动安装和配置Horizon X5 BPU工具链

set -e  # 遇到错误立即退出

# 配置
INSTALL_PATH="/opt/horizon"
DOWNLOAD_URL="${HORIZON_DOWNLOAD_URL:-https://horizon-x5.example.com/toolchain.tar.gz}"
CHECKSUM_FILE="${HORIZON_CHECKSUM_FILE:-placeholder_checksum}"
LOG_FILE="/var/log/horizon-install.log"

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

# 检查权限
check_permissions() {
    log_info "检查安装权限..."

    if [[ $EUID -ne 0 ]]; then
        log_error "需要root权限来安装工具链"
        log_error_msg "请使用: sudo $0"
        exit 1
    fi

    # 检查磁盘空间
    AVAILABLE_SPACE=$(df "$INSTALL_PATH" | tail -1 | awk '{print $4}')
    if [[ $AVAILABLE_SPACE -lt 2097152 ]]; then  # 2GB
        log_warning "磁盘空间不足，至少需要2GB可用空间"
    fi

    log_success "权限检查通过"
}

# 创建安装目录
create_install_directory() {
    log_info "创建安装目录..."

    if [[ -d "$INSTALL_PATH" ]]; then
        log_warning "安装目录已存在，清理旧安装..."
        rm -rf "$INSTALL_PATH.old" 2>/dev/null || true
        mv "$INSTALL_PATH" "$INSTALL_PATH.old" 2>/dev/null || true
    fi

    mkdir -p "$INSTALL_PATH"
    log_success "安装目录创建完成: $INSTALL_PATH"
}

# 下载工具链
download_toolchain() {
    log_info "下载Horizon X5 BPU工具链..."

    cd /tmp

    # 下载工具链包
    if ! wget -O "horizon-toolchain.tar.gz" "$DOWNLOAD_URL"; then
        log_error "工具链下载失败"
        exit 1
    fi

    # 验证文件完整性
    log_info "验证下载文件完整性..."
    if ! command -v sha256sum &>/dev/null; then
        log_warning "sha256sum命令不可用，跳过完整性验证"
    else
        DOWNLOAD_CHECKSUM=$(sha256sum "horizon-toolchain.tar.gz" | awk '{print $1}')
        if [[ "$DOWNLOAD_CHECKSUM" != "$CHECKSUM_FILE" && "$CHECKSUM_FILE" != "placeholder_checksum" ]]; then
            log_error "文件完整性验证失败"
            log_error "期望: $CHECKSUM_FILE"
            log_error "实际: $DOWNLOAD_CHECKSUM"
            exit 1
        fi
        log_success "文件完整性验证通过"
    fi

    log_success "工具链下载完成"
}

# 解压和安装
extract_and_install() {
    log_info "解压和安装工具链..."

    cd "$INSTALL_PATH"

    # 解压工具链包
    if ! tar -xzf "/tmp/horizon-toolchain.tar.gz"; then
        log_error "解压失败"
        exit 1
    fi

    # 清理临时文件
    rm -f "/tmp/horizon-toolchain.tar.gz"

    log_success "工具链解压完成"
}

# 设置环境变量
setup_environment() {
    log_info "设置环境变量..."

    # 创建环境变量配置文件
    cat > /etc/profile.d/horizon-toolchain.sh << 'EOF'
# Horizon X5 BPU工具链环境变量
export HORIZON_TOOLCHAIN_ROOT="$INSTALL_PATH"
export PATH="\$HORIZON_TOOLCHAIN_ROOT/bin:\$PATH"
export LD_LIBRARY_PATH="\$HORIZON_TOOLCHAIN_ROOT/lib:\$LD_LIBRARY_PATH"
EOF

    # 应用环境变量到当前会话
    export HORIZON_TOOLCHAIN_ROOT="$INSTALL_PATH"
    export PATH="$HORIZON_TOOLCHAIN_ROOT/bin:$PATH"
    export LD_LIBRARY_PATH="$HORIZON_TOOLCHAIN_ROOT/lib:$LD_LIBRARY_PATH"

    log_success "环境变量设置完成"
}

# 设置权限
setup_permissions() {
    log_info "设置文件权限..."

    # 设置目录权限
    chmod 755 "$INSTALL_PATH"

    # 设置可执行文件权限
    find "$INSTALL_PATH/bin" -type f -exec chmod 755 {} \;
    find "$INSTALL_PATH/lib" -type f -exec chmod 644 {} \;

    log_success "权限设置完成"
}

# 验证安装
verify_installation() {
    log_info "验证工具链安装..."

    # 检查关键文件
    local errors=0

    # 检查可执行文件
    for tool in hbdk hb_mapper hb_perf hb_gdb; do
        if [[ ! -x "$INSTALL_PATH/bin/$tool" ]]; then
            log_error "工具 $tool 不可执行"
            ((errors++))
        fi
    done

    # 检查库文件
    if [[ ! -d "$INSTALL_PATH/lib" ]]; then
        log_error "库目录不存在"
        ((errors++))
    fi

    if [[ $errors -eq 0 ]]; then
        log_success "工具链安装验证通过"
        return 0
    else
        log_error "工具链安装验证失败，发现 $errors 个问题"
        return 1
    fi
}

# 创建版本信息文件
create_version_info() {
    log_info "创建版本信息文件..."

    # 这里应该从安装包中读取实际版本信息
    # 使用占位符版本
    VERSION="1.0.0"
    DATE=$(date '+%Y-%m-%d')

    cat > "$INSTALL_PATH/version.txt" << EOF
Horizon X5 BPU Toolchain
Version: $VERSION
Install Date: $DATE
Install Path: $INSTALL_PATH
EOF

    log_success "版本信息文件创建完成"
}

# 清理函数
cleanup() {
    log_info "清理临时文件..."
    rm -f /tmp/horizon-toolchain.tar.gz 2>/dev/null || true
}

# 主函数
main() {
    log_info "开始Horizon X5 BPU工具链安装"
    log_info "安装路径: $INSTALL_PATH"

    # 设置错误处理
    trap cleanup EXIT
    trap 'log_error "安装过程中断，退出码: $?"' INT TERM

    # 执行安装步骤
    check_permissions
    create_install_directory
    download_toolchain
    extract_and_install
    setup_environment
    setup_permissions
    create_version_info

    # 验证安装
    if verify_installation; then
        log_success "Horizon X5 BPU工具链安装成功！"
        log_info "请运行 'source /etc/profile.d/horizon-toolchain.sh' 或重新登录以加载环境变量"
    else
        log_error "Horizon X5 BPU工具链安装失败"
        exit 1
    fi

    cleanup
}

# 显示帮助信息
show_help() {
    echo "Horizon X5 BPU工具链自动安装脚本"
    echo ""
    echo "用法: $0 [选项]"
    echo ""
    echo "选项:"
    echo "  -h, --help              显示此帮助信息"
    echo "  -u, --url URL          指定下载URL"
    echo "  -c, --checksum CHECKSUM 指定文件校验和"
    echo "  -p, --path PATH         指定安装路径 (默认: $INSTALL_PATH)"
    echo ""
    echo "环境变量:"
    echo "  HORIZON_DOWNLOAD_URL  下载URL"
    echo "  HORIZON_CHECKSUM_FILE   文件校验和"
    echo ""
    echo "示例:"
    echo "  $0 --url https://example.com/toolchain.tar.gz --checksum abc123"
}

# 解析命令行参数
while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help)
            show_help
            exit 0
            ;;
        -u|--url)
            DOWNLOAD_URL="$2"
            shift 2
            ;;
        -c|--checksum)
            CHECKSUM_FILE="$2"
            shift 2
            ;;
        -p|--path)
            INSTALL_PATH="$2"
            shift 2
            ;;
        *)
            log_error "未知参数: $1"
            show_help
            exit 1
            ;;
    esac
    shift
done

# 运行主函数
main "$@"