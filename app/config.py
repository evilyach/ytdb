import logging

from pydantic import Field, validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
    )

    bot_name: str = Field(
        alias="BOT_NAME",
        frozen=True,
        default="",
        description="The name of a Telegram bot.",
        examples=["ytdb_bot"],
    )
    bot_token: str = Field(
        alias="BOT_TOKEN",
        pattern="^[0-9]{8,10}:[a-zA-Z0-9_-]{35}$",
        frozen=True,
        default="",
        description="A secret token for a Telegram bot.",
        examples=["0123456789:budPUlIkeEYED0PaSaFEqYNTdtyvI6LFZCh"],
    )
    api_id: int = Field(
        alias="API_ID",
        frozen=True,
        default=0,
        description="An id number required for user authentication.",
        examples=["1337"],
    )
    api_hash: str = Field(
        alias="API_HASH",
        frozen=True,
        default="",
        description="An id number required for user authentication.",
        examples=["1337"],
    )

    logging_level: int | str = Field(
        alias="LOGGING_LEVEL",
        default=30,
        description="Logging level for your app.",
        examples=["ERROR", 40],
    )
    video_cache_time: int = Field(
        alias="VIDEO_CACHE_TIME",
        default=0,
        description="Amount of seconds we want to keep videos in a folder as a cache.",
        examples=[0, 180],
    )
    db_path: str = Field(
        alias="DB_PATH",
        default="ytdb.db",
        description="Path to a SQLite DB that is going to keep some settings.",
        examples=["storage/ytdb.db"],
    )

    @validator("logging_level")
    def get_logging_level(cls, value: int | str) -> int:
        if isinstance(value, int):
            return value
        return logging.getLevelNamesMapping().get(value, logging.DEBUG)


settings = Settings()
