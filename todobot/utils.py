from enum import Enum

from telegram import (
    ReplyKeyboardMarkup,
    KeyboardButton,
)


class Actions(Enum):
    DELETE_TASK = 0
    ADD_CATEGORY = 1
    DELETE_CATEGORY = 2


class ChatInfo:
    def __init__(self):
        self.tasks: dict[int, dict[str, list[str]]] = {}
        self.cur_category: dict[int, str] = {}
        self.help_text: list[str] = [
            "/help - get help about the bot\n",
            "/category - select category to record tasks\n",
            "/showall - print all tasks from all categories\n",
            "/show - print tasks from current categories\n",
            "Currently there are 3 buttons on the keyboard:\n",
            "🟢 Add category\n",
            "🔴 Delete task\n",
            "🔴 Delete category",
        ]
        self.actions: ReplyKeyboardMarkup = ReplyKeyboardMarkup(
            [
                [KeyboardButton("📝 Add category ✅")],
                [KeyboardButton("✍🏼 Delete task ❌")],
                [KeyboardButton("📌 Delete category ❌")],
            ],
            resize_keyboard=True,
            one_time_keyboard=True,
        )
        self.checks_buttons: dict[int, list[bool]] = {}


chat = ChatInfo()
