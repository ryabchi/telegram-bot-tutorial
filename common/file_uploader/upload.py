from dataclasses import dataclass
from enum import Enum
from typing import Callable, Optional

from telegram import Bot, Message, error


class ResourceType(str, Enum):
    PICTURE = 'picture'
    GIF = 'gif'
    VIDEO = 'video'
    AUDIO = 'audio'


@dataclass
class Resource:
    """ Struct for file data """

    path: str
    resource_type: ResourceType
    file_id: Optional[str] = None


async def get_upload_method(bot: Bot, resource: Resource) -> Callable:  # type:ignore
    """ Select upload file method depends in file type """
    if resource.resource_type == ResourceType.PICTURE:
        return bot.send_photo
    if resource.resource_type == ResourceType.GIF:
        return bot.send_animation
    if resource.resource_type == ResourceType.AUDIO:
        return bot.send_audio
    if resource.resource_type == ResourceType.VIDEO:
        return bot.send_video
    raise TypeError('Unsupported file type')


async def extract_resources_id(resource: Resource, result: Message) -> str:
    """ Extract file ID from object after file was uploaded """
    if resource.resource_type == ResourceType.PICTURE:
        return result.photo[-1].file_id
    if resource.resource_type == ResourceType.GIF:
        return result.document.file_id
    if resource.resource_type == ResourceType.VIDEO:
        result_obj = (
                result.video or result.animation or result.document or result.video_note
        )
        return result_obj.file_id
    if resource.resource_type == ResourceType.AUDIO:
        return result.audio.file_id
    raise Exception('Unsupported resource')


async def _upload_new(
        bot: Bot, chat_id: int, resource: Resource, text: Optional[str] = None
) -> None:
    """ Upload file from file system """
    if resource.path:
        uploaded_from = open(resource.path, 'rb')
    else:
        raise Exception('Broken resources')
    upload_method = await get_upload_method(bot, resource)
    try:
        result = await upload_method(chat_id, uploaded_from, caption=text)
    except error.BadRequest:
        raise Exception('Not supported media resources')

    resource.file_id = extract_resources_id(resource, result)


async def upload(
        bot: Bot, chat_id: int, resource: Resource, text: Optional[str] = None
) -> Resource:
    """ Upload file to Telegram """
    if resource.file_id:
        upload_method = await get_upload_method(bot, resource)
        try:
            await upload_method(chat_id, resource.file_id, caption=text)
        except error.BadRequest:
            raise Exception('Not supported media resources')
    elif resource.path:
        await _upload_new(bot, chat_id, resource, text)
    else:
        raise Exception('Broken resources')
    return resource
