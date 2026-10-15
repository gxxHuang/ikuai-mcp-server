"""
爱快 iKuai 路由器 API 客户端 — 兼容 iKuai 3.x / 4.x（免费版 & 企业版）

实机验证：IK-Q3000 / 4.0.313 x64 arm（免费版）
错误码约定（实测）：
    0     成功
    1003  函数不存在（Access denied）—— func_name 写错
    1005  账号或密码错误
    1007  权限不足
    1008  会话已过期（需重新登录）
    2006  业务错误
    2007  函数存在但 TYPE 不合法 —— 参数里 TYPE 写错
    2014  服务启动异常（如抓包）
    3001  action 不合法 / 请求参数不合法 —— action 名错或参数缺失

注意：旧版响应会带 Result:10000，但它在成功和失败时都会出现，不能作为成功判据。
唯一权威判据是 code == 0。
"""

import base64
import hashlib
import logging
from typing import Any, Optional

import requests
import urllib3

# 设备用自签证书，默认不校验；这里关掉对应的重复告警，避免刷屏
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

logger = logging.getLogger(__name__)

# 会话失效的错误码，命中后自动重登一次
_SESSION_EXPIRED_CODES = (1008,)


class IKuaiClient:
    """爱快路由器 API 客户端"""

    def __init__(self, url: str, username: str, password: str, timeout: int = 30):
        self.base_url = url.rstrip("/")
        self.username = username
        self._password = password
        self._session: Optional[requests.Session] = None
        self.timeout = timeout
        # 设备是自签证书，https 时默认跳过校验
        self.verify: bool | str = False

    @property
    def session(self) -> requests.Session:
        """懒加载 session，自动登录"""
        if self._session is None:
            self._session = requests.Session()
            self._session.verify = self.verify
            self._authenticate()
        return self._session

    def _authenticate(self) -> None:
        """登录路由器

        401 由设备自身返回（未登录访问 /Action/call 时），需转为明确的认证失败。
        """
        passwd_md5 = hashlib.md5(self._password.encode()).hexdigest()
        pass_encoded = base64.b64encode(
            f"salt_11{passwd_md5}".encode()
        ).decode()

        payload = {
            "username": self.username,
            "passwd": passwd_md5,
            "pass": pass_encoded,
            "remember_password": "",
        }

        try:
            resp = self._session.post(
                f"{self.base_url}/Action/login",
                json=payload,
                headers={"isajax": "1"},
                timeout=self.timeout,
            )
        except requests.RequestException as e:
            raise RequestError(f"登录请求失败: {e}") from e

        if resp.status_code == 401:
            raise AuthenticationError(
                "登录被拒绝 (HTTP 401)：账号或密码错误，或该账号无权访问 API"
            )

        try:
            data = resp.json()
        except ValueError as e:
            raise AuthenticationError(
                f"登录响应不是 JSON (HTTP {resp.status_code}): {resp.text[:200]}"
            ) from e

        # 关键：唯一成功判据是 code == 0。
        # 旧版固件会同时返回 Result:10000，但该字段在失败时同样存在，不能参与判断。
        code = data.get("code")
        if code is None:
            # 极旧版本可能不带 code，回落到 Result + ErrMsg 判断
            if data.get("Result") == 10000 and str(data.get("ErrMsg", "Success")) == "Success":
                logger.info("iKuai 登录成功 (旧版协议)")
                return
            raise AuthenticationError(f"登录失败: {data}")

        if code != 0:
            raise AuthenticationError(
                f"登录失败: code={code} {data.get('message', '未知错误')}"
            )
        logger.info("iKuai 登录成功")

    def call(
        self,
        func_name: str,
        action: str = "show",
        param: Optional[dict] = None,
        retry: bool = True,
        timeout: Optional[int] = None,
    ) -> Any:
        """
        通用 API 调用

        Args:
            func_name: 功能模块名
            action: 操作类型 (show/add/edit/del/up/down/start/stop/save...)
            param: 参数字典
            retry: 是否在 session 过期时自动重试
            timeout: 自定义超时（Ping/Traceroute 等长任务需要更大值）

        Returns:
            API 响应中的 results 字段（无 results 时返回 data 或整体）
        """
        payload = {
            "func_name": func_name,
            "action": action,
            "param": param or {},
        }

        try:
            resp = self.session.post(
                f"{self.base_url}/Action/call",
                json=payload,
                headers={"isajax": "1"},
                timeout=timeout or self.timeout,
            )

            # 未登录时设备返回 302/401 而非 JSON
            if resp.status_code in (301, 302, 401, 403):
                if retry:
                    self._session = None
                    return self.call(func_name, action, param, retry=False, timeout=timeout)
                raise RouterAPIError(
                    f"[{func_name}] 会话失效 (HTTP {resp.status_code})，请检查账号密码"
                )

            try:
                data = resp.json()
            except ValueError:
                raw = resp.text
                if "sending to kernel" in raw:
                    raw = raw.replace("sending to kernel ...", "").strip()
                try:
                    import json as _json
                    data = _json.loads(raw) if raw else {}
                except ValueError as e:
                    raise RouterAPIError(
                        f"[{func_name}] 响应不是 JSON (HTTP {resp.status_code}): {raw[:200]}"
                    ) from e

            # 新版 4.0+ 格式: {"code":0,"message":"Success","results":{...}}
            if "code" in data:
                code = data["code"]
                if code != 0:
                    msg = data.get("message", "未知错误")
                    low = str(msg).lower()
                    if retry and (
                        code in _SESSION_EXPIRED_CODES
                        or "no login" in low
                        or "会话已过期" in str(msg)
                    ):
                        self._session = None
                        return self.call(func_name, action, param, retry=False, timeout=timeout)
                    raise RouterAPIError(f"[{func_name}] code={code} {msg}")
                if "results" in data:
                    return data["results"]
                return data.get("data", data)

            # 旧版格式: {"Result":10000,"ErrMsg":"Success","Data":{...}}
            err = str(data.get("ErrMsg", ""))
            if err and err != "Success":
                if retry and "no login authentication" in err.lower():
                    self._session = None
                    return self.call(func_name, action, param, retry=False, timeout=timeout)
                raise RouterAPIError(f"[{func_name}] {err}")
            return data.get("Data", data)

        except requests.RequestException as e:
            raise RequestError(f"请求失败 [{func_name}]: {e}") from e

    # ─── 便捷封装 ───

    def show(self, func_name: str, param: Optional[dict] = None, timeout: Optional[int] = None) -> Any:
        """执行 show 操作"""
        return self.call(func_name, "show", param, timeout=timeout)

    def save(self, func_name: str, param: dict) -> Any:
        """执行 save 操作（爱快多数配置修改需用 save 而非 edit）"""
        return self.call(func_name, "save", param)

    def save_config(self, func_name: str, updates: dict) -> Any:
        """读取配置 → 合并修改 → save（一步完成配置修改）；save 不支持时回退 edit"""
        current = self.show(func_name, {"TYPE": "data"})
        data = current.get("data", [{}])[0] if isinstance(current.get("data"), list) else current
        if not isinstance(data, dict):
            data = {}
        data.update(updates)
        try:
            return self.call(func_name, "save", data)
        except RouterAPIError:
            return self.call(func_name, "edit", data)

    def show_list(
        self,
        func_name: str,
        param: Optional[dict] = None,
        offset: int = 0,
        limit: int = 500,
        paginate: bool = True,
    ) -> Any:
        """执行列表查询，自动适配不同固件的分页方言

        实测（IK-Q3000 / 4.0.313 免费版）：同一批 func_name 里，一部分只认
        ``TYPE=total,data``，另一部分只认空参数 ``{}``，还有一部分要 ``TYPE=all``。
        传错会得到 ``code=2007 unknown TYPE``。

        这里按「分页参数 → 空参数 → TYPE=all」依次回退，让调用方不必关心固件差异。
        只有 2007（TYPE 不合法）才回退；其它错误（如 1003 函数不存在）照常抛出。

        Args:
            paginate: 传 False 时跳过 ``TYPE``/``limit``，直接发 ``param``（或空参）。
                      适合已知只认空参数的接口，可省掉一次探测请求。
        """
        if paginate:
            p = {"TYPE": "total,data", "limit": f"{offset},{limit}"}
            if param:
                p.update(param)
        else:
            p = dict(param or {})
        try:
            return self.call(func_name, "show", p)
        except RouterAPIError as e:
            if "2007" not in str(e):
                raise
        # 该固件不认这批 TYPE，退回调用方原始参数
        try:
            return self.call(func_name, "show", param or {})
        except RouterAPIError as e:
            if "2007" not in str(e):
                raise
        # 极端情况：只认 TYPE=all
        q = {"TYPE": "all"}
        if param:
            q.update({k: v for k, v in param.items() if k != "TYPE"})
        return self.call(func_name, "show", q)

    def add(self, func_name: str, param: dict) -> Any:
        """执行 add 操作"""
        return self.call(func_name, "add", param)

    def edit(self, func_name: str, param: dict) -> Any:
        """执行 edit 操作"""
        return self.call(func_name, "edit", param)

    def delete(self, func_name: str, param: dict) -> Any:
        """执行 del 操作"""
        return self.call(func_name, "del", param)

    def enable(self, func_name: str, param: dict) -> Any:
        """启用 (up)"""
        return self.call(func_name, "up", param)

    def disable(self, func_name: str, param: dict) -> Any:
        """禁用 (down)"""
        return self.call(func_name, "down", param)

    # ─── 系统概览 ───

    def get_sysstat(self) -> Any:
        """获取系统概览（CPU/内存/流量/版本等）"""
        return self.show("sysstat", {"TYPE": "all"})

    def get_version_info(self) -> dict:
        """获取设备版本信息（型号/版本/架构/SN）"""
        res = self.show("sysstat", {"TYPE": "verinfo"})
        return res.get("verinfo", {}) if isinstance(res, dict) else {}

    def get_wan_info(self) -> Any:
        """获取 WAN 口信息"""
        return self.show("homepage", {"TYPE": "wan_speed,sysstat,ac_status", "interface": ""})

    # ─── 监控中心 ───

    def get_line_monitor(self) -> Any:
        """线路监控"""
        return self.show("monitor_iface", {"TYPE": "iface_stream"})

    def get_terminal_list(self, ip_type: str = "v4", **kwargs) -> Any:
        """终端监控列表"""
        fn = "monitor_lanip" if ip_type == "v4" else "monitor_lanipv6"
        return self.show_list(fn, kwargs)

    def get_behavior_insight(self) -> Any:
        """行为洞察（应用流量）"""
        return self.show("monitor_app_flow", {"TYPE": "proto1_flow_history"})

    def get_policy_monitor(self) -> Any:
        """策略监控"""
        return self.show("monitor_l7qos", {"TYPE": "interface"})

    def get_load_monitor(self) -> Any:
        """负载监控"""
        return self.show("monitor_system", {"TYPE": "cpu,memory,stream"})

    def get_wireless_status(self) -> Any:
        """无线监控"""
        return self.show("homepage", {"TYPE": "wan_speed,sysstat,ac_status", "interface": "wan2"})


class AuthenticationError(Exception):
    """认证失败"""
    pass


class RouterAPIError(Exception):
    """路由器 API 返回错误"""
    pass


class RequestError(Exception):
    """网络请求失败"""
    pass
