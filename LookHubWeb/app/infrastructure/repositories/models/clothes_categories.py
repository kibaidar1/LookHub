from typing import List

from sqlalchemy import Integer, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, relationship, mapped_column

from app.infrastructure.repositories.models.association import clothescategory_clothes
from app.infrastructure.repositories.models.base_model import Base


class ClothesCategory(Base):
    """Model representing a category of clothes within a look.
    
    Attributes:
        name (str): Name of the category (e.g., "Верх", "Низ", "Обувь")
        look_id (int): ID of the look this category belongs to
        clothes (List[Clothes]): List of clothes items in this category
    """

    name: Mapped[str]
    look_id: Mapped[int] = mapped_column(ForeignKey("look.id", ondelete="CASCADE"))
    clothes: Mapped[List["Clothes"]] = relationship(
        secondary=clothescategory_clothes, lazy="joined"
    )

    def __str__(self):
        """String representation of the clothes category.
        
        Returns:
            str: Name of the category
        """
        return self.name
