import asyncio
import logging
from io import StringIO

from pyrogram.client import Client
from pyrogram.types import Message
from yt_dlp import YoutubeDL

from app.logger import YtdlpLogger
from app.queries import get_user_by_id
from app.security import whitelisted
from app.tasks import HandleUrlTaskData, handle_url_task, register_user_task
from app.validators import validate_url

logger = logging.getLogger(__name__)


async def start_handler(client: Client, message: Message) -> None:
    await client.delete_messages(message.chat.id, message.id)

    if not await get_user_by_id(message.from_user.id):
        await register_user_task(message.from_user.id)
        await message.reply("Вы зарегистрированы. Обратитесь к @evilyach за доступом к боту.")

    await message.reply("Привет! Отправьте ссылку на любое видео, которое хотите скачать.")


async def help_handler(client: Client, message: Message) -> None:
    await client.delete_messages(message.chat.id, message.id)

    msg = (
        "Бот для скачивания видео из интернета.\n"
        "\n"
        "Для скачивания видео просто отправьте ссылку на видео, и в ответ Вы получите "
        "видео, которое можно посмотреть прямо в Telegram.\n"
        "\n"
        "Бот точно умеет скачать видео из:\n"
        "- YouTube.\n"
        "- YouTube Shorts.\n"
        "- RuTube.\n"
        "- TikTok.\n"
        "- Двач.\n"
        "- 4chan.\n"
        "- DailyMotion.\n"
        "\n"
        "В настоящее время есть проблемы с:\n"
        "- Instagram Reels.\n"
        "- RuTube Shorts.\n"
        "\n"
        "Бот доступен для пользователей из белого списка. Чтобы попасть в него, обратитесь "
        "к админу (@evilyach).\n"
    )

    await message.reply(msg)


@whitelisted
async def download_handler(client: Client, message: Message) -> None:
    urls = []

    for url in StringIO(message.text).readlines():
        if not validate_url(url):
            logger.info(f"Tried to download link '{url}', which is not a valid URL.")
            continue

        urls.append(url.strip())

    if not urls:
        logger.info(f"User {message.from_user.id} tried to provide invalid links only.")
        await message.reply("Похоже, Вы не отправили ни одной ссылки. Попробуйте еще раз.")

        return

    opts = {
        "format": "mp4/best",
        "logger": YtdlpLogger(),
        "merge_output_format": "mp4",
        "outtmpl": "./output/%(id)s.%(ext)s",
        "postprocessors": [
            {
                "key": "FFmpegVideoConvertor",
                "preferedformat": "mp4",
            }
        ],
        "writethumbnail": True,
    }

    start_message = await client.send_message(message.chat.id, "Начинаю скачивание...")

    with YoutubeDL(opts) as ydl:
        # Get the tasks for downloading the videos
        tasks = [
            handle_url_task(
                HandleUrlTaskData(
                    url=url,
                    client=client,
                    message=message,
                    chat_id=message.chat.id,
                    user_id=message.from_user.id,
                    ydl=ydl,
                )
            )
            for url in urls
        ]

        # Run the tasks
        for task in asyncio.as_completed(tasks):
            try:
                await task
            except Exception:
                await message.reply("Не удалось скачать видео по ссылке. 😢")
                logger.warning("Error occurred while executing the task.")

                raise
            finally:
                await client.delete_messages(message.chat.id, start_message.id)
                await client.delete_messages(message.chat.id, message.id)
