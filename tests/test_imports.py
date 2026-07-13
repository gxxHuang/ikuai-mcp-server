"""Smoke tests — verify all tool modules can be imported and registered"""


def test_import_client():
    from src.ikuai_mcp.client import IKuaiClient
    assert IKuaiClient is not None


def test_import_all_tools():
    modules = [
        "system", "network", "security", "qos_routing",
        "auth", "wireless", "advanced", "logs", "settings",
    ]
    for mod in modules:
        __import__(f"src.ikuai_mcp.tools.{mod}")
