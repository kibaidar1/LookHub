from pydantic import BaseModel, ConfigDict, field_validator
from typing_extensions import Any

from src.entities.categories import ClothesCategory, ClothesCategoryCreate, ClothesCategoryRead
from src.entities.enums import GenderEnum


class Look(BaseModel):
    """Base model for fashion looks/outfits.
    
    Represents a complete fashion look with associated clothing categories and images.
    
    Attributes:
        name (str): The name of the look
        gender (GenderEnum): Target gender for the look
        description (str): Description of the look
        clothes_categories (list[ClothesCategory]): List of clothing categories in the look
        image_prompts (list[str]): List of prompts used to generate images
        image_urls (list[str]): List of URLs to the look's images
        content_json (str | None): Optional JSON content for the look
        checked (bool): Whether the look has been verified
        pushed (bool): Whether the look has been published
    """
    name: str
    gender: GenderEnum
    description: str
    clothes_categories: list[ClothesCategory] = []
    image_prompts: list[str]
    image_urls: list[str] = []
    content_json: str | None = None
    checked: bool = False
    pushed: bool = False

    model_config = ConfigDict(
        from_attributes=True, arbitrary_types_allowed=True, use_enum_values=True
    )


class LookCreate(Look):
    """Model for creating a new look.
    
    Uses ClothesCategoryCreate for the clothes_categories field.
    """
    clothes_categories: list[ClothesCategoryCreate] = []


class LookUpdate(Look):
    """Model for updating an existing look.
    
    All fields are optional with default values for partial updates.
    
    Attributes:
        name (str): The name of the look
        gender (GenderEnum): Target gender
        description (str): Description of the look
        clothes_categories (list[Any]): List of clothing categories
        image_prompts (list[str]): List of image generation prompts
    """
    name: str = ""
    gender: GenderEnum = GenderEnum.unisex
    description: str = ""
    clothes_categories: list[Any] = []
    image_prompts: list[str] = []


class LookRead(Look):
    """Model for reading look data.
    
    Extends the base Look model with an ID and uses ClothesCategoryRead for categories.
    
    Attributes:
        id (int): The unique identifier of the look
        clothes_categories (list[ClothesCategoryRead]): List of clothing categories with full data
    """
    id: int
    clothes_categories: list[ClothesCategoryRead] = []
