from typing import List

from sqlalchemy import String, ARRAY
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.repositories.models.base_model import Base


class Clothes(Base):
    """Model representing a clothing item in the database.
    
    Attributes:
        name (str): Name of the clothing item
        description (str): Detailed description of the item (optional)
        colours (List[str]): List of available colors
        gender (str): Gender category (мужской/женский/унисекс)
        link (str): URL to the original product page
        image_url (str): URL to the product image
    """

    name: Mapped[str]
    description: Mapped[str] = mapped_column(String, nullable=True)
    colours: Mapped[List[str]] = mapped_column(ARRAY(String))
    gender: Mapped[str]
    link: Mapped[str]
    image_url: Mapped[str]

    def __str__(self):
        """String representation of the clothes item.
        
        Returns:
            str: Name of the clothing item
        """
        return self.name
