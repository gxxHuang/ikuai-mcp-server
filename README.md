# 🚀 iKuai MCP Server

[![PyPI](https://img.shields.io/badge/PyPI-v1.0.0-blue)](https://pypi.org/project/ikuai-mcp-server/)
[![Python](https://img.shields.io/badge/Python-3.10+-blue)](https://www.python.org/)
[![License](https://img.shields.io/github/license/gxxHuang/ikuai-mcp-server)](LICENSE)
[![Tests](https://github.com/gxxHuang/ikuai-mcp-server/actions/workflows/test.yml/badge.svg)](https://github.com/gxxHuang/ikuai-mcp-server/actions/workflows/test.yml)
[![MCP](https://img.shields.io/badge/MCP-2025--11--25-blue)](https://modelcontextprotocol.io/)

**爱快 iKuai 路由器全功能 MCP Server** — 让 AI 助手直接操控你的 iKuai 路由器。

> 229 个工具 · 149 个 API 端点 · 100% Web 后台功能覆盖

## 前置条件

- **Python 3.10+**
- **iKuai 路由器**（企业版 4.x；免费版部分 API 不可用）
- **AI 客户端**：Claude Desktop / Cursor / VS Code + GitHub Copilot

---

## 📦 安装

```bash
pip install ikuai-mcp-server
```

## ⚡ 快速开始

### 1. 配置

```bash
cp .env.example .env
# 编辑 .env，填入路由器信息：
#   IKUAI_URL=http://192.168.9.1
#   IKUAI_USERNAME=admin
#   IKUAI_PASSWORD=你的密码
```

### 2. 接入 AI 客户端

**Claude Desktop** — 编辑 `claude_desktop_config.json`：

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

**Cursor** — 创建 `.cursor/mcp.json`：

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

### 3. 使用

配置完成后，在 AI 客户端中自然对话：

- "查看路由器当前状态" → CPU、内存、流量、版本
- "列出所有在线设备" → 终端 IP/MAC/流量一览
- "把 192.168.9.100 限速 10MB/s" → 添加终端限速
- "添加端口映射 8080 到内网 192.168.9.50" → 一键端口映射
- "修改 Wi-Fi 密码为 xxxxxxxx" → 改密码
- "开启 SSH" → 启用隐藏的 SSH 服务

### HTTP 模式（不使用 AI 客户端）

```bash
python -m ikuai_mcp.server --transport http --port 8000
# 访问 http://localhost:8000
```

适合脚本调用、自定义集成，或配合其他 HTTP MCP 客户端使用。

---

## 📊 功能覆盖

| 模块 | 工具数 | 主要功能 |
|------|--------|---------|
| 🔍 系统监控 | 17 | 系统概览、线路/终端/行为/负载/分流监控、下联设备 |
| 🌐 网络配置 | 58 | WAN/LAN、IPv6、VLAN、DHCP、DNS、静态路由、端口映射、NAT、UPnP、DDNS |
| 🛡️ 安全管控 | 39 | ACL、连接数限制、ARP、MAC 控制、网址浏览控制、URL 控制、应用协议控制 |
| ⚡ 流控分流 | 21 | 智能流控、IP/MAC 限速、多线负载、协议/端口/域名分流 |
| 🔐 认证计费 | 28 | PPPoE、Web 认证、VPN 服务端/客户端、套餐、通知推送 |
| 📡 无线服务 | 16 | AP 管理、Wi-Fi 设置、信道扫描、Mesh |
| 🔧 高级服务 | 21 | Ping/Traceroute/iPerf/测速/WOL、抓包、SNMP |
| 📋 日志中心 | 11 | 认证/ARP/DHCP/DDNS/操作等 9 类日志、告警 |
| ⚙️ 设备设置 | 18 | SSH/Telnet/FTP 开关、固件升级、配置快照、密码管理 |

---

## 🐳 Docker

```bash
# 1. 先配置 .env（必做！否则容器内密码为空）
cp .env.example .env
# 编辑 .env

# 2. 启动
docker-compose up -d
```

---

## 🧪 开发

```bash
pip install -e ".[dev]"
make test   # 运行测试
make lint   # 代码检查
```

## 📁 项目结构

```
ikuai-mcp-server/
├── src/ikuai_mcp/
│   ├── server.py              # FastMCP 入口
│   ├── client.py              # API 客户端
│   └── tools/                 # 9 个工具模块
├── tests/                     # pytest 测试
├── .github/workflows/         # CI/CD
└── Dockerfile                 # Docker 镜像
```

## 🔧 兼容性

| 路由器 | 固件 | 状态 |
|--------|------|------|
| IK-Q 系列 | 4.x 企业版 | ✅ 兼容 |
| IK-G 系列 | 3.x+ | ⚠️ 部分兼容 |
| 免费版 | 3.x | ⚠️ API 有限 |

## 🆘 故障排查

| 问题 | 解决 |
|------|------|
| 连不上路由器 | 检查 `IKUAI_URL` 是否正确、电脑和路由器是否在同一网段 |
| 认证失败 | 用浏览器登录一次确认密码正确；检查 `.env` 中的 `IKUAI_PASSWORD` |
| `.env` 没加载 | 确保 `.env` 在项目根目录，或直接将环境变量写入 Claude Desktop 的 `env` 字段 |
| Python 版本过低 | 需要 Python 3.10+，运行 `python --version` 确认 |
| 某些功能报错 | 免费版/旧固件部分 API 不可用，升级到企业版 4.x |
| MCP 工具不显示 | 重启 Claude Desktop / Cursor 后重试 |

## 🤝 贡献

欢迎贡献！详见 [CONTRIBUTING.md](CONTRIBUTING.md)。

## 📜 许可证

MIT License — 详见 [LICENSE](LICENSE)。

## ⚠️ 安全提示

- 危险操作（重启/固件升级/恢复出厂）需要 `confirm=True` 二次确认
- 密码通过 `.env` 管理，不要提交到 Git
- 仅支持局域网连接，不会暴露到公网
