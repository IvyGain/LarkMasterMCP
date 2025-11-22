"""Remote MCP Server with SSE support for LarkMasterMCP."""

import asyncio
import json
import logging
import os
from typing import Any, Dict, List, Optional
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import StreamingResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

from .lark_client import LarkClient
from .tools import LARK_TOOLS
from .smart_builder import SmartBitableBuilder, DocumentationGenerator
from .message_handler import MessageHandler, MessageParser

# Setup logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ToolCallRequest(BaseModel):
    """Tool call request model."""
    name: str
    arguments: Dict[str, Any] = {}


class LarkRemoteMCPServer:
    """Remote MCP Server with SSE and HTTP endpoints."""

    def __init__(self, app_id: str, app_secret: str):
        self.app_id = app_id
        self.app_secret = app_secret
        self.lark_client = LarkClient(app_id, app_secret)

        # Initialize smart components
        self.smart_builder = SmartBitableBuilder(self.lark_client)
        self.doc_generator = DocumentationGenerator(self.lark_client)
        self.message_handler = MessageHandler(self.lark_client, self.smart_builder)
        self.message_parser = MessageParser()

        logger.info("Initialized LarkMasterMCP Remote Server with 108 tools")

    async def list_tools(self) -> List[Dict[str, Any]]:
        """List available tools."""
        return LARK_TOOLS

    async def call_tool(self, name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a tool and return result."""
        logger.info(f"Executing tool: {name}")

        try:
            # Import the tool execution logic from server.py
            result = await self._execute_tool(name, arguments)
            return {"success": True, "result": result}
        except Exception as e:
            logger.error(f"Tool execution error: {e}")
            return {"success": False, "error": str(e)}

    async def _execute_tool(self, name: str, arguments: Dict[str, Any]) -> Any:
        """Execute tool implementation."""

        # Messaging tools
        if name == "send_message":
            return await self.lark_client.send_message(
                chat_id=arguments["chat_id"],
                message=arguments["message"],
                message_type=arguments.get("message_type", "text")
            )

        elif name == "list_chats":
            return await self.lark_client.list_chats()

        elif name == "search_messages":
            return await self.lark_client.search_messages(
                query=arguments["query"],
                chat_id=arguments.get("chat_id")
            )

        # Bitable tools
        elif name == "create_bitable_app":
            return await self.lark_client.create_bitable_app(
                name=arguments["name"],
                folder_token=arguments.get("folder_token")
            )

        elif name == "create_bitable_table":
            return await self.lark_client.create_bitable_table(
                app_token=arguments["app_token"],
                name=arguments["name"],
                fields=arguments["fields"]
            )

        elif name == "batch_create_records":
            return await self.lark_client.batch_create_records(
                app_token=arguments["app_token"],
                table_id=arguments["table_id"],
                records=arguments["records"]
            )

        elif name == "get_bitable_records":
            return await self.lark_client.get_bitable_records(
                app_token=arguments["app_token"],
                table_id=arguments["table_id"],
                view_id=arguments.get("view_id"),
                filter=arguments.get("filter")
            )

        # Document tools
        elif name == "create_document":
            return await self.lark_client.create_document(
                title=arguments["title"],
                content=arguments.get("content", ""),
                folder_token=arguments.get("folder_token")
            )

        elif name == "search_documents":
            return await self.lark_client.search_documents(
                query=arguments["query"],
                doc_types=arguments.get("doc_types"),
                owner_ids=arguments.get("owner_ids"),
                chat_ids=arguments.get("chat_ids")
            )

        # Wiki tools
        elif name == "create_wiki_space":
            return await self.lark_client.create_wiki_space(
                name=arguments["name"],
                description=arguments.get("description", ""),
                members=arguments.get("members", [])
            )

        elif name == "create_wiki_page":
            return await self.lark_client.create_wiki_page(
                space_id=arguments["space_id"],
                title=arguments["title"],
                content=arguments.get("content", ""),
                parent_page_id=arguments.get("parent_page_id")
            )

        # Smart tools
        elif name == "smart_build_bitable":
            return await self.smart_builder.build_from_message(
                message=arguments["message"],
                name=arguments.get("name"),
                folder_token=arguments.get("folder_token")
            )

        elif name == "process_lark_message":
            cmd_result = await self.message_handler.handle_message(
                message=arguments["message"]
            )
            return {
                "success": cmd_result.success,
                "command_type": cmd_result.command_type.value,
                "message": cmd_result.message,
                "data": cmd_result.data
            }

        elif name == "generate_bitable_documentation":
            design = self.smart_builder.design_bitable(
                message=arguments["message"],
                name=arguments.get("name")
            )
            doc_content = self.doc_generator.generate_bitable_documentation(design)
            return {
                "documentation": doc_content,
                "design_name": design.name
            }

        elif name == "create_bitable_with_wiki":
            # 1. Build Bitable
            bitable_result = await self.smart_builder.build_from_message(
                message=arguments["message"],
                name=arguments.get("name"),
                folder_token=arguments.get("folder_token")
            )

            # 2. Create Wiki space
            wiki_name = arguments.get("name", "システムドキュメント")
            wiki_result = await self.lark_client.create_wiki_space(
                name=f"{wiki_name} Wiki",
                description=f"{wiki_name}のドキュメンテーション"
            )

            # 3. Generate documentation
            design = self.smart_builder.design_bitable(
                message=arguments["message"],
                name=arguments.get("name")
            )
            space_id = wiki_result.get("space", {}).get("space_id", "")
            if space_id:
                doc_result = await self.doc_generator.create_wiki_documentation(
                    design=design,
                    space_id=space_id
                )
            else:
                doc_result = {"error": "Failed to get wiki space_id"}

            return {
                "bitable": bitable_result,
                "wiki": wiki_result,
                "documentation": doc_result
            }

        elif name == "list_bitable_templates":
            templates_info = {}
            for name_key, template in self.smart_builder.TEMPLATES.items():
                templates_info[name_key] = {
                    "name": template["name"],
                    "description": template["description"],
                    "fields": [
                        {"name": f.name, "type": f.field_type.name}
                        for f in template["fields"]
                    ]
                }
            return {"templates": templates_info}

        elif name == "analyze_message_intent":
            parsed = self.message_parser.parse(arguments["message"])
            return {
                "command_type": parsed.command_type.value,
                "confidence": parsed.confidence,
                "parameters": parsed.parameters,
                "original_message": parsed.original_message
            }

        elif name == "get_lark_bot_help":
            help_result = await self.message_handler.handle_message("ヘルプ")
            return {
                "help_text": help_result.message,
                "templates": help_result.data.get("templates", []) if help_result.data else []
            }

        else:
            raise ValueError(f"Unknown or unimplemented tool: {name}")


def create_app() -> FastAPI:
    """Create FastAPI application."""

    app_id = os.environ.get("LARK_APP_ID", "")
    app_secret = os.environ.get("LARK_APP_SECRET", "")

    if not app_id or not app_secret:
        logger.warning("LARK_APP_ID or LARK_APP_SECRET not set")

    mcp_server = LarkRemoteMCPServer(app_id, app_secret) if app_id and app_secret else None

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        logger.info("🚀 LarkMasterMCP Remote Server starting...")
        yield
        logger.info("👋 LarkMasterMCP Remote Server shutting down...")

    app = FastAPI(
        title="LarkMasterMCP Remote Server",
        description="自然言語でLarkを操作できるMCPサーバー | 108ツール",
        version="0.2.0",
        lifespan=lifespan
    )

    # CORS設定
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.get("/")
    async def root():
        """Root endpoint."""
        return {
            "name": "LarkMasterMCP Remote Server",
            "version": "0.2.0",
            "tools": 108,
            "status": "running",
            "endpoints": {
                "tools": "/tools",
                "call": "/call",
                "sse": "/sse",
                "health": "/health"
            }
        }

    @app.get("/health")
    async def health():
        """Health check endpoint."""
        return {"status": "healthy", "tools_count": 108}

    @app.get("/tools")
    async def list_tools():
        """List all available tools."""
        if not mcp_server:
            raise HTTPException(status_code=503, detail="Server not configured")
        tools = await mcp_server.list_tools()
        return {"tools": tools, "count": len(tools)}

    @app.get("/tools/{tool_name}")
    async def get_tool(tool_name: str):
        """Get specific tool information."""
        if not mcp_server:
            raise HTTPException(status_code=503, detail="Server not configured")
        tools = await mcp_server.list_tools()
        for tool in tools:
            if tool["name"] == tool_name:
                return tool
        raise HTTPException(status_code=404, detail=f"Tool '{tool_name}' not found")

    @app.post("/call")
    async def call_tool(request: ToolCallRequest):
        """Call a tool."""
        if not mcp_server:
            raise HTTPException(status_code=503, detail="Server not configured")
        result = await mcp_server.call_tool(request.name, request.arguments)
        return result

    @app.get("/sse")
    async def sse_endpoint(request: Request):
        """SSE endpoint for streaming responses."""

        async def event_generator():
            # Send initial connection event
            yield f"data: {json.dumps({'type': 'connected', 'server': 'LarkMasterMCP'})}\n\n"

            # Keep connection alive
            while True:
                if await request.is_disconnected():
                    break
                yield f"data: {json.dumps({'type': 'ping'})}\n\n"
                await asyncio.sleep(30)

        return StreamingResponse(
            event_generator(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
            }
        )

    @app.post("/sse/call")
    async def sse_call_tool(request: Request):
        """SSE endpoint for tool calls with streaming response."""
        if not mcp_server:
            raise HTTPException(status_code=503, detail="Server not configured")

        body = await request.json()
        tool_name = body.get("name")
        arguments = body.get("arguments", {})

        async def stream_response():
            yield f"data: {json.dumps({'type': 'start', 'tool': tool_name})}\n\n"

            try:
                result = await mcp_server.call_tool(tool_name, arguments)
                yield f"data: {json.dumps({'type': 'result', 'data': result})}\n\n"
            except Exception as e:
                yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"

            yield f"data: {json.dumps({'type': 'end'})}\n\n"

        return StreamingResponse(
            stream_response(),
            media_type="text/event-stream"
        )

    # MCP Protocol endpoints
    @app.post("/mcp/list_tools")
    async def mcp_list_tools():
        """MCP Protocol: List tools."""
        if not mcp_server:
            raise HTTPException(status_code=503, detail="Server not configured")
        tools = await mcp_server.list_tools()
        return {
            "jsonrpc": "2.0",
            "result": {"tools": tools}
        }

    @app.post("/mcp/call_tool")
    async def mcp_call_tool(request: Request):
        """MCP Protocol: Call tool."""
        if not mcp_server:
            raise HTTPException(status_code=503, detail="Server not configured")

        body = await request.json()
        params = body.get("params", {})
        tool_name = params.get("name")
        arguments = params.get("arguments", {})

        result = await mcp_server.call_tool(tool_name, arguments)

        return {
            "jsonrpc": "2.0",
            "result": {"content": [{"type": "text", "text": json.dumps(result)}]}
        }

    return app


def run_server(host: str = "0.0.0.0", port: int = 8000):
    """Run the remote MCP server."""
    app = create_app()
    uvicorn.run(app, host=host, port=port)


if __name__ == "__main__":
    run_server()
