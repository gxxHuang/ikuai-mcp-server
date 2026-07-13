"""安全管控工具 — ACL/连接数/ARP/MAC控制/网址浏览控制/URL控制/应用协议控制/行为记录/流量审计"""


def register_tools(mcp, get_client):

    # ═══ ACL 规则 ═══

    @mcp.tool(annotations={"readOnlyHint": True})
    def list_acl_rules() -> dict:
        """列出 ACL 访问控制规则"""
        return get_client().show_list("acl")

    @mcp.tool
    def add_acl_rule(action: str, protocol: str = "any", src_addr: str = "", dst_addr: str = "",
                     src_port: str = "", dst_port: str = "", interface: str = "", direction: str = "forward",
                     time_range: str = "", comment: str = "", enabled: bool = True) -> dict:
        """添加 ACL 规则"""
        return get_client().add("acl", {"action": action, "protocol": protocol, "src_addr": src_addr,
            "dst_addr": dst_addr, "src_port": src_port, "dst_port": dst_port, "interface": interface,
            "direction": direction, "time": time_range, "comment": comment, "enabled": enabled})

    @mcp.tool
    def delete_acl_rule(rule_id: int) -> dict:
        """删除 ACL 规则"""
        return get_client().delete("acl", {"id": rule_id})

    @mcp.tool
    def toggle_acl_rule(rule_id: int, enable: bool) -> dict:
        """启用/禁用 ACL 规则"""
        return get_client().enable("acl", {"id": rule_id}) if enable else get_client().disable("acl", {"id": rule_id})

    # ═══ 连接数限制 ═══

    @mcp.tool(annotations={"readOnlyHint": True})
    def list_connection_limits() -> dict:
        """列出连接数限制规则"""
        return get_client().show_list("conn_limit")

    @mcp.tool
    def add_connection_limit(ip_addr: str = "", mac: str = "", max_connections: int = 100,
                             comment: str = "", time_range: str = "00:00-23:59", enabled: bool = True) -> dict:
        """添加连接数限制"""
        return get_client().add("conn_limit", {"ip_addr": ip_addr, "mac": mac, "max_conn": max_connections,
            "comment": comment, "time": time_range, "enabled": enabled})

    @mcp.tool
    def delete_connection_limit(rule_id: int) -> dict:
        """删除连接数限制"""
        return get_client().delete("conn_limit", {"id": rule_id})

    # ═══ ARP 设置 ═══

    @mcp.tool(annotations={"readOnlyHint": True})
    def list_arp_bindings() -> dict:
        """列出 ARP 绑定列表"""
        return get_client().show_list("arp")

    @mcp.tool
    def add_arp_binding(mac: str, ip: str, comment: str = "") -> dict:
        """添加 ARP 绑定"""
        return get_client().add("arp", {"mac": mac, "ip_addr": ip, "comment": comment})

    @mcp.tool
    def delete_arp_binding(binding_id: int) -> dict:
        """删除 ARP 绑定"""
        return get_client().delete("arp", {"id": binding_id})

    @mcp.tool(annotations={"readOnlyHint": True})
    def list_ipv6_neighbors() -> dict:
        """列出 IPv6 邻居列表"""
        return get_client().show_list("ipv6_neighbor")

    # ═══ MAC 访问控制 ═══

    @mcp.tool(annotations={"readOnlyHint": True})
    def list_mac_access_control() -> dict:
        """列出 MAC 访问控制规则"""
        return get_client().show_list("acl_mac")

    @mcp.tool
    def add_mac_access_control(mac: str, action: str = "drop", comment: str = "",
                               time_range: str = "00:00-23:59", enabled: bool = True) -> dict:
        """添加 MAC 访问控制"""
        return get_client().add("acl_mac", {"mac": mac, "action": action, "comment": comment, "time": time_range, "enabled": enabled})

    @mcp.tool
    def delete_mac_access_control(rule_id: int) -> dict:
        """删除 MAC 访问控制"""
        return get_client().delete("acl_mac", {"id": rule_id})

    # ═══ 网址浏览控制（3 个 tab）═══

    @mcp.tool(annotations={"readOnlyHint": True})
    def list_url_blacklist() -> dict:
        """列出网址黑白名单（tab: 网址黑白名单）"""
        return get_client().show_list("url_black")

    @mcp.tool
    def add_url_blacklist(url: str, mode: int = 0, comment: str = "",
                          time_range: str = "00:00-23:59", week: str = "1234567", enabled: bool = True) -> dict:
        """添加网址黑白名单"""
        return get_client().add("url_black", {"url": url, "mode": mode, "comment": comment,
            "time": time_range, "week": week, "enabled": enabled})

    @mcp.tool
    def delete_url_blacklist(rule_id: int) -> dict:
        """删除网址黑白名单"""
        return get_client().delete("url_black", {"id": rule_id})

    @mcp.tool(annotations={"readOnlyHint": True})
    def list_domain_blacklist() -> dict:
        """列出禁止娱乐网站（tab: 禁止娱乐网站）"""
        return get_client().show_list("domain_blacklist")

    @mcp.tool
    def add_domain_blacklist(domain_groups: str, comment: str = "",
                             time_range: str = "00:00-23:59", weekdays: str = "1234567", enabled: bool = True) -> dict:
        """添加禁止娱乐网站"""
        return get_client().add("domain_blacklist", {"domain_groups": domain_groups, "comment": comment,
            "time": time_range, "weekdays": weekdays, "enabled": enabled})

    @mcp.tool
    def delete_domain_blacklist(rule_id: int) -> dict:
        """删除禁止娱乐网站"""
        return get_client().delete("domain_blacklist", {"id": rule_id})

    @mcp.tool(annotations={"readOnlyHint": True})
    def list_custom_url_library() -> dict:
        """列出自定义网址库（tab: 自定义网址库）"""
        return get_client().show_list("domain_group")

    @mcp.tool
    def add_custom_url_library(name: str, domains: str, comment: str = "") -> dict:
        """添加自定义网址库"""
        return get_client().add("domain_group", {"name": name, "domains": domains, "comment": comment})

    @mcp.tool
    def delete_custom_url_library(group_id: int) -> dict:
        """删除自定义网址库"""
        return get_client().delete("domain_group", {"id": group_id})

    # ═══ URL 控制（3 个 tab）═══

    @mcp.tool(annotations={"readOnlyHint": True})
    def list_url_redirects() -> dict:
        """列出 URL 跳转规则（tab: URL 跳转）"""
        return get_client().show_list("url_redirect")

    @mcp.tool(annotations={"readOnlyHint": True})
    def list_url_keywords() -> dict:
        """列出 URL 关键字替换（tab: 关键字替换）"""
        return get_client().show_list("url_keywords")

    @mcp.tool(annotations={"readOnlyHint": True})
    def list_url_params_replace() -> dict:
        """列出 URL 参数替换（tab: 参数替换）"""
        return get_client().show_list("url_replace")

    # ═══ 应用协议控制 ═══

    @mcp.tool(annotations={"readOnlyHint": True})
    def list_app_protocol_rules() -> dict:
        """列出应用协议控制规则 (L7 ACL)"""
        return get_client().show_list("acl_l7")

    @mcp.tool
    def add_app_protocol_rule(action: str, app_protos: str = "", src_addrs: str = "",
                              comment: str = "", prio: int = 32, time_range: str = "00:00-23:59",
                              week: str = "1234567", enabled: bool = True) -> dict:
        """添加应用协议控制规则"""
        return get_client().add("acl_l7", {"action": action, "app_protos": app_protos, "src_addrs": src_addrs,
            "comment": comment, "prio": prio, "time": time_range, "week": week, "enabled": enabled})

    @mcp.tool
    def delete_app_protocol_rule(rule_id: int) -> dict:
        """删除应用协议控制"""
        return get_client().delete("acl_l7", {"id": rule_id})

    @mcp.tool
    def toggle_app_protocol_rule(rule_id: int, enable: bool) -> dict:
        """启用/禁用应用协议控制"""
        return get_client().enable("acl_l7", {"id": rule_id}) if enable else get_client().disable("acl_l7", {"id": rule_id})

    # ═══ 其他控制（网络分享控制）═══

    @mcp.tool(annotations={"readOnlyHint": True})
    def list_network_sharing_controls() -> dict:
        """列出网络分享控制（二级路由/热点控制）"""
        return get_client().show_list("acl_l2route")

    # ═══ 行为记录 ═══

    @mcp.tool(annotations={"readOnlyHint": True})
    def get_url_browsing_log() -> dict:
        """获取网址浏览记录"""
        return get_client().show_list("audit_url_log")

    @mcp.tool(annotations={"readOnlyHint": True})
    def get_im_log() -> dict:
        """获取 IM 上下线记录"""
        return get_client().show_list("audit_im_log")

    @mcp.tool(annotations={"readOnlyHint": True})
    def get_terminal_log() -> dict:
        """获取终端上下线记录"""
        return get_client().show_list("audit_terminal_log")

    # ═══ 流量审计 ═══

    @mcp.tool(annotations={"readOnlyHint": True})
    def get_traffic_audit_by_mac() -> dict:
        """按 MAC 审计终端流量"""
        return get_client().show_list("audit_terminal_stat_mac")

    @mcp.tool(annotations={"readOnlyHint": True})
    def get_traffic_audit_by_user() -> dict:
        """按账号审计终端流量"""
        return get_client().show_list("audit_terminal_stat_user")

    # ═══ 终端名称管理 ═══

    @mcp.tool(annotations={"readOnlyHint": True})
    def list_device_names() -> dict:
        """列出终端名称/备注"""
        return get_client().show_list("mac_comment")

    @mcp.tool
    def set_device_name(mac: str, name: str) -> dict:
        """设置终端名称"""
        c = get_client()
        existing = c.show_list("mac_comment")
        for item in existing.get("data", []):
            if item.get("mac") == mac:
                return c.save_config("mac_comment", {"id": item["id"], "mac": mac, "comment": name})
        return c.add("mac_comment", {"mac": mac, "comment": name})

    # ═══ 高级设置 ═══

    @mcp.tool(annotations={"readOnlyHint": True})
    def get_security_advanced_settings() -> dict:
        """获取安全中心高级设置"""
        return get_client().show_list("advanced")
