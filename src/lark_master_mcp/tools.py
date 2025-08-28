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
    }
]