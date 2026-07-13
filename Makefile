.PHONY: help install test lint clean dev

help: ## 显示帮助
	@grep -E '^[a-zA-Z_-]+:.*##' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## 安装依赖
	pip install -e ".[dev]"

test: ## 运行测试
	pytest --cov=src/ikuai_mcp -v

lint: ## 代码检查
	ruff check . && ruff format --check .

fmt: ## 代码格式化
	ruff format .

clean: ## 清理
	rm -rf dist/ build/ *.egg-info/ .pytest_cache/ .ruff_cache/ __pycache__/
	find . -name __pycache__ -exec rm -rf {} + 2>/dev/null || true

dev: ## 开发模式运行
	python -m ikuai_mcp.server

docker-build: ## 构建 Docker 镜像
	docker build -t ikuai-mcp-server .

docker-run: ## 运行 Docker 容器
	docker-compose up -d

docker-stop: ## 停止 Docker 容器
	docker-compose down
