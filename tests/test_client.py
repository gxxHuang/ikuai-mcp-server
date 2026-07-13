"""Tests for IKuaiClient"""

import pytest

from src.ikuai_mcp.client import AuthenticationError, IKuaiClient, RouterAPIError


class TestIKuaiClient:
    def test_init(self):
        client = IKuaiClient("http://192.168.1.1", "admin", "password")
        assert client.base_url == "http://192.168.1.1"
        assert client.username == "admin"

    def test_authenticate_success(self, mock_router):
        mock_router.post.return_value.json.return_value = {"code": 0, "message": "Success"}

        client = IKuaiClient("http://192.168.1.1", "admin", "password")
        session = client.session  # triggers auth
        assert session is not None

    def test_authenticate_failure(self, mock_router):
        mock_router.post.return_value.json.return_value = {"code": 1001, "message": "密码错误"}

        client = IKuaiClient("http://192.168.1.1", "admin", "wrong")
        with pytest.raises(AuthenticationError):
            _ = client.session

    def test_call_show(self, mock_router, mock_sysstat):
        mock_router.post.return_value.json.side_effect = [
            {"code": 0, "message": "Success"},  # login
            mock_sysstat,  # call
        ]

        client = IKuaiClient("http://192.168.1.1", "admin", "password")
        result = client.show("homepage", {"TYPE": "sysstat"})
        assert result["sysstat"]["verinfo"]["modelname"] == "IK-Q3000"

    def test_call_api_error(self, mock_router):
        mock_router.post.return_value.json.side_effect = [
            {"code": 0, "message": "Success"},  # login
            {"code": 3001, "message": "invalid action"},  # call
        ]

        client = IKuaiClient("http://192.168.1.1", "admin", "password")
        with pytest.raises(RouterAPIError):
            client.edit("nonexist", {})

    def test_show_list_pagination(self, mock_router, mock_empty_list):
        mock_router.post.return_value.json.side_effect = [
            {"code": 0, "message": "Success"},  # login
            mock_empty_list,  # call
        ]

        client = IKuaiClient("http://192.168.1.1", "admin", "password")
        result = client.show_list("acl")
        assert result["total"] == 0
