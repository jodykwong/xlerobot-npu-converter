# XLeRobot NPU Converter Makefile
# 提供常用的开发和测试命令

.PHONY: help install install-dev test test-coverage test-benchmark lint format clean docs coverage-report coverage-enhanced check-coverage docker-build docker-run

# 默认目标
.DEFAULT_GOAL := help

# 项目配置
PYTHON := python3
PIP := pip3
PYTEST := pytest

help: ## 显示帮助信息
	@echo "XLeRobot NPU Converter - 开发工具集"
	@echo ""
	@echo "可用命令:"
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  %-20s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

install: ## 安装项目依赖
	$(PIP) install -r requirements.txt

install-dev: ## 安装开发依赖
	$(PIP) install -r requirements-dev.txt
	pre-commit install

test: ## 运行测试套件
	$(PYTEST) tests/ -v

test-coverage: ## 运行测试并生成覆盖率报告
	$(PYTEST) tests/ --cov=src --cov-report=term-missing --cov-report=html --cov-report=xml --cov-report=json

test-benchmark: ## 运行性能基准测试
	$(PYTEST) tests/benchmarks/ --benchmark-only

test-watch: ## 监控文件变化并自动运行测试
	$(PYTEST) tests/ -f

lint: ## 运行代码检查
	@echo "运行 Ruff 检查..."
	ruff check src/ tests/
	@echo "运行 MyPy 类型检查..."
	mypy src/ --ignore-missing-imports
	@echo "运行 Bandit 安全扫描..."
	bandit -r src/

format: ## 格式化代码
	@echo "运行 Black 格式化..."
	black src/ tests/
	@echo "运行 isort 导入排序..."
	isort src/ tests/

format-check: ## 检查代码格式
	black --check --diff src/ tests/
	isort --check-only --diff src/ tests/

coverage-report: ## 生成详细覆盖率报告
	python scripts/coverage_monitor.py report
	python scripts/enhance_coverage_report.py
	python scripts/generate_coverage_badge.py
	@echo "✅ 覆盖率报告已生成"
	@echo "📊 HTML报告: htmlcov/index.html"
	@echo "📈 增强报告: htmlcov/enhanced_index.html"
	@echo "🏷️ 徽章文件: docs/coverage_badge.svg"

coverage-enhanced: ## 生成增强覆盖率报告
	python scripts/enhance_coverage_report.py
	@echo "✅ 增强覆盖率报告已生成: htmlcov/enhanced_index.html"

check-coverage: ## 检查覆盖率是否达标
	python scripts/coverage_monitor.py check

coverage-full: ## 完整覆盖率流程（运行测试+生成报告+检查）
	python scripts/coverage_monitor.py full

coverage-watch: ## 监控覆盖率变化
	watchmedo shell-command --patterns="*.py" --recursive --command='make coverage-report' .

# 测试报告和性能基准
test-report: ## 生成完整测试报告
	python scripts/test_report_generator.py

test-visualization: ## 生成测试可视化仪表板
	python scripts/test_visualizer.py

performance-benchmark: ## 运行性能基准测试
	pytest tests/benchmarks/ --benchmark-only --benchmark-json=reports/benchmark_results.json

performance-analysis: ## 分析性能趋势
	python scripts/performance_trend_analyzer.py

full-test-report: ## 完整测试报告（包含性能和可视化）
	@echo "🔄 生成完整测试报告..."
	make test-coverage
	make test-report
	make test-visualization
	make performance-analysis
	@echo "✅ 完整测试报告生成完成"
	@echo "📊 测试报告: reports/test_report.html"
	@echo "📈 可视化仪表板: reports/visualizations/dashboard.html"
	@echo "📋 性能分析: reports/trend_analysis.json"
	@echo "📄 趋势报告: reports/trend_report.md"

docs: ## 生成文档
	@echo "生成项目文档..."
	@mkdir -p docs
	@if [ -f "docs/coverage_badge.svg" ]; then echo "覆盖率徽章已存在"; else python scripts/generate_coverage_badge.py; fi
	@echo "✅ 文档生成完成"

clean: ## 清理临时文件
	@echo "清理临时文件..."
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	rm -rf build/
	rm -rf dist/
	rm -rf .coverage
	rm -rf coverage.xml
	rm -rf coverage.json
	rm -rf htmlcov/
	rm -rf .pytest_cache/
	rm -rf .mypy_cache/
	rm -rf coverage_report.json
	rm -rf coverage_history.json
	@echo "✅ 清理完成"

clean-all: clean ## 清理所有生成文件
	@echo "清理所有生成文件..."
	rm -rf docs/
	@echo "✅ 深度清理完成"

docker-build: ## 构建Docker镜像
	docker build -t xlerobot/npu-converter:latest .

docker-run: ## 运行Docker容器
	docker run --rm -it xlerobot/npu-converter:latest

docker-test: ## 在Docker中运行测试
	docker run --rm -v $(PWD):/app xlerobot/npu-converter:latest make test-coverage

quality: ## 运行完整代码质量检查
	@echo "🔍 运行完整代码质量检查..."
	$(MAKE) format-check
	$(MAKE) lint
	$(MAKE) test-coverage
	$(MAKE) check-coverage
	@echo "✅ 代码质量检查完成"

ci-local: ## 本地运行CI检查
	@echo "🚀 运行本地CI检查..."
	$(MAKE) quality
	$(MAKE) docker-build
	$(MAKE) docker-test
	@echo "✅ 本地CI检查完成"

install-hooks: ## 安装Git hooks
	@echo "安装Git hooks..."
	pre-commit install
	pre-commit install --hook-type commit-msg
	@echo "✅ Git hooks安装完成"

update-deps: ## 更新依赖
	@echo "更新依赖..."
	$(PIP) install --upgrade pip
	$(PIP) install --upgrade -r requirements.txt
	$(PIP) install --upgrade -r requirements-dev.txt
	@echo "✅ 依赖更新完成"

check-security: ## 安全检查
	@echo "🔒 运行安全检查..."
	safety check
	bandit -r src/
	@echo "✅ 安全检查完成"

benchmark: ## 运行性能基准测试
	@echo "🏃 运行性能基准测试..."
	$(MAKE) test-benchmark
	@echo "✅ 基准测试完成"

all-test: ## 运行所有测试
	@echo "🧪 运行所有测试..."
	$(MAKE) test
	$(MAKE) test-coverage
	$(MAKE) test-benchmark
	@echo "✅ 所有测试完成"

pre-commit-check: ## Pre-commit检查
	@echo "🔍 运行pre-commit检查..."
	pre-commit run --all-files
	@echo "✅ Pre-commit检查完成"

# 文档检查命令
doc-sync-check: ## 检查文档同步状态
	@echo "🔍 检查文档同步状态..."
	python scripts/sync_docs.py --check-only
	@echo "✅ 文档同步状态正常"

doc-sync: ## 同步文档状态
	@echo "🔄 同步文档状态..."
	python scripts/sync_docs.py --sync
	@echo "✅ 文档同步完成"

doc-audit-quick: ## 快速文档质量检查
	@echo "🔍 运行快速文档质量检查..."
	python scripts/doc_audit.py --quick --report
	@echo "✅ 快速检查完成"

doc-audit-full: ## 完整文档质量审计
	@echo "🔍 运行完整文档质量审计..."
	python scripts/doc_audit.py --full --report
	@echo "✅ 完整审计完成"

doc-check: doc-sync-check doc-audit-quick ## 完整文档检查 (同步+快速审计)
	@echo "✅ 文档检查完成"

# 开发环境设置
setup-dev: ## 设置开发环境
	@echo "🛠️ 设置开发环境..."
	$(MAKE) install-dev
	$(MAKE) install-hooks
	$(MAKE) docs
	@echo "✅ 开发环境设置完成"

# 发布准备
release-check: ## 发布前检查
	@echo "🚀 发布前检查..."
	$(MAKE) clean
	$(MAKE) quality
	$(MAKE) docs
	$(MAKE) docker-build
	$(MAKE) all-test
	@echo "✅ 发布检查完成"

# 项目状态
status: ## 显示项目状态
	@echo "📊 XLeRobot NPU Converter 项目状态"
	@echo "=================================="
	@echo "Python版本: $$($(PYTHON) --version)"
	@echo "Pip版本: $$($(PIP) --version)"
	@echo ""
	@echo "测试文件数量: $$(find tests/ -name "test_*.py" | wc -l)"
	@echo "源码文件数量: $$(find src/ -name "*.py" | wc -l)"
	@echo ""
	@if [ -f "coverage.json" ]; then \
		echo "当前覆盖率: $$(python -c "import json; data=json.load(open('coverage.json')); print(data['totals']['percent_covered'])")%"; \
	else \
		echo "覆盖率报告不存在，运行 make test-coverage 生成"; \
	fi
	@echo ""
	@if command -v docker >/dev/null 2>&1; then \
		echo "Docker: 已安装"; \
	else \
		echo "Docker: 未安装"; \
	fi

# 快速命令别名
t: test ## test的别名
tc: test-coverage ## test-coverage的别名
l: lint ## lint的别名
f: format ## format的别名
c: clean ## clean的别名
d: docs ## docs的别名