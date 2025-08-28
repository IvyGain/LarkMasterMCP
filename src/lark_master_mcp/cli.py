"""CLI interface for LarkMasterMCP server."""

import asyncio
import os
import sys
from typing import Optional
import click
from dotenv import load_dotenv

from .server import LarkMCPServer


@click.command()
@click.option(
    "--app-id",
    envvar="LARK_APP_ID",
    help="Lark App ID (can also be set via LARK_APP_ID environment variable)"
)
@click.option(
    "--app-secret", 
    envvar="LARK_APP_SECRET",
    help="Lark App Secret (can also be set via LARK_APP_SECRET environment variable)"
)
@click.option(
    "--env-file",
    default=".env",
    help="Path to environment file (default: .env)"
)
def main(app_id: Optional[str], app_secret: Optional[str], env_file: str):
    """Start the LarkMasterMCP server."""
    
    # Load environment variables
    if os.path.exists(env_file):
        load_dotenv(env_file)
    
    # Get credentials
    app_id = app_id or os.getenv("LARK_APP_ID")
    app_secret = app_secret or os.getenv("LARK_APP_SECRET")
    
    if not app_id or not app_secret:
        click.echo(
            "Error: Lark App ID and App Secret are required.\n"
            "Provide them via --app-id and --app-secret options, "
            "or set LARK_APP_ID and LARK_APP_SECRET environment variables.",
            err=True
        )
        sys.exit(1)
    
    # Create and run server
    server = LarkMCPServer(app_id, app_secret)
    
    try:
        asyncio.run(server.run())
    except KeyboardInterrupt:
        click.echo("\nShutting down server...")
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


if __name__ == "__main__":
    main()