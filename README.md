# iKuai MCP Server

[![License: MIT](https://img.shields.io/github/license/gxxHuang/ikuai-mcp-server)](LICENSE)
[![MCP](https://img.shields.io/badge/MCP-2025--11--25-blue)](https://modelcontextprotocol.io/)
[![Python](https://img.shields.io/badge/Python-3.10+-blue)](https://www.python.org/)

**让 AI 直接管理你的爱快路由器。** 基于 [FastMCP](https://github.com/jlowin/fastmcp) 构建,把 iKuai Web 后台 **229 个功能**变成自然语言对话——不用再记那堆网页操作。

```text
"查看在线设备"          → 终端 IP/MAC/流量一览
"把 192.168.9.100 限速" → 一键添加 IP 限速
"添加端口映射"          → 8080 → 内网 192.168.9.50
"改 Wi-Fi 密码"          → 完成
"看下今天谁掉线了"      → 终端上下线记录
```

## 功能亮点

- **全功能覆盖**:229 个 MCP 工具 · 149 个 API 端点,覆盖 Web 后台 9 大模块
- **智能 API 客户端**:自动登录(处理爱快加密协议)、会话过期自动重试、兼容新旧两代 API 响应格式
- **读写双模式**:查询类工具标记为只读,修改类工具(ACL/限速/端口映射等)读写分离
- **危险操作防护**:重启、固件升级、改管理员密码等操作要求 `confirm=True` 显式确认
- **双传输模式**:stdio(接入 Claude Desktop/Cursor)或 HTTP(脚本调用/远程集成)
- **Docker 一键部署**:`docker-compose up -d` 直接跑

## 快速开始

### 1. 安装

从 GitHub 源码安装(需要 [Git](https://git-scm.com/) 和 **Python 3.10+**):

```bash
pip install git+https://github.com/gxxHuang/ikuai-mcp-server.git
```

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

> 企业版 4.x 支持全部功能;免费版/3.x 部分 API 不可用,见[兼容性](#兼容性)。

### 3. 接入 AI 客户端

**Claude Desktop** — 编辑 `claude_desktop_config.json`:

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

**Cursor** — 同样的配置写到 `.cursor/mcp.json`。

**HTTP 模式**(脚本调用 / 非 AI 客户端集成):

```bash
python -m ikuai_mcp.server --transport http --port 8000
```

### 4. 开始用

配置完直接对话:

- "查看路由器当前状态" — CPU / 内存 / 流量 / 版本
- "列出所有在线设备" — 终端 IP / MAC / 流量
- "把 192.168.9.100 限速到 10Mbps" — 添加 IP 限速
- "开启 SSH" — 启用隐藏的 SSH 服务
- "查看今天的登录日志" — 认证日志一览
- "重启客厅的 AP" — 重启指定无线 AP

## 功能覆盖

229 个工具 · 149 个 API 端点,9 大模块:

| 模块 | 工具数 | 能做什么 |
|------|-------|---------|
| 系统监控 | 17 | 系统概览、线路/终端/负载监控、行为洞察、下联设备 |
| 网络配置 | 58 | WAN/LAN、IPv6、VLAN、DHCP、DNS、端口映射、NAT、DDNS、VPN 客户端 |
| 安全管控 | 39 | ACL、连接数限制、ARP、MAC 控制、网址/URL/应用协议控制、流量审计 |
| 流控分流 | 21 | 智能流控、IP/MAC 限速、多线负载、端口/协议/域名分流 |
| 认证计费 | 28 | PPPoE、Web 认证、VPN 服务端、套餐、账号管理 |
| 无线服务 | 16 | AP 管理/升级、Wi-Fi 设置、Mesh、信道扫描 |
| 高级服务 | 21 | SNMP、内网穿透、抓包、测速、Ping/Traceroute、WOL |
| 日志中心 | 11 | 认证/ARP/DHCP/DDNS/操作等 11 类日志、告警 |
| 设备设置 | 18 | SSH/Telnet/FTP 开关、管理员账号、固件升级、双机热备 |

**完整逐模块工具清单见 [docs/COVERAGE.md](docs/COVERAGE.md)。**

## 安全设计

路由器是网络核心设备,本项目内置三层防护:

1. **只读标注**:所有查询工具标记 `readOnlyHint`,客户端可据此拒绝误操作
2. **二次确认**:`change_admin_password`、`upgrade_ap_firmware` 等危险操作要求 `confirm=True` 显式传入
3. **凭据隔离**:密码仅通过 `.env` / 环境变量注入,不出现在代码和日志中;仅限局域网访问,不暴露公网

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

## 开发

```bash
pip install -e ".[dev]"
make test    # pytest + 覆盖率
make lint    # ruff 检查
```

项目结构:

```
src/ikuai_mcp/
├── server.py        # FastMCP 入口,注册 9 个模块
├── client.py        # API 客户端:自动登录/会话重试/兼容双格式
└── tools/           # 9 个工具模块(每个约 100-350 行)
```

## 常见问题

| 问题 | 解决 |
|------|------|
| 连不上路由器 | 检查 `IKUAI_URL`;确认电脑和路由器在同一网段 |
| 认证失败 | 浏览器登录一次验证密码;检查 `.env` 中 `IKUAI_PASSWORD` |
| `.env` 没生效 | 确保 `.env` 在项目根目录,或直接写进客户端 `env` 字段 |
| 某些功能报错 | 免费版/旧固件 API 有限,升级企业版 4.x |
| MCP 工具不显示 | 重启 AI 客户端后重试 |

## 贡献 & 许可

欢迎 PR,见 [CONTRIBUTING.md](CONTRIBUTING.md)。MIT License,见 [LICENSE](LICENSE)。
