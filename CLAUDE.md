# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

LarkMasterMCP is a comprehensive MCP (Model Context Protocol) server for Lark (Feishu) integration. It provides AI assistants with powerful tools to interact with Lark's collaboration platform including messaging, calendar management, document operations, and more.

### Related Projects and Resources

1. **Official Lark OpenAPI MCP**: https://github.com/larksuite/lark-openapi-mcp
   - Official TypeScript implementation with 100+ auto-generated tools
   - Supports OAuth 2.0 and user access tokens
   - Available via NPM: `@larksuiteoapi/lark-mcp`
   
2. **Forked Repository**: https://github.com/IvyGain/lark-openapi-mcp
   - Fork of the official implementation

3. **Lark Node SDK**: `@larksuiteoapi/node-sdk`
   - Official SDK for Node.js applications

4. **Documentation**: https://open.larksuite.com/document/uAjLw4CM/ukTMukTMukTM/mcp_integration/mcp_introduction

### Comparison with Official Implementation

Our LarkMasterMCP is a comprehensive Python implementation compared to the official TypeScript version:

**Our Implementation**:
- 101 manually curated tools covering all major Lark features
- Python-based for easy customization
- Tenant access token authentication
- Comprehensive coverage of Lark platform capabilities

**Official Implementation**:
- 100+ auto-generated tools from OpenAPI specs
- OAuth 2.0 support with user access tokens
- Multiple transport modes (stdio, SSE, streamable)
- Preset tool collections (light, default, im, base, doc, task, calendar)
- Multi-language support (English/Chinese)

## Development Commands

### Environment Setup
```bash
# Install dependencies
pip install -e .

# Install with development dependencies  
pip install -e ".[dev]"

# Copy environment template
cp .env.example .env
# Then edit .env with your Lark app credentials
```

### Testing and Quality
```bash
# Run tests
pytest

# Run tests with coverage
pytest --cov=src/lark_master_mcp

# Format code
black src/

# Type checking
mypy src/

# Linting
ruff src/
```

### Running the Server
```bash
# Start MCP server (requires LARK_APP_ID and LARK_APP_SECRET in .env)
lark-mcp

# Or with explicit credentials
lark-mcp --app-id YOUR_APP_ID --app-secret YOUR_APP_SECRET
```

## Architecture

### Project Structure
```
src/lark_master_mcp/
├── __init__.py          # Package initialization
├── server.py            # Main MCP server implementation  
├── lark_client.py       # Lark API client with authentication
├── tools.py             # Tool definitions and schemas
└── cli.py               # Command-line interface
```

### Key Components

1. **MCP Server (`server.py`)**: 
   - Handles MCP protocol communication
   - Registers tool handlers
   - Manages tool execution and error handling

2. **Lark Client (`lark_client.py`)**:
   - Manages OAuth 2.0 authentication with auto-refresh
   - Provides async methods for all Lark API operations
   - Handles API errors and rate limiting

3. **Tool Definitions (`tools.py`)**:
   - Defines 101 comprehensive tools for Lark operations
   - JSON schemas for input validation
   - Covers all major Lark platform features including messaging, calendar, documents, tasks, wiki, HR, Bitable, AI agents, workflows, OKRs, forms, and more

4. **CLI Interface (`cli.py`)**:
   - Environment variable and command-line argument handling
   - Server startup and error handling

### Available Tools (101 total)

**Messaging & Communication (16 tools)**: `send_message`, `search_messages`, `list_chats`, `create_chat_group`, `get_chat_members`, `add_bot_to_chat`, `create_poll`, `reply_message`, `add_message_reaction`, `delete_message_reaction`, `pin_message`, `unpin_message`, `forward_message`, `send_urgent_message`, `read_message`, `get_message_read_users`

**Calendar & Meetings (11 tools)**: `create_calendar_event`, `get_user_calendar`, `create_meeting`, `share_screen`, `set_out_of_office`, `list_free_busy`, `create_calendar_reminder`, `create_recurring_event`, `book_meeting_room`, `search_meeting_rooms`, `accept_calendar_event`, `decline_calendar_event`

**Documents & Files (17 tools)**: `create_document`, `upload_file`, `create_drive_folder`, `share_file`, `get_spreadsheet_data`, `update_spreadsheet_data`, `search_documents`, `import_document`, `export_document`, `get_document_content`, `add_document_permission`, `add_document_comment`, `get_document_comments`, `create_document_from_template`, `lock_document_section`, `unlock_document_section`, `subscribe_document_changes`

**Bitable (Multi-dimensional Tables) (5 tools)**: `batch_create_records`, `batch_update_records`, `create_bitable_table`, `create_bitable_view`, `add_bitable_field`, `get_bitable_records`, `delete_bitable_records`

**Tasks & Workflows (7 tools)**: `create_task`, `update_task_status`, `create_approval`, `get_approval_status`, `add_task_reminder`, `create_workflow`, `execute_workflow`

**Advanced Approval Management (5 tools)**: `transfer_approval`, `cancel_approval`, `cc_approval`, `add_approval_comment`, `rollback_approval`

**Video Conference Recording (3 tools)**: `start_meeting_recording`, `stop_meeting_recording`, `get_meeting_recording`

**Advanced Bitable Operations (6 tools)**: `search_bitable_records`, `get_bitable_fields`, `update_bitable_field`, `create_bitable_app`, `get_bitable_views`, `update_bitable_view`

**Helpdesk/Support Management (4 tools)**: `create_helpdesk_ticket`, `get_helpdesk_ticket`, `update_helpdesk_ticket`, `list_helpdesk_tickets`

**Drive Advanced Operations (4 tools)**: `create_file_version`, `get_file_versions`, `update_file_permission`, `get_file_permissions`

**Knowledge Management (3 tools)**: `create_wiki_space`, `create_wiki_page`, `search_wiki`

**HR & Organization (5 tools)**: `get_user_info`, `get_department_users`, `create_leave_request`, `get_attendance_records`, `get_user_by_email_or_phone`

**Bot/App Management (3 tools)**: `create_bot_menu`, `update_bot_info`, `subscribe_events`

**Admin & Security (3 tools)**: `get_app_usage_stats`, `get_audit_logs`, `manage_app_permissions`

**AI/Assistant (2 tools)**: `create_ai_agent`, `chat_with_ai`

**OKR Management (2 tools)**: `create_okr`, `update_okr_progress`

**Forms (2 tools)**: `create_form`, `get_form_responses`

## Configuration

- `.env`: Environment variables for Lark app credentials
- `.claude/settings.local.json`: Claude Code IDE permissions
- `pyproject.toml`: Python project configuration with MCP dependencies

## Credentials Setup

1. Go to [Lark Open Platform](https://open.feishu.cn/app) or [Lark Suite (International)](https://open.larksuite.com)
2. Create new app or use existing one
3. Copy App ID and App Secret to `.env` file
4. Ensure app has required permissions for intended operations

## Future Enhancements Based on Official Implementation

### High Priority Features to Add
1. **OAuth 2.0 Support**: Enable user access tokens for personal resource access
2. **Batch Operations**: 
   - `batchCreateRecords`, `batchUpdateRecords` for Bitable
   - Bulk message operations
3. **Document Import/Export**: Complete document lifecycle management
4. **Advanced Search**: Cross-platform search capabilities
5. **User ID Resolution**: Lookup users by email/phone

### Tools Missing from Our Implementation
The official Lark OpenAPI MCP includes these additional tool categories:
- **AI/Aily**: Feishu AI assistant integration
- **aPaaS**: Low-code platform tools
- **Advanced HR**: Shift management, detailed attendance
- **Developer Tools**: API documentation recall
- **Batch Operations**: Efficient bulk data processing
- **SSE/Streamable Transport**: For web integrations

### Official Preset Tool Collections
- `preset.light`: Minimal essential tools (10 tools)
- `preset.default`: Common tools for most users (25 tools)  
- `preset.im.default`: Messaging focused (5 tools)
- `preset.base.default`: Bitable operations (7 tools)
- `preset.base.batch`: Batch Bitable operations (6 tools)
- `preset.doc.default`: Document operations (6 tools)
- `preset.task.default`: Task management (4 tools)
- `preset.calendar.default`: Calendar operations (5 tools)