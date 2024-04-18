import logging
from uuid import uuid4

from telegram import (
    InlineQueryResultArticle,
    InputTextMessageContent,
    Update,
)
from telegram.constants import ParseMode
from telegram.ext import (
    CallbackContext,
    CallbackQueryHandler,
    CommandHandler,
    InlineQueryHandler,
    MessageHandler,
    Application,
)

from templatebot.config import TELEGRAM_BOT_TOKEN

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG
)

logger = logging.getLogger(__name__)


async def start_command_handler(update: Update, _: CallbackContext) -> None:
    """ Send a message when the command /start is issued."""
    await update.message.reply_text('Add your text here')


async def text_handler(update: Update, context: CallbackContext) -> None:
    user_id = update.message.from_user.id
    user_name = update.message.from_user.username

    message_text = update.message.text

    await context.bot.send_message(
        update.message.from_user.id,
        message_text,
    )
    await update.message.reply_text('Some reply')


async def button_handler(update: Update, _: CallbackContext) -> None:
    """ Handle all query when user press buttons that created by this bot """
    query = update.callback_query
    await query.answer()

    await query.edit_message_text(query.data)


async def inline_query_handler(update: Update, _: CallbackContext) -> None:
    """ Handle the inline query. """
    if not update.inline_query.query:
        return

    results = [
        InlineQueryResultArticle(
            id=str(uuid4()),
            title='Do nothing',
            input_message_content=InputTextMessageContent(
                update.inline_query.query, parse_mode=ParseMode.MARKDOWN
            ),
        ),
    ]

    await update.inline_query.answer(results)  # type: ignore


def main() -> None:
    """Start the bot."""
    # Create the Application and pass it your bot's token.
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    application.add_handler(CommandHandler('start', start_command_handler))
    application.add_handler(InlineQueryHandler(inline_query_handler))
    application.add_handler(CallbackQueryHandler(button_handler))

    application.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, text_handler)  # type: ignore
    )

    # Run the bot until the user presses Ctrl-C
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == '__main__':
    main()
