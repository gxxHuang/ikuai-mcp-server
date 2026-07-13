"""网络配置工具 — 内外网/WAN/LAN/VLAN/DHCP/DNS/静态路由/端口映射/NAT/UPnP/路由对象/IPv6/DDNS"""


def register_tools(mcp, get_client):

    # ═══ 内外网设置 ═══

    @mcp.tool(annotations={"readOnlyHint": True})
    def list_wan_configs() -> dict:
        """列出所有 WAN 口配置（IP/接入方式/网卡/VLAN/速率）"""
        return get_client().show_list("wan")

    @mcp.tool(annotations={"readOnlyHint": True})
    def list_lan_configs() -> dict:
        """列出所有 LAN 口配置"""
        return get_client().show_list("lan")

    # ─── IPv6 设置 ───

    @mcp.tool(annotations={"readOnlyHint": True})
    def get_ipv6_config() -> dict:
        """获取 IPv6 总配置"""
        return get_client().show_list("ipv6")

    @mcp.tool(annotations={"readOnlyHint": True})
    def get_ipv6_wan_config() -> dict:
        """获取 IPv6 外网设置"""
        return get_client().show_list("ipv6_extranet_setting")

    @mcp.tool(annotations={"readOnlyHint": True})
    def get_ipv6_lan_config() -> dict:
        """获取 IPv6 内网设置"""
        return get_client().show_list("ipv6_intranet_setting")

    @mcp.tool
    def set_ipv6(enabled: bool) -> dict:
        """启用/禁用 IPv6"""
        return get_client().save_config("ipv6", {"enabled": 1 if enabled else 0})

    # ─── VPN 客户端 ───

    @mcp.tool(annotations={"readOnlyHint": True})
    def list_vpn_clients() -> dict:
        """列出所有 VPN 客户端配置（PPTP/L2TP/OpenVPN/IPSec/IKEv2/WireGuard）"""
        c = get_client()
        result = {}
        for fn in ["pptp_client", "l2tp_client", "openvpn-client", "ike_client", "wireguard"]:
            try:
                result[fn] = c.show_list(fn)
            except Exception:
                result[fn] = {"status": "未配置"}
        return result

    @mcp.tool(annotations={"readOnlyHint": True})
    def get_pptp_client_config() -> dict:
        """获取 PPTP 客户端配置"""
        return get_client().show_list("pptp_client")

    @mcp.tool(annotations={"readOnlyHint": True})
    def get_l2tp_client_config() -> dict:
        """获取 L2TP 客户端配置"""
        return get_client().show_list("l2tp_client")

    @mcp.tool(annotations={"readOnlyHint": True})
    def get_openvpn_client_config() -> dict:
        """获取 OpenVPN 客户端配置"""
        return get_client().show_list("openvpn-client")

    @mcp.tool(annotations={"readOnlyHint": True})
    def get_ipsec_client_config() -> dict:
        """获取 IPSec VPN 客户端配置"""
        return get_client().show_list("ipsec-vpn")

    @mcp.tool(annotations={"readOnlyHint": True})
    def get_ikev2_client_config() -> dict:
        """获取 IKEv2/IPSec 客户端配置"""
        return get_client().show_list("ike_client")

    @mcp.tool(annotations={"readOnlyHint": True})
    def get_wireguard_client_config() -> dict:
        """获取 WireGuard 客户端配置"""
        return get_client().show_list("wireguard")

    # ═══ VLAN ═══

    @mcp.tool(annotations={"readOnlyHint": True})
    def list_vlan_configs() -> dict:
        """列出所有 VLAN 配置"""
        return get_client().show_list("vlan")

    @mcp.tool
    def add_vlan(vlan_id: int, name: str, interface: str, ip: str = "", comment: str = "") -> dict:
        """添加 VLAN"""
        return get_client().add("vlan", {"vlan_id": vlan_id, "name": name, "interface": interface, "ip_addr": ip, "comment": comment})

    @mcp.tool
    def delete_vlan(vlan_id: int) -> dict:
        """删除 VLAN"""
        return get_client().delete("vlan", {"id": vlan_id})

    # ═══ DHCP ═══

    @mcp.tool(annotations={"readOnlyHint": True})
    def list_dhcp_servers() -> dict:
        """列出 DHCP 服务端配置"""
        return get_client().show_list("dhcp_server")

    @mcp.tool(annotations={"readOnlyHint": True})
    def list_dhcp_static_bindings() -> dict:
        """列出 DHCP 静态分配（IP-MAC 绑定）"""
        return get_client().show_list("dhcp_static")

    @mcp.tool
    def add_dhcp_static_binding(mac: str, ip: str, comment: str = "") -> dict:
        """添加 DHCP 静态分配（IP-MAC 绑定）"""
        return get_client().add("dhcp_static", {"mac": mac, "ip_addr": ip, "comment": comment})

    @mcp.tool
    def delete_dhcp_static_binding(record_id: int) -> dict:
        """删除 DHCP 静态分配"""
        return get_client().delete("dhcp_static", {"id": record_id})

    @mcp.tool(annotations={"readOnlyHint": True})
    def list_dhcp_leases(ip_type: str = "v4") -> dict:
        """列出 DHCP 租约列表（当前分配 IP）

        Args:
            ip_type: "v4" 或 "v6"
        """
        fn = "dhcp_lease" if ip_type == "v4" else "dhcp6_lease"
        return get_client().show_list(fn)

    @mcp.tool(annotations={"readOnlyHint": True})
    def list_dhcp_blackwhite_list(ip_type: str = "v4") -> dict:
        """列出 DHCP 黑白名单

        Args:
            ip_type: "v4" 或 "v6"
        """
        fn = "dhcp_acl_mac" if ip_type == "v4" else "dhcp6_acl_mac"
        return get_client().show_list(fn)

    @mcp.tool(annotations={"readOnlyHint": True})
    def list_ipv6_static_bindings() -> dict:
        """列出 IPv6 前缀静态分配"""
        return get_client().show_list("ipv6_static")

    # ═══ DNS ═══

    @mcp.tool(annotations={"readOnlyHint": True})
    def get_dns_config() -> dict:
        """获取 DNS 加速服务配置（通过多线路 DNS 接口读取）"""
        return get_client().show_list("dns_replace")

    @mcp.tool
    def set_dns_config(primary_dns: str = "", secondary_dns: str = "", enable_cache: bool = True) -> dict:
        """修改 DNS 配置"""
        return get_client().save_config("dns", {"dns1": primary_dns, "dns2": secondary_dns, "dns_cache": 1 if enable_cache else 0})

    @mcp.tool(annotations={"readOnlyHint": True})
    def get_multi_line_dns() -> dict:
        """获取多线路 DNS 配置"""
        return get_client().show_list("dns_replace")

    # ═══ 静态路由 ═══

    @mcp.tool(annotations={"readOnlyHint": True})
    def list_static_routes() -> dict:
        """列出所有静态路由规则"""
        return get_client().show_list("static_rt")

    @mcp.tool
    def add_static_route(destination: str, netmask: str, gateway: str, interface: str = "", comment: str = "", metric: int = 1) -> dict:
        """添加静态路由"""
        return get_client().add("static_rt", {"dst_addr": destination, "dst_mask": netmask, "gateway": gateway, "interface": interface, "comment": comment, "metric": metric})

    @mcp.tool
    def delete_static_route(route_id: int) -> dict:
        """删除静态路由"""
        return get_client().delete("static_rt", {"id": route_id})

    @mcp.tool(annotations={"readOnlyHint": True})
    def get_routing_table(ip_type: str = "v4") -> dict:
        """查看当前路由表

        Args:
            ip_type: "v4" 或 "v6"
        """
        fn = "static_rt_table_ipv4" if ip_type == "v4" else "static_rt_table_ipv6"
        return get_client().show_list(fn)

    # ═══ 跨三层服务 ═══

    @mcp.tool(annotations={"readOnlyHint": True})
    def get_cross_layer3_config() -> dict:
        """获取跨三层服务配置"""
        return get_client().show_list("netsnmpc")

    # ═══ 路由对象（地址分组）═══

    @mcp.tool(annotations={"readOnlyHint": True})
    def list_ip_groups(ip_type: str = "v4") -> dict:
        """列出 IP 地址分组（IPv4/IPv6）"""
        fn = "route_object_ip" if ip_type == "v4" else "route_object_ip6"
        return get_client().show_list(fn)

    @mcp.tool
    def add_ip_group(name: str, ip_type: str = "v4", ip_list: str = "", comment: str = "") -> dict:
        """添加 IP 地址分组"""
        fn = "route_object_ip" if ip_type == "v4" else "route_object_ip6"
        return get_client().add(fn, {"name": name, "ip_list": ip_list, "comment": comment})

    @mcp.tool
    def delete_ip_group(group_id: int, ip_type: str = "v4") -> dict:
        """删除 IP 地址分组"""
        fn = "route_object_ip" if ip_type == "v4" else "route_object_ip6"
        return get_client().delete(fn, {"id": group_id})

    @mcp.tool(annotations={"readOnlyHint": True})
    def list_mac_groups() -> dict:
        """列出 MAC 地址分组"""
        return get_client().show_list("route_object_mac")

    @mcp.tool
    def add_mac_group(name: str, mac_list: str = "", comment: str = "") -> dict:
        """添加 MAC 地址分组"""
        return get_client().add("route_object_mac", {"name": name, "mac_list": mac_list, "comment": comment})

    @mcp.tool
    def delete_mac_group(group_id: int) -> dict:
        """删除 MAC 地址分组"""
        return get_client().delete("route_object_mac", {"id": group_id})

    @mcp.tool(annotations={"readOnlyHint": True})
    def list_time_plans() -> dict:
        """列出时间计划"""
        return get_client().show_list("route_object_time")

    @mcp.tool(annotations={"readOnlyHint": True})
    def list_domain_groups() -> dict:
        """列出域名分组"""
        return get_client().show_list("route_object_domain")

    @mcp.tool(annotations={"readOnlyHint": True})
    def list_protocol_groups() -> dict:
        """列出协议分组"""
        return get_client().show_list("route_object_proto")

    @mcp.tool(annotations={"readOnlyHint": True})
    def list_port_groups() -> dict:
        """列出端口分组"""
        return get_client().show_list("route_object_port")

    # ═══ 自定义协议 ═══

    @mcp.tool(annotations={"readOnlyHint": True})
    def list_custom_protocols() -> dict:
        """列出自定义协议"""
        return get_client().show_list("dprotos")

    @mcp.tool(annotations={"readOnlyHint": True})
    def list_advanced_custom_protocols() -> dict:
        """列出高级自定义协议 (L7)"""
        return get_client().show_list("dprotos_l7")

    # ═══ 组播管理 ═══

    @mcp.tool(annotations={"readOnlyHint": True})
    def get_igmp_proxy_config() -> dict:
        """获取 IGMP 代理配置"""
        return get_client().show_list("igmp_proxy")

    @mcp.tool(annotations={"readOnlyHint": True})
    def get_iptv_config() -> dict:
        """获取 IPTV 透传配置"""
        return get_client().show_list("iptv")

    @mcp.tool(annotations={"readOnlyHint": True})
    def get_udp_proxy_config() -> dict:
        """获取 UDPXY 配置（组播转 HTTP）"""
        return get_client().show_list("udp_proxy")

    # ═══ UPnP / NAT ═══

    @mcp.tool(annotations={"readOnlyHint": True})
    def get_upnp_settings() -> dict:
        """获取 UPnP 设置"""
        return get_client().show_list("upnpd_leases")

    @mcp.tool(annotations={"readOnlyHint": True})
    def get_upnp_status() -> dict:
        """获取 UPnP 当前状态和映射表"""
        return get_client().show_list("upnpd")

    @mcp.tool(annotations={"readOnlyHint": True})
    def list_nat_rules() -> dict:
        """列出 NAT 规则"""
        return get_client().show_list("nat_rule")

    @mcp.tool(annotations={"readOnlyHint": True})
    def list_port_mappings() -> dict:
        """列出端口映射 (DNAT) 规则"""
        return get_client().show_list("dnat")

    @mcp.tool
    def add_port_mapping(name: str, internal_ip: str, internal_port: str, external_port: str,
                         protocol: str = "tcp", interface: str = "", enabled: bool = True, comment: str = "") -> dict:
        """添加端口映射"""
        return get_client().add("dnat", {"name": name, "interface": interface, "protocol": protocol,
            "src_port": external_port, "dst_addr": internal_ip, "dst_port": internal_port, "enabled": enabled, "comment": comment})

    @mcp.tool
    def delete_port_mapping(rule_id: int) -> dict:
        """删除端口映射"""
        return get_client().delete("dnat", {"id": rule_id})

    @mcp.tool(annotations={"readOnlyHint": True})
    def get_dmz_config() -> dict:
        """获取 DMZ 主机配置"""
        return get_client().show_list("netmap")

    @mcp.tool
    def set_dmz(enabled: bool, internal_ip: str = "", interface: str = "") -> dict:
        """配置 DMZ 主机"""
        return get_client().save_config("netmap", {"enabled": 1 if enabled else 0, "ip_addr": internal_ip, "interface": interface})

    # ═══ SD-WAN ═══

    @mcp.tool(annotations={"readOnlyHint": True})
    def get_sdwan_status() -> dict:
        """获取 SD-WAN 智能组网状态"""
        return get_client().show_list("ik_web_sdwan")

    # ═══ 动态域名 DDNS ═══

    @mcp.tool(annotations={"readOnlyHint": True})
    def get_ddns_config() -> dict:
        """获取动态域名 (DDNS) 配置"""
        return get_client().show_list("ddns")

    @mcp.tool
    def add_ddns(domain: str, provider: str, username: str, password: str, interface: str = "", enabled: bool = True) -> dict:
        """添加 DDNS"""
        return get_client().add("ddns", {"domain": domain, "provider": provider, "username": username, "password": password, "interface": interface, "enabled": enabled})

    @mcp.tool
    def delete_ddns(record_id: int) -> dict:
        """删除 DDNS"""
        return get_client().delete("ddns", {"id": record_id})
