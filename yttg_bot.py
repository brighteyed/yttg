import json
import logging
import os

import socks
import telegram
import youtube_dl

from functools import wraps
from telegram import MessageEntity
from urllib.request import urlopen

from telegram.ext import Updater
from telegram.ext import CommandHandler, MessageHandler, Filters


logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.WARNING)


CHATS = json.loads(os.environ["CHATS"])
USERS = json.loads(os.environ["USERS"])


def restricted(func):
    @wraps(func)
    def wrapped(update, context, *args, **kwargs):
        if update.effective_user:
            user_id = update.effective_user.id
            if user_id not in USERS:
                context.bot.send_message(chat_id=update.effective_chat.id, text="You are unathorized to use this bot")
                print(f'Unauthorized user: {user_id}')
                return
        else:
            chat_id = update.effective_chat.id
            if chat_id not in CHATS:
                print(f'Unauthorized chat: {chat_id}')
                return
        return func(update, context, *args, **kwargs)
    return wrapped


class Error(Exception):
    pass


def download_audiofile(video_url):
    """Download audio for video_url and convert it into mp3 format"""
    
    ydl_opts = {
        'outtmpl': os.path.join(os.environ["MEDIADIR"], '%(title)s.%(ext)s'),
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'm4a'
        }]
    }

    try:
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=True)
            return f'{os.path.splitext(ydl.prepare_filename(info))[0]}.m4a'

    except:
        return None


@restricted
def bot_start(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="Welcome! Please send me a link to the video")


@restricted
def bot_download(update, context):
    progress_msg = context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Downloading...",
        disable_notification=True)

    try:
        video_url = update.effective_message.text
        print(f'{download_audiofile.__name__}: url={video_url}')

        filename = download_audiofile(video_url)
        if not filename:
            raise Error(f"Failed downloading [this]({video_url}) video")

        size = os.path.getsize(filename)
        if size > 50000000:
            os.remove(filename)
            raise Error(f"Can not upload an audio file for [this]({video_url}) video because it is greater than 50Mb")

        try:
            with open(filename, 'rb') as audio:
                context.bot.send_audio(
                    chat_id=update.effective_chat.id,
                    caption=f"Done! Here is an audio only version for [this]({video_url}) video",
                    audio=audio,
                    parse_mode=telegram.ParseMode.MARKDOWN)
        except:
            raise Error(f"Failed uploading an audio file for [this]({video_url}) video")

    except Error as e:
        context.bot.send_message(chat_id=update.effective_chat.id, text=str(e), parse_mode=telegram.ParseMode.MARKDOWN)

    finally:
        # Always (?) delete initial message
        context.bot.delete_message(chat_id=update.effective_chat.id, message_id=update.effective_message.message_id)
        # Always delete "Downloading..." message
        context.bot.delete_message(chat_id=update.effective_chat.id, message_id=progress_msg.message_id)
        # Delete audio file if exists
        if filename and os.path.exists(filename):
            os.remove(filename)


if __name__ == "__main__":
    updater = Updater(token=os.environ["TOKEN"], use_context=True, request_kwargs={"proxy_url": os.environ["PROXY"]})
    dispatcher = updater.dispatcher

    dispatcher.add_handler(MessageHandler(Filters.text & (Filters.entity(MessageEntity.URL) | Filters.entity(MessageEntity.TEXT_LINK)), bot_download))
    dispatcher.add_handler(CommandHandler('start', bot_start))

    updater.start_polling()
