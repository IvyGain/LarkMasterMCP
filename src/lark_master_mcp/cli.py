"""CLI interface for LarkMasterMCP server."""

import asyncio
import logging
import os
import sys
from typing import Optional
import click
from dotenv import load_dotenv

from .server import LarkMCPServer

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)


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
    
    logger.info("Starting LarkMasterMCP CLI...")
    
    # Load environment variables
    if os.path.exists(env_file):
        logger.info(f"Loading environment from {env_file}")
        load_dotenv(env_file)
    else:
        logger.warning(f"Environment file {env_file} not found")
    
    # Get credentials
    app_id = app_id or os.getenv("LARK_APP_ID")
    app_secret = app_secret or os.getenv("LARK_APP_SECRET")
    
    if not app_id or not app_secret:
        logger.error("Missing required credentials")
        click.echo(
            "Error: Lark App ID and App Secret are required.\n"
            "Provide them via --app-id and --app-secret options, "
            "or set LARK_APP_ID and LARK_APP_SECRET environment variables.",
            err=True
        )
        sys.exit(1)
    
    logger.info("Credentials loaded successfully")
    
    # Create and run server
    server = LarkMCPServer(app_id, app_secret)
    
    try:
        asyncio.run(server.run())
    except KeyboardInterrupt:
        logger.info("Received shutdown signal")
        click.echo("\nShutting down server...")
    except Exception as e:
        logger.error(f"Server error: {e}")
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


if __name__ == "__main__":
    main()