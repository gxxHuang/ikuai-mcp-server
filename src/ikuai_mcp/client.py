"""
爱快 iKuai 路由器 API 客户端
支持 iKuai 4.0.303+ 企业版 API
"""

import base64
import hashlib
import json
import logging
from typing import Optional

import requests

logger = logging.getLogger(__name__)


class IKuaiClient:
    """爱快路由器 API 客户端"""

    def __init__(self, url: str, username: str, password: str):
        self.base_url = url.rstrip("/")
        self.username = username
        self._password = password
        self._session: Optional[requests.Session] = None

    @property
    def session(self) -> requests.Session:
        """懒加载 session，自动登录"""
        if self._session is None:
            self._session = requests.Session()
            self._authenticate()
        return self._session

    def _authenticate(self):
        """登录路由器"""
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

        resp = self._session.post(
            f"{self.base_url}/Action/login",
            json=payload,
            headers={"isajax": "1"},
            timeout=10,
        )
        data = resp.json()
        if data.get("code") != 0 and data.get("Result") != 10000:
            raise AuthenticationError(
                f"登录失败: {data.get('message', data.get('ErrMsg', '未知错误'))}"
            )
        logger.info("iKuai 登录成功")

    def call(
        self,
        func_name: str,
        action: str = "show",
        param: Optional[dict] = None,
        retry: bool = True,
    ) -> dict:
        """
        通用 API 调用

        Args:
            func_name: 功能模块名
            action: 操作类型 (show/add/edit/del/up/down)
            param: 参数字典
            retry: 是否在 session 过期时自动重试

        Returns:
            API 响应中的 results 字段
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
                timeout=30,
            )

            # 处理非 JSON 响应
            try:
                data = resp.json()
            except Exception:
                raw = resp.text
                if "sending to kernel" in raw:
                    raw = raw.replace("sending to kernel ...", "").strip()
                data = json.loads(raw) if raw else {}

            # 企业版 4.0+ 格式: {"code": 0, "message": "Success", "results": {...}}
            if "code" in data:
                if data["code"] != 0:
                    msg = data.get("message", "未知错误")
                    if "no login" in str(msg).lower() and retry:
                        self._session = None
                        return self.call(func_name, action, param, retry=False)
                    raise RouterAPIError(f"[{func_name}] {msg}")
                return data.get("results", data)

            # 旧版格式: {"Result": 10000, "ErrMsg": "Success", "Data": {...}}
            if data.get("ErrMsg") != "Success":
                msg = data.get("ErrMsg", "未知错误")
                if "no login authentication" in str(msg) and retry:
                    self._session = None
                    return self.call(func_name, action, param, retry=False)
                raise RouterAPIError(f"[{func_name}] {msg}")
            return data.get("Data", data)

        except requests.RequestException as e:
            raise RequestError(f"请求失败 [{func_name}]: {e}")

    def show(self, func_name: str, param: Optional[dict] = None) -> dict:
        """执行 show 操作"""
        return self.call(func_name, "show", param)

    def save(self, func_name: str, param: dict) -> dict:
        """执行 save 操作（爱快多数配置修改需用 save 而非 edit）"""
        return self.call(func_name, "save", param)

    def save_config(self, func_name: str, updates: dict) -> dict:
        """读取配置 → 合并修改 → save（一步完成配置修改）；save 不支持时回退 edit"""
        current = self.show(func_name, {})
        data = current.get("data", [{}])[0] if isinstance(current.get("data"), list) else current
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
    ) -> dict:
        """执行列表查询（自动拼接分页参数）"""
        p = {"TYPE": "total,data", "limit": f"{offset},{limit}"}
        if param:
            p.update(param)
        return self.call(func_name, "show", p)

    def add(self, func_name: str, param: dict) -> dict:
        """执行 add 操作"""
        return self.call(func_name, "add", param)

    def edit(self, func_name: str, param: dict) -> dict:
        """执行 edit 操作"""
        return self.call(func_name, "edit", param)

    def delete(self, func_name: str, param: dict) -> dict:
        """执行 del 操作"""
        return self.call(func_name, "del", param)

    def enable(self, func_name: str, param: dict) -> dict:
        """启用 (up)"""
        return self.call(func_name, "up", param)

    def disable(self, func_name: str, param: dict) -> dict:
        """禁用 (down)"""
        return self.call(func_name, "down", param)

    # ─── 系统概览 ───

    def get_sysstat(self) -> dict:
        """获取系统运行状态（CPU/内存/流量/版本等）"""
        return self.show("homepage", {"TYPE": "sysstat"})

    def get_wan_info(self) -> dict:
        """获取 WAN 口信息"""
        return self.show("homepage", {"TYPE": "wan_speed,sysstat,ac_status", "interface": ""})

    # ─── 监控中心 ───

    def get_line_monitor(self) -> dict:
        """线路监控"""
        return self.show("monitor_iface", {"TYPE": "iface_stream"})

    def get_terminal_list(self, ip_type: str = "v4", **kwargs) -> dict:
        """终端监控列表"""
        fn = "monitor_lanip" if ip_type == "v4" else "monitor_lanipv6"
        return self.show_list(fn, kwargs)

    def get_behavior_insight(self) -> dict:
        """行为洞察（应用流量）"""
        return self.show("monitor_app_flow", {"TYPE": "proto1_flow_history"})

    def get_policy_monitor(self) -> dict:
        """策略监控"""
        return self.show("monitor_l7qos", {"TYPE": "interface"})

    def get_load_monitor(self) -> dict:
        """负载监控"""
        return self.show("monitor_system", {"TYPE": "cpu,memory,stream"})

    def get_wireless_status(self) -> dict:
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
