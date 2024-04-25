import logging
from telegram import ForceReply, Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters
from toDoBot.config import TELEGRAM_BOT_TOKEN

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
    user = update.effective_user
    await update.message.reply_html(
        rf"Hi {user.mention_html()}!",
        reply_markup=ForceReply(selective=True),
    )
    await update.message.reply_text('Привет я toDoBot, здесь ты можешь добавлять задачи и отмечать их.)')
    await context.bot.send_poll(user.id, 'Какой сегодня год', ['2024', '2023', '2022'])


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /help is issued."""
    await update.message.reply_text("Help!")


async def text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    tesk = update.message.text
    if not TASKS.get(user.id):
        TASKS[user.id] = []
    TASKS[user.id].append(tesk)
    
    message = 'Задача была добавлена\n'
    message = f'{message}Список задач: '
    tasks_list = '\n'.join(TASKS[user.id])
    message = f'{message} {tasks_list}'
    await update.message.reply_text(message)


def main() -> None:
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))

    # on non command i.e message - echo the message on Telegram
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_handler))

    # Run the bot until the user presses Ctrl-C
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
