"""无线服务工具 — AP管理(列表/配置/升级)/WiFi设置/高级设置/Mesh/信道扫描/终端VLAN/黑白名单/优化"""


def register_tools(mcp, get_client):

    # ═══ AP 管理 ═══

    @mcp.tool(annotations={"readOnlyHint": True})
    def list_ap_devices() -> dict:
        """列出 AP 设备列表（状态/型号/客户端数）"""
        return get_client().show_list("ac_server")

    @mcp.tool(annotations={"readOnlyHint": True})
    def get_ap_group_config() -> dict:
        """获取 AP 分组配置"""
        return get_client().show_list("ac_group")

    @mcp.tool
    def restart_ap(ap_id: int) -> dict:
        """重启指定 AP"""
        return get_client().call("ac_server", "edit", {"id": ap_id, "action": "reboot"})

    @mcp.tool(annotations={"readOnlyHint": True})
    def get_ap_firmware_versions() -> dict:
        """获取 AP 固件版本列表"""
        return get_client().show_list("ac_upgrade")

    @mcp.tool
    def upgrade_ap_firmware(ap_id: int, version: str, confirm: bool = False) -> dict:
        """升级 AP 固件 ⚠️ AP 会重启"""
        if not confirm:
            return {"error": "请设置 confirm=True 确认"}
        return get_client().call("ac_upgrade", "upgrade", {"id": ap_id, "version": version})

    # ═══ WiFi 设置 ═══

    @mcp.tool(annotations={"readOnlyHint": True})
    def get_wifi_basic_settings() -> dict:
        """获取 Wi-Fi 基本设置（SSID/加密/信道）"""
        return get_client().show_list("wifiSettings")

    @mcp.tool
    def set_wifi_ssid(ssid: str, radio: str = "2g") -> dict:
        """修改 Wi-Fi SSID"""
        return get_client().edit("wifiSettings", {"ssid": ssid, "radio": radio})

    @mcp.tool
    def set_wifi_password(password: str, radio: str = "2g") -> dict:
        """修改 Wi-Fi 密码 (至少8位)"""
        return get_client().edit("wifiSettings", {"passwd": password, "radio": radio})

    @mcp.tool
    def toggle_wifi(enabled: bool, radio: str = "2g") -> dict:
        """启用/禁用 Wi-Fi"""
        return get_client().call("wifiSettings", "up" if enabled else "down", {"radio": radio})

    @mcp.tool(annotations={"readOnlyHint": True})
    def get_wifi_advanced_settings() -> dict:
        """获取 Wi-Fi 高级设置"""
        return get_client().show_list("wifiAdvancedSettings")

    # ═══ 周边信道扫描 ═══

    @mcp.tool(annotations={"readOnlyHint": True})
    def scan_surrounding_channels() -> dict:
        """扫描周边信道"""
        return get_client().show_list("surroundingChannelScan")

    # ═══ Mesh 快连 ═══

    @mcp.tool(annotations={"readOnlyHint": True})
    def get_mesh_config() -> dict:
        """获取 Mesh 快连配置"""
        return get_client().show_list("mesh")

    # ═══ 终端 VLAN ═══

    @mcp.tool(annotations={"readOnlyHint": True})
    def list_wireless_vlans() -> dict:
        """列出无线终端 VLAN 配置"""
        return get_client().show_list("wls_mvlan")

    # ═══ 黑白名单 ═══

    @mcp.tool(annotations={"readOnlyHint": True})
    def list_wireless_blackwhite_list() -> dict:
        """列出无线黑白名单"""
        return get_client().show_list("wls_black")

    # ═══ 无线网优 ═══

    @mcp.tool(annotations={"readOnlyHint": True})
    def get_ap_optimization() -> dict:
        """获取 AP 优化状态"""
        return get_client().show_list("ap_optimization")

    @mcp.tool(annotations={"readOnlyHint": True})
    def get_optimization_records() -> dict:
        """获取优化记录"""
        return get_client().show_list("ac_net_optimize")
