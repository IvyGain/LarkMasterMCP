# LarkMasterMCP - Super Lark MCP

A comprehensive MCP (Model Context Protocol) server for Lark (Feishu) integration with **intelligent automation capabilities**. Build complete database systems from natural language!

## ✨ Highlights

- **108 Tools** - Most comprehensive Lark MCP implementation
- **Smart Bitable Builder** - Create databases from natural language
- **Auto Documentation** - Generate Wiki docs for created systems
- **Message Bot** - Intelligent chat bot that executes commands

## 🚀 Quick Start

### 1. Prerequisites
- Python 3.8+
- Lark App credentials ([Get from Lark Open Platform](https://open.feishu.cn/app))

### 2. Installation

```bash
# Clone
git clone https://github.com/IvyGain/LarkMasterMCP.git
cd LarkMasterMCP

# Install
pip install -e .

# Configure
cp .env.example .env
# Edit .env with your credentials:
# LARK_APP_ID=your_app_id
# LARK_APP_SECRET=your_app_secret
```

### 3. Run

```bash
lark-mcp
```

## 📋 Configuration for AI Clients

### Claude Desktop

Add to `~/Library/Application Support/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "lark-master": {
      "command": "lark-mcp",
      "env": {
        "LARK_APP_ID": "cli_xxxxx",
        "LARK_APP_SECRET": "xxxxx"
      }
    }
  }
}
```

### Cursor / VS Code

Add to `.cursor/mcp.json` or workspace settings:

```json
{
  "mcpServers": {
    "lark-master": {
      "command": "lark-mcp",
      "env": {
        "LARK_APP_ID": "cli_xxxxx",
        "LARK_APP_SECRET": "xxxxx"
      }
    }
  }
}
```

### Direct Python Usage

```python
import asyncio
from lark_master_mcp.server import LarkMCPServer

async def main():
    server = LarkMCPServer(
        app_id="cli_xxxxx",
        app_secret="xxxxx"
    )
    await server.run()

asyncio.run(main())
```

---

## 🧠 Smart Tools (New!)

### smart_build_bitable
Build complete Bitable databases from natural language:

```
"顧客管理テーブルを作成して"
→ Creates a full CRM with fields: Company, Contact, Email, Phone, Status, Priority, etc.

"プロジェクト管理用のベースを作って"
→ Creates project tracking with: Task, Description, Status, Assignee, Due Date, etc.
```

**Available Templates:**
| Template | Description |
|----------|-------------|
| 顧客管理 | CRM with contacts, status, priority |
| プロジェクト管理 | Tasks, status, assignees, deadlines |
| 在庫管理 | Products, SKU, stock levels, pricing |
| 売上管理 | Sales tracking, payments, revenue |
| イベント管理 | Events, registrations, capacity |
| 採用管理 | Candidates, interviews, evaluations |
| 問い合わせ管理 | Support tickets, priority, status |
| 会議メモ | Meeting notes, attendees, actions |

### process_lark_message
Intelligent message processing - just send a message and the bot figures out what to do:

```
"顧客管理システムを作って" → Creates Bitable
"Wikiスペースを作成" → Creates Wiki space
"タスクを追加: レビュー依頼" → Creates task
"ヘルプ" → Shows help
```

### create_bitable_with_wiki
Create a complete system with documentation:

```json
{
  "tool": "create_bitable_with_wiki",
  "arguments": {
    "message": "顧客管理システム",
    "name": "CRM System"
  }
}
```
This creates:
1. Bitable with appropriate structure
2. Wiki space for documentation
3. Auto-generated manual

---

## 🛠️ All Tools (108 Total)

### Messaging & Communication (16 tools)
| Tool | Description |
|------|-------------|
| `send_message` | Send text/rich text/media messages |
| `reply_message` | Reply to a specific message |
| `search_messages` | Search messages across chats |
| `list_chats` | List accessible chats |
| `create_chat_group` | Create a new chat group |
| `get_chat_members` | Get members of a chat |
| `add_bot_to_chat` | Add bot to a chat |
| `create_poll` | Create polls |
| `add_message_reaction` | Add emoji reaction |
| `delete_message_reaction` | Remove reaction |
| `pin_message` | Pin a message |
| `unpin_message` | Unpin a message |
| `forward_message` | Forward to another chat |
| `send_urgent_message` | Send urgent notification |
| `read_message` | Mark as read |
| `get_message_read_users` | Get who read a message |

### Calendar & Meetings (12 tools)
| Tool | Description |
|------|-------------|
| `create_calendar_event` | Create calendar events |
| `get_user_calendar` | Get calendar events |
| `create_meeting` | Create video meetings |
| `share_screen` | Start screen sharing |
| `set_out_of_office` | Set OOO auto-reply |
| `list_free_busy` | Check availability |
| `create_calendar_reminder` | Add event reminders |
| `create_recurring_event` | Create recurring events |
| `book_meeting_room` | Book a room |
| `search_meeting_rooms` | Find available rooms |
| `accept_calendar_event` | Accept invitation |
| `decline_calendar_event` | Decline invitation |

### Documents & Files (17 tools)
| Tool | Description |
|------|-------------|
| `create_document` | Create Lark Docs |
| `upload_file` | Upload files |
| `create_drive_folder` | Create folders |
| `share_file` | Share files |
| `get_spreadsheet_data` | Read spreadsheet |
| `update_spreadsheet_data` | Update spreadsheet |
| `search_documents` | Search documents |
| `import_document` | Import external docs |
| `export_document` | Export to PDF/DOCX |
| `get_document_content` | Get document content |
| `add_document_permission` | Add collaborators |
| `add_document_comment` | Add comments |
| `get_document_comments` | Get comments |
| `create_document_from_template` | Use templates |
| `lock_document_section` | Lock sections |
| `unlock_document_section` | Unlock sections |
| `subscribe_document_changes` | Watch for changes |

### Bitable / Multi-dimensional Tables (12 tools)
| Tool | Description |
|------|-------------|
| `create_bitable_app` | Create new Bitable |
| `create_bitable_table` | Create table |
| `create_bitable_view` | Create views |
| `add_bitable_field` | Add fields |
| `update_bitable_field` | Update field properties |
| `get_bitable_fields` | Get field definitions |
| `get_bitable_records` | Get records |
| `batch_create_records` | Bulk create records |
| `batch_update_records` | Bulk update records |
| `delete_bitable_records` | Delete records |
| `search_bitable_records` | Search with filters |
| `get_bitable_views` | Get all views |
| `update_bitable_view` | Update view |

### Tasks & Workflows (7 tools)
| Tool | Description |
|------|-------------|
| `create_task` | Create tasks |
| `update_task_status` | Update status |
| `add_task_reminder` | Add reminders |
| `create_approval` | Create approval requests |
| `get_approval_status` | Get approval status |
| `create_workflow` | Create automations |
| `execute_workflow` | Run workflows |

### Advanced Approvals (5 tools)
| Tool | Description |
|------|-------------|
| `transfer_approval` | Transfer to another user |
| `cancel_approval` | Cancel request |
| `cc_approval` | CC additional users |
| `add_approval_comment` | Add comments |
| `rollback_approval` | Rollback to previous step |

### Video Conference (3 tools)
| Tool | Description |
|------|-------------|
| `start_meeting_recording` | Start recording |
| `stop_meeting_recording` | Stop recording |
| `get_meeting_recording` | Get recording file |

### Knowledge Management (3 tools)
| Tool | Description |
|------|-------------|
| `create_wiki_space` | Create Wiki spaces |
| `create_wiki_page` | Create Wiki pages |
| `search_wiki` | Search Wiki |

### HR & Organization (5 tools)
| Tool | Description |
|------|-------------|
| `get_user_info` | Get user profile |
| `get_department_users` | Get dept members |
| `get_user_by_email_or_phone` | Find users |
| `create_leave_request` | Submit leave |
| `get_attendance_records` | Get attendance |

### Helpdesk (4 tools)
| Tool | Description |
|------|-------------|
| `create_helpdesk_ticket` | Create tickets |
| `get_helpdesk_ticket` | Get ticket details |
| `update_helpdesk_ticket` | Update tickets |
| `list_helpdesk_tickets` | List tickets |

### Drive Advanced (4 tools)
| Tool | Description |
|------|-------------|
| `create_file_version` | Create versions |
| `get_file_versions` | Get version history |
| `update_file_permission` | Update permissions |
| `get_file_permissions` | Get permissions |

### Bot/App Management (3 tools)
| Tool | Description |
|------|-------------|
| `create_bot_menu` | Create bot menus |
| `update_bot_info` | Update bot profile |
| `subscribe_events` | Subscribe to events |

### Admin & Security (3 tools)
| Tool | Description |
|------|-------------|
| `get_app_usage_stats` | Usage statistics |
| `get_audit_logs` | Audit logs |
| `manage_app_permissions` | Manage permissions |

### AI/Assistant (2 tools)
| Tool | Description |
|------|-------------|
| `create_ai_agent` | Create AI agents |
| `chat_with_ai` | Chat with agents |

### OKR (2 tools)
| Tool | Description |
|------|-------------|
| `create_okr` | Create OKRs |
| `update_okr_progress` | Update progress |

### Forms (2 tools)
| Tool | Description |
|------|-------------|
| `create_form` | Create forms |
| `get_form_responses` | Get responses |

### Smart Tools (7 tools)
| Tool | Description |
|------|-------------|
| `smart_build_bitable` | Build Bitable from natural language |
| `process_lark_message` | Auto-execute based on message |
| `generate_bitable_documentation` | Generate docs |
| `create_bitable_with_wiki` | Create system + docs |
| `list_bitable_templates` | List templates |
| `analyze_message_intent` | Analyze intent |
| `get_lark_bot_help` | Get help |

---

## 📝 Examples

### Create CRM System

```json
{
  "tool": "smart_build_bitable",
  "arguments": {
    "message": "顧客管理システムを作成して",
    "name": "CRM"
  }
}
```

### Send Message to Chat

```json
{
  "tool": "send_message",
  "arguments": {
    "chat_id": "oc_abc123",
    "message": "Hello from AI!",
    "message_type": "text"
  }
}
```

### Create Calendar Event

```json
{
  "tool": "create_calendar_event",
  "arguments": {
    "title": "Team Meeting",
    "start_time": "2024-01-15T10:00:00",
    "end_time": "2024-01-15T11:00:00",
    "attendees": ["ou_user1", "ou_user2"]
  }
}
```

### Batch Create Records

```json
{
  "tool": "batch_create_records",
  "arguments": {
    "app_token": "bascnxxxxxx",
    "table_id": "tblxxxxxx",
    "records": [
      {"fields": {"Name": "Alice", "Email": "alice@example.com"}},
      {"fields": {"Name": "Bob", "Email": "bob@example.com"}}
    ]
  }
}
```

---

## 🔒 Security

- Use environment variables for credentials
- OAuth 2.0 tenant access tokens
- All communications over HTTPS
- Auto token refresh

## 🔧 Development

```bash
# Install dev dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Format code
black src/

# Type check
mypy src/

# Lint
ruff src/
```

## 📁 Project Structure

```
src/lark_master_mcp/
├── __init__.py          # Package init
├── server.py            # MCP server
├── lark_client.py       # Lark API client
├── tools.py             # Tool definitions (108 tools)
├── cli.py               # CLI interface
├── smart_builder.py     # Smart Bitable builder
└── message_handler.py   # Message processing
```

## 📄 License

MIT License

## 🤝 Contributing

1. Fork the repository
2. Create feature branch
3. Make changes
4. Add tests
5. Submit PR

## 📞 Support

- [GitHub Issues](https://github.com/IvyGain/LarkMasterMCP/issues)
- [Lark Open Platform Docs](https://open.larksuite.com/document)

---

## Changelog

### v0.2.0 (Current)
- Added 7 Smart Tools
- Smart Bitable Builder with 8 templates
- Message Handler for bot integration
- Documentation Generator
- Total 108 tools

### v0.1.0
- Initial release
- 101 core Lark tools
- Basic MCP functionality
