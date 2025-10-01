import uuid
import os
from app.config import UPLOAD_IMAGES_DIR

from PIL.Image import Image


async def save_image(image: Image, filename: str) -> str:
    """Save an image to the upload directory with a unique filename.

    Args:
        image (Image): PIL Image object to save
        filename (str): Base filename to use (will be combined with UUID)

    Returns:
        str: The generated filename of the saved image
    """
    image_name = f"{filename}-{uuid.uuid4()}.png"
    image.save(UPLOAD_IMAGES_DIR / image_name)
    return image_name


async def delete_image(image_name: str) -> bool:
    """Delete an image file from the upload directory.

    Args:
        image_name (str): Name of the image file to delete

    Returns:
        bool: True if deletion was successful, False otherwise
    """
    try:
        image_path = UPLOAD_IMAGES_DIR / image_name
        if image_path.exists():
            os.remove(image_path)
            return True
    except Exception as e:
        print(f"Error deleting image {image_name}: {e}")
    return False
