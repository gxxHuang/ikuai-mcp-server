"""高级服务工具 — SNMP/本地服务/内网穿透/路由体检/健康检测/工具包(抓包/测速/Ping/Trace/吞吐/子网换算/网络唤醒)"""


def register_tools(mcp, get_client):

    # ═══ SNMP ═══

    @mcp.tool(annotations={"readOnlyHint": True})
    def get_snmp_config() -> dict:
        """获取 SNMP 服务配置"""
        return get_client().show_list("netsnmp")

    @mcp.tool
    def set_snmp(enabled: bool, community: str = "public") -> dict:
        """配置 SNMP"""
        return get_client().save_config("netsnmp", {"enabled": 1 if enabled else 0, "community": community})

    # ═══ 本地服务 ═══

    @mcp.tool(annotations={"readOnlyHint": True})
    def list_local_services() -> dict:
        """列出本地服务状态（Samba/FTP/HTTP）

        注意：免费版固件（实测 4.0.313）未编译这些服务端模块，会返回
        ``code=1003 Access denied``。企业版可用。
        """
        c = get_client()
        services = {}
        for label, fn in (("samba", "smbd"), ("ftp", "ftp_server"), ("http", "http_server")):
            try:
                services[label] = c.show(fn, {"TYPE": "data"})
            except Exception as e:
                services[label] = {"status": "unsupported", "detail": str(e)[:120]}
        return services

    # ═══ 内网穿透 ═══

    @mcp.tool(annotations={"readOnlyHint": True})
    def get_intranet_penetration_config() -> dict:
        """获取内网穿透配置"""
        return get_client().show_list("nat_ddns")

    # ═══ 路由体检 ═══

    @mcp.tool(annotations={"readOnlyHint": True})
    def run_router_health_report() -> dict:
        """运行路由体检"""
        return get_client().show_list("iksyscheck")

    # ═══ 健康检测 ═══

    @mcp.tool(annotations={"readOnlyHint": True})
    def get_health_check_config() -> dict:
        """获取健康检测配置"""
        return get_client().show_list("watchdog")

    # ═══ 抓包工具 ═══

    @mcp.tool(annotations={"readOnlyHint": True})
    def get_tcpdump_config() -> dict:
        """获取抓包工具配置

        注意：实测 4.0.313 免费版的 tcpdump 模块是裁剪版——
        ``show TYPE=data,total`` 与 ``TYPE=interface`` 可用，但
        ``add``/``start``/``TYPE=detail`` 均不可用（返回 3001/2014/2007）。
        """
        return get_client().show("tcpdump", {"TYPE": "data,total"})

    @mcp.tool(annotations={"readOnlyHint": True})
    def get_capture_interfaces() -> dict:
        """获取可抓包的网络接口列表"""
        return get_client().show("tcpdump", {"TYPE": "interface"})

    # ═══ 流表查看 ═══

    @mcp.tool(annotations={"readOnlyHint": True})
    def get_connection_table() -> dict:
        """获取流表/连接查看（当前实时连接）"""
        return get_client().show("collect_conn", {"TYPE": "all"})

    # ═══ Ping 测试 ═══

    @mcp.tool(annotations={"readOnlyHint": True})
    def ping_test(host: str, interface: str = "wan1", count: int = 4,
                  proto: str = "ipv4", l4proto: str = "icmp",
                  port: str = "", dns: str = "") -> dict:
        """执行 Ping 测试

        实测（IK-Q3000 / 4.0.313）：必须带全部字段，且 ``interface`` 不能为空，
        否则返回 ``3001 请求参数不合法``。结果通过 ``ping_result`` 读取。

        Args:
            host: 目标 IP 或域名
            interface: 出口接口，如 "wan1"/"lan1"（必需，不能为空）
            count: 发包次数
            proto: 协议族 "ipv4" 或 "ipv6"
            l4proto: 传输层协议 "icmp"/"tcp"/"udp"
            port: 端口（l4proto 为 tcp/udp 时使用）
            dns: 反向解析用 DNS
        """
        return get_client().call("Ping", "start", {
            "host": host, "interface": interface, "count": count,
            "proto": proto, "l4proto": l4proto, "port": port, "dns": dns,
        })

    @mcp.tool(annotations={"readOnlyHint": True})
    def ping_result() -> dict:
        """读取 Ping 测试结果"""
        return get_client().show("Ping", {})

    @mcp.tool
    def stop_ping() -> dict:
        """停止 Ping 测试"""
        return get_client().call("Ping", "stop", {})

    @mcp.tool(annotations={"readOnlyHint": True})
    def get_ping_interfaces() -> dict:
        """获取 Ping 可用出口接口"""
        return get_client().show("Ping", {"TYPE": "interface"})

    # ═══ 路由追踪 ═══

    @mcp.tool
    def traceroute(host: str, interface: str = "wan1", max_hops: int = 5,
                   wait: int = 3, dns: str = "") -> dict:
        """执行 Traceroute 路由追踪

        实测：``max`` 为最大跳数（默认 5），``wait`` 为超时秒数（默认 3）。
        该调用为长任务，设备可能不立即返回，用 ``traceroute_result`` 读取结果。

        Args:
            host: 目标 IP 或域名
            interface: 出口接口
            max_hops: 最大跳数
            wait: 每跳等待秒数
            dns: 反向解析用 DNS
        """
        return get_client().call("Traceroute", "start", {
            "host": host, "interface": interface,
            "max": max_hops, "wait": wait, "dns": dns,
        }, timeout=90)

    @mcp.tool(annotations={"readOnlyHint": True})
    def traceroute_result() -> dict:
        """读取 Traceroute 结果"""
        return get_client().show("Traceroute", {"TYPE": "data"})

    @mcp.tool
    def stop_traceroute() -> dict:
        """停止 Traceroute"""
        return get_client().call("Traceroute", "stop", {})

    # ═══ 端口镜像 ═══

    @mcp.tool(annotations={"readOnlyHint": True})
    def get_port_mirror_config() -> dict:
        """获取端口镜像配置"""
        return get_client().show_list("port_mirror")

    # ═══ 动态域名 ═══

    @mcp.tool(annotations={"readOnlyHint": True})
    def get_dynamic_dns_config() -> dict:
        """获取动态域名 (DDNS) 配置"""
        return get_client().show_list("ddns")

    # ═══ 网络唤醒 ═══

    @mcp.tool
    def wake_on_lan(mac: str, interface: str = "lan1") -> dict:
        """发送网络唤醒包 (Wake-on-LAN)

        Args:
            mac: 目标 MAC，如 "AA:BB:CC:DD:EE:FF"
            interface: 发送接口
        """
        return get_client().call("wakeup", "wake", {"mac": mac, "interface": interface})

    # ═══ 吞吐测试 ═══

    @mcp.tool
    def iperf_test(server: str, port: int = 5201, duration: int = 10, interface: str = "") -> dict:
        """执行 iPerf 吞吐测试

        Args:
            server: iPerf 服务器 IP
            port: 端口
            duration: 测试时长(秒)
            interface: 出口接口
        """
        return get_client().call("iperf", "test", {"server": server, "port": port, "time": duration, "interface": interface})

    # ═══ 线路测速 ═══

    @mcp.tool
    def speed_test(interface: str = "wan2") -> dict:
        """执行线路测速

        Args:
            interface: WAN 接口
        """
        return get_client().call("speedtest", "test", {"interface": interface})

    # ═══ 子网换算 ═══

    @mcp.tool(annotations={"readOnlyHint": True})
    def subnet_calculator(ip: str, mask: str = "255.255.255.0") -> dict:
        """子网换算工具（本地计算，不依赖设备）

        设备侧没有 ``subnet`` func_name（实测 4.0.313 返回 1003），
        因此该工具在本地完成换算。

        Args:
            ip: IP 地址，如 "192.168.9.101"
            mask: 子网掩码 "255.255.255.0" 或前缀长度 "24"
        """
        import ipaddress

        try:
            iface = ipaddress.ip_interface(f"{ip}/{mask}")
        except ValueError as e:
            return {"error": f"无效的 IP 或掩码: {e}"}

        net = iface.network
        hosts = list(net.hosts())
        return {
            "ip": str(iface.ip),
            "netmask": str(net.netmask),
            "prefix_length": net.prefixlen,
            "network": str(net.network_address),
            "broadcast": str(net.broadcast_address),
            "first_host": str(hosts[0]) if hosts else None,
            "last_host": str(hosts[-1]) if hosts else None,
            "total_addresses": net.num_addresses,
            "usable_hosts": max(0, net.num_addresses - 2),
            "is_private": iface.ip.is_private,
            "version": iface.version,
        }

    # ═══ 固件升级 ═══

    @mcp.tool(annotations={"readOnlyHint": True})
    def get_firmware_version() -> dict:
        """获取固件版本与可用升级信息

        返回 ``system_ver``（当前版本）、``new_system_ver``（可用新版本）、
        ``update_content``（更新说明）、``firmware_channel`` 等字段。
        """
        return get_client().show("upgrade", {"TYPE": "data"})

    @mcp.tool(annotations={"readOnlyHint": True})
    def get_ota_info() -> dict:
        """获取完整 OTA 信息（版本 + 本地固件文件状态）"""
        return get_client().show("upgrade", {"TYPE": "data,fileinfo"})

    @mcp.tool(annotations={"readOnlyHint": True})
    def check_firmware_update() -> dict:
        """检查是否有新固件（只读，不触发下载与安装）"""
        return get_client().call("upgrade", "check_newest_ver", {}, timeout=60)

    @mcp.tool(annotations={"readOnlyHint": True})
    def get_auto_upgrade_status() -> dict:
        """获取自动升级状态"""
        return get_client().show("upgrade", {"TYPE": "auto_upgrade"})

    @mcp.tool(annotations={"readOnlyHint": True})
    def get_cloud_sync_status() -> dict:
        """获取固件云同步开关状态"""
        return get_client().show("upgrade", {"TYPE": "cloud_sync"})

    @mcp.tool
    def start_firmware_upgrade(confirm: bool = False) -> dict:
        """安装已下载的固件包 ⚠️⚠️ 路由器会重启断网 1-2 分钟

        前提：本地已有固件文件（``get_ota_info`` 的 ``fileinfo`` 非空）。
        未下载固件时设备返回 ``2022 升级未成功，系统保持当前版本``。

        Args:
            confirm: 必须设为 True 才会执行
        """
        if not confirm:
            return {"error": "请设置 confirm=True 确认固件升级（路由器将重启断网）"}
        return get_client().call("upgrade", "update_file", {}, timeout=300)

    @mcp.tool
    def clean_firmware_files(confirm: bool = False) -> dict:
        """清理已下载的固件文件

        Args:
            confirm: 必须设为 True 才会执行
        """
        if not confirm:
            return {"error": "请设置 confirm=True 确认清理固件文件"}
        return get_client().call("upgrade", "clean_file", {})

    # ═══ 配置备份 ═══

    @mcp.tool(annotations={"readOnlyHint": True})
    def get_backup_snapshots() -> dict:
        """获取版本快照列表"""
        return get_client().show_list("backup")

    # ═══ 重启计划 ═══

    @mcp.tool(annotations={"readOnlyHint": True})
    def get_reboot_schedule() -> dict:
        """获取重启计划"""
        return get_client().show_list("reboots")

    # ═══ 路由器重启 ═══

    @mcp.tool
    def reboot_router(confirm: bool = False) -> dict:
        """重启路由器 ⚠️ 断网 1-2 分钟"""
        if not confirm:
            return {"error": "请设置 confirm=True 确认重启"}
        return get_client().call("sysstat", "reboot", {})
