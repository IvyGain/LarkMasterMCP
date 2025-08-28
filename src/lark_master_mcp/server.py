"""MCP server implementation for Lark integration."""

import asyncio
import json
from typing import Any, Dict, List, Optional, Sequence
from mcp import types
from mcp.server import Server
from mcp.server.stdio import stdio_server
from pydantic import BaseModel

from .lark_client import LarkClient
from .tools import LARK_TOOLS


class LarkMCPServer:
    """Main MCP server for Lark integration."""
    
    def __init__(self, app_id: str, app_secret: str):
        self.server = Server("lark-master-mcp")
        self.lark_client = LarkClient(app_id, app_secret)
        self._register_handlers()
    
    def _register_handlers(self):
        """Register all MCP handlers."""
        
        @self.server.list_tools()
        async def handle_list_tools() -> List[types.Tool]:
            """List available Lark tools."""
            return [
                types.Tool(
                    name=tool["name"],
                    description=tool["description"],
                    inputSchema=tool["inputSchema"]
                )
                for tool in LARK_TOOLS
            ]
        
        @self.server.call_tool()
        async def handle_call_tool(
            name: str, arguments: Dict[str, Any]
        ) -> List[types.TextContent]:
            """Handle tool calls for Lark operations."""
            
            try:
                if name == "send_message":
                    result = await self.lark_client.send_message(
                        chat_id=arguments["chat_id"],
                        message=arguments["message"],
                        message_type=arguments.get("message_type", "text")
                    )
                    
                elif name == "create_calendar_event":
                    result = await self.lark_client.create_calendar_event(
                        title=arguments["title"],
                        start_time=arguments["start_time"],
                        end_time=arguments["end_time"],
                        attendees=arguments.get("attendees", []),
                        description=arguments.get("description", "")
                    )
                    
                elif name == "get_user_info":
                    result = await self.lark_client.get_user_info(
                        user_id=arguments["user_id"]
                    )
                    
                elif name == "list_chats":
                    result = await self.lark_client.list_chats()
                    
                elif name == "upload_file":
                    result = await self.lark_client.upload_file(
                        file_path=arguments["file_path"],
                        file_type=arguments["file_type"]
                    )
                    
                elif name == "create_document":
                    result = await self.lark_client.create_document(
                        title=arguments["title"],
                        content=arguments.get("content", ""),
                        folder_token=arguments.get("folder_token")
                    )
                    
                elif name == "search_messages":
                    result = await self.lark_client.search_messages(
                        query=arguments["query"],
                        chat_id=arguments.get("chat_id")
                    )
                    
                elif name == "get_department_users":
                    result = await self.lark_client.get_department_users(
                        department_id=arguments["department_id"]
                    )
                    
                elif name == "create_meeting":
                    result = await self.lark_client.create_meeting(
                        title=arguments["title"],
                        start_time=arguments["start_time"],
                        duration=arguments["duration"],
                        attendees=arguments.get("attendees", [])
                    )
                    
                elif name == "get_spreadsheet_data":
                    result = await self.lark_client.get_spreadsheet_data(
                        spreadsheet_token=arguments["spreadsheet_token"],
                        range_=arguments.get("range", "")
                    )
                    
                elif name == "update_spreadsheet_data":
                    result = await self.lark_client.update_spreadsheet_data(
                        spreadsheet_token=arguments["spreadsheet_token"],
                        range_=arguments["range"],
                        values=arguments["values"]
                    )
                    
                elif name == "create_task":
                    result = await self.lark_client.create_task(
                        title=arguments["title"],
                        description=arguments.get("description", ""),
                        due_date=arguments.get("due_date"),
                        assignee=arguments.get("assignee"),
                        followers=arguments.get("followers", [])
                    )
                    
                elif name == "update_task_status":
                    result = await self.lark_client.update_task_status(
                        task_id=arguments["task_id"],
                        status=arguments["status"],
                        comment=arguments.get("comment")
                    )
                    
                elif name == "create_approval":
                    result = await self.lark_client.create_approval(
                        approval_code=arguments["approval_code"],
                        form_data=arguments["form_data"],
                        approvers=arguments.get("approvers", []),
                        cc_users=arguments.get("cc_users", [])
                    )
                    
                elif name == "get_approval_status":
                    result = await self.lark_client.get_approval_status(
                        instance_id=arguments["instance_id"]
                    )
                    
                elif name == "create_wiki_space":
                    result = await self.lark_client.create_wiki_space(
                        name=arguments["name"],
                        description=arguments.get("description", ""),
                        members=arguments.get("members", [])
                    )
                    
                elif name == "create_wiki_page":
                    result = await self.lark_client.create_wiki_page(
                        space_id=arguments["space_id"],
                        title=arguments["title"],
                        content=arguments.get("content", ""),
                        parent_page_id=arguments.get("parent_page_id")
                    )
                    
                elif name == "add_bot_to_chat":
                    result = await self.lark_client.add_bot_to_chat(
                        chat_id=arguments["chat_id"]
                    )
                    
                elif name == "create_chat_group":
                    result = await self.lark_client.create_chat_group(
                        name=arguments["name"],
                        description=arguments.get("description", ""),
                        member_ids=arguments.get("member_ids", []),
                        owner_id=arguments.get("owner_id")
                    )
                    
                elif name == "get_chat_members":
                    result = await self.lark_client.get_chat_members(
                        chat_id=arguments["chat_id"]
                    )
                    
                elif name == "create_leave_request":
                    result = await self.lark_client.create_leave_request(
                        leave_type=arguments["leave_type"],
                        start_date=arguments["start_date"],
                        end_date=arguments["end_date"],
                        reason=arguments["reason"],
                        approver_id=arguments.get("approver_id")
                    )
                    
                elif name == "get_attendance_records":
                    result = await self.lark_client.get_attendance_records(
                        user_ids=arguments["user_ids"],
                        start_date=arguments["start_date"],
                        end_date=arguments["end_date"]
                    )
                    
                elif name == "create_poll":
                    result = await self.lark_client.create_poll(
                        chat_id=arguments["chat_id"],
                        question=arguments["question"],
                        options=arguments["options"],
                        anonymous=arguments.get("anonymous", False),
                        multiple_choice=arguments.get("multiple_choice", False)
                    )
                    
                elif name == "share_screen":
                    result = await self.lark_client.share_screen(
                        meeting_id=arguments["meeting_id"],
                        share_type=arguments.get("share_type", "screen")
                    )
                    
                elif name == "create_drive_folder":
                    result = await self.lark_client.create_drive_folder(
                        name=arguments["name"],
                        parent_token=arguments.get("parent_token")
                    )
                    
                elif name == "share_file":
                    result = await self.lark_client.share_file(
                        file_token=arguments["file_token"],
                        user_ids=arguments["user_ids"],
                        permission=arguments.get("permission", "view"),
                        notify=arguments.get("notify", True)
                    )
                    
                elif name == "search_wiki":
                    result = await self.lark_client.search_wiki(
                        query=arguments["query"],
                        space_id=arguments.get("space_id")
                    )
                    
                elif name == "get_user_calendar":
                    result = await self.lark_client.get_user_calendar(
                        user_id=arguments.get("user_id"),
                        start_time=arguments["start_time"],
                        end_time=arguments["end_time"]
                    )
                    
                elif name == "set_out_of_office":
                    result = await self.lark_client.set_out_of_office(
                        enabled=arguments["enabled"],
                        message=arguments.get("message"),
                        start_time=arguments.get("start_time"),
                        end_time=arguments.get("end_time")
                    )
                    
                elif name == "batch_create_records":
                    result = await self.lark_client.batch_create_records(
                        app_token=arguments["app_token"],
                        table_id=arguments["table_id"],
                        records=arguments["records"]
                    )
                    
                elif name == "batch_update_records":
                    result = await self.lark_client.batch_update_records(
                        app_token=arguments["app_token"],
                        table_id=arguments["table_id"],
                        records=arguments["records"]
                    )
                    
                elif name == "get_user_by_email_or_phone":
                    result = await self.lark_client.get_user_by_email_or_phone(
                        emails=arguments.get("emails", []),
                        mobiles=arguments.get("mobiles", [])
                    )
                    
                elif name == "search_documents":
                    result = await self.lark_client.search_documents(
                        query=arguments["query"],
                        doc_types=arguments.get("doc_types"),
                        owner_ids=arguments.get("owner_ids"),
                        chat_ids=arguments.get("chat_ids")
                    )
                    
                elif name == "import_document":
                    result = await self.lark_client.import_document(
                        file_path=arguments["file_path"],
                        file_type=arguments["file_type"],
                        folder_token=arguments.get("folder_token")
                    )
                    
                elif name == "export_document":
                    result = await self.lark_client.export_document(
                        document_id=arguments["document_id"],
                        export_format=arguments["export_format"]
                    )
                    
                elif name == "get_document_content":
                    result = await self.lark_client.get_document_content(
                        document_id=arguments["document_id"],
                        format=arguments.get("format", "text")
                    )
                    
                elif name == "add_document_permission":
                    result = await self.lark_client.add_document_permission(
                        document_token=arguments["document_token"],
                        member_type=arguments["member_type"],
                        member_id=arguments["member_id"],
                        permission=arguments["permission"]
                    )
                    
                elif name == "list_free_busy":
                    result = await self.lark_client.list_free_busy(
                        user_ids=arguments["user_ids"],
                        start_time=arguments["start_time"],
                        end_time=arguments["end_time"]
                    )
                    
                elif name == "add_task_reminder":
                    result = await self.lark_client.add_task_reminder(
                        task_id=arguments["task_id"],
                        reminder_time=arguments["reminder_time"],
                        reminder_type=arguments.get("reminder_type", "absolute")
                    )
                    
                else:
                    raise ValueError(f"Unknown tool: {name}")
                
                return [types.TextContent(
                    type="text",
                    text=json.dumps(result, indent=2, ensure_ascii=False)
                )]
                
            except Exception as e:
                return [types.TextContent(
                    type="text",
                    text=f"Error executing {name}: {str(e)}"
                )]

    async def run(self):
        """Run the MCP server."""
        async with stdio_server() as (read_stream, write_stream):
            await self.server.run(
                read_stream,
                write_stream,
                self.server.create_initialization_options()
            )