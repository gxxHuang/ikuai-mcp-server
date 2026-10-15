"""Tests for IKuaiClient

重点覆盖 v1.0.1 修复的真实 bug：
1. 登录失败被静默吞掉（致命）
2. 旧版 Result:10000 不能作为成功判据
3. show_list 的 TYPE 方言自动回退
4. 会话失效自动重登
5. 302/401 响应处理
"""
from unittest.mock import MagicMock, patch

import pytest

from ikuai_mcp.client import (
    AuthenticationError,
    IKuaiClient,
    RequestError,
    RouterAPIError,
)


@pytest.fixture
def session():
    """返回一个被 patch 过的 requests.Session 实例"""
    with patch("requests.Session") as mock_session:
        inst = MagicMock()
        mock_session.return_value = inst
        yield inst


def make_client(**kw):
    return IKuaiClient("http://192.168.1.1", "admin", kw.pop("password", "password"), **kw)


class TestInit:
    def test_init(self):
        client = IKuaiClient("http://192.168.1.1/", "admin", "password")
        # 尾部斜杠应被去掉
        assert client.base_url == "http://192.168.1.1"
        assert client.username == "admin"

    def test_missing_password_raises_at_server_layer(self):
        # client 本身允许空密码，由 server.get_client() 拒绝
        c = IKuaiClient("http://x", "admin", "")
        assert c._password == ""


class TestAuthenticate:
    def test_success_code_zero(self, session):
        session.post.return_value.json.return_value = {"code": 0, "message": "成功"}
        c = make_client()
        assert c.session is not None

    def test_failure_raises(self, session):
        """回归测试：错误密码必须抛异常。

        设备实测返回 {"code":1005,"message":"账号或密码错误","Result":10000}。
        旧实现用 `code != 0 and Result != 10000` 判断，会因 Result 恒为 10000
        而使整个条件为 False —— 错误密码被当成登录成功。
        """
        session.post.return_value.json.return_value = {
            "code": 1005,
            "message": "账号或密码错误",
            "Result": 10000,  # 关键：这个字段在失败时同样存在
        }
        c = make_client(password="wrong")
        with pytest.raises(AuthenticationError) as ei:
            _ = c.session
        assert "1005" in str(ei.value)

    def test_result_10000_alone_is_not_success(self, session):
        """Result:10000 不能单独作为成功判据（除极旧版无 code 的情况）"""
        session.post.return_value.json.return_value = {
            "code": 1005,
            "message": "登录失败",
            "Result": 10000,
        }
        c = make_client()
        with pytest.raises(AuthenticationError):
            _ = c.session

    def test_legacy_protocol_without_code(self, session):
        """极旧固件不带 code 时，回退到 Result + ErrMsg 判断"""
        session.post.return_value.json.return_value = {
            "Result": 10000,
            "ErrMsg": "Success",
            "Data": {},
        }
        c = make_client()
        assert c.session is not None

    def test_401_raises_auth_error(self, session):
        resp = MagicMock()
        resp.status_code = 401
        resp.text = "401 Authorization Required"
        session.post.return_value = resp
        c = make_client()
        with pytest.raises(AuthenticationError) as ei:
            _ = c.session
        assert "401" in str(ei.value)

    def test_non_json_response(self, session):
        resp = MagicMock()
        resp.status_code = 200
        resp.text = "<html>not json</html>"
        resp.json.side_effect = ValueError("no json")
        session.post.return_value = resp
        c = make_client()
        with pytest.raises(AuthenticationError):
            _ = c.session

    def test_request_exception_wrapped(self, session):
        import requests
        session.post.side_effect = requests.RequestException("boom")
        c = make_client()
        with pytest.raises(RequestError):
            _ = c.session


class TestCall:
    def login_ok(self, session, payload):
        """让登录返回成功，后续返回 payload"""
        session.post.return_value.json.side_effect = [
            {"code": 0, "message": "成功"},
            payload,
        ]

    def test_show_returns_results(self, session):
        self.login_ok(session, {
            "code": 0, "message": "Success",
            "results": {"verinfo": {"modelname": "IK-Q3000"}},
        })
        c = make_client()
        r = c.show("sysstat", {"TYPE": "verinfo"})
        assert r["verinfo"]["modelname"] == "IK-Q3000"

    def test_returns_data_when_no_results(self, session):
        self.login_ok(session, {"code": 0, "message": "Success", "data": {"x": 1}})
        c = make_client()
        assert c.show("basic")["x"] == 1

    def test_api_error_raises_with_code(self, session):
        self.login_ok(session, {"code": 1003, "message": "Access denied"})
        c = make_client()
        with pytest.raises(RouterAPIError) as ei:
            c.show("nosuchfunc")
        assert "1003" in str(ei.value)

    def test_type_error_raises_2007(self, session):
        self.login_ok(session, {"code": 2007, "message": "unknown TYPE (nope)"})
        c = make_client()
        with pytest.raises(RouterAPIError) as ei:
            c.show("upgrade", {"TYPE": "nope"})
        assert "2007" in str(ei.value)

    def test_legacy_format_success(self, session):
        self.login_ok(session, {
            "Result": 10000, "ErrMsg": "Success", "Data": {"ok": True},
        })
        c = make_client()
        assert c.show("x")["ok"] is True

    def test_legacy_format_error(self, session):
        self.login_ok(session, {"Result": 10001, "ErrMsg": "Some error"})
        c = make_client()
        with pytest.raises(RouterAPIError):
            c.show("x")

    def test_kernel_message_stripped(self, session):
        """设备有时在 JSON 前输出 'sending to kernel ...'"""
        resp = MagicMock()
        resp.status_code = 200
        resp.text = 'sending to kernel ... {"code":0,"results":{"a":1}}'
        # 第一次 json() 抛错触发兜底解析，第二次返回真实结构
        resp.json.side_effect = [{"code": 0}, ValueError("not json")]
        session.post.side_effect = None
        session.post.return_value = resp

        c = make_client()
        r = c.call("x", "show", {})
        assert r == {"a": 1}

    def test_session_expired_relogin(self, session):
        """遇到 1008（会话已过期）应自动重登一次"""
        session.post.return_value.json.side_effect = [
            {"code": 0},                                  # 登录
            {"code": 1008, "message": "会话已过期"},      # 第一次调用
            {"code": 0},                                  # 重登
            {"code": 0, "results": {"ok": 1}},            # 重试
        ]
        c = make_client()
        r = c.call("acl", "show", {})
        assert r == {"ok": 1}

    def test_302_triggers_relogin(self, session):
        """未登录时 /Action/call 返回 302 而非 JSON"""
        r302 = MagicMock()
        r302.status_code = 302
        r302.text = "302 Found"

        r_ok = MagicMock()
        r_ok.status_code = 200
        r_ok.json.return_value = {"code": 0, "message": "成功"}

        # 登录成功 → 调用返回 302 → 重登成功 → 再次调用仍 302（retry=False）
        session.post.side_effect = [r_ok, r302, r_ok, r302]
        c = make_client()
        with pytest.raises(RouterAPIError) as ei:
            c.call("acl", "show", {})
        assert "302" in str(ei.value)


class TestShowListFallback:
    """show_list 的 TYPE 方言回退 —— 覆盖免费版固件的真实差异"""

    def test_paginated_dialect_works_first_try(self, session):
        session.post.return_value.json.side_effect = [
            {"code": 0},
            {"code": 0, "results": {"total": 0, "data": []}},
        ]
        c = make_client()
        assert c.show_list("acl")["total"] == 0

    def test_falls_back_to_empty_param(self, session):
        """第一档 2007，第二档空参成功（如 wifi / alg / mesh 这类）"""
        session.post.return_value.json.side_effect = [
            {"code": 0},
            {"code": 2007, "message": "unknown TYPE (total)"},
            {"code": 0, "results": {"data": [{"id": 1}]}},
        ]
        c = make_client()
        r = c.show_list("wifi")
        assert r["data"] == [{"id": 1}]

    def test_falls_back_to_type_all(self, session):
        """前两档 2007，第三档 TYPE=all 成功（如 dns / collect_conn）"""
        session.post.return_value.json.side_effect = [
            {"code": 0},
            {"code": 2007, "message": "unknown TYPE (total)"},
            {"code": 2007, "message": "unknown TYPE (data)"},
            {"code": 0, "results": {"data": [], "total": 0}},
        ]
        c = make_client()
        assert c.show_list("dns")["total"] == 0

    def test_1003_not_retried(self, session):
        """函数不存在时不应重试，直接抛出"""
        session.post.return_value.json.side_effect = [
            {"code": 0},
            {"code": 1003, "message": "Access denied"},
        ]
        c = make_client()
        with pytest.raises(RouterAPIError) as ei:
            c.show_list("nonexistent_func")
        assert "1003" in str(ei.value)

    def test_paginate_false_sends_param_only(self, session):
        session.post.return_value.json.side_effect = [
            {"code": 0},
            {"code": 0, "results": {"data": []}},
        ]
        c = make_client()
        c.show_list("mesh", paginate=False)
        # 验证发出的 param 不含 TYPE/limit
        sent = session.post.call_args.kwargs["json"]
        assert sent["param"] == {}


class TestConvenience:
    def test_save_config_merges(self, session):
        session.post.return_value.json.side_effect = [
            {"code": 0},
            {"code": 0, "results": {"data": [{"hostname": "iKuai", "tz": 8}]}},
            {"code": 0, "results": {"code": 0}},
        ]
        c = make_client()
        c.save_config("basic", {"hostname": "new"})
        sent = session.post.call_args.kwargs["json"]
        assert sent["param"]["hostname"] == "new"
        assert sent["param"]["tz"] == 8     # 原字段保留

    def test_delete_uses_del_action(self, session):
        session.post.return_value.json.side_effect = [
            {"code": 0}, {"code": 0, "results": {}},
        ]
        c = make_client()
        c.delete("acl", {"id": 1})
        assert session.post.call_args.kwargs["json"]["action"] == "del"

    def test_enable_disable(self, session):
        session.post.return_value.json.side_effect = [
            {"code": 0}, {"code": 0}, {"code": 0},
        ]
        c = make_client()
        c.enable("acl", {"id": 1})
        assert session.post.call_args.kwargs["json"]["action"] == "up"
        c.disable("acl", {"id": 1})
        assert session.post.call_args.kwargs["json"]["action"] == "down"
