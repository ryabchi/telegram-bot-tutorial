import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from config import TELEGRAM_BOT_TOKEN

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

logger = logging.getLogger(__name__)

tasks = {}


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "Я ToDo бот. Используй команды /add, /delete, /list и /help для управления задачами.")


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("Используй команды /add <task>, /delete <task> и /list для управления задачами.")
    await update.message.reply_text("/add <Категория> <task> - добавить новую задачу.")
    await update.message.reply_text("/delete <Категория> <task> - удалить задачу по названию.")
    await update.message.reply_text("/list - вывести список задач.")
    await update.message.reply_text("/help - инструкция к боту.")

async def add(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.message.from_user.id
    if len(context.args) < 2:
        await update.message.reply_text("Укажите категорию и задачу после команды /add.")
        return

    category, task = context.args[0], ' '.join(context.args[1:])
    if user_id not in tasks:
        tasks[user_id] = {}

    if category not in tasks[user_id]:
        tasks[user_id][category] = []
    if task in tasks[user_id][category]:
        await update.message.reply_text(f"Задача '{task}' уже добавлена в категории '{category}'.")
        return
    tasks[user_id][category].append(task)
    await update.message.reply_text(f"Задача '{task}' добавлена в категорию '{category}'.")


async def delete(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.message.from_user.id
    if len(context.args) < 2:
        await update.message.reply_text("Пожалуйста, укажите категорию и задачу после команды /delete.")
        return

    category, task = context.args[0], ' '.join(context.args[1:])
    if user_id not in tasks or category not in tasks[user_id]:
        await update.message.reply_text(
            "Неверная категория или ошибка пользователя. Доступные категории: " + ', '.join(
                tasks[user_id].keys()) + ".")
        return

    if task not in tasks[user_id][category]:
        await update.message.reply_text(f"Задача '{task}' не найдена в категории '{category}'.")
        return

    tasks[user_id][category].remove(task)
    await update.message.reply_text(f"Задача '{task}' удалена из категории '{category}'.")

    if not tasks[user_id][category]:
        del tasks[user_id][category]


async def list_(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.message.from_user.id
    if user_id not in tasks:
        tasks[user_id] = {}

    if not tasks[user_id]:
        await update.message.reply_text("На данный момент нет текущих задач")
        return

    message = ""
    for category in tasks[user_id]:
        if tasks[user_id][category]:
            task_list = "\n".join(tasks[user_id][category])
            message += f"Категория '{category}':\n{task_list}\n"
        else:
            message += f"Категория '{category}':\nНет задач\n"

    await update.message.reply_text(message.strip())


def main() -> None:
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("add", add))
    application.add_handler(CommandHandler("delete", delete))
    application.add_handler(CommandHandler("list", list_))

    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
