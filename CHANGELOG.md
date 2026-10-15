# 更新日志

## [1.0.1] - 2026-10-15

针对 **IK-Q3000 / 固件 4.0.313 x64 (arm, 免费版)** 做全量实机审计后修复。
审计覆盖 156 个声明的 `func_name`，逐一对真机调用验证，发现 **19 个接口不存在**
（返回 `code=1003`），另有若干端点用错 `TYPE`/`action`。

### 🔴 修复：致命 — 登录失败被静默吞掉

`client.py` 的登录校验写成：

```python
if data.get("code") != 0 and data.get("Result") != 10000:   # ❌
```

设备在**密码错误**时返回：

```json
{"code":1005,"message":"账号或密码错误","Result":10000}
```

求值 `(1005 != 0) and (10000 != 10000)` → `True and False` → **False**，于是
不抛异常，还打印 `登录成功`。密码错、账号不存在、账号被锁全部被当成登录成功，
后续每个接口才零散报错，排查方向被完全带偏。

`Result:10000` 在成功与失败时**都会返回**，是无条件回显字段，不能参与判断。
现已改为唯一判据 `code == 0`（极旧固件不带 `code` 时才回退到 `Result + ErrMsg`）。

同时补充：HTTP 401/302 处理、非 JSON 响应、`1008 会话已过期` 自动重登、
`RequestException` 包装，以及关闭自签证书的重复告警刷屏。

### 🟠 修复：接口名与参数（原调用在真机上全部失效）

| 工具 | 原来 | 实际返回 | 修复为 |
|---|---|---|---|
| `get_firmware_version` | `upgrade` + `TYPE=version` | `2007 unknown TYPE` | `TYPE=data` |
| `start_firmware_upgrade` | `upgrade/start` | `3001 invalid action` | `upgrade/update_file` |
| `ping_test` | `Ping/ping` | `3001 invalid action` | `Ping/start` |
| `traceroute` | `Traceroute/trace` | `3001 invalid action` | `Traceroute/start` |
| `get_wifi_basic_settings` | `wifiSettings` | `1003 Access denied` | `wifi` |
| `get_wifi_advanced_settings` | `wifiAdvancedSettings` | `1003` | `wifi` (`TYPE=all`) |
| `scan_surrounding_channels` | `surroundingChannelScan` | `1003` | `ac_scan_nearby_ap` |
| `get_ap_optimization` | `ap_optimization` | `1003` | `ac_net_optimize` |
| `list_tasks` | `task_management` | `1003` | `task_queue` |
| `list_proxy_dial_accounts` | `pppoe_proxy_user` | `1003` | `pppoe_proxy` |
| `get_traffic_audit_by_mac/user` | `audit_terminal_stat_mac/_user` | `1003` | `audit_terminal_stat` |
| `get_ipv6_wan/lan_config` | `ipv6_extranet/intranet_setting` | `1003` | `ipv6` |
| `list_vpn_accounts` | `pptp_user`/`l2tp_user`/… | `1003` | `pptp_client`/`l2tp_client`/… |
| `list_local_services` | `samba_server` | `1003` | `smbd` |
| `get_routing_table` | `static_rt_table_ipv4/ipv6` | `1003` | `static_rt` / `ipv6_static` |
| `subnet_calculator` | 设备无 `subnet` | `1003` | 改为本地计算 |
| `get_connection_table` | `collect_conn/start` | 不返回数据 | `collect_conn` + `TYPE=all` |
| `get_system_overview` | `homepage` + `TYPE=sysstat` | `2007` | `sysstat` + `TYPE=all` |

**`Ping` 的隐藏要求**：必须带全部 7 个字段，且 `interface` 不能为空，
否则一律 `3001 请求参数不合法`。正确形态：
`{host, interface, count, proto, l4proto, port, dns}`，实测
`interface="wan1"` 通过、`""` 失败。

### 🟠 修复：`show_list` 的 TYPE 方言不兼容

同一批 `func_name` 里，一部分只认 `TYPE=total,data`，一部分只认空参数 `{}`，
还有一部分要 `TYPE=all`（如 `wifi`/`alg`/`mesh` 只认空参，`dns`/`collect_conn` 只认
`all`）。统一硬塞 `total,data` 会让大量接口返回 `2007 unknown TYPE`。

`show_list` 现按 **分页参数 → 空参数 → `TYPE=all`** 依次回退，只对 `2007` 重试，
其它错误（如 `1003`）立即抛出；并新增 `paginate=False` 便于已知只要空参的接口
省掉一次探测请求。

### 🟢 新增工具（本次实机验证可用）

- `get_ota_info` — 完整 OTA 信息（版本 + 本地固件文件状态）
- `check_firmware_update` — 只读检查新版本（`check_newest_ver`）
- `get_auto_upgrade_status` / `get_cloud_sync_status` — 自动升级与云同步开关
- `clean_firmware_files` — 清理已下载固件
- `ping_result` / `stop_ping` / `get_ping_interfaces` — Ping 结果与生命周期
- `traceroute_result` / `stop_traceroute` — Traceroute 结果与停止
- `get_capture_interfaces` — 抓包可用网口
- `start_channel_scan` / `get_channel_scan_status` / `scan_nearby_signals` — 信道扫描
- `get_ac_status` — AC 控制器状态
- `get_version_info` — 版本信息快捷入口
- `retry_task` / `abort_task` — 任务队列操作
- `get_wifi_all_settings` — Wi-Fi 全量设置（基础+高级+信道列表）

工具总数：**229 → 248**

### ⚠️ 已知限制（免费版功能裁剪，已在 docstring 标注）

实测 4.0.313 免费版未编译这些模块，调用返回 `1003`，属预期而非 bug：
`tcpdump` 的 `add`/`start`/`detail`（抓包规则创建）、`smbd`/`ftp_server`/`http_server`
（本地文件服务）、`pppoe_proxy_online`（代拨在线，企业版）、`disk_mgmt`、
`docker_*`、`appmarket_*` 等。

对应工具的 docstring 已写明限制，失败时返回结构化说明而非静默异常。

### 🧪 测试

- 测试数 **12 → 52**，覆盖：登录判据回归、`Result:10000` 陷阱、401/302 处理、
  会话过期重登、`show_list` 三档回退、`1003` 不重试、`save_config` 合并语义、
  端点名回归守卫（对 15 组「旧名→新名」做静态断言，已用变异测试验证有效）。
- 回归守卫能捕获重新引入的废弃端点名。

### 📌 审计方法

设备前端 394 个懒加载 chunk 中含权威 `func_name` 全集（243 个），
以「设备前端声明 ∩ 后端实际响应」交叉比对定位错误。错误码语义：

| code | 含义 |
|---|---|
| 0 | 成功 |
| 1003 | 函数不存在（名字错） |
| 1005 | 账号或密码错误 |
| 1008 | 会话已过期 |
| 2006 | 业务错误 |
| 2007 | 函数存在但 TYPE 不合法 |
| 2014 | 服务启动异常 |
| 2022 | 升级未成功 |
| 3001 | action 不合法 / 参数不合法 |

### 🔧 发布后补修

**HTTP 传输模式此前不生效。** `server.py` 的 `main()` 只有一句 `mcp.run()`，
没有参数解析，README 与模块 docstring 里宣传的
`python -m ikuai_mcp.server --transport http --port 8000` 会被**静默忽略** ——
实测日志输出 `with transport 'stdio'`，8000 端口无监听，进程在 stdin EOF 后退出。
现已补上 `argparse`，支持 `--transport {stdio,http,sse,streamable-http}`
与 `--host` / `--port`，默认仍是 stdio。

**逐模块工具数与代码不符。** 总数 248 正确，但 3 个模块的分项数字与
实际注册数对不上（-1 / -1 / +2，正好抵消）：

| 模块 | 原文档 | 实际 |
|---|---|---|
| 系统监控 | 19 | **18** |
| 无线服务 | 22 | **21** |
| 高级服务 | 30 | **32** |

README 的「功能覆盖」表与 `docs/COVERAGE.md` 已按实际注册数订正，
并补齐了此前遗漏的工具名描述（如 `get_memory_history`、`get_policy_monitoring`、
`get_backup_snapshots`、`get_reboot_schedule`、`reboot_router` 等）。

> 订正依据：拉取 tag `v1.0.1` 源码在 Python 3.12 + fastmcp 4.1.0 下实装，
> 逐模块注册后计数并与 248 个工具名逐一核对。

---

## [1.0.0] - 2026-07-13

### 新增
- 🎉 首次发布
- 229 个 MCP 工具，覆盖 iKuai 4.0.303 Web 后台全部功能
- 9 个功能模块：系统监控、网络配置、安全管控、流控分流、认证计费、无线服务、高级服务、日志中心、设备设置
- 支持 stdio 和 HTTP 传输
- 通过 Chrome DevTools 分析完整 API (149 func_names)
- 三层安全设计：只读标记、二次确认、凭据隔离

### 系统监控
- 系统概览、线路监控、终端监控（IPv4/IPv6）
- 行为洞察、策略监控、负载监控、分流监控
- 下联设备管理（摄像头/交换机/周边设备）

### 网络配置
- WAN/LAN 接口管理、IPv6 内/外网设置
- VLAN、DHCP（服务端/静态分配/租约/黑白名单）
- DNS 加速/多线路、静态路由、路由表
- 端口映射 (DNAT)、NAT 规则、DMZ、UPnP
- 路由对象（IP/MAC/域名/协议/端口/时间分组）
- 自定义协议/高级协议、组播管理 (IGMP/IPTV/UDPXY)
- SD-WAN、动态域名 (DDNS)

### 安全管控
- ACL 规则（增删改查+启用/禁用）
- 连接数限制、ARP 绑定、IPv6 邻居
- MAC 访问控制
- 网址浏览控制（黑白名单/禁止娱乐/自定义库 3个tab）
- URL 控制（跳转/关键字替换/参数替换 3个tab）
- 应用协议控制 (L7 ACL)
- 网络分享控制、行为记录/流量审计
- 终端名称管理、安全高级设置

### 流控分流
- 智能流控（线路/优先域名/独立限速/策略 4个tab）
- IP/MAC 终端限速
- 多线负载、协议/端口/域名分流
- 上下行分离、自定义运营商

### 认证计费
- 在线用户管理、Web 认证
- PPPoE 服务端/账号管理
- VPN 服务端（PPTP/L2TP/OpenVPN/IKEv2/WireGuard）
- VPN 账号管理、套餐管理
- 代拨服务、通知推送（实时/定期/到期/拨号过期）

### 无线服务
- AP 列表/配置/固件升级
- WiFi 基本/高级设置、信道扫描
- 终端 VLAN、无线黑白名单
- AP 优化、Mesh 快连

### 设备设置
- 基础设置、双机热备 (VRRP)
- 固件升级、配置快照、重启计划
- 云服务绑定、密码管理、API 令牌
- SSH/Telnet/FTP 远程服务管理
- ALG/协议控制/内核设置

### 其他
- 11 类系统日志
- Ping/Traceroute/iPerf/测速/子网换算/WOL
- 路由体检、抓包工具
