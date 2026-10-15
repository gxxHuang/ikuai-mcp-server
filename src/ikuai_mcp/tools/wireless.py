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
        """获取 Wi-Fi 基本设置（SSID/加密/信道）

        实测：设备用的是 ``wifi`` 而不是 ``wifiSettings``（后者返回 1003）。
        """
        return get_client().show("wifi", {"TYPE": "data"})

    @mcp.tool(annotations={"readOnlyHint": True})
    def get_wifi_all_settings() -> dict:
        """获取 Wi-Fi 全部设置（基础 + 高级 + 信道列表）"""
        return get_client().show("wifi", {"TYPE": "all"})

    @mcp.tool
    def set_wifi_ssid(ssid: str, radio: str = "2g") -> dict:
        """修改 Wi-Fi SSID"""
        return get_client().save_config("wifi", {"ssid": ssid, "radio": radio})

    @mcp.tool
    def set_wifi_password(password: str, radio: str = "2g") -> dict:
        """修改 Wi-Fi 密码 (至少8位)"""
        return get_client().save_config("wifi", {"passwd": password, "radio": radio})

    @mcp.tool
    def toggle_wifi(enabled: bool, radio: str = "2g") -> dict:
        """启用/禁用 Wi-Fi"""
        return get_client().call("wifi", "up" if enabled else "down", {"radio": radio})

    @mcp.tool(annotations={"readOnlyHint": True})
    def get_wifi_advanced_settings() -> dict:
        """获取 Wi-Fi 高级设置（信道/频宽/工作模式）"""
        return get_client().show("wifi", {"TYPE": "all"})

    # ═══ 周边信道扫描 ═══

    @mcp.tool(annotations={"readOnlyHint": True})
    def scan_surrounding_channels() -> dict:
        """扫描周边 AP 信道（读取扫描结果）

        实测：设备用 ``ac_scan_nearby_ap`` 而非 ``surroundingChannelScan``。
        本工具只读结果；启动扫描请用 ``start_channel_scan``。
        """
        return get_client().show("ac_scan_nearby_ap", {"TYPE": "total,data"})

    @mcp.tool
    def start_channel_scan() -> dict:
        """启动周边信道扫描"""
        return get_client().call("ac_scan_nearby_ap", "start", {})

    @mcp.tool(annotations={"readOnlyHint": True})
    def get_channel_scan_status() -> dict:
        """查询信道扫描进度"""
        return get_client().show("ac_scan_nearby_ap", {"TYPE": "scan_status"})

    @mcp.tool(annotations={"readOnlyHint": True})
    def scan_nearby_signals() -> dict:
        """扫描周边无线信号详情（含 BSSID/信号强度）"""
        return get_client().show("ac_scan_nearby_sig", {"TYPE": "data,total"})

    # ═══ Mesh 快连 ═══

    @mcp.tool(annotations={"readOnlyHint": True})
    def get_mesh_config() -> dict:
        """获取 Mesh 快连配置"""
        return get_client().show_list("mesh", paginate=False)

    # ═══ 终端 VLAN ═══

    @mcp.tool(annotations={"readOnlyHint": True})
    def list_wireless_vlans() -> dict:
        """列出无线终端 VLAN 配置"""
        return get_client().show_list("wls_mvlan", paginate=False)

    # ═══ 黑白名单 ═══

    @mcp.tool(annotations={"readOnlyHint": True})
    def list_wireless_blackwhite_list() -> dict:
        """列出无线黑白名单"""
        return get_client().show_list("wls_black", paginate=False)

    # ═══ 无线网优 ═══

    @mcp.tool(annotations={"readOnlyHint": True})
    def get_ap_optimization() -> dict:
        """获取无线网优状态

        实测：设备用 ``ac_net_optimize`` 而非 ``ap_optimization``。
        """
        return get_client().show("ac_net_optimize", {"TYPE": "status,process,total,data"})

    @mcp.tool(annotations={"readOnlyHint": True})
    def get_optimization_records() -> dict:
        """获取网优记录"""
        return get_client().show_list("ac_net_optimize", paginate=False)

    @mcp.tool(annotations={"readOnlyHint": True})
    def get_ac_status() -> dict:
        """获取 AC 控制器状态（AP 数量/在线数）"""
        return get_client().show("ac_status", {"TYPE": "all"})
