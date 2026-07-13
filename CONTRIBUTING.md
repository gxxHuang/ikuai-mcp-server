# 贡献指南

感谢你对 iKuai MCP Server 的关注！以下是参与项目的流程。

## 开发环境

```bash
git clone https://github.com/gxxHuang/ikuai-mcp-server.git
cd ikuai-mcp-server
pip install -e ".[dev]"
pre-commit install
```

## 项目结构

```
ikuai-mcp-server/
├── src/ikuai_mcp/
│   ├── server.py              # FastMCP 入口
│   ├── client.py              # API 客户端（认证 + 通用调用）
│   └── tools/                 # MCP 工具模块（按功能域分组）
│       ├── system.py          # 系统监控
│       ├── network.py         # 网络配置
│       ├── security.py        # 安全管控
│       ├── qos_routing.py     # 流控分流
│       ├── auth.py            # 认证计费
│       ├── wireless.py        # 无线服务
│       ├── advanced.py        # 高级服务
│       ├── logs.py            # 日志中心
│       └── settings.py        # 设备设置
├── tests/                     # 测试
└── .github/                   # CI/CD
```

## 分支策略

- `main` — 稳定版本
- `develop` — 开发分支
- `feature/xxx` — 新功能
- `fix/xxx` — Bug 修复

## 提交规范

使用 [Conventional Commits](https://www.conventionalcommits.org/)：

```
feat: 添加 PPPoE 账号管理工具
fix: 修复 DHCPv6 租约查询错误
docs: 更新 API 文档
test: 添加 client.py 单元测试
```

## 添加新工具

1. 确定 func_name（通过浏览器 F12 抓包 /Action/call 请求）
2. 在对应的 `tools/*.py` 中添加 `@mcp.tool` 装饰的函数
3. 只读工具标注 `@mcp.tool(annotations={"readOnlyHint": True})`
4. 危险操作要求 `confirm=True` 参数
5. 写测试 `tests/test_xxx.py`
6. 更新 `README.md` 功能表格

## 测试

```bash
pytest                          # 运行全部测试
pytest tests/test_client.py     # 单文件
pytest --cov=src/ikuai_mcp      # 含覆盖率
```

## 代码风格

```bash
ruff check . && ruff format .
```
