# !/usr/bin/env python
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

from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)
from todobot.config import TELEGRAM_TOKEN


TASKS: dict[int, list[str]] = dict()

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
    await update.message.reply_text("Hello, my friend!")
    await update.message.reply_text("I'm todo bot and I can add tasks to your list! 😃")


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /help is issued."""
    await update.message.reply_text("Help!")


async def add_task(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Add new task using /add command."""
    user = update.effective_user
    task_description = ' '.join(context.args)
    if task_description:
        TASKS.setdefault(user.id, []).append(task_description)
        tasks = '\n'.join(TASKS[user.id])
        message = f"Task added to list. All list:\n{tasks}"
        await update.message.reply_text(message)
    else:
        await update.message.reply_text("Please provide a task description.")

async def remove_task(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Remove a task using /remove command."""
    user = update.effective_user
    args = context.args
    if not args:
        await update.message.reply_text("Please provide a task description or a task index.")
        return

    # Check if the argument is a task description or a task index
    try:
        task_index = int(args[0]) - 1
        tasks = TASKS.get(user.id, [])
        if 0 <= task_index < len(tasks):
            removed_task = tasks.pop(task_index)
            await update.message.reply_text(f"Removed task: {removed_task}")
        else:
            await update.message.reply_text("Invalid task index.")
    except ValueError:
        task_description = ' '.join(args)
        tasks = TASKS.get(user.id, [])
        if task_description in tasks:
            tasks.remove(task_description)
            await update.message.reply_text(f"Removed task: {task_description}")
        else:
            await update.message.reply_text("Task not found.")

async def view_tasks(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """View all tasks in the user's list."""
    user = update.effective_user
    tasks = TASKS.get(user.id, [])
    if tasks:
        tasks_message = '\n'.join(tasks)
        await update.message.reply_text(f"Your tasks:\n{tasks_message}")
    else:
        await update.message.reply_text("You have no tasks.")

def main() -> None:
    """Start the bot."""
    # Create the Application and pass it your bot's token.
    application = Application.builder().token(TELEGRAM_TOKEN).build()

    # on different commands - answer in Telegram
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("add", add_task))
    application.add_handler(CommandHandler("remove", remove_task))
    application.add_handler(CommandHandler("view", view_tasks))

    # on non command i.e message - echo the message on Telegram
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, add_task))

    # Run the bot until the user presses Ctrl-C
    application.run_polling(allowed_updates=Update.ALL_TYPES)