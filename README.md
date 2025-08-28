# LarkMasterMCP

A comprehensive MCP (Model Context Protocol) server for Lark (Feishu) integration, providing AI assistants with powerful tools to interact with Lark's collaboration platform.

## Features

### 🚀 Core Capabilities
- **Messaging**: Send messages to chats and users
- **Calendar Management**: Create and manage calendar events
- **Document Operations**: Create and manage Lark documents
- **File Management**: Upload and share files
- **User & Organization**: Get user info and department data
- **Meetings**: Create video meetings
- **Spreadsheets**: Read and write spreadsheet data
- **Search**: Search messages across chats

### 🛠️ Available Tools

#### 📨 Messaging & Communication
| Tool | Description |
|------|-------------|
| `send_message` | Send text, rich text, or media messages |
| `search_messages` | Search for messages across chats |
| `list_chats` | List accessible chats |
| `create_chat_group` | Create a new chat group |
| `get_chat_members` | Get members of a chat group |
| `add_bot_to_chat` | Add the bot to a chat group |
| `create_poll` | Create polls in chats |

#### 📅 Calendar & Meetings
| Tool | Description |
|------|-------------|
| `create_calendar_event` | Create calendar events with attendees |
| `get_user_calendar` | Get user's calendar events |
| `create_meeting` | Create video meetings |
| `share_screen` | Start screen sharing in meetings |
| `set_out_of_office` | Set out of office auto-reply |

#### 📄 Documents & Files
| Tool | Description |
|------|-------------|
| `create_document` | Create new documents in Lark Docs |
| `upload_file` | Upload files to Lark |
| `create_drive_folder` | Create folders in Lark Drive |
| `share_file` | Share files with users |
| `get_spreadsheet_data` | Extract data from spreadsheets |
| `update_spreadsheet_data` | Update spreadsheet data |

#### 📋 Tasks & Workflows
| Tool | Description |
|------|-------------|
| `create_task` | Create tasks with assignees |
| `update_task_status` | Update task status |
| `create_approval` | Create approval requests |
| `get_approval_status` | Get approval request status |

#### 📚 Knowledge Management
| Tool | Description |
|------|-------------|
| `create_wiki_space` | Create wiki spaces |
| `create_wiki_page` | Create wiki pages |
| `search_wiki` | Search wiki content |

#### 👥 HR & Organization
| Tool | Description |
|------|-------------|
| `get_user_info` | Retrieve user profile information |
| `get_department_users` | Get users in departments |
| `create_leave_request` | Create leave/time-off requests |
| `get_attendance_records` | Get attendance records |

## Installation

### Prerequisites
- Python 3.8+
- Lark App credentials (App ID and App Secret)

### Setup

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd LarkMasterMCP
   ```

2. **Install dependencies**:
   ```bash
   pip install -e .
   ```

3. **Configure credentials**:
   ```bash
   cp .env.example .env
   # Edit .env with your Lark app credentials
   ```

4. **Get Lark App Credentials**:
   - Go to [Lark Open Platform](https://open.feishu.cn/app)
   - Create a new app or use existing one
   - Copy App ID and App Secret to your `.env` file

## Usage

### As MCP Server

Start the server for use with MCP clients:

```bash
lark-mcp
```

Or with explicit credentials:

```bash
lark-mcp --app-id YOUR_APP_ID --app-secret YOUR_APP_SECRET
```

### With Claude Desktop

Add to your Claude Desktop configuration:

```json
{
  "mcpServers": {
    "lark-master": {
      "command": "lark-mcp",
      "env": {
        "LARK_APP_ID": "your_app_id",
        "LARK_APP_SECRET": "your_app_secret"
      }
    }
  }
}
```

## Development

### Project Structure

```
src/lark_master_mcp/
├── __init__.py          # Package initialization
├── server.py            # Main MCP server implementation
├── lark_client.py       # Lark API client
├── tools.py             # Tool definitions
└── cli.py               # Command-line interface
```

### Development Commands

```bash
# Install in development mode
pip install -e ".[dev]"

# Run tests
pytest

# Format code
black src/

# Type checking
mypy src/

# Linting
ruff src/
```

### Architecture

The MCP server architecture consists of:

1. **MCP Server (`server.py`)**: Handles MCP protocol communication
2. **Lark Client (`lark_client.py`)**: Manages authentication and API calls
3. **Tool Definitions (`tools.py`)**: Defines available tools and their schemas
4. **CLI Interface (`cli.py`)**: Provides command-line access

## Examples

### Basic Message Sending

```python
# Through MCP tool call
{
  "tool": "send_message",
  "arguments": {
    "chat_id": "oc_abc123",
    "message": "Hello from AI assistant!",
    "message_type": "text"
  }
}
```

### Creating Calendar Events

```python
{
  "tool": "create_calendar_event",
  "arguments": {
    "title": "Team Meeting",
    "start_time": "2024-01-15T10:00:00",
    "end_time": "2024-01-15T11:00:00",
    "attendees": ["ou_user1", "ou_user2"],
    "description": "Weekly team sync"
  }
}
```

## Security

- Store credentials securely using environment variables
- The server uses OAuth 2.0 tenant access tokens
- All API communications use HTTPS
- Tokens are automatically refreshed as needed

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## License

MIT License - see LICENSE file for details

## Support

For issues and questions:
- Check the [Issues](https://github.com/your-username/lark-master-mcp/issues) page
- Review Lark API documentation
- Ensure your app has the necessary permissions

## Changelog

### v0.1.0
- Initial release
- Basic MCP server functionality
- Core Lark API integration
- 30 comprehensive tools covering:
  - Messaging & Communication
  - Calendar & Meetings
  - Documents & Files
  - Tasks & Workflows
  - Knowledge Management
  - HR & Organization