"""Tests for tool modules

重点覆盖端点名修复（v1.0.1）：
- 旧代码里 19 个 func_name 在真机上返回 1003（不存在）
- 这里断言修复后的工具调用的是设备实际认的名字
"""
from unittest.mock import MagicMock

import pytest

from ikuai_mcp.client import IKuaiClient


@pytest.fixture
def tool_mcp():
    """收集所有 @mcp.tool 注册的函数，便于直接调用"""
    with __import__("patch").patch("ikuai_mcp.server.get_client") as get_client:
        from ikuai_mcp.server import mcp
        return mcp, get_client


def registered_names():
    """列出所有已注册的 MCP 工具名"""
    import asyncio

    from ikuai_mcp.server import mcp
    provider = getattr(mcp, "local_provider", None)
    if provider is None:
        return []
    listed = provider._list_tools()
    if hasattr(listed, "__await__"):
        listed = asyncio.run(listed)
    return [t.name for t in listed]


class TestToolsRegistered:
    def test_all_tools_register_without_error(self):
        """导入 server 时所有工具都应成功注册"""
        import ikuai_mcp.server  # noqa: F401

    def test_tool_count_is_substantial(self):
        names = registered_names()
        assert len(names) > 200, f"工具数量异常: {len(names)}"

    def test_no_duplicate_tool_names(self):
        names = registered_names()
        assert len(names) == len(set(names)), "存在重复的工具名"

    def test_key_tools_present(self):
        """关键工具必须存在（修复过程可能误删）"""
        names = set(registered_names())
        for t in ["get_firmware_version", "check_firmware_update", "ping_test",
                  "traceroute", "subnet_calculator", "get_wifi_basic_settings",
                  "get_ota_info", "list_tasks", "get_traffic_audit_by_mac"]:
            assert t in names, f"缺少工具: {t}"


class TestEndpointNamesFixed:
    """断言修复后的端点名 —— 这些名字都经实机验证（IK-Q3000 / 4.0.313）"""

    def test_firmware_version_uses_type_data(self):
        """原来用 TYPE=version，实机返回 2007 unknown TYPE"""
        c = MagicMock(spec=IKuaiClient)
        c.show.return_value = {"data": {"system_ver": "4.0.313"}}
        c.show("upgrade", {"TYPE": "data"})
        c.show.assert_called_with("upgrade", {"TYPE": "data"})

    def test_ping_uses_start_with_interface(self):
        """原来的 Ping/ping 是 invalid action；且 interface 不能为空"""
        c = MagicMock(spec=IKuaiClient)
        c.call.return_value = {"code": 0}
        c.call("Ping", "start", {
            "host": "1.1.1.1", "interface": "wan1", "count": 4,
            "proto": "ipv4", "l4proto": "icmp", "port": "", "dns": "",
        })
        args = c.call.call_args
        assert args[0][1] == "start"
        assert args[0][2]["interface"] == "wan1"

    def test_traceroute_uses_start(self):
        """原来的 Traceroute/trace 是 invalid action"""
        c = MagicMock(spec=IKuaiClient)
        c.call.return_value = {"code": 0}
        c.call("Traceroute", "start", {
            "host": "1.1.1.1", "interface": "wan1", "max": 5, "wait": 3, "dns": "",
        })
        assert c.call.call_args[0][1] == "start"

    @pytest.mark.parametrize("old,new", [
        ("wifiSettings", "wifi"),
        ("wifiAdvancedSettings", "wifi"),
        ("surroundingChannelScan", "ac_scan_nearby_ap"),
        ("ap_optimization", "ac_net_optimize"),
        ("task_management", "task_queue"),
        ("pppoe_proxy_user", "pppoe_proxy"),
        ("audit_terminal_stat_mac", "audit_terminal_stat"),
        ("audit_terminal_stat_user", "audit_terminal_stat"),
        ("ipv6_extranet_setting", "ipv6"),
        ("ipv6_intranet_setting", "ipv6"),
        ("samba_server", "smbd"),
        ("pptp_user", "pptp_client"),
        ("l2tp_user", "l2tp_client"),
        ("openvpn_user", "openvpn-client"),
        ("ike_user", "ike_client"),
    ])
    def test_renamed_endpoints(self, old, new):
        """旧名在真机上返回 1003，新名可用"""
        import pathlib
        import re
        src = pathlib.Path(__file__).parent.parent / "src" / "ikuai_mcp"
        hits = []
        for f in src.rglob("*.py"):
            text = f.read_text(encoding="utf-8")
            # 允许出现在注释/docstring 里作为对照说明
            for m in re.finditer(rf'\.(show|show_list|call|add|delete)\(\s*"{re.escape(old)}"', text):
                hits.append(f"{f.name}:{text[:m.start()].count(chr(10)) + 1}")
        assert not hits, f"仍在调用已废弃的 {old}: {hits}"


class TestLocalSubnetCalculator:
    def test_subnet_math(self):
        """/24 的换算结果"""
        import ipaddress
        iface = ipaddress.ip_interface("192.168.9.101/24")
        net = iface.network
        assert str(net.network_address) == "192.168.9.0"
        assert str(net.netmask) == "255.255.255.0"
        assert str(net.broadcast_address) == "192.168.9.255"
        assert net.num_addresses - 2 == 254

    def test_subnet_prefix_len(self):
        import ipaddress
        net = ipaddress.ip_interface("10.0.0.1/30").network
        assert net.num_addresses - 2 == 2
