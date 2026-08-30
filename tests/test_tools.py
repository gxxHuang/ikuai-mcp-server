"""Tests for tool modules"""
from unittest.mock import MagicMock

from ikuai_mcp.client import IKuaiClient
from ikuai_mcp.tools.advanced import _run_ping


class TestSystemTools:
    def test_get_system_overview(self, mock_sysstat):
        client = MagicMock(spec=IKuaiClient)
        client.show.return_value = mock_sysstat["results"]

        result = client.show("homepage", {"TYPE": "sysstat"})
        assert "sysstat" in result
        assert result["sysstat"]["verinfo"]["modelname"] == "IK-Q3000"

    def test_get_terminal_list_v4(self):
        client = MagicMock(spec=IKuaiClient)
        client.show_list.return_value = {"total": 1, "data": [{"ip": "192.168.9.100"}]}

        result = client.show_list("monitor_lanip")
        assert result["total"] == 1


class TestAdvancedTools:
    def test_ping_uses_start_show_stop_api_flow(self):
        client = MagicMock(spec=IKuaiClient)
        completed = {"data": [{"status": 0, "response": "4 packets transmitted, 4 received"}]}
        client.call.side_effect = [{}, completed, {}]

        result = _run_ping(client, "google.com", count=4, interface="auto")

        assert result == completed
        assert client.call.call_args_list == [
            (("Ping", "start", {
                "host": "google.com",
                "proto": "ipv4",
                "l4proto": "icmp",
                "count": 4,
                "interface": "auto",
            }),),
            (("Ping", "show", {}),),
            (("Ping", "stop", {}),),
        ]

    def test_ping_returns_partial_result_when_router_does_not_finish(self, monkeypatch):
        client = MagicMock(spec=IKuaiClient)
        running = {"data": [{"status": 1, "response": "PING google.com ...\n"}]}
        client.call.side_effect = [{}, running, {}]
        moments = iter([0, 1, 11])
        monkeypatch.setattr("ikuai_mcp.tools.advanced.time.monotonic", lambda: next(moments))
        monkeypatch.setattr("ikuai_mcp.tools.advanced.time.sleep", lambda _seconds: None)

        result = _run_ping(client, "google.com", count=4, interface="auto")

        assert result == {**running, "timed_out": True}
        client.call.assert_called_with("Ping", "stop", {})


class TestSecurityTools:
    def test_list_acl_rules(self):
        client = MagicMock(spec=IKuaiClient)
        client.show_list.return_value = {"total": 0, "data": []}

        result = client.show_list("acl")
        assert result["total"] == 0

    def test_add_acl_rule(self):
        client = MagicMock(spec=IKuaiClient)
        client.add.return_value = {"code": 0}

        client.add("acl", {"action": "drop", "src_addr": "192.168.9.100"})
        client.add.assert_called_once()
