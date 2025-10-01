import re
import logging
from pathlib import Path

from instagrapi import Client

from src.config import UPLOAD_FILES_DIR
from src.entities.looks import LookRead
from src.interfaces import ServiceInterface
from src.services.utils import get_image_from_url, create_temporary_file, delete_temporary_file

logger = logging.getLogger(__name__)


class InstagramService(ServiceInterface):
    """
    Service for posting content to Instagram.
    """
    def __init__(self, login: str, password: str):
        """
        Initialize the InstagramService with login credentials.

        Args:
            login (str): Instagram login username.
            password (str): Instagram login password.
        """
        self.client = Client()
        self.login = login
        self.password = password
        self.session_path: str = "session.json"

    @staticmethod
    async def _create_media(look: LookRead) -> tuple:
        """
        Prepare media and caption for Instagram post from LookRead.

        Args:
            look (LookRead): The look object containing images and description.

        Returns:
            dict: Dictionary with 'path' (list of image file paths) and 'caption' (str).
        """
        photos_paths = []
        for image_url in look.image_urls:
            image_bytes = await get_image_from_url(image_url)
            image_file = create_temporary_file(image_bytes, suffix=".jpg")
            photos_paths.append(image_file)

        description = re.sub(r"\<[^>]*\>", "", look.description)
        caption = f"{look.name}\n\n{description}"
        return photos_paths, caption

    def login_to_instagram(self):
        self.client.login(self.login, self.password)

    async def send_new_post(self, look: LookRead):
        """
        Publish a new post to Instagram based on LookRead.

        Args:
            look (LookRead): The look object to post.
        """
        file_paths, caption = await self._create_media(look)

        async def post(file_paths, caption):
            if len(file_paths) == 1:
                return self.client.photo_upload(file_paths[0], caption=caption)
            else:
                return self.client.album_upload(file_paths, caption=caption)

        try:
            # пробуем постить сразу (если сессия сохранена и рабочая)
            self.login_to_instagram()
            if Path(self.session_path).exists():
                self.client.load_settings(self.session_path)
            media = await post(file_paths, caption)
            logger.info(f"Attempting to send new post for look: {look.name}")
        except Exception as e:
            # если не получилось (нужно логиниться) → входим и пробуем ещё раз
            logger.error(f"Failed to send new post for look {look.name}: {e}")
            self.client.set_settings({})
            self.login_to_instagram()
            self.client.dump_settings(self.session_path)
            media = await post(file_paths, caption)

        for path in file_paths:
            delete_temporary_file(path)

