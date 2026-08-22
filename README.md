# iKuai MCP Server

[![License: MIT](https://img.shields.io/github/license/gxxHuang/ikuai-mcp-server)](LICENSE)
[![MCP](https://img.shields.io/badge/MCP-2025--11--25-blue)](https://modelcontextprotocol.io/)

**让 AI 直接管理你的爱快路由器。** 一个 MCP Server,把 iKuai Web 后台 229 个功能变成自然语言对话——不用再记那堆网页操作。

```
"查看在线设备"        → 终端 IP/MAC/流量一览
"把 192.168.9.100 限速" → 一键限速
"添加端口映射"        → 8080 → 内网 192.168.9.50
"改 Wi-Fi 密码"        → 完成
```

## 快速开始

### 1. 安装

```bash
pip install ikuai-mcp-server
```

需要 **Python 3.10+** 和一台 **iKuai 路由器**(企业版 4.x 全功能;免费版部分 API 不可用)。

### 2. 配置

```bash
cp .env.example .env
```

编辑 `.env`,填入路由器信息:

```ini
IKUAI_URL=http://192.168.9.1
IKUAI_USERNAME=admin
IKUAI_PASSWORD=你的密码
```

### 3. 接入 AI 客户端

以 Claude Desktop 为例,编辑 `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "ikuai": {
      "command": "ikuai-mcp",
      "args": [],
      "env": {
        "IKUAI_URL": "http://192.168.9.1",
        "IKUAI_USERNAME": "admin",
        "IKUAI_PASSWORD": "你的密码"
      }
    }
  }
}
```

> **Cursor**: 同样的配置写到 `.cursor/mcp.json`。
> **HTTP 模式**(不用 AI 客户端,脚本/自定义集成): `python -m ikuai_mcp.server --transport http --port 8000`

### 4. 开始用

配置完直接对话:

- "查看路由器当前状态" — CPU / 内存 / 流量 / 版本
- "列出所有在线设备" — 终端 IP / MAC / 流量
- "开启 SSH" — 启用隐藏的 SSH 服务
- "查看今天的登录日志" — 认证日志一览

## 功能覆盖

229 个工具 · 149 个 API 端点,覆盖 Web 后台 9 大模块:

| 模块 | 工具数 | 能做什么 |
|------|-------|---------|
| 系统监控 | 17 | 状态概览、线路/终端/负载监控 |
| 网络配置 | 58 | WAN/LAN、IPv6、DHCP、DNS、端口映射、DDNS |
| 安全管控 | 39 | ACL、MAC 控制、网址/URL/应用协议控制 |
| 流控分流 | 21 | 智能流控、IP/MAC 限速、多线负载、分流 |
| 认证计费 | 28 | PPPoE、Web 认证、VPN、套餐 |
| 无线服务 | 16 | AP 管理、Wi-Fi 设置、Mesh |
| 高级服务 | 21 | Ping/Traceroute/测速/WOL、抓包、SNMP |
| 日志中心 | 11 | 9 类日志、告警 |
| 设备设置 | 18 | SSH/Telnet/FTP 开关、固件升级、配置快照 |

**完整逐模块工具清单见 [docs/COVERAGE.md](docs/COVERAGE.md)。**

## Docker

```bash
cp .env.example .env   # 必做,否则容器内密码为空
docker-compose up -d
```

## 兼容性

| 路由器 | 固件 | 状态 |
|--------|------|------|
| IK-Q 系列 | 4.x 企业版 | ✅ 全功能 |
| IK-G 系列 | 3.x+ | ⚠️ 部分兼容 |
| 免费版 | 3.x | ⚠️ API 有限 |

## 常见问题

| 问题 | 解决 |
|------|------|
| 连不上路由器 | 检查 `IKUAI_URL`;确认电脑和路由器在同一网段 |
| 认证失败 | 浏览器登录一次验证密码;检查 `.env` 中 `IKUAI_PASSWORD` |
| `.env` 没生效 | 确保 `.env` 在项目根目录,或直接写进客户端 `env` 字段 |
| 某些功能报错 | 免费版/旧固件 API 有限,升级企业版 4.x |
| MCP 工具不显示 | 重启 AI 客户端后重试 |

## 开发

```bash
pip install -e ".[dev]"
make test
make lint
```

项目结构:

```
src/ikuai_mcp/
├── server.py        # FastMCP 入口
├── client.py        # API 客户端
└── tools/           # 9 个工具模块
```

## 安全

- 危险操作(重启/固件升级/恢复出厂)内置二次确认
- 密码走 `.env`,**不要提交到 Git**
- 仅限局域网,不暴露公网

## 贡献 & 许可

欢迎 PR,见 [CONTRIBUTING.md](CONTRIBUTING.md)。MIT License,见 [LICENSE](LICENSE)。
