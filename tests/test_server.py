"""Tests for the MCP server."""

import pytest
from unittest.mock import AsyncMock, MagicMock
from lark_master_mcp.server import LarkMCPServer


@pytest.fixture
def mock_lark_client():
    """Mock Lark client for testing."""
    client = AsyncMock()
    client.send_message.return_value = {"message_id": "test_msg_123"}
    client.get_user_info.return_value = {"user": {"name": "Test User"}}
    return client


@pytest.fixture
def server(mock_lark_client):
    """Create server instance with mocked client."""
    server = LarkMCPServer("test_app_id", "test_app_secret")
    server.lark_client = mock_lark_client
    return server


class TestLarkMCPServer:
    """Test cases for LarkMCPServer."""
    
    def test_server_initialization(self):
        """Test server initializes correctly."""
        server = LarkMCPServer("app_id", "app_secret")
        assert server.server.name == "lark-master-mcp"
        assert server.lark_client.app_id == "app_id"
        assert server.lark_client.app_secret == "app_secret"
    
    @pytest.mark.asyncio  
    async def test_list_tools(self, server):
        """Test list_tools handler."""
        # Get all available tools from server
        tools = await server.server._list_tools_handlers["list_tools"]()
        
        # Verify we have 30 tools as expected
        assert len(tools) == 30
        
        # Check some key tools exist
        tool_names = [tool.name for tool in tools]
        assert "send_message" in tool_names
        assert "get_user_info" in tool_names  
        assert "create_calendar_event" in tool_names
        assert "upload_file" in tool_names
        
        # Verify tool structure
        assert all(hasattr(tool, 'name') for tool in tools)
        assert all(hasattr(tool, 'description') for tool in tools)
        assert all(hasattr(tool, 'inputSchema') for tool in tools)