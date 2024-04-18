import logging

from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
    Update,
)
from telegram.constants import ParseMode
from telegram.ext import (
    CallbackContext,
    CallbackQueryHandler,
    CommandHandler,
    filters,
    MessageHandler,
    Application,
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


async def start(update: Update, _: CallbackContext) -> None:
    name = update.message.from_user.first_name
    if not name:
        name = 'Anonymous user'
    await update.message.reply_text(get_start_text(name), reply_markup=ReplyKeyboardRemove())


async def command_tutorial_handler(update: Update, context: CallbackContext) -> None:
    await update.message.reply_text(command_tutorial_text, reply_markup=ReplyKeyboardRemove())
    await send_botfather_command(context.bot, update.message.chat.id)


async def help_command(update: Update, _: CallbackContext) -> None:
    await update.message.reply_text(help_text)


async def keyboard_command(update: Update, context: CallbackContext) -> None:
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

    await context.bot.send_message(
        update.message.chat.id,
        keyboard_text,
        reply_markup=keyboard,
        parse_mode=ParseMode.MARKDOWN,
        disable_web_page_preview=True,
    )


async def inline_keyboard_command(update: Update, context: CallbackContext) -> None:
    keyboard = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton('👍', callback_data='like'),
                InlineKeyboardButton('👎', callback_data='dislike'),
            ],
            [InlineKeyboardButton('Нажми чтобы изменить', callback_data='edit')],
        ]
    )

    await context.bot.send_message(
        update.message.chat.id,
        inline_text,
        reply_markup=keyboard,
        parse_mode=ParseMode.MARKDOWN,
        disable_web_page_preview=True,
    )


async def keyboard_text_handler(update: Update, _: CallbackContext) -> None:
    await update.message.reply_text(get_keyboard_text_handler(BUTTON_SEND_TEXT_TO_CHAT))


async def inline_handler(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    await query.answer()

    if query.data == 'edit':
        text = (
            'При нажатии на кнопку, можно менять содержимое сообщения, '
            'к которому она была прикреплена'
        )
        await query.edit_message_text(text)
    if query.data in ('upload_png', 'upload_video', 'upload_audio'):
        await process_file_command(
            context.bot, update.callback_query.message.chat.id, query.data
        )
    else:
        await context.bot.send_message(
            query.message.chat.id,
            text=f'Selected option: {query.data}',
            parse_mode=ParseMode.MARKDOWN,
        )


async def file_command(update: Update, context: CallbackContext) -> None:
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

    await context.bot.send_message(
        update.message.chat.id,
        file_text,
        reply_markup=keyboard,
        parse_mode=ParseMode.MARKDOWN,
        disable_web_page_preview=True,
    )


async def text_handler(update: Update, _: CallbackContext) -> None:
    await update.message.reply_text("Введите команду /start чтобы вернуться в основное меню.")


def main() -> None:
    """Start the bot."""
    # Create the Application and pass it your bot's token.
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    # on different commands - answer in Telegram

    application.add_handler(CommandHandler('start', start))
    application.add_handler(CommandHandler('help', help_command))
    application.add_handler(CommandHandler('keyboard', keyboard_command))
    application.add_handler(CommandHandler('command', command_tutorial_handler))
    application.add_handler(CommandHandler('inlinekeyboard', inline_keyboard_command))
    application.add_handler(CommandHandler('file', file_command))
    application.add_handler(CallbackQueryHandler(inline_handler))

    application.add_handler(
        MessageHandler(
            filters.TEXT & filters.Text(BUTTON_SEND_TEXT_TO_CHAT),  # type: ignore
            keyboard_text_handler,
        )
    )
    application.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, text_handler)  # type: ignore
    )

    # Run the bot until the user presses Ctrl-C
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == '__main__':
    main()
