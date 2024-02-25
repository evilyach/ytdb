import asyncio
import logging
import os
from pathlib import Path
from typing import Annotated

from dotenv import load_dotenv
from pyrogram.client import Client
from rich.logging import RichHandler
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session
from typer import Argument, Option, Typer

app = Typer()
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, handlers=[RichHandler()])


async def send_message(message: str, dot_env_path: str = ".env") -> None:
    # Get environment variables from .env
    load_dotenv(dot_env_path)

    bot_name = os.getenv("BOT_NAME")
    if not bot_name:
        logger.error("Can't get BOT_NAME. Please check your .env file.")
        return

    bot_token = os.getenv("BOT_TOKEN")
    if not bot_token:
        logger.error("Can't get BOT_TOKEN. Please check your .env file.")
        return

    api_id = os.getenv("API_ID")
    if not api_id:
        logger.error("Can't get API_ID. Please check your .env file.")
        return
    api_id = int(api_id)

    api_hash = os.getenv("API_HASH")
    if not api_hash:
        logger.error("Can't get API_ID. Please check your .env file.")
        return

    answer = input("Type 'Yes' to confirm sending the message to all users -> ")
    if answer != "Yes":
        logger.info("Aborted.")
        return

    async with Client(bot_name, bot_token=bot_token, api_id=api_id, api_hash=api_hash) as client:
        await client.send_message("self", message)


@app.command()
def broadcast(
    message: Annotated[str, Argument(help="Message that you want to broadcast")],
    dot_env_path: Annotated[str, Option(help="Path to the .env file")] = ".env",
    db_path: Annotated[str, Option(help="Path to a SQLite database")] = "ytdb.db",
) -> None:
    """Broadcast a message for all users in the database.

    By default, you are supposed to launch this script from repo root.
    """

    # Initialise DB
    if not Path(db_path).exists():
        logger.error(f"No database found at '{db_path}'")
        return

    engine = create_engine(f"sqlite:///{db_path}")

    with Session(engine) as session:
        stmt = text(f"SELECT * FROM users WHERE is_whitelisted=1")
        users = session.execute(stmt).scalars().all()

        logger.info(f"Got {len(users)} users.")

    asyncio.run(send_message(message, dot_env_path=dot_env_path))


if __name__ == "__main__":
    app()
