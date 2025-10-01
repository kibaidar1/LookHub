from typing import List

from sqlalchemy import ARRAY, String, JSON, Boolean
from sqlalchemy.orm import Mapped, relationship, mapped_column, class_mapper

from app.infrastructure.repositories.models.base_model import Base


class Look(Base):
    """Model representing a complete look or outfit in the database.
    
    Attributes:
        name (str): Name of the look
        gender (str): Target gender for the look
        description (str): Detailed description of the look
        clothes_categories (List[ClothesCategory]): Categories of clothes in the look
        image_prompts (List[str]): Prompts used for generating look images
        image_urls (List[str]): URLs of generated look images
        content_json (str): JSON representation of the look's content
        checked (bool): Whether the look has been reviewed
        pushed (bool): Whether the look has been published
    """

    name: Mapped[str]
    gender: Mapped[str]
    description: Mapped[str]
    clothes_categories: Mapped[List["ClothesCategory"]] = relationship(
        "ClothesCategory", uselist=True, lazy="joined", cascade="all, delete-orphan"
    )
    image_prompts: Mapped[List[str]] = mapped_column(ARRAY(String))
    image_urls: Mapped[List[str]] = mapped_column(ARRAY(String), nullable=True)
    content_json: Mapped[str] = mapped_column(JSON, nullable=True)
    checked: Mapped[bool] = mapped_column(Boolean, default=False)
    pushed: Mapped[bool] = mapped_column(Boolean, default=False)

    def __str__(self):
        """String representation of the look.
        
        Returns:
            str: Name of the look
        """
        return self.name
