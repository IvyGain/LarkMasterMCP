"""Lark API client for interacting with Lark (Feishu) services."""

import asyncio
import json
import logging
import time
from typing import Any, Dict, List, Optional
import httpx
from pydantic import BaseModel

# Setup logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


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
        
        try:
            logger.info("Requesting new Lark access token...")
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
                error_msg = f"Failed to get access token: {data.get('msg')}"
                logger.error(error_msg)
                raise Exception(error_msg)
            
            self.auth = LarkAuth(
                access_token=data["tenant_access_token"],
                expires_at=int(time.time()) + data["expire"] - 60  # 1 minute buffer
            )
            logger.info("Successfully obtained new access token")
            return self.auth.access_token
            
        except httpx.HTTPError as e:
            error_msg = f"HTTP error during authentication: {str(e)}"
            logger.error(error_msg)
            raise Exception(error_msg)
        except Exception as e:
            logger.error(f"Unexpected error during authentication: {str(e)}")
            raise
    
    async def _make_request(
        self, 
        method: str, 
        endpoint: str, 
        data: Optional[Dict] = None,
        params: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Make authenticated request to Lark API."""
        try:
            token = await self._ensure_auth()
            headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            }
            
            url = f"{self.BASE_URL}{endpoint}"
            logger.debug(f"Making {method} request to {url}")
            
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
                error_msg = f"API Error ({result.get('code')}): {result.get('msg', 'Unknown error')}"
                logger.error(f"API Error for {endpoint}: {error_msg}")
                raise Exception(error_msg)
            
            logger.debug(f"Successful API call to {endpoint}")
            return result.get("data", {})
            
        except httpx.HTTPError as e:
            error_msg = f"HTTP error for {endpoint}: {str(e)}"
            logger.error(error_msg)
            raise Exception(error_msg)
        except json.JSONDecodeError as e:
            error_msg = f"Invalid JSON response from {endpoint}: {str(e)}"
            logger.error(error_msg)
            raise Exception(error_msg)
        except Exception as e:
            logger.error(f"Unexpected error for {endpoint}: {str(e)}")
            raise
    
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
    
    async def transfer_approval(
        self,
        instance_id: str,
        user_id: str,
        comment: Optional[str] = None
    ) -> Dict[str, Any]:
        """Transfer approval to another user."""
        data = {"user_id": user_id}
        if comment:
            data["comment"] = comment
        return await self._make_request(
            "POST",
            f"/approval/v4/instances/{instance_id}/transfer",
            data=data
        )
    
    async def cancel_approval(
        self,
        instance_id: str,
        reason: Optional[str] = None
    ) -> Dict[str, Any]:
        """Cancel an approval instance."""
        data = {}
        if reason:
            data["reason"] = reason
        return await self._make_request(
            "POST",
            f"/approval/v4/instances/{instance_id}/cancel",
            data=data
        )
    
    async def cc_approval(
        self,
        instance_id: str,
        cc_users: List[str],
        comment: Optional[str] = None
    ) -> Dict[str, Any]:
        """CC approval to additional users."""
        data = {"cc_users": cc_users}
        if comment:
            data["comment"] = comment
        return await self._make_request(
            "POST",
            f"/approval/v4/instances/{instance_id}/cc",
            data=data
        )
    
    async def add_approval_comment(
        self,
        instance_id: str,
        comment: str,
        comment_type: str = "general"
    ) -> Dict[str, Any]:
        """Add comment to approval."""
        data = {
            "comment": comment,
            "comment_type": comment_type
        }
        return await self._make_request(
            "POST",
            f"/approval/v4/instances/{instance_id}/comments",
            data=data
        )
    
    async def rollback_approval(
        self,
        instance_id: str,
        reason: Optional[str] = None
    ) -> Dict[str, Any]:
        """Rollback approval to previous step."""
        data = {}
        if reason:
            data["reason"] = reason
        return await self._make_request(
            "POST",
            f"/approval/v4/instances/{instance_id}/rollback",
            data=data
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
    
    async def start_meeting_recording(
        self,
        meeting_id: str
    ) -> Dict[str, Any]:
        """Start meeting recording."""
        return await self._make_request(
            "POST",
            f"/vc/v1/meetings/{meeting_id}/recording/start"
        )
    
    async def stop_meeting_recording(
        self,
        meeting_id: str
    ) -> Dict[str, Any]:
        """Stop meeting recording."""
        return await self._make_request(
            "POST",
            f"/vc/v1/meetings/{meeting_id}/recording/stop"
        )
    
    async def get_meeting_recording(
        self,
        meeting_id: str
    ) -> Dict[str, Any]:
        """Get meeting recording file information."""
        return await self._make_request(
            "GET",
            f"/vc/v1/meetings/{meeting_id}/recording"
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
    
    async def batch_create_records(
        self,
        app_token: str,
        table_id: str,
        records: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Batch create records in Bitable."""
        endpoint = f"/bitable/v1/apps/{app_token}/tables/{table_id}/records/batch_create"
        data = {"records": records}
        return await self._make_request("POST", endpoint, data=data)
    
    async def batch_update_records(
        self,
        app_token: str,
        table_id: str,
        records: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Batch update records in Bitable."""
        endpoint = f"/bitable/v1/apps/{app_token}/tables/{table_id}/records/batch_update"
        data = {"records": records}
        return await self._make_request("POST", endpoint, data=data)
    
    async def get_user_by_email_or_phone(
        self,
        emails: List[str] = None,
        mobiles: List[str] = None
    ) -> Dict[str, Any]:
        """Get user by email or phone."""
        params = {}
        if emails:
            params["emails"] = ",".join(emails)
        if mobiles:
            params["mobiles"] = ",".join(mobiles)
        
        return await self._make_request("GET", "/contact/v3/users/batch", params=params)
    
    async def search_documents(
        self,
        query: str,
        doc_types: List[str] = None,
        owner_ids: List[str] = None,
        chat_ids: List[str] = None
    ) -> Dict[str, Any]:
        """Search documents."""
        params = {"query": query}
        if doc_types:
            params["doc_types"] = ",".join(doc_types)
        if owner_ids:
            params["owner_ids"] = ",".join(owner_ids)
        if chat_ids:
            params["chat_ids"] = ",".join(chat_ids)
            
        return await self._make_request("GET", "/suite/docs-api/search/object", params=params)
    
    async def import_document(
        self,
        file_path: str,
        file_type: str,
        folder_token: Optional[str] = None
    ) -> Dict[str, Any]:
        """Import document to Lark Docs."""
        with open(file_path, "rb") as f:
            files = {"file": f}
            token = await self._ensure_auth()
            
            params = {"type": file_type}
            if folder_token:
                params["folder_token"] = folder_token
                
            response = await self.client.post(
                f"{self.BASE_URL}/drive/v1/import_tasks/import_user_file",
                headers={"Authorization": f"Bearer {token}"},
                files=files,
                params=params
            )
            response.raise_for_status()
            
            result = response.json()
            if result.get("code") != 0:
                raise Exception(f"Import failed: {result.get('msg')}")
            
            return result.get("data", {})
    
    async def export_document(
        self,
        document_id: str,
        export_format: str
    ) -> Dict[str, Any]:
        """Export document from Lark Docs."""
        endpoint = f"/drive/v1/export_tasks"
        data = {
            "file_token": document_id,
            "type": export_format
        }
        return await self._make_request("POST", endpoint, data=data)
    
    async def get_document_content(
        self,
        document_id: str,
        format: str = "text"
    ) -> Dict[str, Any]:
        """Get document content."""
        endpoint = f"/docx/v1/documents/{document_id}/raw_content"
        params = {"format": format}
        return await self._make_request("GET", endpoint, params=params)
    
    async def add_document_permission(
        self,
        document_token: str,
        member_type: str,
        member_id: str,
        permission: str
    ) -> Dict[str, Any]:
        """Add document permission."""
        endpoint = f"/drive/v1/permissions/{document_token}/members"
        data = {
            "member_type": member_type,
            "member_id": member_id,
            "perm": permission
        }
        return await self._make_request("POST", endpoint, data=data)
    
    async def list_free_busy(
        self,
        user_ids: List[str],
        start_time: str,
        end_time: str
    ) -> Dict[str, Any]:
        """List free/busy status."""
        data = {
            "user_ids": user_ids,
            "start_time": start_time,
            "end_time": end_time
        }
        return await self._make_request("POST", "/calendar/v4/freebusy/list", data=data)
    
    async def add_task_reminder(
        self,
        task_id: str,
        reminder_time: str,
        reminder_type: str = "absolute"
    ) -> Dict[str, Any]:
        """Add task reminder."""
        data = {
            "reminder_time": reminder_time,
            "reminder_type": reminder_type
        }
        return await self._make_request(
            "POST",
            f"/tasks/v1/tasks/{task_id}/reminders",
            data=data
        )
    
    # Bitable (Base) Additional Tools
    async def create_bitable_table(
        self,
        app_token: str,
        name: str,
        fields: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Create a new table in Bitable."""
        endpoint = f"/bitable/v1/apps/{app_token}/tables"
        data = {
            "table": {
                "name": name,
                "fields": fields
            }
        }
        return await self._make_request("POST", endpoint, data=data)
    
    async def create_bitable_view(
        self,
        app_token: str,
        table_id: str,
        view_name: str,
        view_type: str = "grid"
    ) -> Dict[str, Any]:
        """Create a view in Bitable table."""
        endpoint = f"/bitable/v1/apps/{app_token}/tables/{table_id}/views"
        data = {
            "view_name": view_name,
            "view_type": view_type
        }
        return await self._make_request("POST", endpoint, data=data)
    
    async def add_bitable_field(
        self,
        app_token: str,
        table_id: str,
        field_name: str,
        field_type: str
    ) -> Dict[str, Any]:
        """Add a field to Bitable table."""
        endpoint = f"/bitable/v1/apps/{app_token}/tables/{table_id}/fields"
        data = {
            "field_name": field_name,
            "type": field_type
        }
        return await self._make_request("POST", endpoint, data=data)
    
    async def get_bitable_records(
        self,
        app_token: str,
        table_id: str,
        view_id: Optional[str] = None,
        filter: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Get records from Bitable table."""
        endpoint = f"/bitable/v1/apps/{app_token}/tables/{table_id}/records"
        params = {}
        if view_id:
            params["view_id"] = view_id
        if filter:
            params["filter"] = json.dumps(filter)
        return await self._make_request("GET", endpoint, params=params)
    
    async def delete_bitable_records(
        self,
        app_token: str,
        table_id: str,
        record_ids: List[str]
    ) -> Dict[str, Any]:
        """Delete records from Bitable."""
        endpoint = f"/bitable/v1/apps/{app_token}/tables/{table_id}/records/batch_delete"
        data = {"records": record_ids}
        return await self._make_request("POST", endpoint, data=data)
    
    async def search_bitable_records(
        self,
        app_token: str,
        table_id: str,
        filter_info: Optional[Dict] = None,
        sort: Optional[List[Dict]] = None,
        field_names: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Search Bitable records with advanced filtering and sorting."""
        endpoint = f"/bitable/v1/apps/{app_token}/tables/{table_id}/records/search"
        data = {}
        if filter_info:
            data["filter"] = filter_info
        if sort:
            data["sort"] = sort
        if field_names:
            data["field_names"] = field_names
        return await self._make_request("POST", endpoint, data=data)
    
    async def get_bitable_fields(
        self,
        app_token: str,
        table_id: str
    ) -> Dict[str, Any]:
        """Get all fields information from Bitable table."""
        endpoint = f"/bitable/v1/apps/{app_token}/tables/{table_id}/fields"
        return await self._make_request("GET", endpoint)
    
    async def update_bitable_field(
        self,
        app_token: str,
        table_id: str,
        field_id: str,
        field_name: Optional[str] = None,
        property: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Update Bitable field properties."""
        endpoint = f"/bitable/v1/apps/{app_token}/tables/{table_id}/fields/{field_id}"
        data = {}
        if field_name:
            data["field_name"] = field_name
        if property:
            data["property"] = property
        return await self._make_request("PATCH", endpoint, data=data)
    
    async def create_bitable_app(
        self,
        name: str,
        folder_token: Optional[str] = None
    ) -> Dict[str, Any]:
        """Create a new Bitable app."""
        endpoint = "/bitable/v1/apps"
        data = {"name": name}
        if folder_token:
            data["folder_token"] = folder_token
        return await self._make_request("POST", endpoint, data=data)
    
    async def get_bitable_views(
        self,
        app_token: str,
        table_id: str
    ) -> Dict[str, Any]:
        """Get all views from Bitable table."""
        endpoint = f"/bitable/v1/apps/{app_token}/tables/{table_id}/views"
        return await self._make_request("GET", endpoint)
    
    async def update_bitable_view(
        self,
        app_token: str,
        table_id: str,
        view_id: str,
        view_name: Optional[str] = None,
        property: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Update Bitable view."""
        endpoint = f"/bitable/v1/apps/{app_token}/tables/{table_id}/views/{view_id}"
        data = {}
        if view_name:
            data["view_name"] = view_name
        if property:
            data["property"] = property
        return await self._make_request("PATCH", endpoint, data=data)
    
    # Messaging Additional Tools
    async def reply_message(
        self,
        message_id: str,
        content: str,
        message_type: str = "text"
    ) -> Dict[str, Any]:
        """Reply to a message."""
        data = {
            "content": json.dumps({"text": content}) if message_type == "text" else content,
            "msg_type": message_type
        }
        return await self._make_request(
            "POST",
            f"/im/v1/messages/{message_id}/reply",
            data=data
        )
    
    async def add_message_reaction(
        self,
        message_id: str,
        emoji_type: str
    ) -> Dict[str, Any]:
        """Add reaction to a message."""
        return await self._make_request(
            "POST",
            f"/im/v1/messages/{message_id}/reactions",
            data={"reaction_type": {"emoji_type": emoji_type}}
        )
    
    async def delete_message_reaction(
        self,
        message_id: str,
        reaction_id: str
    ) -> Dict[str, Any]:
        """Delete reaction from a message."""
        return await self._make_request(
            "DELETE",
            f"/im/v1/messages/{message_id}/reactions/{reaction_id}"
        )
    
    async def pin_message(
        self,
        message_id: str
    ) -> Dict[str, Any]:
        """Pin a message in chat."""
        return await self._make_request(
            "POST",
            f"/im/v1/pins",
            data={"message_id": message_id}
        )
    
    async def unpin_message(
        self,
        message_id: str
    ) -> Dict[str, Any]:
        """Unpin a message."""
        return await self._make_request(
            "DELETE",
            f"/im/v1/pins",
            params={"message_id": message_id}
        )
    
    async def forward_message(
        self,
        message_id: str,
        receive_id: str
    ) -> Dict[str, Any]:
        """Forward a message to another chat."""
        return await self._make_request(
            "POST",
            f"/im/v1/messages/{message_id}/forward",
            data={"receive_id": receive_id}
        )
    
    async def send_urgent_message(
        self,
        chat_id: str,
        message: str,
        urgent_users: List[str]
    ) -> Dict[str, Any]:
        """Send urgent message with notification."""
        data = {
            "receive_id": chat_id,
            "content": json.dumps({"text": message}),
            "msg_type": "text",
            "urgent_type": "urgent",
            "urgent_users": urgent_users
        }
        return await self._make_request(
            "POST",
            "/im/v1/messages",
            data=data,
            params={"receive_id_type": "chat_id"}
        )
    
    async def read_message(
        self,
        message_ids: List[str]
    ) -> Dict[str, Any]:
        """Mark messages as read."""
        return await self._make_request(
            "POST",
            "/im/v1/messages/read_users",
            data={"message_ids": message_ids}
        )
    
    async def get_message_read_users(
        self,
        message_id: str
    ) -> Dict[str, Any]:
        """Get list of users who read the message."""
        return await self._make_request(
            "GET",
            f"/im/v1/messages/{message_id}/read_users"
        )
    
    # Calendar Additional Tools
    async def create_calendar_reminder(
        self,
        event_id: str,
        minutes: int
    ) -> Dict[str, Any]:
        """Add reminder to calendar event."""
        return await self._make_request(
            "POST",
            f"/calendar/v4/calendars/primary/events/{event_id}/reminders",
            data={"minutes": minutes}
        )
    
    async def create_recurring_event(
        self,
        title: str,
        start_time: str,
        end_time: str,
        recurrence: str,
        attendees: List[str] = None
    ) -> Dict[str, Any]:
        """Create recurring calendar event."""
        attendee_list = []
        if attendees:
            attendee_list = [{"type": "user", "user_id": uid} for uid in attendees]
            
        data = {
            "summary": title,
            "start_time": {"timestamp": start_time},
            "end_time": {"timestamp": end_time},
            "recurrence": recurrence,
            "attendees": attendee_list
        }
        return await self._make_request(
            "POST",
            "/calendar/v4/calendars/primary/events",
            data=data
        )
    
    async def book_meeting_room(
        self,
        room_id: str,
        start_time: str,
        end_time: str,
        event_title: str
    ) -> Dict[str, Any]:
        """Book a meeting room."""
        data = {
            "summary": event_title,
            "start_time": {"timestamp": start_time},
            "end_time": {"timestamp": end_time},
            "location": {"room_id": room_id}
        }
        return await self._make_request(
            "POST",
            "/calendar/v4/calendars/primary/events",
            data=data
        )
    
    async def search_meeting_rooms(
        self,
        start_time: str,
        end_time: str,
        capacity: Optional[int] = None
    ) -> Dict[str, Any]:
        """Search available meeting rooms."""
        params = {
            "start_time": start_time,
            "end_time": end_time
        }
        if capacity:
            params["capacity"] = capacity
        return await self._make_request(
            "GET",
            "/calendar/v4/meeting_rooms/search",
            params=params
        )
    
    async def accept_calendar_event(
        self,
        event_id: str
    ) -> Dict[str, Any]:
        """Accept calendar event invitation."""
        return await self._make_request(
            "POST",
            f"/calendar/v4/calendars/primary/events/{event_id}/accept"
        )
    
    async def decline_calendar_event(
        self,
        event_id: str,
        reason: Optional[str] = None
    ) -> Dict[str, Any]:
        """Decline calendar event invitation."""
        data = {}
        if reason:
            data["reason"] = reason
        return await self._make_request(
            "POST",
            f"/calendar/v4/calendars/primary/events/{event_id}/decline",
            data=data
        )
    
    # Document Additional Tools
    async def add_document_comment(
        self,
        document_id: str,
        content: str,
        reply_to: Optional[str] = None
    ) -> Dict[str, Any]:
        """Add comment to document."""
        data = {"content": content}
        if reply_to:
            data["reply_to"] = reply_to
        return await self._make_request(
            "POST",
            f"/docx/v1/documents/{document_id}/comments",
            data=data
        )
    
    async def get_document_comments(
        self,
        document_id: str
    ) -> Dict[str, Any]:
        """Get document comments."""
        return await self._make_request(
            "GET",
            f"/docx/v1/documents/{document_id}/comments"
        )
    
    async def create_document_from_template(
        self,
        template_id: str,
        title: str,
        folder_token: Optional[str] = None
    ) -> Dict[str, Any]:
        """Create document from template."""
        data = {
            "template_id": template_id,
            "title": title
        }
        if folder_token:
            data["folder_token"] = folder_token
        return await self._make_request(
            "POST",
            "/docx/v1/documents/create_from_template",
            data=data
        )
    
    async def lock_document_section(
        self,
        document_id: str,
        block_id: str
    ) -> Dict[str, Any]:
        """Lock a section of document for editing."""
        return await self._make_request(
            "POST",
            f"/docx/v1/documents/{document_id}/blocks/{block_id}/lock"
        )
    
    async def unlock_document_section(
        self,
        document_id: str,
        block_id: str
    ) -> Dict[str, Any]:
        """Unlock a section of document."""
        return await self._make_request(
            "POST",
            f"/docx/v1/documents/{document_id}/blocks/{block_id}/unlock"
        )
    
    async def subscribe_document_changes(
        self,
        document_id: str,
        events: List[str]
    ) -> Dict[str, Any]:
        """Subscribe to document change events."""
        data = {"events": events}
        return await self._make_request(
            "POST",
            f"/docx/v1/documents/{document_id}/subscribe",
            data=data
        )
    
    # Bot/App Management Tools
    async def create_bot_menu(
        self,
        menu_items: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Create custom bot menu."""
        data = {"menu": {"items": menu_items}}
        return await self._make_request(
            "POST",
            "/bot/v3/menu",
            data=data
        )
    
    async def update_bot_info(
        self,
        name: Optional[str] = None,
        description: Optional[str] = None,
        avatar_key: Optional[str] = None
    ) -> Dict[str, Any]:
        """Update bot information."""
        data = {}
        if name:
            data["app_name"] = name
        if description:
            data["description"] = description
        if avatar_key:
            data["avatar_key"] = avatar_key
        return await self._make_request(
            "POST",
            "/bot/v3/info/update",
            data=data
        )
    
    async def subscribe_events(
        self,
        event_types: List[str],
        callback_url: str
    ) -> Dict[str, Any]:
        """Subscribe to bot events."""
        data = {
            "event_types": event_types,
            "callback_url": callback_url
        }
        return await self._make_request(
            "POST",
            "/event/v1/outbound_subscription",
            data=data
        )
    
    # Admin Tools
    async def get_app_usage_stats(
        self,
        start_date: str,
        end_date: str
    ) -> Dict[str, Any]:
        """Get app usage statistics."""
        params = {
            "start_date": start_date,
            "end_date": end_date
        }
        return await self._make_request(
            "GET",
            "/admin/v1/app_usage_stats",
            params=params
        )
    
    async def get_audit_logs(
        self,
        start_time: str,
        end_time: str,
        event_types: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Get audit logs."""
        params = {
            "start_time": start_time,
            "end_time": end_time
        }
        if event_types:
            params["event_types"] = ",".join(event_types)
        return await self._make_request(
            "GET",
            "/admin/v1/audit_logs",
            params=params
        )
    
    async def manage_app_permissions(
        self,
        app_id: str,
        permissions: List[str],
        action: str = "grant"
    ) -> Dict[str, Any]:
        """Manage app permissions."""
        data = {
            "app_id": app_id,
            "permissions": permissions,
            "action": action
        }
        return await self._make_request(
            "POST",
            "/admin/v1/app_permissions",
            data=data
        )
    
    # AI/Assistant Tools
    async def create_ai_agent(
        self,
        name: str,
        prompt: str,
        capabilities: List[str]
    ) -> Dict[str, Any]:
        """Create AI agent."""
        data = {
            "name": name,
            "prompt": prompt,
            "capabilities": capabilities
        }
        return await self._make_request(
            "POST",
            "/ai/v1/agents",
            data=data
        )
    
    async def chat_with_ai(
        self,
        agent_id: str,
        message: str,
        context: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Chat with AI agent."""
        data = {
            "agent_id": agent_id,
            "message": message
        }
        if context:
            data["context"] = context
        return await self._make_request(
            "POST",
            "/ai/v1/chat",
            data=data
        )
    
    # Workflow/Automation Tools
    async def create_workflow(
        self,
        name: str,
        trigger: Dict[str, Any],
        actions: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Create automation workflow."""
        data = {
            "name": name,
            "trigger": trigger,
            "actions": actions
        }
        return await self._make_request(
            "POST",
            "/workflow/v1/workflows",
            data=data
        )
    
    async def execute_workflow(
        self,
        workflow_id: str,
        input_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute a workflow."""
        return await self._make_request(
            "POST",
            f"/workflow/v1/workflows/{workflow_id}/execute",
            data=input_data
        )
    
    # OKR Tools
    async def create_okr(
        self,
        objective: str,
        key_results: List[Dict[str, Any]],
        period_id: str
    ) -> Dict[str, Any]:
        """Create OKR."""
        data = {
            "objective": objective,
            "key_results": key_results,
            "period_id": period_id
        }
        return await self._make_request(
            "POST",
            "/okr/v1/okrs",
            data=data
        )
    
    async def update_okr_progress(
        self,
        okr_id: str,
        key_result_id: str,
        progress: float,
        comment: Optional[str] = None
    ) -> Dict[str, Any]:
        """Update OKR progress."""
        data = {
            "progress": progress
        }
        if comment:
            data["comment"] = comment
        return await self._make_request(
            "POST",
            f"/okr/v1/okrs/{okr_id}/key_results/{key_result_id}/progress",
            data=data
        )
    
    # Form Tools
    async def create_form(
        self,
        title: str,
        fields: List[Dict[str, Any]],
        settings: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Create a form."""
        data = {
            "title": title,
            "fields": fields
        }
        if settings:
            data["settings"] = settings
        return await self._make_request(
            "POST",
            "/form/v1/forms",
            data=data
        )
    
    async def get_form_responses(
        self,
        form_id: str,
        start_time: Optional[str] = None,
        end_time: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get form responses."""
        params = {}
        if start_time:
            params["start_time"] = start_time
        if end_time:
            params["end_time"] = end_time
        return await self._make_request(
            "GET",
            f"/form/v1/forms/{form_id}/responses",
            params=params
        )
    
    # Helpdesk/Ticket Management Tools
    async def create_helpdesk_ticket(
        self,
        title: str,
        description: str,
        category: Optional[str] = None,
        priority: str = "normal"
    ) -> Dict[str, Any]:
        """Create a helpdesk ticket."""
        data = {
            "subject": title,
            "description": description,
            "priority": priority
        }
        if category:
            data["category"] = category
        return await self._make_request("POST", "/helpdesk/v1/tickets", data=data)
    
    async def get_helpdesk_ticket(
        self,
        ticket_id: str
    ) -> Dict[str, Any]:
        """Get helpdesk ticket details."""
        return await self._make_request(
            "GET",
            f"/helpdesk/v1/tickets/{ticket_id}"
        )
    
    async def update_helpdesk_ticket(
        self,
        ticket_id: str,
        status: Optional[str] = None,
        assignee: Optional[str] = None,
        comment: Optional[str] = None
    ) -> Dict[str, Any]:
        """Update helpdesk ticket."""
        data = {}
        if status:
            data["status"] = status
        if assignee:
            data["assignee"] = assignee
        if comment:
            data["comment"] = comment
        return await self._make_request(
            "PATCH",
            f"/helpdesk/v1/tickets/{ticket_id}",
            data=data
        )
    
    async def list_helpdesk_tickets(
        self,
        status: Optional[str] = None,
        assignee: Optional[str] = None
    ) -> Dict[str, Any]:
        """List helpdesk tickets."""
        params = {}
        if status:
            params["status"] = status
        if assignee:
            params["assignee"] = assignee
        return await self._make_request(
            "GET",
            "/helpdesk/v1/tickets",
            params=params
        )
    
    # Drive Advanced Operations
    async def create_file_version(
        self,
        file_token: str,
        name: Optional[str] = None,
        parent_type: str = "drive"
    ) -> Dict[str, Any]:
        """Create a new version of a file."""
        data = {"parent_type": parent_type}
        if name:
            data["name"] = name
        return await self._make_request(
            "POST",
            f"/drive/v1/files/{file_token}/versions",
            data=data
        )
    
    async def get_file_versions(
        self,
        file_token: str
    ) -> Dict[str, Any]:
        """Get file version history."""
        return await self._make_request(
            "GET",
            f"/drive/v1/files/{file_token}/versions"
        )
    
    async def update_file_permission(
        self,
        file_token: str,
        permission_id: str,
        role: str
    ) -> Dict[str, Any]:
        """Update file permission."""
        data = {"role": role}
        return await self._make_request(
            "PUT",
            f"/drive/v1/permissions/{file_token}/members/{permission_id}",
            data=data
        )
    
    async def get_file_permissions(
        self,
        file_token: str,
        type: str = "user"
    ) -> Dict[str, Any]:
        """Get file permissions."""
        params = {"type": type}
        return await self._make_request(
            "GET",
            f"/drive/v1/permissions/{file_token}/members",
            params=params
        )
    
    # ===== Minutes (議事録) API =====

    async def get_minute(
        self,
        minute_token: str
    ) -> Dict[str, Any]:
        """
        Get minute metadata.

        Args:
            minute_token: The token of the minute (from minute URL)

        Returns:
            Minute metadata including title, owner, create_time, etc.
        """
        return await self._make_request(
            "GET",
            f"/minutes/v1/minutes/{minute_token}"
        )

    async def get_minute_transcript(
        self,
        minute_token: str
    ) -> Dict[str, Any]:
        """
        Get minute transcript (文字起こし).

        Args:
            minute_token: The token of the minute

        Returns:
            Transcript data with speakers and text segments
        """
        return await self._make_request(
            "GET",
            f"/minutes/v1/minutes/{minute_token}/transcript"
        )

    async def get_minute_statistics(
        self,
        minute_token: str
    ) -> Dict[str, Any]:
        """
        Get minute statistics (発言統計).

        Args:
            minute_token: The token of the minute

        Returns:
            Statistics including speaker duration, word count, etc.
        """
        return await self._make_request(
            "GET",
            f"/minutes/v1/minutes/{minute_token}/statistics"
        )

    # ===== Interactive Message (インタラクティブメッセージ) =====

    async def send_interactive_message(
        self,
        chat_id: str,
        card: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Send an interactive card message with buttons.

        Args:
            chat_id: The chat ID to send to
            card: The card content (Lark Message Card format)

        Returns:
            API response with message_id
        """
        import json
        data = {
            "receive_id": chat_id,
            "msg_type": "interactive",
            "content": json.dumps(card)
        }
        return await self._make_request(
            "POST",
            "/im/v1/messages",
            data=data,
            params={"receive_id_type": "chat_id"}
        )

    async def update_interactive_message(
        self,
        message_id: str,
        card: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Update an existing interactive card message.

        Args:
            message_id: The message ID to update
            card: The new card content

        Returns:
            API response
        """
        import json
        data = {
            "content": json.dumps(card)
        }
        return await self._make_request(
            "PATCH",
            f"/im/v1/messages/{message_id}",
            data=data
        )

    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()