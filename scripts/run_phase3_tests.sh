#!/bin/bash

# =============================================================================
# Story 3.1 Phase 3: 验证和测试快速启动脚本
# =============================================================================

set -e

# 颜色定义
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# 打印标题
print_header() {
    echo -e "${BLUE}=================================================================${NC}"
    echo -e "${BLUE}  Story 3.1 - Phase 3: 验证和测试${NC}"
    echo -e "${BLUE}  执行性能测试套件${NC}"
    echo -e "${BLUE}=================================================================${NC}"
    echo ""
}

# 打印成功信息
print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

# 打印信息
print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# 打印警告
print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

# 打印错误
print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# 检查依赖
check_dependencies() {
    print_info "检查依赖..."

    if ! command -v python3 &> /dev/null; then
        print_error "Python3 未安装"
        exit 1
    fi

    # 检查必要的包
    python3 -c "import unittest, psutil, pathlib, json, threading, time" 2>/dev/null
    if [ $? -ne 0 ]; then
        print_error "缺少必要的Python包"
        exit 1
    fi

    print_success "依赖检查通过"
}

# 运行测试
run_tests() {
    print_info "开始运行Phase 3测试套件..."

    cd /home/sunrise/xlerobot

    # 运行测试
    python3 tests/performance/run_phase3_tests.py

    print_success "测试执行完成"
}

# 查看测试报告
view_reports() {
    print_info "查找测试报告..."

    reports_dir="reports/performance"
    if [ -d "$reports_dir" ]; then
        latest_report=$(ls -t ${reports_dir}/*.json 2>/dev/null | head -1)
        if [ -n "$latest_report" ]; then
            print_info "最新报告: $latest_report"
            echo ""
            print_info "报告内容:"
            python3 -c "
import json
with open('$latest_report', 'r') as f:
    report = json.load(f)
    print('测试套件数:', len(report['test_suites']))
    print('总测试数:', report['summary']['total_tests'])
    print('通过:', report['summary']['passed'])
    print('失败:', report['summary']['failed'])
    print('错误:', report['summary']['errors'])
"
        else
            print_warning "未找到测试报告"
        fi
    else
        print_warning "报告目录不存在"
    fi
}

# 运行单个测试套件
run_suite() {
    local suite_name=$1
    print_info "运行测试套件: $suite_name"

    cd /home/sunrise/xlerobot

    case $suite_name in
        "large-scale")
            python3 -m unittest tests.performance.stress.test_large_scale_models -v
            ;;
        "stress")
            python3 -m unittest tests.performance.stress.test_concurrent_stress -v
            ;;
        "stability")
            python3 -m unittest tests.performance.stability.test_long_term_stability -v
            ;;
        "benchmark")
            python3 -m unittest tests.performance.integration.test_performance_benchmarks -v
            ;;
        *)
            print_error "未知测试套件: $suite_name"
            echo "可用套件: large-scale, stress, stability, benchmark"
            exit 1
            ;;
    esac

    print_success "$suite_name 测试完成"
}

# 显示帮助
show_help() {
    echo "用法: $0 [选项]"
    echo ""
    echo "选项:"
    echo "  --help, -h          显示帮助信息"
    echo "  --check             检查依赖"
    echo "  --all               运行所有测试 (默认)"
    echo "  --suite <name>      运行指定测试套件"
    echo "                      可用套件: large-scale, stress, stability, benchmark"
    echo "  --reports           查看测试报告"
    echo ""
    echo "示例:"
    echo "  $0                  # 运行所有测试"
    echo "  $0 --suite stress   # 只运行并发压力测试"
    echo "  $0 --reports        # 查看测试报告"
}

# 主函数
main() {
    print_header

    # 检查是否在正确目录
    if [ ! -f "README.md" ] || [ ! -d "tests" ]; then
        print_error "请在项目根目录 (/home/sunrise/xlerobot) 运行此脚本"
        exit 1
    fi

    # 解析命令行参数
    case "${1:-}" in
        -h|--help)
            show_help
            exit 0
            ;;
        --check)
            check_dependencies
            ;;
        --all|"")
            check_dependencies
            run_tests
            view_reports
            ;;
        --suite)
            if [ -z "$2" ]; then
                print_error "请提供测试套件名称"
                show_help
                exit 1
            fi
            check_dependencies
            run_suite "$2"
            ;;
        --reports)
            view_reports
            ;;
        *)
            print_error "未知选项: $1"
            show_help
            exit 1
            ;;
    esac

    echo ""
    print_success "操作完成！"
}

# 执行主函数
main "$@"
