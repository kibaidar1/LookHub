import re
import logging
from io import BytesIO

from aiogram import Bot
from aiogram.types import InputMediaPhoto, InputFile, BufferedInputFile

from src.entities.looks import LookRead
from src.interfaces import ServiceInterface
from src.services.utils import get_image_from_url, create_temporary_file

logger = logging.getLogger(__name__)


class TelegramService(ServiceInterface):
    """
    Service for posting content to Telegram.
    """
    def __init__(self, token: str, chanel_id: str):
        """
        Initialize the TelegramService with bot token and channel ID.

        Args:
            token (str): Telegram bot token.
            chanel_id (str): Telegram channel ID.
        """
        self.bot = Bot(token=token)
        self.chanel_id = chanel_id

    @staticmethod
    async def _create_media(look: LookRead) -> list[InputMediaPhoto]:
        """
        Create a formatted media group for a look post.

        Formats the look information into a Telegram post with:
        - Formatted name and description
        - Categorized list of clothes with links
        - Associated images

        Args:
            look (LookRead): The look to create a post for.

        Returns:
            list[InputMediaPhoto]: List of formatted media items for the post.

        Raises:
            ValueError: If the look has no image URLs.
        """
        name = f"<strong><em>{look.name}</em></strong>"
        description = re.sub(r"\<[^>]*\>", "", look.description)
        categories_and_clothes = []
        for category in look.clothes_categories:
            clothes = list(
                map(
                    lambda cloth: f'<a href="{cloth.image_url}">   -{cloth.name}</a>',
                    category.clothes,
                )
            )
            clothes = "\n".join(clothes)
            categories_and_clothes.append(
                f"<b><i>{category.name}:</i></b>\n{clothes}"
            )
        clothes = "\n\n".join(categories_and_clothes)
        caption = f"{name}\n\n{clothes}\n\n{description}"
        if not look.image_urls:
            raise ValueError("Look without image urls is not supported")
        input_media_photo_array = []
        for i, image_url in enumerate(look.image_urls):
            image_bytes = await get_image_from_url(image_url)
            input_file = BufferedInputFile(image_bytes, filename=look.name + str(i))
            input_media_photo_array.append(InputMediaPhoto(media=input_file))
        input_media_photo_array[0].parse_mode = "HTML"
        input_media_photo_array[0].caption = caption
        return input_media_photo_array

    async def send_new_post(self, look: LookRead):
        """
        Publish a new post to Telegram based on LookRead.

        Args:
            look (LookRead): The look object to post.
        """
        media = await self._create_media(look)
        await self.bot.send_media_group(
            self.chanel_id, media=media
        )
        await self.bot.session.close()

