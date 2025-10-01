from typing import Any

from pydantic import BaseModel, ConfigDict, field_validator

from app.domain.entities.categories import (
    ClothesCategory,
    ClothesCategoryCreate,
    ClothesCategoryRead,
)
from app.domain.entities.enums import GenderEnum
from app.config import API_HOST


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
    checked: bool | None = False
    pushed: bool | None = False

    model_config = ConfigDict(
        from_attributes=True, arbitrary_types_allowed=True, use_enum_values=True
    )

    @field_validator("image_urls", mode="after")
    def create_image_urls(cls, value):
        """Adds API_HOST prefix to image URLs during serialization.
        
        Args:
            value (list[str]): List of image URLs
            
        Returns:
            list[str]: List of image URLs with API_HOST prefix
        """
        if not value:
            return []
        return [
            f"{API_HOST}/images/{url}" if not url.startswith("http") else url
            for url in value
        ]

    @field_validator("image_urls", mode="before")
    def strip_api_host(cls, value):
        """Removes API_HOST prefix from image URLs during deserialization.
        
        Args:
            value (list[str]): List of image URLs
            
        Returns:
            list[str]: List of image URLs without API_HOST prefix
        """
        if not value:
            return []
        if isinstance(value, list):
            prefix = f"{API_HOST}/images/"
            return [
                url.replace(prefix, "") if url.startswith(prefix) else url
                for url in value
            ]
        return value

    def get_storage_paths(self) -> list[str]:
        """Get the storage paths of images without API_HOST prefix.
        
        Returns:
            list[str]: List of image storage paths
        """
        return [
            (
                url.replace(f"{API_HOST}/images/", "")
                if url.startswith(f"{API_HOST}/images/")
                else url
            )
            for url in self.image_urls
        ]


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
    checked: bool | None = None
    pushed: bool | None = None


class LookRead(Look):
    """Model for reading look data.
    
    Extends the base Look model with an ID and uses ClothesCategoryRead for categories.
    
    Attributes:
        id (int): The unique identifier of the look
        clothes_categories (list[ClothesCategoryRead]): List of clothing categories with full data
    """
    id: int
    clothes_categories: list[ClothesCategoryRead] = []
