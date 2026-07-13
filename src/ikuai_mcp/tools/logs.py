"""日志中心工具 — 认证/ARP/无线/DHCP/DDNS/外网拨号/通知/系统/操作/告警/消息 共 11 类日志"""


def register_tools(mcp, get_client):

    @mcp.tool(annotations={"readOnlyHint": True})
    def get_auth_log() -> dict:
        """获取认证日志（PPPoE/VPN 认证记录）"""
        return get_client().show_list("syslog-pppauth")

    @mcp.tool(annotations={"readOnlyHint": True})
    def get_arp_log() -> dict:
        """获取 ARP 日志"""
        return get_client().show_list("syslog-arp")

    @mcp.tool(annotations={"readOnlyHint": True})
    def get_wireless_terminal_log() -> dict:
        """获取无线终端日志"""
        return get_client().show_list("syslog-apaction")

    @mcp.tool(annotations={"readOnlyHint": True})
    def get_dhcp_log() -> dict:
        """获取 DHCP 日志"""
        return get_client().show_list("syslog-dhcpd")

    @mcp.tool(annotations={"readOnlyHint": True})
    def get_ddns_log() -> dict:
        """获取动态域名日志"""
        return get_client().show_list("syslog-ddns")

    @mcp.tool(annotations={"readOnlyHint": True})
    def get_wan_pppoe_log() -> dict:
        """获取外网拨号日志"""
        return get_client().show_list("syslog-wanpppoe")

    @mcp.tool(annotations={"readOnlyHint": True})
    def get_notification_log() -> dict:
        """获取推送通知日志"""
        return get_client().show_list("syslog-notice")

    @mcp.tool(annotations={"readOnlyHint": True})
    def get_system_event_log() -> dict:
        """获取系统事件日志（重启/升级等）"""
        return get_client().show_list("syslog-sysevent")

    @mcp.tool(annotations={"readOnlyHint": True})
    def get_admin_operation_log() -> dict:
        """获取管理员操作日志"""
        return get_client().show_list("syslog-webadmin")

    @mcp.tool(annotations={"readOnlyHint": True})
    def get_messages() -> dict:
        """获取消息通知"""
        return get_client().show_list("msgcenter")

    @mcp.tool(annotations={"readOnlyHint": True})
    def get_warnings() -> dict:
        """获取告警信息"""
        return get_client().show_list("warning")
