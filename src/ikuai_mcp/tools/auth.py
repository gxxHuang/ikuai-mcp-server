"""认证计费工具 — 在线用户/Web认证/PPPoE/VPN服务端/套餐/账号/代拨/通知推送"""


def register_tools(mcp, get_client):

    # ═══ 账号在线用户 ═══

    @mcp.tool(annotations={"readOnlyHint": True})
    def list_pppoe_online_users() -> dict:
        """列出当前在线账号"""
        return get_client().show_list("ppp_online")

    @mcp.tool
    def kick_pppoe_user(username: str) -> dict:
        """踢下线指定用户"""
        c = get_client()
        users = c.show_list("ppp_online")
        for u in users.get("data", []):
            if u.get("user") == username:
                return c.call("ppp_online", "del", {"id": u.get("id")})
        return {"error": f"未找到在线用户: {username}"}

    # ═══ Web 认证服务 ═══

    @mcp.tool(annotations={"readOnlyHint": True})
    def get_web_auth_config() -> dict:
        """获取 Web 认证服务配置"""
        return get_client().show_list("webauth")

    @mcp.tool
    def toggle_web_auth(enabled: bool) -> dict:
        """启用/禁用 Web 认证"""
        return get_client().call("webauth", "up" if enabled else "down", {})

    # ═══ VPN 服务端 ═══

    @mcp.tool(annotations={"readOnlyHint": True})
    def list_vpn_servers() -> dict:
        """列出所有 VPN 服务端状态"""
        c = get_client()
        result = {}
        for fn in ["pptp_server", "l2tp_server", "openvpn-server", "ike_server", "wireguard"]:
            try:
                result[fn] = c.show_list(fn)
            except Exception:
                result[fn] = {"status": "unknown"}
        return result

    @mcp.tool(annotations={"readOnlyHint": True})
    def get_pppoe_server_config() -> dict:
        """获取 PPPoE 服务端配置"""
        return get_client().show_list("pppoe_server")

    @mcp.tool
    def toggle_pppoe_server(enabled: bool) -> dict:
        """启用/禁用 PPPoE 服务端"""
        return get_client().call("pppoe_server", "up" if enabled else "down", {})

    @mcp.tool(annotations={"readOnlyHint": True})
    def get_pptp_server_config() -> dict:
        """获取 PPTP 服务端配置"""
        return get_client().show_list("pptp_server")

    @mcp.tool(annotations={"readOnlyHint": True})
    def get_l2tp_server_config() -> dict:
        """获取 L2TP 服务端配置"""
        return get_client().show_list("l2tp_server")

    @mcp.tool(annotations={"readOnlyHint": True})
    def get_openvpn_server_config() -> dict:
        """获取 OpenVPN 服务端配置"""
        return get_client().show_list("openvpn-server")

    @mcp.tool(annotations={"readOnlyHint": True})
    def get_ike_server_config() -> dict:
        """获取 IKEv2/IPSec 服务端配置"""
        return get_client().show_list("ike_server")

    @mcp.tool
    def toggle_vpn_server(vpn_type: str, enabled: bool) -> dict:
        """启用/禁用 VPN 服务端"""
        type_map = {"pptp": "pptp_server", "l2tp": "l2tp_server", "openvpn": "openvpn-server", "wireguard": "wireguard"}
        fn = type_map.get(vpn_type)
        if not fn:
            return {"error": f"不支持的 VPN: {vpn_type}"}
        return get_client().call(fn, "up" if enabled else "down", {})

    # ═══ 认证账号管理 ═══

    @mcp.tool(annotations={"readOnlyHint": True})
    def list_pppoe_accounts() -> dict:
        """列出 PPPoE 账号"""
        return get_client().show_list("pppuser")

    @mcp.tool
    def add_pppoe_account(username: str, password: str, ip_type: str = "auto",
                          upload_kbps: int = 0, download_kbps: int = 0, comment: str = "") -> dict:
        """添加 PPPoE 账号"""
        return get_client().add("pppuser", {"user": username, "pass": password, "ip_type": ip_type,
            "upload": upload_kbps, "download": download_kbps, "comment": comment})

    @mcp.tool
    def delete_pppoe_account(user_id: int) -> dict:
        """删除 PPPoE 账号"""
        return get_client().delete("pppuser", {"id": user_id})

    @mcp.tool(annotations={"readOnlyHint": True})
    def list_vpn_accounts(vpn_type: str = "pptp") -> dict:
        """列出 VPN 账号"""
        fn_map = {"pptp": "pptp_user", "l2tp": "l2tp_user", "openvpn": "openvpn_user"}
        return get_client().show_list(fn_map.get(vpn_type, "pptp_user"))

    @mcp.tool
    def add_vpn_account(vpn_type: str, username: str, password: str,
                        ip_type: str = "auto", comment: str = "") -> dict:
        """添加 VPN 账号"""
        fn_map = {"pptp": "pptp_user", "l2tp": "l2tp_user", "openvpn": "openvpn_user"}
        return get_client().add(fn_map.get(vpn_type, "pptp_user"),
            {"user": username, "pass": password, "ip_type": ip_type, "comment": comment})

    @mcp.tool
    def delete_vpn_account(vpn_type: str, user_id: int) -> dict:
        """删除 VPN 账号"""
        fn_map = {"pptp": "pptp_user", "l2tp": "l2tp_user", "openvpn": "openvpn_user"}
        return get_client().delete(fn_map.get(vpn_type, "pptp_user"), {"id": user_id})

    # ═══ 套餐管理 ═══

    @mcp.tool(annotations={"readOnlyHint": True})
    def list_packages() -> dict:
        """列出套餐"""
        return get_client().show_list("ppp_package")

    # ═══ 其他账号管理 ═══

    @mcp.tool(annotations={"readOnlyHint": True})
    def get_password_self_service() -> dict:
        """获取自助密码管理配置"""
        return get_client().show_list("ppp_passwd")

    @mcp.tool(annotations={"readOnlyHint": True})
    def get_billing_summary() -> dict:
        """获取总账管理"""
        return get_client().show_list("ppp_paylog")

    @mcp.tool(annotations={"readOnlyHint": True})
    def list_coupons() -> dict:
        """列出上网码/优惠券"""
        return get_client().show_list("coupon")

    # ═══ 代拨服务管理 ═══

    @mcp.tool(annotations={"readOnlyHint": True})
    def list_proxy_dial_accounts() -> dict:
        """列出代拨账号"""
        return get_client().show_list("pppoe_proxy_user")

    @mcp.tool(annotations={"readOnlyHint": True})
    def list_proxy_dial_online() -> dict:
        """列出代拨在线账号"""
        return get_client().show_list("pppoe_proxy_online")

    # ═══ 通知推送 ═══

    @mcp.tool(annotations={"readOnlyHint": True})
    def list_realtime_notices() -> dict:
        """列出实时通知"""
        return get_client().show_list("notice_temp")

    @mcp.tool(annotations={"readOnlyHint": True})
    def list_periodic_notices() -> dict:
        """列出定期通知"""
        return get_client().show_list("notice_cycle")

    @mcp.tool(annotations={"readOnlyHint": True})
    def list_expiry_notices() -> dict:
        """列出到期通知"""
        return get_client().show_list("notice_remind")

    @mcp.tool(annotations={"readOnlyHint": True})
    def list_dial_user_expiry_notices() -> dict:
        """列出拨号用户过期通知"""
        return get_client().show_list("notice_expires")
