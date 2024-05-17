# Press Ctrl-C on the command line or send a signal to the process to stop the bot.

import logging

from telegram import (
    Update,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
    CallbackContext,
    CallbackQueryHandler,
)

from todobot.config import TELEGRAM_TOKEN
from todobot.utils import chat, Actions


logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logging.getLogger("httpx").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)


async def showall_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    cur_category = chat.cur_category[user_id]

    if chat.tasks[user_id]:
        for categ in chat.tasks[user_id]:
            chat.cur_category[user_id] = categ
            await show_command(update, context)
        chat.cur_category[user_id] = cur_category
    else:
        await update.message.reply_text("There are no categories.")


async def show_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    categ = chat.cur_category[user_id]

    if categ is not None:
        tasks = [
            f"✍🏼 {i + 1}) {task}" for i, task in enumerate(chat.tasks[user_id][categ])
        ]
        tasks = "\n".join(tasks)
        message = f"📝 Category: {categ.upper()}\n List:\n{tasks}"
        await update.message.reply_text(message)
    else:
        await update.message.reply_text("Run /category to choose current category.")


async def category_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    if chat.tasks[user_id]:
        keyboards = [
            [InlineKeyboardButton(categ.upper(), callback_data=categ)]
            for categ in chat.tasks[user_id]
        ]
        inline_keyboard = InlineKeyboardMarkup(keyboards)
        await context.bot.send_message(
            update.message.chat.id,
            "Choose category from list:",
            reply_markup=inline_keyboard,
            disable_web_page_preview=True,
        )
    else:
        await update.message.reply_text(f"There are no categories yet.")


async def inline_handler(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    user_id = update.effective_user.id
    categ = chat.cur_category[user_id]
    await query.answer()

    if chat.checks_buttons[user_id][Actions.DELETE_TASK.value]:
        chat.checks_buttons[user_id][Actions.DELETE_TASK.value] = False
        chat.tasks[user_id][categ].pop(int(query.data))
        await query.edit_message_text(f"Task {int(query.data) + 1} deleted successfully! ✅")

    elif chat.checks_buttons[user_id][Actions.DELETE_CATEGORY.value]:
        chat.checks_buttons[user_id][Actions.DELETE_CATEGORY.value] = False
        chat.tasks[user_id].pop(query.data)
        await query.edit_message_text(
            f"Category {query.data.upper()} deleted successfully! ✅"
        )

        if not chat.tasks[user_id] or categ == query.data:
            chat.cur_category[user_id] = None
            await context.bot.send_message(
                query.message.chat.id, text="Run /category to choose current category."
            )

    else:
        chat.cur_category[user_id] = query.data
        await query.edit_message_text(f"📝 Current category: {query.data.upper()}.")


async def keyboard_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message = update.message.text
    user_id = update.effective_user.id
    categ = chat.cur_category[user_id]

    if message == "📝 Add category ✅":
        chat.checks_buttons[user_id][Actions.DELETE_TASK.value] = False
        chat.checks_buttons[user_id][Actions.ADD_CATEGORY.value] = True
        chat.checks_buttons[user_id][Actions.DELETE_CATEGORY.value] = False
        await update.message.reply_text("Enter new category:")

    elif message == "✍🏼 Delete task ❌":
        chat.checks_buttons[user_id][Actions.DELETE_CATEGORY.value] = False
        chat.checks_buttons[user_id][Actions.ADD_CATEGORY.value] = False
        if categ is not None and chat.tasks[user_id][categ]:
            keyboards = [
                [InlineKeyboardButton(task, callback_data=str(i))]
                for i, task in enumerate(chat.tasks[user_id][categ])
            ]
            inline_keyboard = InlineKeyboardMarkup(keyboards)
            chat.checks_buttons[user_id][Actions.DELETE_TASK.value] = True
            await context.bot.send_message(
                update.message.chat.id,
                "Choose task to delete from list below:",
                reply_markup=inline_keyboard,
                disable_web_page_preview=True,
            )
        elif categ is None:
            await update.message.reply_text("Run /category to choose current category.")
        else:
            await update.message.reply_text(
                f"There are no tasks in category {categ.upper()}."
            )

    elif message == "📌 Delete category ❌":
        chat.checks_buttons[user_id][Actions.DELETE_TASK.value] = False
        chat.checks_buttons[user_id][Actions.ADD_CATEGORY.value] = False
        if chat.tasks[user_id]:
            categories = chat.tasks[user_id].keys()
            keyboards = [
                [InlineKeyboardButton(categ, callback_data=categ)]
                for categ in categories
            ]
            inline_keyboard = InlineKeyboardMarkup(keyboards)
            chat.checks_buttons[user_id][Actions.DELETE_CATEGORY.value] = True
            await context.bot.send_message(
                update.message.chat.id,
                "Choose category to delete from list below:",
                reply_markup=inline_keyboard,
                disable_web_page_preview=True,
            )
        else:
            await update.message.reply_text("There are no categories.")


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    user_id = update.effective_user.id
    chat.tasks[user_id] = {}
    chat.cur_category[user_id] = None
    chat.checks_buttons[user_id] = [False, False, False]
    await context.bot.send_message(
        update.message.chat.id,
        f"Hello, my friend, {update.effective_user.first_name}! 🙍‍♂️🖐",
        reply_markup=chat.actions,
        disable_web_page_preview=True,
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /help is issued."""
    await update.message.reply_text(
        f"I'm todo bot 😃 and I can do next actions:\n {''.join(chat.help_text)}"
    )


async def text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    message = update.message.text
    categ = chat.cur_category[user_id]

    if chat.checks_buttons[user_id][Actions.ADD_CATEGORY.value]:
        chat.tasks[user_id][message] = []
        chat.checks_buttons[user_id][Actions.ADD_CATEGORY.value] = False
        chat.cur_category[user_id] = message
        await update.message.reply_text("Category added successfully! ✅")
        await update.message.reply_text(f"📝 Current category: {message.upper()}")

    elif categ is not None:
        chat.tasks[user_id].setdefault(categ, []).append(message)
        await update.message.reply_text("Task added successfully! ✅")
    else:
        await update.message.reply_text("Run /category to choose current category.")


def main() -> None:
    """Start the bot."""
    # Create the Application and pass it your bot's token.
    application = Application.builder().token(TELEGRAM_TOKEN).build()

    # on different commands - answer in Telegram
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("category", category_command))
    application.add_handler(CommandHandler("show", show_command))
    application.add_handler(CommandHandler("showall", showall_command))
    application.add_handler(CallbackQueryHandler(inline_handler))

    # on non command i.e message - echo the message on Telegram
    application.add_handler(
        MessageHandler(
            filters.TEXT
            & (
                filters.Text("📝 Add category ✅")
                | filters.Text("✍🏼 Delete task ❌")
                | filters.Text("📌 Delete category ❌")
            ),
            keyboard_handler,
        )
    )
    application.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, text_handler)
    )

    # Run the bot until the user presses Ctrl-C
    application.run_polling(allowed_updates=Update.ALL_TYPES)
