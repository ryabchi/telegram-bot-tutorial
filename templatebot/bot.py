import logging
from uuid import uuid4

from telegram import (
    InlineQueryResultArticle,
    InputTextMessageContent,
    ParseMode,
    Update,
)
from telegram.ext import (
    CallbackContext,
    CallbackQueryHandler,
    CommandHandler,
    InlineQueryHandler,
    Updater,
)

from templatebot.config import TELEGRAM_BOT_TOKEN

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG
)

logger = logging.getLogger(__name__)


def start_command_handler(update: Update, _: CallbackContext) -> None:
    """ Send a message when the command /start is issued."""
    update.message.reply_text('Add your text here')


def button_handler(update: Update, _: CallbackContext) -> None:
    """ Handle all query when user press buttons that created by this bot """
    query = update.callback_query
    query.answer()

    query.edit_message_text(query.data)


def inline_query_handler(update: Update, _: CallbackContext) -> None:
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

    update.inline_query.answer(results)  # type: ignore


def main() -> None:
    # Create the Updater and pass it your bot's token.
    updater = Updater(TELEGRAM_BOT_TOKEN)  # type: ignore

    dispatcher = updater.dispatcher  # type: ignore

    dispatcher.add_handler(CommandHandler('start', start_command_handler))
    dispatcher.add_handler(InlineQueryHandler(inline_query_handler))
    dispatcher.add_handler(CallbackQueryHandler(button_handler))

    # Start the Bot
    updater.start_polling()

    # Run the bot until the user presses Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT
    updater.idle()


if __name__ == '__main__':
    main()
