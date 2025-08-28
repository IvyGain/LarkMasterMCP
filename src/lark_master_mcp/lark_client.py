"""Lark API client for interacting with Lark (Feishu) services."""

import asyncio
import json
import time
from typing import Any, Dict, List, Optional
import httpx
from pydantic import BaseModel


class LarkAuth(BaseModel):
    """Lark authentication token holder."""
    access_token: str
    expires_at: int


class LarkClient:
    """Client for Lark (Feishu) API operations."""
    
    BASE_URL = "https://open.feishu.cn/open-apis"
    
    def __init__(self, app_id: str, app_secret: str):
        self.app_id = app_id
        self.app_secret = app_secret
        self.auth: Optional[LarkAuth] = None
        self.client = httpx.AsyncClient()
    
    async def _ensure_auth(self) -> str:
        """Ensure we have a valid access token."""
        if self.auth and self.auth.expires_at > int(time.time()):
            return self.auth.access_token
        
        # Get new access token
        response = await self.client.post(
            f"{self.BASE_URL}/auth/v3/tenant_access_token/internal",
            json={
                "app_id": self.app_id,
                "app_secret": self.app_secret
            }
        )
        response.raise_for_status()
        data = response.json()
        
        if data.get("code") != 0:
            raise Exception(f"Failed to get access token: {data.get('msg')}")
        
        self.auth = LarkAuth(
            access_token=data["tenant_access_token"],
            expires_at=int(time.time()) + data["expire"] - 60  # 1 minute buffer
        )
        
        return self.auth.access_token
    
    async def _make_request(
        self, 
        method: str, 
        endpoint: str, 
        data: Optional[Dict] = None,
        params: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Make authenticated request to Lark API."""
        token = await self._ensure_auth()
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        url = f"{self.BASE_URL}{endpoint}"
        
        response = await self.client.request(
            method=method,
            url=url,
            headers=headers,
            json=data,
            params=params
        )
        response.raise_for_status()
        
        result = response.json()
        if result.get("code") != 0:
            raise Exception(f"API Error: {result.get('msg', 'Unknown error')}")
        
        return result.get("data", {})
    
    async def send_message(
        self, 
        chat_id: str, 
        message: str, 
        message_type: str = "text"
    ) -> Dict[str, Any]:
        """Send a message to a chat or user."""
        content = {"text": message} if message_type == "text" else {"content": message}
        
        data = {
            "receive_id": chat_id,
            "msg_type": message_type,
            "content": json.dumps(content)
        }
        
        return await self._make_request(
            "POST",
            "/im/v1/messages",
            data=data,
            params={"receive_id_type": "chat_id"}
        )
    
    async def create_calendar_event(
        self,
        title: str,
        start_time: str,
        end_time: str,
        attendees: List[str] = None,
        description: str = ""
    ) -> Dict[str, Any]:
        """Create a calendar event."""
        attendee_list = []
        if attendees:
            attendee_list = [{"type": "user", "user_id": uid} for uid in attendees]
        
        data = {
            "summary": title,
            "description": description,
            "start_time": {"timestamp": start_time},
            "end_time": {"timestamp": end_time},
            "attendee_ability": "can_see_others",
            "free_busy_status": "busy",
            "attendees": attendee_list
        }
        
        return await self._make_request("POST", "/calendar/v4/calendars/primary/events", data=data)
    
    async def get_user_info(self, user_id: str) -> Dict[str, Any]:
        """Get user information."""
        return await self._make_request(
            "GET",
            f"/contact/v3/users/{user_id}",
            params={"user_id_type": "user_id"}
        )
    
    async def list_chats(self) -> Dict[str, Any]:
        """List all chats the bot has access to."""
        return await self._make_request("GET", "/im/v1/chats")
    
    async def upload_file(self, file_path: str, file_type: str) -> Dict[str, Any]:
        """Upload a file to Lark."""
        with open(file_path, "rb") as f:
            files = {"file": f}
            token = await self._ensure_auth()
            
            # Use form data for file upload
            response = await self.client.post(
                f"{self.BASE_URL}/im/v1/files",
                headers={"Authorization": f"Bearer {token}"},
                files=files,
                data={"file_type": file_type}
            )
            response.raise_for_status()
            
            result = response.json()
            if result.get("code") != 0:
                raise Exception(f"Upload failed: {result.get('msg')}")
            
            return result.get("data", {})
    
    async def create_document(
        self, 
        title: str, 
        content: str = "", 
        folder_token: Optional[str] = None
    ) -> Dict[str, Any]:
        """Create a new document in Lark Docs."""
        data = {
            "title": title,
            "type": "doc"
        }
        
        if folder_token:
            data["folder_token"] = folder_token
        
        # Create document
        doc_result = await self._make_request("POST", "/docx/v1/documents", data=data)
        
        # Add content if provided
        if content:
            doc_token = doc_result["document"]["document_id"]
            content_data = {
                "requests": [{
                    "insert_text": {
                        "location": {"index": 0},
                        "text": content
                    }
                }]
            }
            await self._make_request(
                "PATCH",
                f"/docx/v1/documents/{doc_token}/content",
                data=content_data
            )
        
        return doc_result
    
    async def search_messages(
        self, 
        query: str, 
        chat_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Search for messages."""
        params = {"query": query}
        if chat_id:
            params["chat_id"] = chat_id
        
        return await self._make_request("GET", "/im/v1/messages/search", params=params)
    
    async def get_department_users(self, department_id: str) -> Dict[str, Any]:
        """Get users in a department."""
        return await self._make_request(
            "GET",
            "/contact/v3/users",
            params={"department_id": department_id}
        )
    
    async def create_meeting(
        self,
        title: str,
        start_time: str,
        duration: int,
        attendees: List[str] = None
    ) -> Dict[str, Any]:
        """Create a video meeting."""
        data = {
            "topic": title,
            "start_time": start_time,
            "duration": duration,
            "settings": {
                "topic": title,
                "action_permissions": [
                    {"permission": "manage_attendee", "permission_checkers": ["host"]}
                ]
            }
        }
        
        if attendees:
            data["attendees"] = [{"user_id": uid} for uid in attendees]
        
        return await self._make_request("POST", "/vc/v1/meetings", data=data)
    
    async def get_spreadsheet_data(
        self, 
        spreadsheet_token: str, 
        range_: str = ""
    ) -> Dict[str, Any]:
        """Get data from a spreadsheet."""
        endpoint = f"/sheets/v4/spreadsheets/{spreadsheet_token}/values_batch_get"
        params = {}
        
        if range_:
            params["ranges"] = range_
        
        return await self._make_request("GET", endpoint, params=params)
    
    async def update_spreadsheet_data(
        self, 
        spreadsheet_token: str, 
        range_: str,
        values: List[List[Any]]
    ) -> Dict[str, Any]:
        """Update data in a spreadsheet."""
        endpoint = f"/sheets/v4/spreadsheets/{spreadsheet_token}/values_batch_update"
        data = {
            "data": [{
                "range": range_,
                "values": values
            }]
        }
        return await self._make_request("POST", endpoint, data=data)
    
    async def create_task(
        self,
        title: str,
        description: str = "",
        due_date: Optional[str] = None,
        assignee: Optional[str] = None,
        followers: List[str] = None
    ) -> Dict[str, Any]:
        """Create a task."""
        data = {
            "title": title,
            "description": description
        }
        if due_date:
            data["due_date"] = due_date
        if assignee:
            data["assignee"] = assignee
        if followers:
            data["followers"] = followers
        
        return await self._make_request("POST", "/tasks/v1/tasks", data=data)
    
    async def update_task_status(
        self,
        task_id: str,
        status: str,
        comment: Optional[str] = None
    ) -> Dict[str, Any]:
        """Update task status."""
        data = {"status": status}
        if comment:
            data["comment"] = comment
            
        return await self._make_request(
            "PATCH",
            f"/tasks/v1/tasks/{task_id}",
            data=data
        )
    
    async def create_approval(
        self,
        approval_code: str,
        form_data: Dict[str, Any],
        approvers: List[str] = None,
        cc_users: List[str] = None
    ) -> Dict[str, Any]:
        """Create an approval request."""
        data = {
            "approval_code": approval_code,
            "form": form_data
        }
        if approvers:
            data["approvers"] = approvers
        if cc_users:
            data["cc_users"] = cc_users
            
        return await self._make_request("POST", "/approval/v4/instances", data=data)
    
    async def get_approval_status(self, instance_id: str) -> Dict[str, Any]:
        """Get approval status."""
        return await self._make_request(
            "GET",
            f"/approval/v4/instances/{instance_id}"
        )
    
    async def create_wiki_space(
        self,
        name: str,
        description: str = "",
        members: List[str] = None
    ) -> Dict[str, Any]:
        """Create a wiki space."""
        data = {
            "name": name,
            "description": description
        }
        if members:
            data["members"] = members
            
        return await self._make_request("POST", "/wiki/v2/spaces", data=data)
    
    async def create_wiki_page(
        self,
        space_id: str,
        title: str,
        content: str = "",
        parent_page_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Create a wiki page."""
        data = {
            "title": title,
            "content": content
        }
        if parent_page_id:
            data["parent_page_id"] = parent_page_id
            
        return await self._make_request(
            "POST",
            f"/wiki/v2/spaces/{space_id}/pages",
            data=data
        )
    
    async def add_bot_to_chat(self, chat_id: str) -> Dict[str, Any]:
        """Add bot to chat."""
        return await self._make_request(
            "POST",
            f"/im/v1/chats/{chat_id}/members",
            data={"member_ids": ["bot"]}
        )
    
    async def create_chat_group(
        self,
        name: str,
        description: str = "",
        member_ids: List[str] = None,
        owner_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Create a chat group."""
        data = {
            "name": name,
            "description": description
        }
        if member_ids:
            data["member_ids"] = member_ids
        if owner_id:
            data["owner_id"] = owner_id
            
        return await self._make_request("POST", "/im/v1/chats", data=data)
    
    async def get_chat_members(self, chat_id: str) -> Dict[str, Any]:
        """Get chat members."""
        return await self._make_request(
            "GET",
            f"/im/v1/chats/{chat_id}/members"
        )
    
    async def create_leave_request(
        self,
        leave_type: str,
        start_date: str,
        end_date: str,
        reason: str,
        approver_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Create a leave request."""
        data = {
            "leave_type": leave_type,
            "start_date": start_date,
            "end_date": end_date,
            "reason": reason
        }
        if approver_id:
            data["approver_id"] = approver_id
            
        return await self._make_request("POST", "/attendance/v1/leave_requests", data=data)
    
    async def get_attendance_records(
        self,
        user_ids: List[str],
        start_date: str,
        end_date: str
    ) -> Dict[str, Any]:
        """Get attendance records."""
        params = {
            "user_ids": ",".join(user_ids),
            "start_date": start_date,
            "end_date": end_date
        }
        return await self._make_request(
            "GET",
            "/attendance/v1/records",
            params=params
        )
    
    async def create_poll(
        self,
        chat_id: str,
        question: str,
        options: List[str],
        anonymous: bool = False,
        multiple_choice: bool = False
    ) -> Dict[str, Any]:
        """Create a poll in chat."""
        data = {
            "question": question,
            "options": options,
            "anonymous": anonymous,
            "multiple_choice": multiple_choice
        }
        return await self._make_request(
            "POST",
            f"/im/v1/chats/{chat_id}/polls",
            data=data
        )
    
    async def share_screen(
        self,
        meeting_id: str,
        share_type: str = "screen"
    ) -> Dict[str, Any]:
        """Share screen in meeting."""
        data = {"share_type": share_type}
        return await self._make_request(
            "POST",
            f"/vc/v1/meetings/{meeting_id}/share_screen",
            data=data
        )
    
    async def create_drive_folder(
        self,
        name: str,
        parent_token: Optional[str] = None
    ) -> Dict[str, Any]:
        """Create a drive folder."""
        data = {"title": name, "type": "folder"}
        if parent_token:
            data["parent_token"] = parent_token
            
        return await self._make_request("POST", "/drive/v1/files", data=data)
    
    async def share_file(
        self,
        file_token: str,
        user_ids: List[str],
        permission: str = "view",
        notify: bool = True
    ) -> Dict[str, Any]:
        """Share a file with users."""
        data = {
            "members": [{"member_id": uid, "perm": permission} for uid in user_ids],
            "notify": notify
        }
        return await self._make_request(
            "POST",
            f"/drive/v1/permissions/{file_token}/members",
            data=data
        )
    
    async def search_wiki(
        self,
        query: str,
        space_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Search wiki."""
        params = {"query": query}
        if space_id:
            params["space_id"] = space_id
            
        return await self._make_request("GET", "/wiki/v2/search", params=params)
    
    async def get_user_calendar(
        self,
        user_id: Optional[str] = None,
        start_time: str = None,
        end_time: str = None
    ) -> Dict[str, Any]:
        """Get user's calendar events."""
        calendar_id = user_id or "primary"
        params = {
            "start_time": start_time,
            "end_time": end_time
        }
        return await self._make_request(
            "GET",
            f"/calendar/v4/calendars/{calendar_id}/events",
            params=params
        )
    
    async def set_out_of_office(
        self,
        enabled: bool,
        message: Optional[str] = None,
        start_time: Optional[str] = None,
        end_time: Optional[str] = None
    ) -> Dict[str, Any]:
        """Set out of office."""
        data = {"enabled": enabled}
        if enabled and message:
            data["message"] = message
        if start_time:
            data["start_time"] = start_time
        if end_time:
            data["end_time"] = end_time
            
        return await self._make_request(
            "POST",
            "/calendar/v4/out_of_office",
            data=data
        )
    
    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()