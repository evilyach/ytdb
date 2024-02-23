from enum import Enum, auto

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base


class VideoQuality(Enum):
    default = auto()
    best = auto()


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)

    is_whitelisted: Mapped[bool] = mapped_column(default=False)

    is_audio_only: Mapped[bool] = mapped_column(default=False)
    is_send_voice: Mapped[bool] = mapped_column(default=False)
    quality: Mapped[VideoQuality] = mapped_column(default=VideoQuality.default)

    def __repr__(self) -> str:
        return f"User(id={self.id!r})"


class DownloadEntry(Base):
    __tablename__ = "downloads"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))

    url: Mapped[str] = mapped_column()
    name: Mapped[str] = mapped_column()

    def __repr__(self) -> str:
        return f"DownloadEntry(id={self.id!r}, name={self.name!r})"
