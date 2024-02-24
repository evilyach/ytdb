from pathlib import Path
from typing import Annotated

from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session
from typer import Argument, Option, Typer

app = Typer()


@app.command()
def whitelist(
    id: Annotated[int, Argument(help="ID of a user to add to a whitelist")],
    db_path: Annotated[str, Option(help="Path to a SQLite database")] = "ytdb.db",
) -> None:
    """Update rights to access the bot for user."""

    if not Path(db_path).exists():
        print(f"No file found at '{db_path}'")
        return

    engine = create_engine(f"sqlite:///{db_path}")

    with Session(engine) as session:
        stmt = text(f"SELECT * FROM users WHERE id={id}")
        user = session.execute(stmt).scalars().one_or_none()

        if not user:
            print("User does not exist.")
            return

        stmt = text(f"UPDATE users SET is_whitelisted=1 WHERE id={id}")
        session.execute(stmt)
        session.commit()

        print(f"Updated whitelist rights for user '{id}'")


if __name__ == "__main__":
    app()
