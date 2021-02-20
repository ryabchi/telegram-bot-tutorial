import logging

from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ParseMode,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
    Update,
)
from telegram.ext import (
    CallbackContext,
    CallbackQueryHandler,
    CommandHandler,
    Dispatcher,
    Filters,
    MessageHandler,
    Updater,
)

from showroombot.config import TELEGRAM_BOT_TOKEN
from showroombot.file_processor import process_file_command, send_botfather_command
from showroombot.text import (
    command_tutorial_text,
    file_text,
    get_keyboard_text_handler,
    get_start_text,
    help_text,
    inline_text,
    keyboard_text,
)

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG
)

logger = logging.getLogger(__name__)

BUTTON_SEND_TEXT_TO_CHAT = 'Отправить текст с кнопки в чат'


def start(update: Update, _: CallbackContext) -> None:
    name = update.message.from_user.first_name
    if not name:
        name = 'Anonymous user'
    update.message.reply_text(get_start_text(name), reply_markup=ReplyKeyboardRemove())


def command_tutorial_handler(update: Update, context: CallbackContext) -> None:
    update.message.reply_text(command_tutorial_text, reply_markup=ReplyKeyboardRemove())
    send_botfather_command(context.bot, update.message.chat_id)


def help_command(update: Update, _: CallbackContext) -> None:
    update.message.reply_text(help_text)


def keyboard_command(update: Update, context: CallbackContext) -> None:
    keyboard = ReplyKeyboardMarkup(
        [
            [KeyboardButton(BUTTON_SEND_TEXT_TO_CHAT)],
            [KeyboardButton('Можно со смайликами 😍')],
            [KeyboardButton('Запросить номер телефона', request_contact=True)],
            [KeyboardButton('Запросить местоположение', request_location=True)],
        ],
        resize_keyboard=True,
        one_time_keyboard=True,
    )

    context.bot.send_message(
        update.message.chat_id,
        keyboard_text,
        reply_markup=keyboard,
        parse_mode=ParseMode.MARKDOWN,
        disable_web_page_preview=True,
    )


def inline_keyboard_command(update: Update, context: CallbackContext) -> None:
    keyboard = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton('👍', callback_data='like'),
                InlineKeyboardButton('👎', callback_data='dislike'),
            ],
            [InlineKeyboardButton('Нажми чтобы изменить', callback_data='edit')],
        ]
    )

    context.bot.send_message(
        update.message.chat_id,
        inline_text,
        reply_markup=keyboard,
        parse_mode=ParseMode.MARKDOWN,
        disable_web_page_preview=True,
    )


def keyboard_text_handler(update: Update, _: CallbackContext) -> None:
    update.message.reply_text(get_keyboard_text_handler(BUTTON_SEND_TEXT_TO_CHAT))


def inline_handler(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    query.answer()

    if query.data == 'edit':
        text = (
            'При нажатии на кнопку, можно менять содержимое сообщения, '
            'к которому она была прикреплена'
        )
        query.edit_message_text(text)
    if query.data in ('upload_png', 'upload_video', 'upload_audio'):
        process_file_command(
            context.bot, update.callback_query.message.chat_id, query.data
        )
    else:
        context.bot.send_message(
            query.message.chat_id,
            text=f'Selected option: {query.data}',
            parse_mode=ParseMode.MARKDOWN,
        )


def file_command(update: Update, context: CallbackContext) -> None:
    keyboard = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    'Прислать изображение', callback_data='upload_png'
                ),
            ],
            [
                InlineKeyboardButton('Прислать видео', callback_data='upload_video'),
            ],
            [
                InlineKeyboardButton('Прислать mp3', callback_data='upload_audio'),
            ],
        ]
    )

    context.bot.send_message(
        update.message.chat_id,
        file_text,
        reply_markup=keyboard,
        parse_mode=ParseMode.MARKDOWN,
        disable_web_page_preview=True,
    )


def text_handler(update: Update, _: CallbackContext) -> None:
    update.message.reply_text("Введите команду /start чтобы вернуться в основное меню.")


def main() -> None:
    """Start the bot."""
    updater = Updater(TELEGRAM_BOT_TOKEN)  # type: ignore

    dispatcher: Dispatcher = updater.dispatcher  # type: ignore

    dispatcher.add_handler(CommandHandler('start', start))
    dispatcher.add_handler(CommandHandler('help', help_command))
    dispatcher.add_handler(CommandHandler('keyboard', keyboard_command))
    dispatcher.add_handler(CommandHandler('command', command_tutorial_handler))
    dispatcher.add_handler(CommandHandler('inlinekeyboard', inline_keyboard_command))
    dispatcher.add_handler(CommandHandler('file', file_command))
    dispatcher.add_handler(CallbackQueryHandler(inline_handler))

    dispatcher.add_handler(
        MessageHandler(
            Filters.text & Filters.text(BUTTON_SEND_TEXT_TO_CHAT),  # type: ignore
            keyboard_text_handler,
        )
    )
    dispatcher.add_handler(
        MessageHandler(Filters.text & ~Filters.command, text_handler)  # type: ignore
    )
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
