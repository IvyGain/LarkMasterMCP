"""MCP server implementation for Lark integration."""

import asyncio
import json
import logging
from typing import Any, Dict, List, Optional, Sequence
from mcp import types
from mcp.server import Server
from mcp.server.stdio import stdio_server
from pydantic import BaseModel

from .lark_client import LarkClient
from .tools import LARK_TOOLS

# Setup logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class LarkMCPServer:
    """Main MCP server for Lark integration."""
    
    def __init__(self, app_id: str, app_secret: str):
        self.server = Server("lark-master-mcp")
        self.lark_client = LarkClient(app_id, app_secret)
        logger.info("Initializing LarkMasterMCP server with 101 tools")
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
            
            logger.info(f"Executing tool: {name}")
            logger.debug(f"Tool arguments: {arguments}")
            
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
                    
                # Bitable Additional Tools
                elif name == "create_bitable_table":
                    result = await self.lark_client.create_bitable_table(
                        app_token=arguments["app_token"],
                        name=arguments["name"],
                        fields=arguments["fields"]
                    )
                    
                elif name == "create_bitable_view":
                    result = await self.lark_client.create_bitable_view(
                        app_token=arguments["app_token"],
                        table_id=arguments["table_id"],
                        view_name=arguments["view_name"],
                        view_type=arguments.get("view_type", "grid")
                    )
                    
                elif name == "add_bitable_field":
                    result = await self.lark_client.add_bitable_field(
                        app_token=arguments["app_token"],
                        table_id=arguments["table_id"],
                        field_name=arguments["field_name"],
                        field_type=arguments["field_type"]
                    )
                    
                elif name == "get_bitable_records":
                    result = await self.lark_client.get_bitable_records(
                        app_token=arguments["app_token"],
                        table_id=arguments["table_id"],
                        view_id=arguments.get("view_id"),
                        filter=arguments.get("filter")
                    )
                    
                elif name == "delete_bitable_records":
                    result = await self.lark_client.delete_bitable_records(
                        app_token=arguments["app_token"],
                        table_id=arguments["table_id"],
                        record_ids=arguments["record_ids"]
                    )
                    
                # Messaging Additional Tools
                elif name == "reply_message":
                    result = await self.lark_client.reply_message(
                        message_id=arguments["message_id"],
                        content=arguments["content"],
                        message_type=arguments.get("message_type", "text")
                    )
                    
                elif name == "add_message_reaction":
                    result = await self.lark_client.add_message_reaction(
                        message_id=arguments["message_id"],
                        emoji_type=arguments["emoji_type"]
                    )
                    
                elif name == "delete_message_reaction":
                    result = await self.lark_client.delete_message_reaction(
                        message_id=arguments["message_id"],
                        reaction_id=arguments["reaction_id"]
                    )
                    
                elif name == "pin_message":
                    result = await self.lark_client.pin_message(
                        message_id=arguments["message_id"]
                    )
                    
                elif name == "unpin_message":
                    result = await self.lark_client.unpin_message(
                        message_id=arguments["message_id"]
                    )
                    
                elif name == "forward_message":
                    result = await self.lark_client.forward_message(
                        message_id=arguments["message_id"],
                        receive_id=arguments["receive_id"]
                    )
                    
                elif name == "send_urgent_message":
                    result = await self.lark_client.send_urgent_message(
                        chat_id=arguments["chat_id"],
                        message=arguments["message"],
                        urgent_users=arguments["urgent_users"]
                    )
                    
                elif name == "read_message":
                    result = await self.lark_client.read_message(
                        message_ids=arguments["message_ids"]
                    )
                    
                elif name == "get_message_read_users":
                    result = await self.lark_client.get_message_read_users(
                        message_id=arguments["message_id"]
                    )
                    
                # Calendar Additional Tools
                elif name == "create_calendar_reminder":
                    result = await self.lark_client.create_calendar_reminder(
                        event_id=arguments["event_id"],
                        minutes=arguments["minutes"]
                    )
                    
                elif name == "create_recurring_event":
                    result = await self.lark_client.create_recurring_event(
                        title=arguments["title"],
                        start_time=arguments["start_time"],
                        end_time=arguments["end_time"],
                        recurrence=arguments["recurrence"],
                        attendees=arguments.get("attendees", [])
                    )
                    
                elif name == "book_meeting_room":
                    result = await self.lark_client.book_meeting_room(
                        room_id=arguments["room_id"],
                        start_time=arguments["start_time"],
                        end_time=arguments["end_time"],
                        event_title=arguments["event_title"]
                    )
                    
                elif name == "search_meeting_rooms":
                    result = await self.lark_client.search_meeting_rooms(
                        start_time=arguments["start_time"],
                        end_time=arguments["end_time"],
                        capacity=arguments.get("capacity")
                    )
                    
                elif name == "accept_calendar_event":
                    result = await self.lark_client.accept_calendar_event(
                        event_id=arguments["event_id"]
                    )
                    
                elif name == "decline_calendar_event":
                    result = await self.lark_client.decline_calendar_event(
                        event_id=arguments["event_id"],
                        reason=arguments.get("reason")
                    )
                    
                # Document Additional Tools
                elif name == "add_document_comment":
                    result = await self.lark_client.add_document_comment(
                        document_id=arguments["document_id"],
                        content=arguments["content"],
                        reply_to=arguments.get("reply_to")
                    )
                    
                elif name == "get_document_comments":
                    result = await self.lark_client.get_document_comments(
                        document_id=arguments["document_id"]
                    )
                    
                elif name == "create_document_from_template":
                    result = await self.lark_client.create_document_from_template(
                        template_id=arguments["template_id"],
                        title=arguments["title"],
                        folder_token=arguments.get("folder_token")
                    )
                    
                elif name == "lock_document_section":
                    result = await self.lark_client.lock_document_section(
                        document_id=arguments["document_id"],
                        block_id=arguments["block_id"]
                    )
                    
                elif name == "unlock_document_section":
                    result = await self.lark_client.unlock_document_section(
                        document_id=arguments["document_id"],
                        block_id=arguments["block_id"]
                    )
                    
                elif name == "subscribe_document_changes":
                    result = await self.lark_client.subscribe_document_changes(
                        document_id=arguments["document_id"],
                        events=arguments["events"]
                    )
                    
                # Bot/App Management Tools
                elif name == "create_bot_menu":
                    result = await self.lark_client.create_bot_menu(
                        menu_items=arguments["menu_items"]
                    )
                    
                elif name == "update_bot_info":
                    result = await self.lark_client.update_bot_info(
                        name=arguments.get("name"),
                        description=arguments.get("description"),
                        avatar_key=arguments.get("avatar_key")
                    )
                    
                elif name == "subscribe_events":
                    result = await self.lark_client.subscribe_events(
                        event_types=arguments["event_types"],
                        callback_url=arguments["callback_url"]
                    )
                    
                # Admin Tools
                elif name == "get_app_usage_stats":
                    result = await self.lark_client.get_app_usage_stats(
                        start_date=arguments["start_date"],
                        end_date=arguments["end_date"]
                    )
                    
                elif name == "get_audit_logs":
                    result = await self.lark_client.get_audit_logs(
                        start_time=arguments["start_time"],
                        end_time=arguments["end_time"],
                        event_types=arguments.get("event_types")
                    )
                    
                elif name == "manage_app_permissions":
                    result = await self.lark_client.manage_app_permissions(
                        app_id=arguments["app_id"],
                        permissions=arguments["permissions"],
                        action=arguments.get("action", "grant")
                    )
                    
                # AI/Assistant Tools
                elif name == "create_ai_agent":
                    result = await self.lark_client.create_ai_agent(
                        name=arguments["name"],
                        prompt=arguments["prompt"],
                        capabilities=arguments["capabilities"]
                    )
                    
                elif name == "chat_with_ai":
                    result = await self.lark_client.chat_with_ai(
                        agent_id=arguments["agent_id"],
                        message=arguments["message"],
                        context=arguments.get("context")
                    )
                    
                # Workflow/Automation Tools
                elif name == "create_workflow":
                    result = await self.lark_client.create_workflow(
                        name=arguments["name"],
                        trigger=arguments["trigger"],
                        actions=arguments["actions"]
                    )
                    
                elif name == "execute_workflow":
                    result = await self.lark_client.execute_workflow(
                        workflow_id=arguments["workflow_id"],
                        input_data=arguments["input_data"]
                    )
                    
                # OKR Tools
                elif name == "create_okr":
                    result = await self.lark_client.create_okr(
                        objective=arguments["objective"],
                        key_results=arguments["key_results"],
                        period_id=arguments["period_id"]
                    )
                    
                elif name == "update_okr_progress":
                    result = await self.lark_client.update_okr_progress(
                        okr_id=arguments["okr_id"],
                        key_result_id=arguments["key_result_id"],
                        progress=arguments["progress"],
                        comment=arguments.get("comment")
                    )
                    
                # Form Tools
                elif name == "create_form":
                    result = await self.lark_client.create_form(
                        title=arguments["title"],
                        fields=arguments["fields"],
                        settings=arguments.get("settings")
                    )
                    
                elif name == "get_form_responses":
                    result = await self.lark_client.get_form_responses(
                        form_id=arguments["form_id"],
                        start_time=arguments.get("start_time"),
                        end_time=arguments.get("end_time")
                    )
                    
                # Advanced Approval Tools
                elif name == "transfer_approval":
                    result = await self.lark_client.transfer_approval(
                        instance_id=arguments["instance_id"],
                        user_id=arguments["user_id"],
                        comment=arguments.get("comment")
                    )
                    
                elif name == "cancel_approval":
                    result = await self.lark_client.cancel_approval(
                        instance_id=arguments["instance_id"],
                        reason=arguments.get("reason")
                    )
                    
                elif name == "cc_approval":
                    result = await self.lark_client.cc_approval(
                        instance_id=arguments["instance_id"],
                        cc_users=arguments["cc_users"],
                        comment=arguments.get("comment")
                    )
                    
                elif name == "add_approval_comment":
                    result = await self.lark_client.add_approval_comment(
                        instance_id=arguments["instance_id"],
                        comment=arguments["comment"],
                        comment_type=arguments.get("comment_type", "general")
                    )
                    
                elif name == "rollback_approval":
                    result = await self.lark_client.rollback_approval(
                        instance_id=arguments["instance_id"],
                        reason=arguments.get("reason")
                    )
                    
                # Video Conference Recording Tools
                elif name == "start_meeting_recording":
                    result = await self.lark_client.start_meeting_recording(
                        meeting_id=arguments["meeting_id"]
                    )
                    
                elif name == "stop_meeting_recording":
                    result = await self.lark_client.stop_meeting_recording(
                        meeting_id=arguments["meeting_id"]
                    )
                    
                elif name == "get_meeting_recording":
                    result = await self.lark_client.get_meeting_recording(
                        meeting_id=arguments["meeting_id"]
                    )
                    
                # Advanced Bitable Tools
                elif name == "search_bitable_records":
                    result = await self.lark_client.search_bitable_records(
                        app_token=arguments["app_token"],
                        table_id=arguments["table_id"],
                        filter_info=arguments.get("filter_info"),
                        sort=arguments.get("sort"),
                        field_names=arguments.get("field_names")
                    )
                    
                elif name == "get_bitable_fields":
                    result = await self.lark_client.get_bitable_fields(
                        app_token=arguments["app_token"],
                        table_id=arguments["table_id"]
                    )
                    
                elif name == "update_bitable_field":
                    result = await self.lark_client.update_bitable_field(
                        app_token=arguments["app_token"],
                        table_id=arguments["table_id"],
                        field_id=arguments["field_id"],
                        field_name=arguments.get("field_name"),
                        property=arguments.get("property")
                    )
                    
                elif name == "create_bitable_app":
                    result = await self.lark_client.create_bitable_app(
                        name=arguments["name"],
                        folder_token=arguments.get("folder_token")
                    )
                    
                elif name == "get_bitable_views":
                    result = await self.lark_client.get_bitable_views(
                        app_token=arguments["app_token"],
                        table_id=arguments["table_id"]
                    )
                    
                elif name == "update_bitable_view":
                    result = await self.lark_client.update_bitable_view(
                        app_token=arguments["app_token"],
                        table_id=arguments["table_id"],
                        view_id=arguments["view_id"],
                        view_name=arguments.get("view_name"),
                        property=arguments.get("property")
                    )
                    
                # Helpdesk/Ticket Management Tools
                elif name == "create_helpdesk_ticket":
                    result = await self.lark_client.create_helpdesk_ticket(
                        title=arguments["title"],
                        description=arguments["description"],
                        category=arguments.get("category"),
                        priority=arguments.get("priority", "normal")
                    )
                    
                elif name == "get_helpdesk_ticket":
                    result = await self.lark_client.get_helpdesk_ticket(
                        ticket_id=arguments["ticket_id"]
                    )
                    
                elif name == "update_helpdesk_ticket":
                    result = await self.lark_client.update_helpdesk_ticket(
                        ticket_id=arguments["ticket_id"],
                        status=arguments.get("status"),
                        assignee=arguments.get("assignee"),
                        comment=arguments.get("comment")
                    )
                    
                elif name == "list_helpdesk_tickets":
                    result = await self.lark_client.list_helpdesk_tickets(
                        status=arguments.get("status"),
                        assignee=arguments.get("assignee")
                    )
                    
                # Drive Advanced Operations
                elif name == "create_file_version":
                    result = await self.lark_client.create_file_version(
                        file_token=arguments["file_token"],
                        name=arguments.get("name"),
                        parent_type=arguments.get("parent_type", "drive")
                    )
                    
                elif name == "get_file_versions":
                    result = await self.lark_client.get_file_versions(
                        file_token=arguments["file_token"]
                    )
                    
                elif name == "update_file_permission":
                    result = await self.lark_client.update_file_permission(
                        file_token=arguments["file_token"],
                        permission_id=arguments["permission_id"],
                        role=arguments["role"]
                    )
                    
                elif name == "get_file_permissions":
                    result = await self.lark_client.get_file_permissions(
                        file_token=arguments["file_token"],
                        type=arguments.get("type", "user")
                    )
                    
                else:
                    raise ValueError(f"Unknown tool: {name}")
                
                logger.info(f"Successfully executed tool: {name}")
                return [types.TextContent(
                    type="text",
                    text=json.dumps(result, indent=2, ensure_ascii=False)
                )]
                
            except ValueError as e:
                error_msg = f"Invalid tool or arguments for {name}: {str(e)}"
                logger.error(error_msg)
                return [types.TextContent(
                    type="text",
                    text=error_msg
                )]
            except Exception as e:
                error_msg = f"Error executing {name}: {str(e)}"
                logger.error(error_msg)
                return [types.TextContent(
                    type="text",
                    text=error_msg
                )]

    async def run(self):
        """Run the MCP server."""
        logger.info("Starting LarkMasterMCP server...")
        try:
            async with stdio_server() as (read_stream, write_stream):
                logger.info("MCP server is running and ready to accept connections")
                await self.server.run(
                    read_stream,
                    write_stream,
                    self.server.create_initialization_options()
                )
        except Exception as e:
            logger.error(f"Server error: {str(e)}")
            raise