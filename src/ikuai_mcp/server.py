#!/usr/bin/env python3
"""
爱快 iKuai 路由器全功能 MCP Server
248 个工具 · 覆盖 iKuai 3.x / 4.x Web 后台功能

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
    """入口函数

    默认 stdio 模式，供 Claude Desktop / Cursor 等 AI 客户端接入；
    传 ``--transport`` 可切换为 HTTP/SSE，供脚本或远程集成调用：

        python -m ikuai_mcp.server                                # stdio
        python -m ikuai_mcp.server --transport http --port 8000    # HTTP
    """
    import argparse

    parser = argparse.ArgumentParser(
        prog="ikuai-mcp",
        description="爱快 iKuai 路由器 MCP Server",
    )
    parser.add_argument(
        "--transport",
        default="stdio",
        choices=["stdio", "http", "sse", "streamable-http"],
        help="传输方式，默认 stdio",
    )
    parser.add_argument("--host", default="127.0.0.1",
                        help="HTTP/SSE 监听地址，默认 127.0.0.1")
    parser.add_argument("--port", type=int, default=8000,
                        help="HTTP/SSE 监听端口，默认 8000")
    args = parser.parse_args()

    if args.transport == "stdio":
        mcp.run()
    else:
        mcp.run(transport=args.transport, host=args.host, port=args.port)


if __name__ == "__main__":
    main()
