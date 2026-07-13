"""流控分流工具 — 智能流控(4子页)/IP限速/MAC限速/多线负载/端口分流/域名分流/协议分流/上下行分离/自定义运营商"""


def register_tools(mcp, get_client):

    # ═══ 智能流控（4 个子页面）═══

    @mcp.tool(annotations={"readOnlyHint": True})
    def get_flow_control_lines() -> dict:
        """获取流控线路配置（智能流控 → 流控线路）"""
        return get_client().show_list("layer7_intell")

    @mcp.tool
    def set_flow_control_line(enabled: bool, interface: str = "wan2") -> dict:
        """启用/禁用某条线路的智能流控"""
        return get_client().call("layer7_intell", "up" if enabled else "down", {"interface": interface})

    @mcp.tool(annotations={"readOnlyHint": True})
    def get_priority_domain_settings() -> dict:
        """获取优先域名设置（智能流控 → 优先域名）"""
        return get_client().show_list("high_prio_host")

    @mcp.tool(annotations={"readOnlyHint": True})
    def get_terminal_independent_speed_limits() -> dict:
        """获取终端独立限速（智能流控 → 终端独立限速）"""
        return get_client().show_list("alone_limit")

    @mcp.tool(annotations={"readOnlyHint": True})
    def get_flow_control_strategies() -> dict:
        """获取流控策略设置（智能流控 → 流控策略设置）"""
        return get_client().show_list("layer7_qos")

    # ═══ 终端限速 ═══

    @mcp.tool(annotations={"readOnlyHint": True})
    def list_ip_speed_limits() -> dict:
        """列出 IP 限速规则"""
        return get_client().show_list("simple_qos")

    @mcp.tool
    def add_ip_speed_limit(ip_addr: str, upload_kbps: int, download_kbps: int,
                           comment: str = "", enabled: bool = True) -> dict:
        """添加 IP 限速"""
        return get_client().add("simple_qos", {"ip_addr": ip_addr, "upload": upload_kbps,
            "download": download_kbps, "comment": comment, "enabled": enabled})

    @mcp.tool
    def delete_ip_speed_limit(rule_id: int) -> dict:
        """删除 IP 限速"""
        return get_client().delete("simple_qos", {"id": rule_id})

    @mcp.tool(annotations={"readOnlyHint": True})
    def list_mac_speed_limits() -> dict:
        """列出 MAC 限速规则"""
        return get_client().show_list("mac_qos")

    @mcp.tool
    def add_mac_speed_limit(mac: str, upload_kbps: int, download_kbps: int,
                            comment: str = "", time_range: str = "00:00-23:59", enabled: bool = True) -> dict:
        """添加 MAC 限速"""
        return get_client().add("mac_qos", {"mac_addrs": mac, "upload": upload_kbps,
            "download": download_kbps, "comment": comment, "time": time_range, "enabled": enabled})

    @mcp.tool
    def delete_mac_speed_limit(rule_id: int) -> dict:
        """删除 MAC 限速"""
        return get_client().delete("mac_qos", {"id": rule_id})

    # ═══ 多线负载 ═══

    @mcp.tool(annotations={"readOnlyHint": True})
    def list_load_balance_rules() -> dict:
        """列出多线负载规则"""
        return get_client().show_list("lb_pcc")

    # ═══ 分流策略 ═══

    @mcp.tool(annotations={"readOnlyHint": True})
    def list_protocol_forwarding_rules() -> dict:
        """列出协议分流规则"""
        return get_client().show_list("stream_layer7")

    @mcp.tool(annotations={"readOnlyHint": True})
    def list_port_forwarding_rules() -> dict:
        """列出端口分流规则"""
        return get_client().show_list("stream_ipport")

    @mcp.tool
    def add_port_forwarding_rule(src_addr: str = "", dst_addr: str = "", src_port: str = "",
                                 dst_port: str = "", protocol: str = "tcp+udp", interface: str = "wan2",
                                 comment: str = "", enabled: bool = True) -> dict:
        """添加端口分流规则"""
        return get_client().add("stream_ipport", {"src_addr": src_addr, "dst_addr": dst_addr,
            "src_port": src_port, "dst_port": dst_port, "protocol": protocol, "interface": interface,
            "comment": comment, "enabled": enabled})

    @mcp.tool
    def delete_port_forwarding_rule(rule_id: int) -> dict:
        """删除端口分流"""
        return get_client().delete("stream_ipport", {"id": rule_id})

    @mcp.tool(annotations={"readOnlyHint": True})
    def list_domain_forwarding_rules() -> dict:
        """列出域名分流规则"""
        return get_client().show_list("stream_domain")

    @mcp.tool
    def add_domain_forwarding_rule(domain: str, interface: str = "wan2", src_addr: str = "",
                                   comment: str = "", enabled: bool = True) -> dict:
        """添加域名分流规则"""
        return get_client().add("stream_domain", {"domain": domain, "interface": interface,
            "src_addr": src_addr, "comment": comment, "enabled": enabled})

    @mcp.tool
    def delete_domain_forwarding_rule(rule_id: int) -> dict:
        """删除域名分流"""
        return get_client().delete("stream_domain", {"id": rule_id})

    @mcp.tool(annotations={"readOnlyHint": True})
    def list_updown_separation_rules() -> dict:
        """列出上下行分离规则"""
        return get_client().show_list("stream_updown")

    # ═══ 自定义运营商 ═══

    @mcp.tool(annotations={"readOnlyHint": True})
    def list_custom_isp_rules() -> dict:
        """列出自定义运营商规则"""
        return get_client().show_list("custom_isp")
