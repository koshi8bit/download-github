# https://stackoverflow.com/questions/61587791/python-telegram-bot-how-to-use-conversationquerycallback-with-instance-method-a
import datetime
import io
import os
from typing import List

import requests
import telegram
from telegram import Update, Message, PhotoSize
from telegram.ext import MessageHandler, Filters, Updater, CommandHandler, ConversationHandler

from lib.koshi8bit.easy_living import Utils


class TelegramBot:
    _types = {
        "_command_callback": CommandHandler,
        "_message_callback": MessageHandler,
        "_conversation_callback": ConversationHandler
    }

    def __init__(self, token):
        self.updater = Updater(token, use_context=True)
        self.dispatcher = self.updater.dispatcher
        self.bot = telegram.Bot(token=token)

    def start_polling(self):
        self.updater.start_polling()
        self.updater.idle()

    @staticmethod
    def save_pic(update: Update, path: str, _format: str = "%user--%filename", pic: List[PhotoSize] = None):
        if not pic:
            pic = update.message.photo
        if not len(pic) > 0:
            return

        Utils.dir_create(path)

        bot = update.message.bot
        user = update.message.from_user.id

        url_pic = bot.getFile(pic[len(pic) - 1].file_id).file_path
        r = requests.get(url_pic, allow_redirects=True)
        server_file_name = url_pic.split('/')[-1]
        _format = _format.replace("%user", str(user))
        _format = _format.replace("%filename", server_file_name)
        file_name = os.path.join(path, _format)
        open(file_name, 'wb').write(r.content)
        return file_name

    def reply_text(self, update: Update, text, markdown=False, reply_markup=None):
        # logging.info(f"reply_text(): {text}")
        if markdown:
            result = update.message.reply_text(text=text,
                                               parse_mode=telegram.ParseMode.MARKDOWN,
                                               reply_markup=reply_markup)
        else:
            result = update.message.reply_text(text=text, reply_markup=reply_markup)
        # logging.warning(f"reply_text() {str(result)}")

    def send_text(self, chat_id: int, text: str, markdown=False):
        if len(text) > 4095:  # telegram max 4096
            self.send_text_as_file(chat_id, text)
            return
        # logging.info(f"send_text({chat_id}, {text})")

        if markdown:
            result = self.bot.sendMessage(chat_id=chat_id, text=text, parse_mode=telegram.ParseMode.MARKDOWN)
        else:
            result = self.bot.sendMessage(chat_id=chat_id, text=text)
        # logging.warning(f"send_text() {str(result)}")

    def send_text_as_file(self, chat_id: int, text: str, file_name=None):
        # logging.info(f"send_text_as_file({chat_id}, {text})")
        if file_name is None:
            now = datetime.datetime.now().strftime("%Y-%m-%dT%H-%M-%S-%f")
            file_name = f'{now}.log'
        file = io.StringIO(text)
        file.name = file_name
        result = self.bot.sendDocument(chat_id, document=file)
        # logging.warning(f"send_text_as_file() {str(result)}")
