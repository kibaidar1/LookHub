import abc
from typing import Any


from app.domain.entities.clothes import ClothesRead
from app.domain.entities.enums import GenderEnum
from app.domain.entities.looks import LookCreate


class BaseRepositoryInterface(abc.ABC):
    """Base interface for repository implementations.
    
    This interface defines basic CRUD operations that all repositories must implement.
    """

    @abc.abstractmethod
    async def add_one(self, data: dict) -> dict:
        """Create a new entity.
        
        Args:
            data (dict): Entity data to create
            
        Returns:
            dict: Created entity data
        """
        raise NotImplementedError

    @abc.abstractmethod
    async def delete_one(self, instance_id: int) -> bool:
        """Delete an entity by its ID.
        
        Args:
            instance_id (int): ID of the entity to delete
            
        Returns:
            bool: True if deletion was successful, False otherwise
        """
        raise NotImplementedError

    @abc.abstractmethod
    async def get_list_by_ids(self, instance_ids: list[int]) -> list[dict]:
        """Get multiple entities by their IDs.
        
        Args:
            instance_ids (list[int]): List of entity IDs to retrieve
            
        Returns:
            list[dict]: List of entity data
        """
        raise NotImplementedError

    @abc.abstractmethod
    async def get_one_by_id(self, instance_id: int) -> dict:
        """Get an entity by its ID.
        
        Args:
            instance_id (int): ID of the entity to retrieve
            
        Returns:
            dict: Entity data
        """
        raise NotImplementedError

    @abc.abstractmethod
    async def get_list(
        self, offset: int, limit: int, order_by: str, desc_order: bool, random_order: bool = False, **filter_by
    ) -> tuple[list[dict[str, Any]], int]:
        """Get a paginated list of entities with optional filtering.
        
        Args:
            offset (int): Number of items to skip
            limit (int): Maximum number of items to return
            order_by (str): Field to order by
            desc_order (bool): Whether to order in descending order
            random_order (bool): If True, ignore order_by and use random order
            **filter_by: Additional filters to apply
            
        Returns:
            tuple[list[dict[str, Any]], int]: List of entity data and total count
        """
        raise NotImplementedError

    @abc.abstractmethod
    async def update_one(self, instance_id: int, data: dict) -> dict:
        """Update an existing entity.
        
        Args:
            instance_id (int): ID of the entity to update
            data (dict): New entity data
            
        Returns:
            dict: Updated entity data
        """
        raise NotImplementedError


class LooksRepositoryInterface(BaseRepositoryInterface, abc.ABC):
    """Interface for looks repository.
    
    This interface extends the base repository with look-specific operations.
    """

    @abc.abstractmethod
    async def add_clothes_category(
        self, look_id: int, clothes_category: dict[str, Any]
    ) -> dict[str, Any]:
        """Add a clothes category to a look.
        
        Args:
            look_id (int): ID of the look
            clothes_category (dict[str, Any]): Category data to add
            
        Returns:
            dict[str, Any]: Updated look data
        """
        raise NotImplementedError

    async def add_clothes_to_clothes_category(
        self, category_id: int, clothes_id: int
    ) -> dict[str, Any]:
        """Add clothes to a category.
        
        Args:
            category_id (int): ID of the category
            clothes_id (int): ID of the clothes to add
            
        Returns:
            dict[str, Any]: Updated look data
        """
        raise NotImplementedError

    async def delete_clothes_category(
        self, look_id: int, clothes_category_id: int
    ) -> dict[str, Any]:
        """Delete a clothes category from a look.
        
        Args:
            look_id (int): ID of the look
            clothes_category_id (int): ID of the category to delete
            
        Returns:
            dict[str, Any]: Updated look data
        """
        raise NotImplementedError

    async def delete_clothes_from_clothes_category(
        self, category_id: int, clothes_id: int
    ) -> dict[str, Any]:
        """Delete clothes from a category.
        
        Args:
            category_id (int): ID of the category
            clothes_id (int): ID of the clothes to delete
            
        Returns:
            dict[str, Any]: Updated look data
        """
        raise NotImplementedError
