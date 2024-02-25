import asyncio
import logging
from io import StringIO

from pyrogram.client import Client
from pyrogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
)
from yt_dlp import YoutubeDL

from app.logger import YtdlpLogger
from app.queries import get_user_by_id
from app.security import whitelisted
from app.tasks import (
    HandleUrlTaskData,
    handle_url_task,
    register_user_task,
    toggle_is_audio_only_task,
)
from app.validators import validate_url

logger = logging.getLogger(__name__)


async def start_handler(client: Client, message: Message) -> None:
    await client.delete_messages(message.chat.id, message.id)

    if not await get_user_by_id(message.from_user.id):
        await register_user_task(message.from_user.id)
        await message.reply("Вы зарегистрированы. Обратитесь к @evilyach за доступом к боту.")

    buttons = [
        InlineKeyboardButton(text="Скачивать только аудио?", callback_data="toggle_is_audio_only_callback_handler"),
    ]

    keyboard = InlineKeyboardMarkup([buttons])

    await message.reply(
        "Привет! Отправьте ссылку на любое видео, которое хотите скачать.",
        reply_markup=keyboard,
    )


async def help_handler(client: Client, message: Message) -> None:
    await client.delete_messages(message.chat.id, message.id)

    msg = (
        "<b>Скачатель Онлайн.</b>\n"
        "\n"
        "Бот для скачивания видео из интернета.\n"
        "\n"
        "Для скачивания видео просто отправьте ссылку на видео, и в ответ Вы получите "
        "видео, которое можно посмотреть прямо в Telegram.\n"
        "\n"
        "Если Вы хотите скачать только аудио, без видео (например, песню или подкаст), можно поменять "
        "режим кнопкой в меню '/start' или командой '/audio_only'.\n"
        "\n"
        "Бот умеет скачивать видео из следующих источников:\n"
        "- YouTube.\n"
        "- YouTube Shorts.\n"
        "- RuTube.\n"
        "- TikTok.\n"
        "- Twitch VODs.\n"
        "- Twitch Clips.\n"
        "- Одноклассники.\n"
        "- VK Video.\n"
        "- VK Клипы.\n"
        "- Двач.\n"
        "- 4chan.\n"
        "- DailyMotion.\n"
        "\n"
        "В настоящее время есть проблемы со скачиванием из:\n"
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

    user = await get_user_by_id(message.from_user.id)
    if not user:
        logger.error(f"Couldn't get user with id = '{message.from_user.id}'")

        return

    logger.info(user)

    if user.is_audio_only:
        format = "ba/best"
        ext = "mp3"
    else:
        format = "mp4[filesize<2G]/best"
        ext = "mp4"

    opts = {
        "format": format,
        "logger": YtdlpLogger(),
        "merge_output_format": ext,
        "outtmpl": "./output/%(id)s.%(ext)s",
        "postprocessors": [
            {
                "key": "FFmpegVideoConvertor",
                "preferedformat": ext,
            }
        ],
        "writethumbnail": True,
    }

    logger.info(opts)

    start_message = await client.send_message(message.chat.id, "Начинаю скачивание...")

    with YoutubeDL(opts) as ydl:
        # Get the tasks for downloading the videos
        tasks = [
            handle_url_task(
                HandleUrlTaskData(
                    url=url,
                    client=client,
                    message=message,
                    user=user,
                    chat_id=message.chat.id,
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


async def toggle_is_audio_only_handler(client: Client, message: Message) -> None:
    try:
        msg = await toggle_is_audio_only_task(message.from_user.id)
    except ValueError:
        await client.send_message(message.chat.id, "Не получилось обновить настройки. 😢")
        return

    await client.send_message(message.chat.id, msg)


async def toggle_is_audio_only_callback_handler(client: Client, callback_query: CallbackQuery) -> None:
    try:
        msg = await toggle_is_audio_only_task(callback_query.from_user.id)
    except ValueError:
        await client.send_message(callback_query.message.chat.id, "Не получилось обновить настройки. 😢")
        return

    await client.send_message(callback_query.message.chat.id, msg)
