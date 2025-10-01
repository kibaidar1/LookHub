from pydantic import BaseModel, ConfigDict

from src.entities.enums import ColourEnum, GenderEnum


class Clothes(BaseModel):
    """Base model for clothing items.
    
    Represents a piece of clothing with its properties and metadata.
    
    Attributes:
        name (str): The name of the clothing item
        description (str | None): Optional description of the item
        colours (list[ColourEnum]): List of available colors for the item
        gender (GenderEnum): Target gender for the clothing item
        link (str): URL to purchase or view the item
        image_url (str): URL to the item's image
    """
    name: str
    description: str | None = None
    colours: list[ColourEnum]
    gender: GenderEnum
    link: str
    image_url: str

    model_config = ConfigDict(
        from_attributes=True, arbitrary_types_allowed=True, use_enum_values=True
    )


class ClothesCreate(Clothes):
    """Model for creating a new clothing item.
    
    Inherits all fields from the base Clothes model.
    """
    ...

    class Config:
        use_enum_values = True


class ClothesUpdate(Clothes):
    """Model for updating an existing clothing item.
    
    All fields are optional with default values for partial updates.
    
    Attributes:
        clothes_id (str): The unique identifier of the clothing item
        name (str): The name of the clothing item
        description (str): Description of the item
        colours (list[ColourEnum]): List of available colors
        gender (GenderEnum): Target gender
        link (str): Purchase/view URL
        image_url (str): Image URL
    """
    clothes_id: str = ""
    name: str = ""
    description: str = ""
    colours: list[ColourEnum] = [ColourEnum.black]
    gender: GenderEnum = GenderEnum.unisex
    link: str = ""
    image_url: str = ""


class ClothesRead(Clothes):
    """Model for reading clothing item data.
    
    Extends the base Clothes model with an ID field.
    
    Attributes:
        id (int): The unique identifier of the clothing item
    """
    id: int

    model_config = ConfigDict(
        from_attributes=True, arbitrary_types_allowed=True, use_enum_values=True
    )
