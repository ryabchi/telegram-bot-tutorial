import logging
from typing import List
from uuid import uuid4

from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
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

from likebot.config import TELEGRAM_BOT_TOKEN
from likebot.database import like_db

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG
)

logger = logging.getLogger(__name__)


def get_keyboard(like: str = '👍', dislike: str = '👎') -> InlineKeyboardMarkup:
    """ Create InlineKeyboardMarkup for adding as reaction to post  """
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(like, callback_data='like'),
                InlineKeyboardButton(dislike, callback_data='dislike'),
            ],
        ]
    )


def start_command_handler(update: Update, _: CallbackContext) -> None:
    """ Send a message when the command /start is issued."""
    update.message.reply_text(
        'Hi! I\'m inline bot for adding reactions to your post. '
        'Use me in channel in inline mode!'
    )


def button_handler(update: Update, _: CallbackContext) -> None:
    """ Handle all query when user press buttons that created by this bot """
    query = update.callback_query

    # CallbackQueries need to be answered, even if no notification to the user is needed
    # Some clients may have trouble otherwise. See https://core.telegram.org/bots/api#callbackquery
    query.answer()

    # add user reaction to database
    like_db.add_reaction(query.inline_message_id, query.from_user.id, query.data)

    # get data for reply keyboard from db
    like = f"👍 {like_db.get_count(query.inline_message_id, 'like')}"
    dislike = f"👎 {like_db.get_count(query.inline_message_id, 'dislike')}"

    # edit only keyboard that attached to message
    query.edit_message_reply_markup(reply_markup=get_keyboard(like, dislike))


def inline_query_handler(update: Update, _: CallbackContext) -> None:
    """ Handle the inline query. """
    if not update.inline_query.query:
        return

    results: List[InlineQueryResultArticle] = [
        InlineQueryResultArticle(
            id=str(uuid4()),
            title='Add reactions to post',
            reply_markup=get_keyboard(),  # add default keyboard with reation
            input_message_content=InputTextMessageContent(
                update.inline_query.query, parse_mode=ParseMode.MARKDOWN
            ),
        ),
    ]  # struct for show bot menu in telegram

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
