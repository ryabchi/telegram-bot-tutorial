import pathlib
from typing import Dict

from telegram import Bot

from common.file_uploader import Resource, ResourceType, upload

FILE_STORAGE: Dict[str, Resource] = {}


async def process_file_command(bot: Bot, chat_id: int, command: str) -> None:
    resource = FILE_STORAGE.get(command)
    if resource:
        text = f'Файл уже загружен, отправляем используя file_id:\n {resource.file_id}'
    else:
        text = 'Загружаем новый файл'
        directory = pathlib.Path(__file__).parent.absolute()
        if command == 'upload_png':
            resource = Resource(
                path=f'{directory}/file_example/logo.png',
                resource_type=ResourceType.PICTURE,
            )
        elif command == 'upload_video':
            resource = Resource(
                path=f'{directory}/file_example/iron_man.mp4',
                resource_type=ResourceType.VIDEO,
            )
        elif command == 'upload_audio':
            resource = Resource(
                path=f'{directory}/file_example/audio.mp3',
                resource_type=ResourceType.AUDIO,
            )
        else:
            raise Exception('Unexpected command')

    await upload(bot, chat_id, resource, text)
    FILE_STORAGE[command] = resource


async def send_botfather_command(bot: Bot, chat_id: int) -> None:
    directory = pathlib.Path(__file__).parent.absolute()
    resource = Resource(
        path=f'{directory}/file_example/botfather_commands.jpg',
        resource_type=ResourceType.PICTURE,
    )
    await upload(bot, chat_id, resource)
