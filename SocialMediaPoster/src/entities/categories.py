from pydantic import BaseModel, ConfigDict

from src.entities.clothes import Clothes, ClothesCreate, ClothesRead


class ClothesCategory(BaseModel):
    """Base model for clothing categories.
    
    Represents a category of clothes with a name and a list of associated clothes items.
    
    Attributes:
        name (str): The name of the category
        clothes (list[Clothes]): List of clothes items in this category
    """
    name: str
    clothes: list[Clothes] = []

    model_config = ConfigDict(from_attributes=True, arbitrary_types_allowed=True)


class ClothesCategoryCreate(BaseModel):
    """Model for creating a new clothing category.
    
    Used when creating a new category, allows specifying clothes by either their full data
    or just their IDs.
    
    Attributes:
        name (str): The name of the category
        clothes (list[ClothesCreate | int]): List of clothes items or their IDs
    """
    name: str
    clothes: list[ClothesCreate | int] = []


class ClothesCategoryUpdate(ClothesCategoryCreate):
    """Model for updating an existing clothing category.
    
    Inherits all fields from ClothesCategoryCreate.
    """
    ...


class ClothesCategoryRead(ClothesCategory):
    """Model for reading clothing category data.
    
    Extends the base ClothesCategory with an ID and uses ClothesRead for the clothes list.
    
    Attributes:
        id (int): The unique identifier of the category
        clothes (list[ClothesRead]): List of clothes items with their full data
    """
    id: int
    clothes: list[ClothesRead] = []
