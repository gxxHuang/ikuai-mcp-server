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
        return get_client().edit("netsnmp", {"enabled": 1 if enabled else 0, "community": community})

    # ═══ 本地服务 ═══

    @mcp.tool(annotations={"readOnlyHint": True})
    def list_local_services() -> dict:
        """列出本地服务状态（FTP/Samba/HTTP）"""
        c = get_client()
        services = {}
        for svc in ["ftp_server", "samba_server", "http_server"]:
            try:
                services[svc] = c.show_list(svc)
            except Exception:
                services[svc] = {"status": "unknown"}
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
        """获取抓包工具配置"""
        return get_client().show_list("tcpdump")

    # ═══ 流表查看 ═══

    @mcp.tool(annotations={"readOnlyHint": True})
    def get_connection_table() -> dict:
        """获取流表/连接查看"""
        return get_client().call("collect_conn", "start", {})

    # ═══ Ping 测试 ═══

    @mcp.tool
    def ping_test(target: str, count: int = 4, interface: str = "") -> dict:
        """执行 Ping 测试

        Args:
            target: 目标 IP 或域名
            count: 发包次数
            interface: 出口接口
        """
        return get_client().call("Ping", "ping", {"host": target, "count": count, "interface": interface})

    # ═══ 路由追踪 ═══

    @mcp.tool
    def traceroute(target: str, interface: str = "") -> dict:
        """执行 Traceroute 路由追踪

        Args:
            target: 目标 IP 或域名
            interface: 出口接口
        """
        return get_client().call("Traceroute", "trace", {"host": target, "interface": interface})

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
    def subnet_calculator(ip: str, mask: str) -> dict:
        """子网换算工具

        Args:
            ip: IP 地址
            mask: 子网掩码
        """
        return get_client().call("subnet", "calc", {"ip": ip, "mask": mask})

    # ═══ 固件升级 ═══

    @mcp.tool(annotations={"readOnlyHint": True})
    def get_firmware_version() -> dict:
        """获取当前固件版本"""
        return get_client().show("upgrade", {"TYPE": "version"})

    @mcp.tool
    def start_firmware_upgrade(confirm: bool = False) -> dict:
        """开始固件升级 ⚠️⚠️ 路由器会重启断网！"""
        if not confirm:
            return {"error": "请设置 confirm=True 确认固件升级"}
        return get_client().call("upgrade", "start", {})

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
