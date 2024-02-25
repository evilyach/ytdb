import logging
from pathlib import Path
from typing import Annotated

from rich.logging import RichHandler
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session
from typer import Argument, Option, Typer

app = Typer()
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, handlers=[RichHandler()])


@app.command()
def whitelist(
    id: Annotated[int, Argument(help="ID of a user to add to a whitelist")],
    db_path: Annotated[str, Option(help="Path to a SQLite database")] = "ytdb.db",
) -> None:
    """Update rights to access the bot for user.

    By default, you are supposed to launch this script from repo root.
    """

    if not Path(db_path).exists():
        logger.error(f"No database found at '{db_path}'")
        return

    engine = create_engine(f"sqlite:///{db_path}")

    with Session(engine) as session:
        stmt = text(f"SELECT * FROM users WHERE id={id}")
        user = session.execute(stmt).scalars().one_or_none()

        if not user:
            logger.error(f"User with id = '{id}' does not exist.")
            return

        stmt = text(f"UPDATE users SET is_whitelisted=1 WHERE id={id}")
        session.execute(stmt)
        session.commit()

    logger.info(f"Updated whitelist rights for user '{id}'")


if __name__ == "__main__":
    app()
