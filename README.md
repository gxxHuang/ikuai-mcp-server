# iKuai MCP Server

[![License: MIT](https://img.shields.io/github/license/gxxHuang/ikuai-mcp-server)](LICENSE)
[![MCP](https://img.shields.io/badge/MCP-2025--11--25-blue)](https://modelcontextprotocol.io/)
[![Python](https://img.shields.io/badge/Python-3.10+-blue)](https://www.python.org/)

**让 AI 直接管理你的爱快路由器。** 基于 [FastMCP](https://github.com/jlowin/fastmcp) 构建,把 iKuai Web 后台 **248 个功能**变成自然语言对话。

```text
"查看在线设备"          → 终端 IP/MAC/流量一览
"给某个设备限速"        → 一键添加 IP 限速
"添加端口映射"          → 公网端口 → 内网设备
"开启 SSH"              → 调用 API 开启隐藏服务
"看下今天谁掉线了"      → 终端上下线记录
```

## 功能亮点

- **全功能覆盖**:248 个 MCP 工具 · 覆盖 Web 后台 9 大模块
- **能开 Web 界面开不了的功能**:SSH / Telnet 等隐藏服务,浏览器里没有开关,只能通过 API 开启——本项目直接开放调用,一句话搞定
- **智能 API 客户端**:自动登录(处理爱快加密协议)、会话过期自动重试、兼容新旧两代 API 响应格式、TYPE 方言自动回退
- **读写双模式**:查询类工具标记为只读,修改类工具(ACL/限速/端口映射等)读写分离
- **危险操作防护**:重启、固件升级、改管理员密码等操作要求 `confirm=True` 显式确认
- **双传输模式**:stdio(接入 Claude Desktop/Cursor)或 HTTP(脚本调用/远程集成)
- **实机验证**:全部端点经 IK-Q3000 / 4.0.313 逐条调用核对,错误码语义明确

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

编辑 `.env`,填**你自己路由器**的信息:

```ini
IKUAI_URL=http://<你的路由器IP>
IKUAI_USERNAME=<你的登录账号>
IKUAI_PASSWORD=<你的登录密码>
```

> 企业版 4.x 支持全部功能;免费版部分 API 不可用,见[兼容性](#兼容性)。

### 3. 接入 AI 客户端

**Claude Desktop** — 编辑 `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "ikuai": {
      "command": "ikuai-mcp",
      "args": [],
      "env": {
        "IKUAI_URL": "http://<你的路由器IP>",
        "IKUAI_USERNAME": "<你的登录账号>",
        "IKUAI_PASSWORD": "<你的登录密码>"
      }
    }
  }
}
```

> 把 `<你的路由器IP>`、`<你的登录账号>`、`<你的登录密码>` 替换成你自己的实际值,并去掉尖括号。

**Cursor** — 同样的配置写到 `.cursor/mcp.json`。

**HTTP 模式**(脚本调用 / 非 AI 客户端集成):

```bash
python -m ikuai_mcp.server --transport http --port 8000
```

### 4. 开始用

配置完直接对话:

- "查看路由器当前状态" — CPU / 内存 / 流量 / 版本
- "列出所有在线设备" — 终端 IP / MAC / 流量
- "给某个设备限速到 10Mbps" — 添加 IP 限速
- "开启 SSH" — 调用 API 开启 Web 界面没有开关的 SSH 服务
- "查看今天的登录日志" — 认证日志一览
- "检查有没有新固件" — 读取 OTA 版本与更新说明
- "重启客厅的 AP" — 重启指定无线 AP

## 功能覆盖

248 个工具,9 大模块:

| 模块 | 工具数 | 能做什么 |
|------|-------|---------|
| 系统监控 | 18 | 系统概览、版本信息、线路(IPv4/IPv6)/终端/负载/分流监控、行为洞察、下联设备(摄像头/交换机/周边)、消息通知 |
| 网络配置 | 58 | WAN/LAN、IPv6、VLAN、DHCP、DNS、端口映射、NAT、DDNS、VPN 客户端 |
| 安全管控 | 39 | ACL、连接数限制、ARP、MAC 控制、网址/URL/应用协议控制、流量审计 |
| 流控分流 | 21 | 智能流控、IP/MAC 限速、多线负载、端口/协议/域名分流 |
| 认证计费 | 28 | PPPoE、Web 认证、VPN 服务端、套餐、账号管理 |
| 无线服务 | 21 | AP 管理/分组/升级、Wi-Fi 基础与高级设置、Mesh、信道扫描、无线网优、AC 状态 |
| 高级服务 | 32 | 固件 OTA、Ping/Traceroute 生命周期、iPerf/测速/WOL、抓包、SNMP、内网穿透、路由体检、配置快照、路由器重启、子网换算 |
| 日志中心 | 11 | 认证/ARP/DHCP/DDNS/操作等 11 类日志、告警 |
| 设备设置 | 20 | SSH/Telnet/FTP 开关、管理员账号、配置快照、任务队列、双机热备 |

**完整逐模块工具清单见 [docs/COVERAGE.md](docs/COVERAGE.md)。**

## 安全设计

路由器是网络核心设备,本项目内置三层防护:

1. **只读标注**:所有查询工具标记 `readOnlyHint`,客户端可据此拒绝误操作
2. **二次确认**:`change_admin_password`、`start_firmware_upgrade` 等危险操作要求 `confirm=True` 显式传入
3. **凭据隔离**:密码仅通过 `.env` / 环境变量注入,不出现在代码和日志中;仅限局域网访问,不暴露公网

## 兼容性

| 路由器 | 固件 | 状态 |
|--------|------|------|
| IK-Q3000 | 4.0.313 x64 (arm) | ✅ 实机验证 |
| IK-Q 系列 | 4.x 企业版 | ✅ 全功能 |
| IK-G 系列 | 3.x+ | ⚠️ 部分兼容 |
| 免费版 | 3.x / 4.x | ⚠️ 功能裁剪(见下) |

### 免费版功能裁剪

实测 4.0.313 免费版未编译以下模块,调用返回 `code=1003`(属预期,非 bug):

- `tcpdump` 抓包规则的 add/start/detail(列表与网口查询可用)
- `smbd` / `ftp_server` / `http_server`(本地文件服务)
- `pppoe_proxy_online`(代拨在线,企业版功能)
- `disk_mgmt`、`docker_*`、`appmarket_*`

对应工具的 docstring 已标注限制,失败时返回结构化说明。

## 错误码速查

客户端把设备的错误码原样带进异常信息,便于定位:

| code | 含义 | 常见原因 |
|------|------|---------|
| 0 | 成功 | — |
| 1003 | 函数不存在 | `func_name` 写错,或该固件未编译此模块 |
| 1005 | 账号或密码错误 | 检查 `.env` 的 `IKUAI_PASSWORD` |
| 1008 | 会话已过期 | 客户端会自动重登一次 |
| 2006 | 业务错误 | 参数值不被接受 |
| 2007 | TYPE 不合法 | 分页方言不匹配(`show_list` 已自动回退三档) |
| 2014 | 服务启动异常 | 如抓包规则创建失败 |
| 3001 | action 或参数不合法 | `action` 名错,或必填参数缺失 |

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
├── client.py        # API 客户端:自动登录/会话重试/兼容双格式/TYPE 回退
└── tools/           # 9 个工具模块(每个约 100-350 行)
```

## 常见问题

| 问题 | 解决 |
|------|------|
| 连不上路由器 | 检查 `IKUAI_URL`;确认电脑和路由器在同一网段 |
| 认证失败 | 浏览器登录一次验证密码;检查 `.env` 中 `IKUAI_PASSWORD` |
| `.env` 没生效 | 确保 `.env` 在项目根目录,或直接写进客户端 `env` 字段 |
| 报 `code=1003` | 该接口在此固件上不存在;对照上方「免费版功能裁剪」 |
| 报 `code=2007` | TYPE 方言问题,`show_list` 会自动回退;若仍失败请提 issue 附固件版本 |
| MCP 工具不显示 | 重启 AI 客户端后重试 |

## 贡献 & 许可

欢迎 PR,见 [CONTRIBUTING.md](CONTRIBUTING.md)。MIT License,见 [LICENSE](LICENSE)。
