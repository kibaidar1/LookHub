import logging
import os
import tempfile
from pathlib import Path
from urllib.parse import urlparse, urlunparse

import aiohttp

from src.config import UPLOAD_FILES_DIR


def _fix_localhost_url(url: str) -> str:
    """
    Заменяет localhost или 127.0.0.1 на nginx:80.
    """
    parsed = urlparse(url)

    # проверяем host
    if parsed.hostname in ("localhost", "127.0.0.1"):
        # заменяем на nginx:80
        new_netloc = "nginx:80"
        parsed = parsed._replace(netloc=new_netloc)

    return str(urlunparse(parsed))


async def get_image_from_url(image_url: str) -> bytes:
    async with aiohttp.ClientSession() as session:
        url = _fix_localhost_url(image_url)
        async with session.get(url, ssl=False) as response:
            response.raise_for_status()
            return await response.read()


def create_temporary_file(file: bytes, suffix=".jpg") -> Path:
    tmp_file = tempfile.NamedTemporaryFile(delete=False, suffix=suffix, dir=UPLOAD_FILES_DIR)
    tmp_file.write(file)
    return Path(tmp_file.name)


def delete_temporary_file(tmp_file_path: Path):
    try:
        os.unlink(tmp_file_path)
    except FileNotFoundError:
        pass


