"""Tests for tool modules"""
from unittest.mock import MagicMock

from src.ikuai_mcp.client import IKuaiClient


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
