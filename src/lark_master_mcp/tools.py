"""Tool definitions for Lark MCP server."""

from typing import Dict, List, Any

LARK_TOOLS: List[Dict[str, Any]] = [
    {
        "name": "send_message",
        "description": "Send a message to a Lark chat or user",
        "inputSchema": {
            "type": "object",
            "properties": {
                "chat_id": {
                    "type": "string",
                    "description": "The chat ID or user ID to send the message to"
                },
                "message": {
                    "type": "string",
                    "description": "The message content to send"
                },
                "message_type": {
                    "type": "string",
                    "enum": ["text", "post", "image", "file"],
                    "default": "text",
                    "description": "Type of message to send"
                }
            },
            "required": ["chat_id", "message"]
        }
    },
    {
        "name": "create_calendar_event",
        "description": "Create a calendar event in Lark",
        "inputSchema": {
            "type": "object",
            "properties": {
                "title": {
                    "type": "string",
                    "description": "Title of the calendar event"
                },
                "start_time": {
                    "type": "string",
                    "description": "Start time in ISO format (YYYY-MM-DDTHH:MM:SS)"
                },
                "end_time": {
                    "type": "string",
                    "description": "End time in ISO format (YYYY-MM-DDTHH:MM:SS)"
                },
                "attendees": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of attendee user IDs"
                },
                "description": {
                    "type": "string",
                    "description": "Event description"
                }
            },
            "required": ["title", "start_time", "end_time"]
        }
    },
    {
        "name": "get_user_info",
        "description": "Get information about a Lark user",
        "inputSchema": {
            "type": "object",
            "properties": {
                "user_id": {
                    "type": "string",
                    "description": "The user ID to get information for"
                }
            },
            "required": ["user_id"]
        }
    },
    {
        "name": "list_chats",
        "description": "List all chats the bot has access to",
        "inputSchema": {
            "type": "object",
            "properties": {},
            "additionalProperties": False
        }
    },
    {
        "name": "upload_file",
        "description": "Upload a file to Lark",
        "inputSchema": {
            "type": "object",
            "properties": {
                "file_path": {
                    "type": "string",
                    "description": "Path to the file to upload"
                },
                "file_type": {
                    "type": "string",
                    "enum": ["image", "file", "media"],
                    "description": "Type of file being uploaded"
                }
            },
            "required": ["file_path", "file_type"]
        }
    },
    {
        "name": "create_document",
        "description": "Create a new document in Lark Docs",
        "inputSchema": {
            "type": "object",
            "properties": {
                "title": {
                    "type": "string",
                    "description": "Title of the document"
                },
                "content": {
                    "type": "string",
                    "description": "Initial content of the document"
                },
                "folder_token": {
                    "type": "string",
                    "description": "Folder token to create document in (optional)"
                }
            },
            "required": ["title"]
        }
    },
    {
        "name": "search_messages",
        "description": "Search for messages in Lark chats",
        "inputSchema": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Search query string"
                },
                "chat_id": {
                    "type": "string",
                    "description": "Specific chat ID to search in (optional)"
                }
            },
            "required": ["query"]
        }
    },
    {
        "name": "get_department_users",
        "description": "Get users in a specific department",
        "inputSchema": {
            "type": "object",
            "properties": {
                "department_id": {
                    "type": "string",
                    "description": "The department ID to get users from"
                }
            },
            "required": ["department_id"]
        }
    },
    {
        "name": "create_meeting",
        "description": "Create a video meeting in Lark",
        "inputSchema": {
            "type": "object",
            "properties": {
                "title": {
                    "type": "string",
                    "description": "Meeting title"
                },
                "start_time": {
                    "type": "string",
                    "description": "Start time in ISO format"
                },
                "duration": {
                    "type": "integer",
                    "description": "Duration in minutes"
                },
                "attendees": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of attendee user IDs"
                }
            },
            "required": ["title", "start_time", "duration"]
        }
    },
    {
        "name": "get_spreadsheet_data",
        "description": "Get data from a Lark spreadsheet",
        "inputSchema": {
            "type": "object",
            "properties": {
                "spreadsheet_token": {
                    "type": "string",
                    "description": "Token of the spreadsheet"
                },
                "range": {
                    "type": "string",
                    "description": "Cell range to get data from (e.g., 'A1:C10')"
                }
            },
            "required": ["spreadsheet_token"]
        }
    },
    {
        "name": "update_spreadsheet_data",
        "description": "Update data in a Lark spreadsheet",
        "inputSchema": {
            "type": "object",
            "properties": {
                "spreadsheet_token": {
                    "type": "string",
                    "description": "Token of the spreadsheet"
                },
                "range": {
                    "type": "string",
                    "description": "Cell range to update (e.g., 'A1:C10')"
                },
                "values": {
                    "type": "array",
                    "items": {
                        "type": "array",
                        "items": {"type": ["string", "number", "boolean", "null"]}
                    },
                    "description": "2D array of values to write"
                }
            },
            "required": ["spreadsheet_token", "range", "values"]
        }
    },
    {
        "name": "create_task",
        "description": "Create a task in Lark",
        "inputSchema": {
            "type": "object",
            "properties": {
                "title": {
                    "type": "string",
                    "description": "Task title"
                },
                "description": {
                    "type": "string",
                    "description": "Task description"
                },
                "due_date": {
                    "type": "string",
                    "description": "Due date in ISO format"
                },
                "assignee": {
                    "type": "string",
                    "description": "User ID of the assignee"
                },
                "followers": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of follower user IDs"
                }
            },
            "required": ["title"]
        }
    },
    {
        "name": "update_task_status",
        "description": "Update the status of a task",
        "inputSchema": {
            "type": "object",
            "properties": {
                "task_id": {
                    "type": "string",
                    "description": "ID of the task to update"
                },
                "status": {
                    "type": "string",
                    "enum": ["todo", "in_progress", "done", "cancelled"],
                    "description": "New status of the task"
                },
                "comment": {
                    "type": "string",
                    "description": "Optional comment for the status update"
                }
            },
            "required": ["task_id", "status"]
        }
    },
    {
        "name": "create_approval",
        "description": "Create an approval request",
        "inputSchema": {
            "type": "object",
            "properties": {
                "approval_code": {
                    "type": "string",
                    "description": "Approval definition code"
                },
                "form_data": {
                    "type": "object",
                    "description": "Form data for the approval"
                },
                "approvers": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of approver user IDs"
                },
                "cc_users": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of CC user IDs"
                }
            },
            "required": ["approval_code", "form_data"]
        }
    },
    {
        "name": "get_approval_status",
        "description": "Get the status of an approval request",
        "inputSchema": {
            "type": "object",
            "properties": {
                "instance_id": {
                    "type": "string",
                    "description": "Approval instance ID"
                }
            },
            "required": ["instance_id"]
        }
    },
    {
        "name": "create_wiki_space",
        "description": "Create a wiki space for knowledge management",
        "inputSchema": {
            "type": "object",
            "properties": {
                "name": {
                    "type": "string",
                    "description": "Name of the wiki space"
                },
                "description": {
                    "type": "string",
                    "description": "Description of the wiki space"
                },
                "members": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of member user IDs"
                }
            },
            "required": ["name"]
        }
    },
    {
        "name": "create_wiki_page",
        "description": "Create a page in a wiki space",
        "inputSchema": {
            "type": "object",
            "properties": {
                "space_id": {
                    "type": "string",
                    "description": "Wiki space ID"
                },
                "title": {
                    "type": "string",
                    "description": "Page title"
                },
                "content": {
                    "type": "string",
                    "description": "Page content in markdown or HTML"
                },
                "parent_page_id": {
                    "type": "string",
                    "description": "Parent page ID for nested pages"
                }
            },
            "required": ["space_id", "title"]
        }
    },
    {
        "name": "add_bot_to_chat",
        "description": "Add the bot to a chat group",
        "inputSchema": {
            "type": "object",
            "properties": {
                "chat_id": {
                    "type": "string",
                    "description": "Chat ID to add the bot to"
                }
            },
            "required": ["chat_id"]
        }
    },
    {
        "name": "create_chat_group",
        "description": "Create a new chat group",
        "inputSchema": {
            "type": "object",
            "properties": {
                "name": {
                    "type": "string",
                    "description": "Name of the chat group"
                },
                "description": {
                    "type": "string",
                    "description": "Description of the chat group"
                },
                "member_ids": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of initial member user IDs"
                },
                "owner_id": {
                    "type": "string",
                    "description": "User ID of the group owner"
                }
            },
            "required": ["name"]
        }
    },
    {
        "name": "get_chat_members",
        "description": "Get members of a chat group",
        "inputSchema": {
            "type": "object",
            "properties": {
                "chat_id": {
                    "type": "string",
                    "description": "Chat ID to get members from"
                }
            },
            "required": ["chat_id"]
        }
    },
    {
        "name": "create_leave_request",
        "description": "Create a leave/time-off request",
        "inputSchema": {
            "type": "object",
            "properties": {
                "leave_type": {
                    "type": "string",
                    "enum": ["annual", "sick", "personal", "maternity", "paternity", "other"],
                    "description": "Type of leave"
                },
                "start_date": {
                    "type": "string",
                    "description": "Start date in ISO format"
                },
                "end_date": {
                    "type": "string",
                    "description": "End date in ISO format"
                },
                "reason": {
                    "type": "string",
                    "description": "Reason for leave"
                },
                "approver_id": {
                    "type": "string",
                    "description": "User ID of the approver"
                }
            },
            "required": ["leave_type", "start_date", "end_date", "reason"]
        }
    },
    {
        "name": "get_attendance_records",
        "description": "Get attendance records for users",
        "inputSchema": {
            "type": "object",
            "properties": {
                "user_ids": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of user IDs to get attendance for"
                },
                "start_date": {
                    "type": "string",
                    "description": "Start date in ISO format"
                },
                "end_date": {
                    "type": "string",
                    "description": "End date in ISO format"
                }
            },
            "required": ["user_ids", "start_date", "end_date"]
        }
    },
    {
        "name": "create_poll",
        "description": "Create a poll in a chat",
        "inputSchema": {
            "type": "object",
            "properties": {
                "chat_id": {
                    "type": "string",
                    "description": "Chat ID to create poll in"
                },
                "question": {
                    "type": "string",
                    "description": "Poll question"
                },
                "options": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of poll options"
                },
                "anonymous": {
                    "type": "boolean",
                    "default": False,
                    "description": "Whether the poll is anonymous"
                },
                "multiple_choice": {
                    "type": "boolean",
                    "default": False,
                    "description": "Allow multiple choices"
                }
            },
            "required": ["chat_id", "question", "options"]
        }
    },
    {
        "name": "share_screen",
        "description": "Start screen sharing in a meeting",
        "inputSchema": {
            "type": "object",
            "properties": {
                "meeting_id": {
                    "type": "string",
                    "description": "Meeting ID"
                },
                "share_type": {
                    "type": "string",
                    "enum": ["screen", "window", "tab"],
                    "description": "Type of screen share"
                }
            },
            "required": ["meeting_id"]
        }
    },
    {
        "name": "create_drive_folder",
        "description": "Create a folder in Lark Drive",
        "inputSchema": {
            "type": "object",
            "properties": {
                "name": {
                    "type": "string",
                    "description": "Folder name"
                },
                "parent_token": {
                    "type": "string",
                    "description": "Parent folder token (optional)"
                }
            },
            "required": ["name"]
        }
    },
    {
        "name": "share_file",
        "description": "Share a file or document with users",
        "inputSchema": {
            "type": "object",
            "properties": {
                "file_token": {
                    "type": "string",
                    "description": "Token of the file to share"
                },
                "user_ids": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of user IDs to share with"
                },
                "permission": {
                    "type": "string",
                    "enum": ["view", "edit", "full_access"],
                    "default": "view",
                    "description": "Permission level"
                },
                "notify": {
                    "type": "boolean",
                    "default": True,
                    "description": "Whether to notify users"
                }
            },
            "required": ["file_token", "user_ids"]
        }
    },
    {
        "name": "search_wiki",
        "description": "Search wiki spaces and pages",
        "inputSchema": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Search query"
                },
                "space_id": {
                    "type": "string",
                    "description": "Limit search to specific wiki space"
                }
            },
            "required": ["query"]
        }
    },
    {
        "name": "get_user_calendar",
        "description": "Get a user's calendar events",
        "inputSchema": {
            "type": "object",
            "properties": {
                "user_id": {
                    "type": "string",
                    "description": "User ID (optional, defaults to self)"
                },
                "start_time": {
                    "type": "string",
                    "description": "Start time in ISO format"
                },
                "end_time": {
                    "type": "string",
                    "description": "End time in ISO format"
                }
            },
            "required": ["start_time", "end_time"]
        }
    },
    {
        "name": "set_out_of_office",
        "description": "Set out of office auto-reply",
        "inputSchema": {
            "type": "object",
            "properties": {
                "enabled": {
                    "type": "boolean",
                    "description": "Enable or disable out of office"
                },
                "message": {
                    "type": "string",
                    "description": "Auto-reply message"
                },
                "start_time": {
                    "type": "string",
                    "description": "Start time in ISO format"
                },
                "end_time": {
                    "type": "string",
                    "description": "End time in ISO format"
                }
            },
            "required": ["enabled"]
        }
    },
    {
        "name": "batch_create_records",
        "description": "Batch create multiple records in a Bitable table",
        "inputSchema": {
            "type": "object",
            "properties": {
                "app_token": {
                    "type": "string",
                    "description": "Bitable app token"
                },
                "table_id": {
                    "type": "string",
                    "description": "Table ID"
                },
                "records": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "fields": {
                                "type": "object",
                                "description": "Record field values"
                            }
                        },
                        "required": ["fields"]
                    },
                    "description": "Array of records to create"
                }
            },
            "required": ["app_token", "table_id", "records"]
        }
    },
    {
        "name": "batch_update_records",
        "description": "Batch update multiple records in a Bitable table",
        "inputSchema": {
            "type": "object",
            "properties": {
                "app_token": {
                    "type": "string",
                    "description": "Bitable app token"
                },
                "table_id": {
                    "type": "string",
                    "description": "Table ID"
                },
                "records": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "record_id": {
                                "type": "string",
                                "description": "Record ID to update"
                            },
                            "fields": {
                                "type": "object",
                                "description": "Fields to update"
                            }
                        },
                        "required": ["record_id", "fields"]
                    },
                    "description": "Array of records to update"
                }
            },
            "required": ["app_token", "table_id", "records"]
        }
    },
    {
        "name": "get_user_by_email_or_phone",
        "description": "Get user ID by email address or phone number",
        "inputSchema": {
            "type": "object",
            "properties": {
                "emails": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of email addresses to search"
                },
                "mobiles": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of mobile phone numbers to search"
                }
            },
            "oneOf": [
                {"required": ["emails"]},
                {"required": ["mobiles"]}
            ]
        }
    },
    {
        "name": "search_documents",
        "description": "Search for documents across Lark Docs, Sheets, and other cloud documents",
        "inputSchema": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Search query"
                },
                "doc_types": {
                    "type": "array",
                    "items": {
                        "type": "string",
                        "enum": ["doc", "sheet", "bitable", "mindnote", "file", "wiki", "docx"]
                    },
                    "description": "Document types to search"
                },
                "owner_ids": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Filter by document owner IDs"
                },
                "chat_ids": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Filter by chat IDs where documents are shared"
                }
            },
            "required": ["query"]
        }
    },
    {
        "name": "import_document",
        "description": "Import external documents into Lark Docs",
        "inputSchema": {
            "type": "object",
            "properties": {
                "file_path": {
                    "type": "string",
                    "description": "Path to the file to import"
                },
                "file_type": {
                    "type": "string",
                    "enum": ["docx", "doc", "txt", "pdf"],
                    "description": "Type of file being imported"
                },
                "folder_token": {
                    "type": "string",
                    "description": "Folder to import the document into"
                }
            },
            "required": ["file_path", "file_type"]
        }
    },
    {
        "name": "export_document",
        "description": "Export Lark documents to various formats",
        "inputSchema": {
            "type": "object",
            "properties": {
                "document_id": {
                    "type": "string",
                    "description": "Document ID to export"
                },
                "export_format": {
                    "type": "string",
                    "enum": ["pdf", "docx", "txt", "markdown"],
                    "description": "Export format"
                }
            },
            "required": ["document_id", "export_format"]
        }
    },
    {
        "name": "get_document_content",
        "description": "Get the raw content of a document",
        "inputSchema": {
            "type": "object",
            "properties": {
                "document_id": {
                    "type": "string",
                    "description": "Document ID"
                },
                "format": {
                    "type": "string",
                    "enum": ["text", "markdown", "json"],
                    "default": "text",
                    "description": "Content format to retrieve"
                }
            },
            "required": ["document_id"]
        }
    },
    {
        "name": "add_document_permission",
        "description": "Add collaboration permissions to a document",
        "inputSchema": {
            "type": "object",
            "properties": {
                "document_token": {
                    "type": "string",
                    "description": "Document token"
                },
                "member_type": {
                    "type": "string",
                    "enum": ["user", "chat", "department"],
                    "description": "Type of member to add"
                },
                "member_id": {
                    "type": "string",
                    "description": "Member ID (user_id, chat_id, or department_id)"
                },
                "permission": {
                    "type": "string",
                    "enum": ["view", "edit", "full_access"],
                    "description": "Permission level"
                }
            },
            "required": ["document_token", "member_type", "member_id", "permission"]
        }
    },
    {
        "name": "list_free_busy",
        "description": "Check free/busy status for users' calendars",
        "inputSchema": {
            "type": "object",
            "properties": {
                "user_ids": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of user IDs to check"
                },
                "start_time": {
                    "type": "string",
                    "description": "Start time in ISO format"
                },
                "end_time": {
                    "type": "string",
                    "description": "End time in ISO format"
                }
            },
            "required": ["user_ids", "start_time", "end_time"]
        }
    },
    {
        "name": "add_task_reminder",
        "description": "Add a reminder to a task",
        "inputSchema": {
            "type": "object",
            "properties": {
                "task_id": {
                    "type": "string",
                    "description": "Task ID"
                },
                "reminder_time": {
                    "type": "string",
                    "description": "Reminder time in ISO format"
                },
                "reminder_type": {
                    "type": "string",
                    "enum": ["absolute", "relative"],
                    "description": "Type of reminder"
                }
            },
            "required": ["task_id", "reminder_time"]
        }
    },
    # Bitable (Base) Additional Tools
    {
        "name": "create_bitable_table",
        "description": "Create a new table in Bitable base app",
        "inputSchema": {
            "type": "object",
            "properties": {
                "app_token": {
                    "type": "string",
                    "description": "Bitable app token"
                },
                "name": {
                    "type": "string",
                    "description": "Table name"
                },
                "fields": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "field_name": {"type": "string"},
                            "field_type": {"type": "string"}
                        },
                        "required": ["field_name", "field_type"]
                    },
                    "description": "Array of field definitions"
                }
            },
            "required": ["app_token", "name", "fields"]
        }
    },
    {
        "name": "create_bitable_view",
        "description": "Create a view in Bitable table",
        "inputSchema": {
            "type": "object",
            "properties": {
                "app_token": {
                    "type": "string",
                    "description": "Bitable app token"
                },
                "table_id": {
                    "type": "string",
                    "description": "Table ID"
                },
                "view_name": {
                    "type": "string",
                    "description": "View name"
                },
                "view_type": {
                    "type": "string",
                    "enum": ["grid", "kanban", "gallery", "gantt", "calendar", "form"],
                    "default": "grid",
                    "description": "Type of view"
                }
            },
            "required": ["app_token", "table_id", "view_name"]
        }
    },
    {
        "name": "add_bitable_field",
        "description": "Add a field to Bitable table",
        "inputSchema": {
            "type": "object",
            "properties": {
                "app_token": {
                    "type": "string",
                    "description": "Bitable app token"
                },
                "table_id": {
                    "type": "string",
                    "description": "Table ID"
                },
                "field_name": {
                    "type": "string",
                    "description": "Field name"
                },
                "field_type": {
                    "type": "string",
                    "enum": ["text", "number", "select", "multiselect", "date", "checkbox", "person", "link", "attachment", "formula", "location"],
                    "description": "Field type"
                }
            },
            "required": ["app_token", "table_id", "field_name", "field_type"]
        }
    },
    {
        "name": "get_bitable_records",
        "description": "Get records from Bitable table with optional filtering",
        "inputSchema": {
            "type": "object",
            "properties": {
                "app_token": {
                    "type": "string",
                    "description": "Bitable app token"
                },
                "table_id": {
                    "type": "string",
                    "description": "Table ID"
                },
                "view_id": {
                    "type": "string",
                    "description": "View ID (optional)"
                },
                "filter": {
                    "type": "object",
                    "description": "Filter conditions (optional)"
                }
            },
            "required": ["app_token", "table_id"]
        }
    },
    {
        "name": "delete_bitable_records",
        "description": "Delete multiple records from Bitable",
        "inputSchema": {
            "type": "object",
            "properties": {
                "app_token": {
                    "type": "string",
                    "description": "Bitable app token"
                },
                "table_id": {
                    "type": "string",
                    "description": "Table ID"
                },
                "record_ids": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of record IDs to delete"
                }
            },
            "required": ["app_token", "table_id", "record_ids"]
        }
    },
    # Messaging Additional Tools
    {
        "name": "reply_message",
        "description": "Reply to a specific message",
        "inputSchema": {
            "type": "object",
            "properties": {
                "message_id": {
                    "type": "string",
                    "description": "Message ID to reply to"
                },
                "content": {
                    "type": "string",
                    "description": "Reply content"
                },
                "message_type": {
                    "type": "string",
                    "enum": ["text", "post", "image", "file"],
                    "default": "text",
                    "description": "Type of reply message"
                }
            },
            "required": ["message_id", "content"]
        }
    },
    {
        "name": "add_message_reaction",
        "description": "Add an emoji reaction to a message",
        "inputSchema": {
            "type": "object",
            "properties": {
                "message_id": {
                    "type": "string",
                    "description": "Message ID"
                },
                "emoji_type": {
                    "type": "string",
                    "description": "Emoji type (e.g., 'thumbsup', 'heart', 'clap')"
                }
            },
            "required": ["message_id", "emoji_type"]
        }
    },
    {
        "name": "delete_message_reaction",
        "description": "Remove an emoji reaction from a message",
        "inputSchema": {
            "type": "object",
            "properties": {
                "message_id": {
                    "type": "string",
                    "description": "Message ID"
                },
                "reaction_id": {
                    "type": "string",
                    "description": "Reaction ID to remove"
                }
            },
            "required": ["message_id", "reaction_id"]
        }
    },
    {
        "name": "pin_message",
        "description": "Pin a message in a chat",
        "inputSchema": {
            "type": "object",
            "properties": {
                "message_id": {
                    "type": "string",
                    "description": "Message ID to pin"
                }
            },
            "required": ["message_id"]
        }
    },
    {
        "name": "unpin_message",
        "description": "Unpin a message from a chat",
        "inputSchema": {
            "type": "object",
            "properties": {
                "message_id": {
                    "type": "string",
                    "description": "Message ID to unpin"
                }
            },
            "required": ["message_id"]
        }
    },
    {
        "name": "forward_message",
        "description": "Forward a message to another chat",
        "inputSchema": {
            "type": "object",
            "properties": {
                "message_id": {
                    "type": "string",
                    "description": "Message ID to forward"
                },
                "receive_id": {
                    "type": "string",
                    "description": "Target chat or user ID"
                }
            },
            "required": ["message_id", "receive_id"]
        }
    },
    {
        "name": "send_urgent_message",
        "description": "Send an urgent message with special notification",
        "inputSchema": {
            "type": "object",
            "properties": {
                "chat_id": {
                    "type": "string",
                    "description": "Chat ID"
                },
                "message": {
                    "type": "string",
                    "description": "Urgent message content"
                },
                "urgent_users": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of user IDs to urgently notify"
                }
            },
            "required": ["chat_id", "message", "urgent_users"]
        }
    },
    {
        "name": "read_message",
        "description": "Mark messages as read",
        "inputSchema": {
            "type": "object",
            "properties": {
                "message_ids": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of message IDs to mark as read"
                }
            },
            "required": ["message_ids"]
        }
    },
    {
        "name": "get_message_read_users",
        "description": "Get list of users who have read a message",
        "inputSchema": {
            "type": "object",
            "properties": {
                "message_id": {
                    "type": "string",
                    "description": "Message ID"
                }
            },
            "required": ["message_id"]
        }
    },
    # Calendar Additional Tools
    {
        "name": "create_calendar_reminder",
        "description": "Add a reminder to a calendar event",
        "inputSchema": {
            "type": "object",
            "properties": {
                "event_id": {
                    "type": "string",
                    "description": "Calendar event ID"
                },
                "minutes": {
                    "type": "integer",
                    "description": "Minutes before event to send reminder"
                }
            },
            "required": ["event_id", "minutes"]
        }
    },
    {
        "name": "create_recurring_event",
        "description": "Create a recurring calendar event",
        "inputSchema": {
            "type": "object",
            "properties": {
                "title": {
                    "type": "string",
                    "description": "Event title"
                },
                "start_time": {
                    "type": "string",
                    "description": "Start time in ISO format"
                },
                "end_time": {
                    "type": "string",
                    "description": "End time in ISO format"
                },
                "recurrence": {
                    "type": "string",
                    "description": "Recurrence rule (RRULE format)"
                },
                "attendees": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of attendee user IDs"
                }
            },
            "required": ["title", "start_time", "end_time", "recurrence"]
        }
    },
    {
        "name": "book_meeting_room",
        "description": "Book a meeting room for an event",
        "inputSchema": {
            "type": "object",
            "properties": {
                "room_id": {
                    "type": "string",
                    "description": "Meeting room ID"
                },
                "start_time": {
                    "type": "string",
                    "description": "Start time in ISO format"
                },
                "end_time": {
                    "type": "string",
                    "description": "End time in ISO format"
                },
                "event_title": {
                    "type": "string",
                    "description": "Event title"
                }
            },
            "required": ["room_id", "start_time", "end_time", "event_title"]
        }
    },
    {
        "name": "search_meeting_rooms",
        "description": "Search for available meeting rooms",
        "inputSchema": {
            "type": "object",
            "properties": {
                "start_time": {
                    "type": "string",
                    "description": "Start time in ISO format"
                },
                "end_time": {
                    "type": "string",
                    "description": "End time in ISO format"
                },
                "capacity": {
                    "type": "integer",
                    "description": "Minimum room capacity"
                }
            },
            "required": ["start_time", "end_time"]
        }
    },
    {
        "name": "accept_calendar_event",
        "description": "Accept a calendar event invitation",
        "inputSchema": {
            "type": "object",
            "properties": {
                "event_id": {
                    "type": "string",
                    "description": "Event ID to accept"
                }
            },
            "required": ["event_id"]
        }
    },
    {
        "name": "decline_calendar_event",
        "description": "Decline a calendar event invitation",
        "inputSchema": {
            "type": "object",
            "properties": {
                "event_id": {
                    "type": "string",
                    "description": "Event ID to decline"
                },
                "reason": {
                    "type": "string",
                    "description": "Reason for declining (optional)"
                }
            },
            "required": ["event_id"]
        }
    },
    # Document Additional Tools
    {
        "name": "add_document_comment",
        "description": "Add a comment to a document",
        "inputSchema": {
            "type": "object",
            "properties": {
                "document_id": {
                    "type": "string",
                    "description": "Document ID"
                },
                "content": {
                    "type": "string",
                    "description": "Comment content"
                },
                "reply_to": {
                    "type": "string",
                    "description": "Comment ID to reply to (optional)"
                }
            },
            "required": ["document_id", "content"]
        }
    },
    {
        "name": "get_document_comments",
        "description": "Get all comments from a document",
        "inputSchema": {
            "type": "object",
            "properties": {
                "document_id": {
                    "type": "string",
                    "description": "Document ID"
                }
            },
            "required": ["document_id"]
        }
    },
    {
        "name": "create_document_from_template",
        "description": "Create a new document from a template",
        "inputSchema": {
            "type": "object",
            "properties": {
                "template_id": {
                    "type": "string",
                    "description": "Template ID"
                },
                "title": {
                    "type": "string",
                    "description": "Document title"
                },
                "folder_token": {
                    "type": "string",
                    "description": "Target folder token (optional)"
                }
            },
            "required": ["template_id", "title"]
        }
    },
    {
        "name": "lock_document_section",
        "description": "Lock a section of document to prevent editing",
        "inputSchema": {
            "type": "object",
            "properties": {
                "document_id": {
                    "type": "string",
                    "description": "Document ID"
                },
                "block_id": {
                    "type": "string",
                    "description": "Block/section ID to lock"
                }
            },
            "required": ["document_id", "block_id"]
        }
    },
    {
        "name": "unlock_document_section",
        "description": "Unlock a previously locked document section",
        "inputSchema": {
            "type": "object",
            "properties": {
                "document_id": {
                    "type": "string",
                    "description": "Document ID"
                },
                "block_id": {
                    "type": "string",
                    "description": "Block/section ID to unlock"
                }
            },
            "required": ["document_id", "block_id"]
        }
    },
    {
        "name": "subscribe_document_changes",
        "description": "Subscribe to document change events",
        "inputSchema": {
            "type": "object",
            "properties": {
                "document_id": {
                    "type": "string",
                    "description": "Document ID"
                },
                "events": {
                    "type": "array",
                    "items": {
                        "type": "string",
                        "enum": ["edit", "comment", "share", "delete"]
                    },
                    "description": "List of event types to subscribe to"
                }
            },
            "required": ["document_id", "events"]
        }
    },
    # Bot/App Management Tools
    {
        "name": "create_bot_menu",
        "description": "Create custom menu for bot in chat",
        "inputSchema": {
            "type": "object",
            "properties": {
                "menu_items": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "text": {"type": "string"},
                            "value": {"type": "string"},
                            "type": {"type": "string"}
                        },
                        "required": ["text", "value"]
                    },
                    "description": "Array of menu items"
                }
            },
            "required": ["menu_items"]
        }
    },
    {
        "name": "update_bot_info",
        "description": "Update bot profile information",
        "inputSchema": {
            "type": "object",
            "properties": {
                "name": {
                    "type": "string",
                    "description": "Bot name"
                },
                "description": {
                    "type": "string",
                    "description": "Bot description"
                },
                "avatar_key": {
                    "type": "string",
                    "description": "Avatar image key"
                }
            },
            "additionalProperties": False
        }
    },
    {
        "name": "subscribe_events",
        "description": "Subscribe to bot events",
        "inputSchema": {
            "type": "object",
            "properties": {
                "event_types": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of event types to subscribe"
                },
                "callback_url": {
                    "type": "string",
                    "description": "Webhook URL for events"
                }
            },
            "required": ["event_types", "callback_url"]
        }
    },
    # Admin Tools
    {
        "name": "get_app_usage_stats",
        "description": "Get app usage statistics",
        "inputSchema": {
            "type": "object",
            "properties": {
                "start_date": {
                    "type": "string",
                    "description": "Start date in YYYY-MM-DD format"
                },
                "end_date": {
                    "type": "string",
                    "description": "End date in YYYY-MM-DD format"
                }
            },
            "required": ["start_date", "end_date"]
        }
    },
    {
        "name": "get_audit_logs",
        "description": "Get audit logs for security and compliance",
        "inputSchema": {
            "type": "object",
            "properties": {
                "start_time": {
                    "type": "string",
                    "description": "Start time in ISO format"
                },
                "end_time": {
                    "type": "string",
                    "description": "End time in ISO format"
                },
                "event_types": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Filter by event types"
                }
            },
            "required": ["start_time", "end_time"]
        }
    },
    {
        "name": "manage_app_permissions",
        "description": "Manage app permissions",
        "inputSchema": {
            "type": "object",
            "properties": {
                "app_id": {
                    "type": "string",
                    "description": "App ID"
                },
                "permissions": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of permissions"
                },
                "action": {
                    "type": "string",
                    "enum": ["grant", "revoke"],
                    "default": "grant",
                    "description": "Grant or revoke permissions"
                }
            },
            "required": ["app_id", "permissions"]
        }
    },
    # AI/Assistant Tools
    {
        "name": "create_ai_agent",
        "description": "Create an AI agent with specific capabilities",
        "inputSchema": {
            "type": "object",
            "properties": {
                "name": {
                    "type": "string",
                    "description": "Agent name"
                },
                "prompt": {
                    "type": "string",
                    "description": "System prompt for the agent"
                },
                "capabilities": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of capabilities"
                }
            },
            "required": ["name", "prompt", "capabilities"]
        }
    },
    {
        "name": "chat_with_ai",
        "description": "Chat with an AI agent",
        "inputSchema": {
            "type": "object",
            "properties": {
                "agent_id": {
                    "type": "string",
                    "description": "AI agent ID"
                },
                "message": {
                    "type": "string",
                    "description": "Message to send to agent"
                },
                "context": {
                    "type": "object",
                    "description": "Additional context for the conversation"
                }
            },
            "required": ["agent_id", "message"]
        }
    },
    # Workflow/Automation Tools
    {
        "name": "create_workflow",
        "description": "Create an automation workflow",
        "inputSchema": {
            "type": "object",
            "properties": {
                "name": {
                    "type": "string",
                    "description": "Workflow name"
                },
                "trigger": {
                    "type": "object",
                    "description": "Workflow trigger configuration"
                },
                "actions": {
                    "type": "array",
                    "items": {"type": "object"},
                    "description": "List of workflow actions"
                }
            },
            "required": ["name", "trigger", "actions"]
        }
    },
    {
        "name": "execute_workflow",
        "description": "Execute a workflow with input data",
        "inputSchema": {
            "type": "object",
            "properties": {
                "workflow_id": {
                    "type": "string",
                    "description": "Workflow ID"
                },
                "input_data": {
                    "type": "object",
                    "description": "Input data for workflow execution"
                }
            },
            "required": ["workflow_id", "input_data"]
        }
    },
    # OKR Tools
    {
        "name": "create_okr",
        "description": "Create OKR (Objectives and Key Results)",
        "inputSchema": {
            "type": "object",
            "properties": {
                "objective": {
                    "type": "string",
                    "description": "Main objective"
                },
                "key_results": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "description": {"type": "string"},
                            "target": {"type": "number"},
                            "unit": {"type": "string"}
                        },
                        "required": ["description", "target"]
                    },
                    "description": "List of key results"
                },
                "period_id": {
                    "type": "string",
                    "description": "OKR period ID"
                }
            },
            "required": ["objective", "key_results", "period_id"]
        }
    },
    {
        "name": "update_okr_progress",
        "description": "Update progress on OKR key result",
        "inputSchema": {
            "type": "object",
            "properties": {
                "okr_id": {
                    "type": "string",
                    "description": "OKR ID"
                },
                "key_result_id": {
                    "type": "string",
                    "description": "Key result ID"
                },
                "progress": {
                    "type": "number",
                    "description": "Progress value (0-100)"
                },
                "comment": {
                    "type": "string",
                    "description": "Progress update comment"
                }
            },
            "required": ["okr_id", "key_result_id", "progress"]
        }
    },
    # Form Tools
    {
        "name": "create_form",
        "description": "Create a form for data collection",
        "inputSchema": {
            "type": "object",
            "properties": {
                "title": {
                    "type": "string",
                    "description": "Form title"
                },
                "fields": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "name": {"type": "string"},
                            "type": {"type": "string"},
                            "required": {"type": "boolean"},
                            "options": {"type": "array", "items": {"type": "string"}}
                        },
                        "required": ["name", "type"]
                    },
                    "description": "Form field definitions"
                },
                "settings": {
                    "type": "object",
                    "description": "Form settings (e.g., response limit, deadline)"
                }
            },
            "required": ["title", "fields"]
        }
    },
    {
        "name": "get_form_responses",
        "description": "Get responses from a form",
        "inputSchema": {
            "type": "object",
            "properties": {
                "form_id": {
                    "type": "string",
                    "description": "Form ID"
                },
                "start_time": {
                    "type": "string",
                    "description": "Filter responses from this time"
                },
                "end_time": {
                    "type": "string",
                    "description": "Filter responses until this time"
                }
            },
            "required": ["form_id"]
        }
    },
    # Advanced Approval Tools
    {
        "name": "transfer_approval",
        "description": "Transfer approval to another user",
        "inputSchema": {
            "type": "object",
            "properties": {
                "instance_id": {
                    "type": "string",
                    "description": "Approval instance ID"
                },
                "user_id": {
                    "type": "string",
                    "description": "User ID to transfer approval to"
                },
                "comment": {
                    "type": "string",
                    "description": "Transfer comment (optional)"
                }
            },
            "required": ["instance_id", "user_id"]
        }
    },
    {
        "name": "cancel_approval",
        "description": "Cancel an approval instance",
        "inputSchema": {
            "type": "object",
            "properties": {
                "instance_id": {
                    "type": "string",
                    "description": "Approval instance ID"
                },
                "reason": {
                    "type": "string",
                    "description": "Cancellation reason (optional)"
                }
            },
            "required": ["instance_id"]
        }
    },
    {
        "name": "cc_approval",
        "description": "CC approval to additional users",
        "inputSchema": {
            "type": "object",
            "properties": {
                "instance_id": {
                    "type": "string",
                    "description": "Approval instance ID"
                },
                "cc_users": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of user IDs to CC"
                },
                "comment": {
                    "type": "string",
                    "description": "CC comment (optional)"
                }
            },
            "required": ["instance_id", "cc_users"]
        }
    },
    {
        "name": "add_approval_comment",
        "description": "Add comment to approval instance",
        "inputSchema": {
            "type": "object",
            "properties": {
                "instance_id": {
                    "type": "string",
                    "description": "Approval instance ID"
                },
                "comment": {
                    "type": "string",
                    "description": "Comment content"
                },
                "comment_type": {
                    "type": "string",
                    "enum": ["general", "approve", "reject"],
                    "default": "general",
                    "description": "Type of comment"
                }
            },
            "required": ["instance_id", "comment"]
        }
    },
    {
        "name": "rollback_approval",
        "description": "Rollback approval to previous step",
        "inputSchema": {
            "type": "object",
            "properties": {
                "instance_id": {
                    "type": "string",
                    "description": "Approval instance ID"
                },
                "reason": {
                    "type": "string",
                    "description": "Rollback reason (optional)"
                }
            },
            "required": ["instance_id"]
        }
    },
    # Video Conference Recording Tools
    {
        "name": "start_meeting_recording",
        "description": "Start recording a meeting",
        "inputSchema": {
            "type": "object",
            "properties": {
                "meeting_id": {
                    "type": "string",
                    "description": "Meeting ID"
                }
            },
            "required": ["meeting_id"]
        }
    },
    {
        "name": "stop_meeting_recording",
        "description": "Stop recording a meeting",
        "inputSchema": {
            "type": "object",
            "properties": {
                "meeting_id": {
                    "type": "string",
                    "description": "Meeting ID"
                }
            },
            "required": ["meeting_id"]
        }
    },
    {
        "name": "get_meeting_recording",
        "description": "Get meeting recording file information",
        "inputSchema": {
            "type": "object",
            "properties": {
                "meeting_id": {
                    "type": "string",
                    "description": "Meeting ID"
                }
            },
            "required": ["meeting_id"]
        }
    },
    # Advanced Bitable Tools
    {
        "name": "search_bitable_records",
        "description": "Search Bitable records with advanced filtering and sorting",
        "inputSchema": {
            "type": "object",
            "properties": {
                "app_token": {
                    "type": "string",
                    "description": "Bitable app token"
                },
                "table_id": {
                    "type": "string",
                    "description": "Table ID"
                },
                "filter_info": {
                    "type": "object",
                    "description": "Advanced filter conditions (supports AND/OR logic)"
                },
                "sort": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "field_name": {"type": "string"},
                            "desc": {"type": "boolean"}
                        },
                        "required": ["field_name"]
                    },
                    "description": "Sort configuration"
                },
                "field_names": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Specific fields to retrieve"
                }
            },
            "required": ["app_token", "table_id"]
        }
    },
    {
        "name": "get_bitable_fields",
        "description": "Get all field information from a Bitable table",
        "inputSchema": {
            "type": "object",
            "properties": {
                "app_token": {
                    "type": "string",
                    "description": "Bitable app token"
                },
                "table_id": {
                    "type": "string",
                    "description": "Table ID"
                }
            },
            "required": ["app_token", "table_id"]
        }
    },
    {
        "name": "update_bitable_field",
        "description": "Update Bitable field properties",
        "inputSchema": {
            "type": "object",
            "properties": {
                "app_token": {
                    "type": "string",
                    "description": "Bitable app token"
                },
                "table_id": {
                    "type": "string",
                    "description": "Table ID"
                },
                "field_id": {
                    "type": "string",
                    "description": "Field ID"
                },
                "field_name": {
                    "type": "string",
                    "description": "New field name"
                },
                "property": {
                    "type": "object",
                    "description": "Field property configuration"
                }
            },
            "required": ["app_token", "table_id", "field_id"]
        }
    },
    {
        "name": "create_bitable_app",
        "description": "Create a new Bitable app",
        "inputSchema": {
            "type": "object",
            "properties": {
                "name": {
                    "type": "string",
                    "description": "App name"
                },
                "folder_token": {
                    "type": "string",
                    "description": "Parent folder token (optional)"
                }
            },
            "required": ["name"]
        }
    },
    {
        "name": "get_bitable_views",
        "description": "Get all views from a Bitable table",
        "inputSchema": {
            "type": "object",
            "properties": {
                "app_token": {
                    "type": "string",
                    "description": "Bitable app token"
                },
                "table_id": {
                    "type": "string",
                    "description": "Table ID"
                }
            },
            "required": ["app_token", "table_id"]
        }
    },
    {
        "name": "update_bitable_view",
        "description": "Update Bitable view properties",
        "inputSchema": {
            "type": "object",
            "properties": {
                "app_token": {
                    "type": "string",
                    "description": "Bitable app token"
                },
                "table_id": {
                    "type": "string",
                    "description": "Table ID"
                },
                "view_id": {
                    "type": "string",
                    "description": "View ID"
                },
                "view_name": {
                    "type": "string",
                    "description": "New view name"
                },
                "property": {
                    "type": "object",
                    "description": "View property configuration"
                }
            },
            "required": ["app_token", "table_id", "view_id"]
        }
    },
    # Helpdesk/Ticket Management Tools
    {
        "name": "create_helpdesk_ticket",
        "description": "Create a helpdesk support ticket",
        "inputSchema": {
            "type": "object",
            "properties": {
                "title": {
                    "type": "string",
                    "description": "Ticket title"
                },
                "description": {
                    "type": "string",
                    "description": "Ticket description"
                },
                "category": {
                    "type": "string",
                    "description": "Ticket category (optional)"
                },
                "priority": {
                    "type": "string",
                    "enum": ["low", "normal", "high", "urgent"],
                    "default": "normal",
                    "description": "Ticket priority"
                }
            },
            "required": ["title", "description"]
        }
    },
    {
        "name": "get_helpdesk_ticket",
        "description": "Get helpdesk ticket details",
        "inputSchema": {
            "type": "object",
            "properties": {
                "ticket_id": {
                    "type": "string",
                    "description": "Ticket ID"
                }
            },
            "required": ["ticket_id"]
        }
    },
    {
        "name": "update_helpdesk_ticket",
        "description": "Update helpdesk ticket status or assignment",
        "inputSchema": {
            "type": "object",
            "properties": {
                "ticket_id": {
                    "type": "string",
                    "description": "Ticket ID"
                },
                "status": {
                    "type": "string",
                    "enum": ["open", "in_progress", "resolved", "closed"],
                    "description": "Ticket status"
                },
                "assignee": {
                    "type": "string",
                    "description": "Assignee user ID"
                },
                "comment": {
                    "type": "string",
                    "description": "Update comment"
                }
            },
            "required": ["ticket_id"]
        }
    },
    {
        "name": "list_helpdesk_tickets",
        "description": "List helpdesk tickets with filters",
        "inputSchema": {
            "type": "object",
            "properties": {
                "status": {
                    "type": "string",
                    "enum": ["open", "in_progress", "resolved", "closed"],
                    "description": "Filter by status"
                },
                "assignee": {
                    "type": "string",
                    "description": "Filter by assignee"
                }
            },
            "additionalProperties": False
        }
    },
    # Drive Advanced Operations
    {
        "name": "create_file_version",
        "description": "Create a new version of a file",
        "inputSchema": {
            "type": "object",
            "properties": {
                "file_token": {
                    "type": "string",
                    "description": "File token"
                },
                "name": {
                    "type": "string",
                    "description": "Version name (optional)"
                },
                "parent_type": {
                    "type": "string",
                    "enum": ["drive", "space"],
                    "default": "drive",
                    "description": "Parent type"
                }
            },
            "required": ["file_token"]
        }
    },
    {
        "name": "get_file_versions",
        "description": "Get file version history",
        "inputSchema": {
            "type": "object",
            "properties": {
                "file_token": {
                    "type": "string",
                    "description": "File token"
                }
            },
            "required": ["file_token"]
        }
    },
    {
        "name": "update_file_permission",
        "description": "Update file permission for a user",
        "inputSchema": {
            "type": "object",
            "properties": {
                "file_token": {
                    "type": "string",
                    "description": "File token"
                },
                "permission_id": {
                    "type": "string",
                    "description": "Permission ID"
                },
                "role": {
                    "type": "string",
                    "enum": ["view", "edit", "full_access"],
                    "description": "Permission role"
                }
            },
            "required": ["file_token", "permission_id", "role"]
        }
    },
    {
        "name": "get_file_permissions",
        "description": "Get file permissions list",
        "inputSchema": {
            "type": "object",
            "properties": {
                "file_token": {
                    "type": "string",
                    "description": "File token"
                },
                "type": {
                    "type": "string",
                    "enum": ["user", "chat", "department"],
                    "default": "user",
                    "description": "Permission type"
                }
            },
            "required": ["file_token"]
        }
    }
]