"""系统监控工具 — 系统概览、线路监控、终端监控、行为洞察、负载监控、分流监控等"""


def register_tools(mcp, get_client):

    # ─── 系统概览 ───

    @mcp.tool(annotations={"readOnlyHint": True})
    def get_system_overview() -> dict:
        """获取系统概览：CPU/内存/流量/版本/运行时间/在线用户"""
        return get_client().show("homepage", {"TYPE": "sysstat"})

    @mcp.tool(annotations={"readOnlyHint": True})
    def get_wan_status() -> dict:
        """获取 WAN 口实时状态：IP/速率/连接数/AC 状态"""
        return get_client().show("homepage", {"TYPE": "wan_speed,sysstat,ac_status", "interface": ""})

    @mcp.tool(annotations={"readOnlyHint": True})
    def get_memory_history(datetype: str = "day-5min") -> dict:
        """获取内存历史使用数据

        Args:
            datetype: 时间粒度 "day-5min" / "hour-1min" / "week-30min"
        """
        return get_client().show("homepage", {"TYPE": "memory", "datetype": datetype})

    # ─── 线路监控 ───

    @mcp.tool(annotations={"readOnlyHint": True})
    def get_line_monitoring() -> dict:
        """获取线路监控：所有 WAN/LAN 接口实时速率/连接数/丢包率"""
        return get_client().show("monitor_iface", {"TYPE": "iface_stream"})

    @mcp.tool(annotations={"readOnlyHint": True})
    def get_ipv6_line_detail() -> dict:
        """获取 IPv6 线路详情"""
        return get_client().show("ipv6_stream", {"TYPE": "stream"})

    # ─── 无线监控 ───

    @mcp.tool(annotations={"readOnlyHint": True})
    def get_wireless_monitoring() -> dict:
        """获取无线监控：AP 数量/在线状态"""
        return get_client().show("homepage", {"TYPE": "wan_speed,sysstat,ac_status", "interface": "wan2"})

    # ─── 终端监控 ───

    @mcp.tool(annotations={"readOnlyHint": True})
    def get_terminal_list(ip_type: str = "v4", offset: int = 0, limit: int = 500) -> dict:
        """获取终端监控列表：所有在线设备 IP/MAC/主机名/流量/连接数

        Args:
            ip_type: "v4" 或 "v6"
            offset: 分页偏移
            limit: 每页数量
        """
        fn = "monitor_lanip" if ip_type == "v4" else "monitor_lanipv6"
        return get_client().show_list(fn, offset=offset, limit=limit)

    # ─── 行为洞察 ───

    @mcp.tool(annotations={"readOnlyHint": True})
    def get_registration_status() -> dict:
        """获取云服务注册/绑定状态 (faststart)"""
        return get_client().show("faststart", {"TYPE": "register"})

    @mcp.tool(annotations={"readOnlyHint": True})
    def get_behavior_insight() -> dict:
        """获取行为洞察：应用协议流量历史数据"""
        return get_client().show("monitor_app_flow", {"TYPE": "proto1_flow_history"})

    # ─── 策略监控 ───

    @mcp.tool(annotations={"readOnlyHint": True})
    def get_policy_monitoring() -> dict:
        """获取策略监控：L7 QoS 流控策略执行状态"""
        return get_client().show("monitor_l7qos", {"TYPE": "interface"})

    # ─── 负载监控 ───

    @mcp.tool(annotations={"readOnlyHint": True})
    def get_load_monitoring() -> dict:
        """获取负载监控：CPU/内存/实时流量"""
        return get_client().show("monitor_system", {"TYPE": "cpu,memory,stream"})

    @mcp.tool(annotations={"readOnlyHint": True})
    def get_cpu_temperature_support() -> dict:
        """查询 CPU 温度检测是否支持"""
        return get_client().show("monitor_system", {"TYPE": "cputemp_support"})

    # ─── 分流监控 ───

    @mcp.tool(annotations={"readOnlyHint": True})
    def get_diversion_monitoring() -> dict:
        """获取分流监控状态"""
        return get_client().show_list("cflow")

    # ─── 下联设备 ───

    @mcp.tool(annotations={"readOnlyHint": True})
    def get_camera_devices() -> dict:
        """获取下联摄像头设备列表"""
        return get_client().show_list("camera")

    @mcp.tool(annotations={"readOnlyHint": True})
    def get_managed_switches() -> dict:
        """获取下联交换机设备列表"""
        return get_client().show_list("cloud_switch")

    @mcp.tool(annotations={"readOnlyHint": True})
    def get_peripheral_devices() -> dict:
        """获取周边设备列表"""
        return get_client().show_list("dev_control")

    # ─── 消息通知 ───

    @mcp.tool(annotations={"readOnlyHint": True})
    def get_notifications() -> dict:
        """获取消息通知列表"""
        return get_client().show_list("ikmessages")
