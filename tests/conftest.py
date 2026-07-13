"""pytest fixtures for iKuai MCP server tests"""
from unittest.mock import MagicMock, patch

import pytest


@pytest.fixture
def mock_router():
    """Mock a router API response"""
    with patch("requests.Session") as mock_session:
        session_instance = MagicMock()
        mock_session.return_value = session_instance

        # Mock login response
        session_instance.post.return_value.json.return_value = {
            "code": 0,
            "message": "Success",
        }

        yield session_instance


@pytest.fixture
def mock_sysstat():
    """Mock system stats response"""
    return {
        "code": 0,
        "message": "Success",
        "results": {
            "sysstat": {
                "cpu": ["5.0%", "3.0%", "7.0%"],
                "memory": {"total": 496444, "used": "45%"},
                "stream": {"connect_num": 100, "upload": 50000, "download": 200000},
                "verinfo": {
                    "modelname": "IK-Q3000",
                    "verstring": "4.0.303 x64 Build202606251646",
                    "version": "4.0.303",
                    "sn": "TEST000000000",
                },
                "uptime": 36000,
            }
        },
    }


@pytest.fixture
def mock_empty_list():
    """Mock empty list response"""
    return {
        "code": 0,
        "message": "Success",
        "results": {"total": 0, "data": []},
    }
