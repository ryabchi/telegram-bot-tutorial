import logging
from uuid import uuid4
import os

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
    file_name = f'data/{str(update.message.from_user.id)}.txt'
    if not os.path.exists(file_name):
        f = open(file_name, 'w')
        f.close()
    update.message.reply_text(f'Hello, {update.message.from_user.name}!\nNow you can count your money!')
    update.message.reply_text('Send me a message like this:\n/add {number} {topic}\n/add 100 products')


def add_transaction(update: Update, _:CallbackContext) -> None:
    if not os.path.exists(f'data/{str(update.message.from_user.id)}.txt'):
        update.message.reply_text('To start, you should send me "/start"')
    else:
        with open(f'data/{str(update.message.from_user.id)}.txt', 'a') as f:
            tmp = tuple(update.message.text.split())
            if len(tmp) != 3 or not tmp[1].isdigit():
                update.message.reply_text('Wrong input\nTry to send something like this'
                                          '/add {number} {topic}\n/add 100 products')
            else:
                transaction = f'{tmp[1]} {tmp[2]} {update.message.date}\n'
                f.write(transaction)
                update.message.reply_text(f'Transaction has created!\n{transaction}')


def total(update: Update, _: CallbackContext) -> None:
    if not os.path.exists(f'data/{str(update.message.from_user.id)}.txt'):
        update.message.reply_text('To start, you should send me "/start"')
    else:
        with open(f'data/{str(update.message.from_user.id)}.txt', 'r') as f:
            d = {}
            global_money = 0
            for line in f.readlines():
                tmp = line.split()
                # print(tmp)
                try:
                    d[tmp[1]] += int(tmp[0])
                except KeyError:
                    d[tmp[1]] = int(tmp[0])
                global_money += int(tmp[0])
        answer = f'Global: {global_money} rub\n'
        for key in d.keys():
            answer += f'{key}: {d[key]}\n'
        update.message.reply_text(answer)


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
    dispatcher.add_handler(CommandHandler('add', add_transaction))
    dispatcher.add_handler(CommandHandler('total', total))

    dispatcher.add_handler(InlineQueryHandler(inline_query_handler))
    dispatcher.add_handler(CallbackQueryHandler(button_handler))

    # Start the Bot
    updater.start_polling()

    # Run the bot until the user presses Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT
    updater.idle()


if __name__ == '__main__':
    main()
