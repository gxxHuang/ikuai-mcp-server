#!/usr/bin/env python3
"""
爱快 iKuai 路由器全功能 MCP Server
229 个工具 · 149 个 API 端点 · 覆盖 iKuai 4.0.303 企业版 Web 后台全部功能

用法:
    python -m ikuai_mcp.server                           # stdio 模式 (Claude Desktop)
    python -m ikuai_mcp.server --transport http --port 8000  # HTTP 模式

配置: 通过 .env 文件或环境变量设置 IKUAI_URL / IKUAI_USERNAME / IKUAI_PASSWORD
"""

import os

from dotenv import load_dotenv
from fastmcp import FastMCP

from .client import IKuaiClient
from .tools.advanced import register_tools as reg_advanced
from .tools.auth import register_tools as reg_auth
from .tools.logs import register_tools as reg_logs
from .tools.network import register_tools as reg_network
from .tools.qos_routing import register_tools as reg_qos
from .tools.security import register_tools as reg_security
from .tools.settings import register_tools as reg_settings
from .tools.system import register_tools
from .tools.wireless import register_tools as reg_wireless

load_dotenv()

mcp = FastMCP("iKuai Router Manager")

_client = None


def get_client():
    """获取或创建 iKuai 客户端单例"""
    global _client
    if _client is None:
        url = os.getenv("IKUAI_URL", "http://192.168.9.1")
        username = os.getenv("IKUAI_USERNAME", "admin")
        password = os.getenv("IKUAI_PASSWORD", "")
        if not password:
            raise RuntimeError("未设置 IKUAI_PASSWORD，请在 .env 文件或环境变量中配置路由器密码")
        _client = IKuaiClient(url, username, password)
    return _client


register_tools(mcp, get_client)
reg_network(mcp, get_client)
reg_security(mcp, get_client)
reg_qos(mcp, get_client)
reg_auth(mcp, get_client)
reg_wireless(mcp, get_client)
reg_advanced(mcp, get_client)
reg_logs(mcp, get_client)
reg_settings(mcp, get_client)


def main():
    """入口函数"""
    mcp.run()


if __name__ == "__main__":
    main()
