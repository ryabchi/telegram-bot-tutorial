#!/usr/bin/env python
# pylint: disable=unused-argument
# This program is dedicated to the public domain under the CC0 license.

"""
Simple Bot to reply to Telegram messages.

First, a few handler functions are defined. Then, those functions are passed to
the Application and registered at their respective places.
Then, the bot is started and runs until we press Ctrl-C on the command line.

Usage:
Basic Echobot example, repeats messages.
Press Ctrl-C on the command line or send a signal to the process to stop the
bot.
"""

import logging

from telegram import ForceReply, Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters

from todobot.config import TELEGRAM_TOKEN

TASKS= dict()
commands = {'/help' : 'view commands','/start':'hi)',
            '/add_action':'add action in todo list','/review_actions':' view actions from todo list'}

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
# set higher logging level for httpx to avoid all GET and POST requests being logged
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)


# Define a few command handlers. These usually take the two arguments update and
# context.
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    user = update.effective_user
    await update.message.reply_text(
        rf"Hello homie {user.name}!"
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /help is issued."""
    await update.message.reply_text("Help!")
    for command,description in commands.items():
        await update.message.reply_text(f'{command} - {description}')


async def add_action_to_list(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    await update.message.reply_text("Пожалуйста, отправьте текст задачи после команды /add_action.")
    context.chat_data["waiting_for_task"] = True

async def get_next_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if "waiting_for_task" in context.chat_data and context.chat_data["waiting_for_task"]:
        user = update.effective_user
        next_message = update.message.text
        if user.id not in TASKS or not TASKS[user.id]:
            TASKS[user.id] = []
        TASKS[user.id].append(next_message)
        del context.chat_data["waiting_for_task"]
        await update.message.reply_text("Задача добавлена.")
    else:
        pass



async def return_actions_from_list(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    if user.id not in TASKS or not TASKS[user.id]:
        message='У вас нет задач'
        await update.message.reply_text(message)
    else:
        message='Список задач:\n\n'
        tasks_list='\n'.join(TASKS[user.id])
        message=f'{message}{tasks_list}'
        await update.message.reply_text(message)


async def text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(update.message.text)


def main() -> None:
    """Start the bot."""
    # Create the Application and pass it your bot's token.
    application = Application.builder().token(TELEGRAM_TOKEN).build()

    # on different commands - answer in Telegram
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("add_action", add_action_to_list))
    application.add_handler(CommandHandler("review_actions", return_actions_from_list))


    # on non command i.e message - echo the message on Telegram
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, get_next_message))

    # Run the bot until the user presses Ctrl-C
    application.run_polling(allowed_updates=Update.ALL_TYPES)