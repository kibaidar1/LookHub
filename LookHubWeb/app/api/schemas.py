from typing import Generic, Type

from pydantic import BaseModel

from app.domain.entities.generics import EntityRead


class Paginated(BaseModel, Generic[EntityRead]):
    """Generic pagination schema for API responses.
    
    This schema is used to wrap paginated responses with a count of total items.
    
    Type Parameters:
        EntityRead: The type of entity being paginated
        
    Attributes:
        results (list[EntityRead]): List of entities for the current page
        count (int): Total number of entities across all pages
    """
    results: list[EntityRead]
    count: int


class ClothesData(BaseModel):
    """Schema for clothes data in API requests.
    
    Used when adding clothes to a category in a look.
    
    Attributes:
        clothes_id (int): ID of the clothes to add
    """
    clothes_id: int
