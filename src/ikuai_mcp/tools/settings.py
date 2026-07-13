"""设备设置工具 — 基础设置/双机热备/云服务/密码管理/API令牌/远程访问(SSH/Telnet/FTP)/ALG/协议控制/内核设置"""


def register_tools(mcp, get_client):

    # ═══ 基础设置 ═══

    @mcp.tool(annotations={"readOnlyHint": True})
    def get_basic_settings() -> dict:
        """获取设备基础设置（主机名/时区/NTP 等）"""
        return get_client().show_list("basic")

    @mcp.tool
    def set_hostname(hostname: str) -> dict:
        """修改路由器主机名"""
        return get_client().save_config("basic", {"hostname": hostname})

    # ═══ 双机热备 ═══

    @mcp.tool(annotations={"readOnlyHint": True})
    def get_vrrp_config() -> dict:
        """获取双机热备 (VRRP) 配置"""
        return get_client().show_list("vrrp_config")

    # ═══ 云服务绑定 ═══

    @mcp.tool(annotations={"readOnlyHint": True})
    def get_cloud_binding_status() -> dict:
        """获取云服务绑定状态"""
        return get_client().show_list("register")

    # ═══ 登录管理 ═══

    @mcp.tool(annotations={"readOnlyHint": True})
    def list_admin_accounts() -> dict:
        """列出管理员账号"""
        return get_client().show("webuser", {"TYPE": "total,data", "limit": "0,100"})

    @mcp.tool
    def add_admin_account(username: str, password: str, permission: str = "admin", allowed_ip: str = "0.0.0.0/0") -> dict:
        """添加管理员账号

        Args:
            username: 用户名
            password: 密码
            permission: 权限组 "admin"(超级管理员) 或 "readonly"(只读)
            allowed_ip: 允许访问IP，如 "0.0.0.0/0"(不限制)
        """
        return get_client().add("webuser", {"username": username, "password": password, "permission": permission, "allow_ip": allowed_ip})

    @mcp.tool
    def change_admin_password(old_password: str, new_password: str, confirm: bool = False) -> dict:
        """修改管理员密码

        Args:
            old_password: 旧密码
            new_password: 新密码
            confirm: 必须设为 True
        """
        if not confirm:
            return {"error": "请设置 confirm=True 确认修改密码"}
        return get_client().call("usergroup", "edit", {"old_pass": old_password, "new_pass": new_password})

    @mcp.tool(annotations={"readOnlyHint": True})
    def list_api_tokens() -> dict:
        """列出个人 API 令牌"""
        return get_client().show_list("api_tokens")

    # ═══ 远程访问（SSH / Telnet / FTP / Web 端口）═══

    @mcp.tool(annotations={"readOnlyHint": True})
    def get_remote_access_config() -> dict:
        """获取远程访问配置（SSH/Telnet/FTP/Web 端口状态）

        返回字段:
        - open_sshd: SSH 服务状态 (0=关闭, 1=开启)
        - sshd_port: SSH 端口 (默认 22)
        - open_telnetd: Telnet 服务状态
        - open_ftp: FTP 服务状态
        - ftp_port: FTP 端口 (默认 21)
        - http_port: HTTP 端口 (默认 80)
        - https_port: HTTPS 端口 (默认 443)
        - force_https: 强制 HTTPS (0=否/1=是)
        - open_wanweb: 外网 Web 访问 (0=关闭/1=开启)
        """
        return get_client().show("remote_control", {})

    @mcp.tool
    def enable_ssh(enabled: bool, port: int = 22) -> dict:
        """启用/禁用 SSH 服务

        Args:
            enabled: True=开启SSH, False=关闭
            port: SSH 端口 (默认 22)
        """
        c = get_client()
        cfg = c.show("remote_control", {})["data"][0]
        cfg["open_sshd"] = 1 if enabled else 0
        cfg["sshd_port"] = port
        return c.call("remote_control", "save", cfg)

    @mcp.tool
    def enable_telnet(enabled: bool) -> dict:
        """启用/禁用 Telnet 服务

        Args:
            enabled: True=开启, False=关闭
        """
        c = get_client()
        cfg = c.show("remote_control", {})["data"][0]
        cfg["open_telnetd"] = 1 if enabled else 0
        return c.call("remote_control", "save", cfg)

    @mcp.tool
    def enable_ftp(enabled: bool, port: int = 21) -> dict:
        """启用/禁用 FTP 服务

        Args:
            enabled: True=开启, False=关闭
            port: FTP 端口 (默认 21)
        """
        c = get_client()
        cfg = c.show("remote_control", {})["data"][0]
        cfg["open_ftp"] = 1 if enabled else 0
        cfg["ftp_port"] = port
        return c.call("remote_control", "save", cfg)

    @mcp.tool
    def set_web_ports(http_port: int = 80, https_port: int = 443, force_https: bool = False) -> dict:
        """设置 Web 管理端口

        Args:
            http_port: HTTP 端口 (默认 80)
            https_port: HTTPS 端口 (默认 443)
            force_https: 是否强制 HTTPS
        """
        c = get_client()
        cfg = c.show("remote_control", {})["data"][0]
        cfg["http_port"] = http_port
        cfg["https_port"] = https_port
        cfg["force_https"] = 1 if force_https else 0
        return c.call("remote_control", "save", cfg)

    @mcp.tool
    def set_wan_web_access(enabled: bool) -> dict:
        """开启/关闭外网 Web 访问（从外网访问路由器后台）

        Args:
            enabled: True=允许外网访问, False=仅内网
        """
        c = get_client()
        cfg = c.show("remote_control", {})["data"][0]
        cfg["open_wanweb"] = 1 if enabled else 0
        return c.call("remote_control", "save", cfg)

    # ═══ ALG 设置 ═══

    @mcp.tool(annotations={"readOnlyHint": True})
    def get_alg_config() -> dict:
        """获取 ALG 设置（FTP/TFTP/SIP/H323 协议穿透）"""
        return get_client().show_list("alg")

    # ═══ 协议控制 ═══

    @mcp.tool(annotations={"readOnlyHint": True})
    def get_protocol_control() -> dict:
        """获取协议控制配置"""
        return get_client().show_list("core_control")

    # ═══ 内核设置 ═══

    @mcp.tool(annotations={"readOnlyHint": True})
    def get_kernel_settings() -> dict:
        """获取内核参数设置"""
        return get_client().show_list("ik_sysctl")

    # ═══ 任务管理 ═══

    @mcp.tool(annotations={"readOnlyHint": True})
    def list_tasks() -> dict:
        """列出任务管理中的任务"""
        return get_client().show_list("task_management")
