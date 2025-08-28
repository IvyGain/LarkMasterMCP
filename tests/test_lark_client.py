"""Tests for the Lark client."""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from lark_master_mcp.lark_client import LarkClient


@pytest.fixture
def mock_httpx():
    """Mock httpx client."""
    with patch('httpx.AsyncClient') as mock_client:
        client_instance = AsyncMock()
        mock_client.return_value.__aenter__.return_value = client_instance
        mock_client.return_value.__aexit__.return_value = None
        yield client_instance


@pytest.fixture
def lark_client():
    """Create LarkClient instance."""
    return LarkClient("test_app_id", "test_app_secret")


class TestLarkClient:
    """Test cases for LarkClient."""
    
    def test_client_initialization(self, lark_client):
        """Test client initializes correctly."""
        assert lark_client.app_id == "test_app_id"
        assert lark_client.app_secret == "test_app_secret"
        assert lark_client.base_url == "https://open.feishu.cn/open-apis"
        assert lark_client.access_token is None
    
    @pytest.mark.asyncio
    async def test_get_access_token(self, lark_client, mock_httpx):
        """Test access token retrieval."""
        # Mock response
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "code": 0,
            "msg": "success",
            "tenant_access_token": "t-test123",
            "expire": 7200
        }
        mock_httpx.post.return_value = mock_response
        
        # Get token
        token = await lark_client._get_access_token()
        
        # Verify
        assert token == "t-test123"
        assert lark_client.access_token == "t-test123"
        mock_httpx.post.assert_called_once()
        
    @pytest.mark.asyncio
    async def test_send_message(self, lark_client, mock_httpx):
        """Test send message functionality."""
        # Setup
        lark_client.access_token = "t-test123"
        
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "code": 0,
            "msg": "success",
            "data": {"message_id": "om_test123"}
        }
        mock_httpx.post.return_value = mock_response
        
        # Execute
        result = await lark_client.send_message("oc_chat123", "Hello", "text")
        
        # Verify
        assert result["message_id"] == "om_test123"
        mock_httpx.post.assert_called_once()
        
    @pytest.mark.asyncio
    async def test_get_user_info(self, lark_client, mock_httpx):
        """Test get user info functionality."""
        # Setup
        lark_client.access_token = "t-test123"
        
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "code": 0,
            "msg": "success", 
            "data": {
                "user": {
                    "user_id": "ou_test123",
                    "name": "Test User",
                    "email": "test@example.com"
                }
            }
        }
        mock_httpx.get.return_value = mock_response
        
        # Execute
        result = await lark_client.get_user_info("ou_test123")
        
        # Verify
        assert result["user"]["name"] == "Test User"
        assert result["user"]["user_id"] == "ou_test123"
        mock_httpx.get.assert_called_once()
        
    @pytest.mark.asyncio
    async def test_api_error_handling(self, lark_client, mock_httpx):
        """Test API error handling."""
        # Setup
        lark_client.access_token = "t-test123"
        
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "code": 99991663,
            "msg": "Invalid access token"
        }
        mock_httpx.post.return_value = mock_response
        
        # Execute and verify exception
        with pytest.raises(Exception) as exc_info:
            await lark_client.send_message("oc_chat123", "Hello", "text")
        
        assert "Invalid access token" in str(exc_info.value)
        
    @pytest.mark.asyncio
    async def test_list_chats(self, lark_client, mock_httpx):
        """Test list chats functionality."""
        # Setup
        lark_client.access_token = "t-test123"
        
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "code": 0,
            "msg": "success",
            "data": {
                "items": [
                    {"chat_id": "oc_chat1", "name": "Chat 1"},
                    {"chat_id": "oc_chat2", "name": "Chat 2"}
                ]
            }
        }
        mock_httpx.get.return_value = mock_response
        
        # Execute
        result = await lark_client.list_chats()
        
        # Verify
        assert len(result["items"]) == 2
        assert result["items"][0]["chat_id"] == "oc_chat1"
        mock_httpx.get.assert_called_once()