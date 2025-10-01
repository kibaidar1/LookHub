from typing import Type, Generic

from app.application.interfaces import BaseRepositoryInterface
from app.domain.entities.generics import EntityCreate, EntityUpdate, EntityRead


class CRUDUseCase(Generic[EntityCreate, EntityUpdate, EntityRead]):
    """Base class for CRUD (Create, Read, Update, Delete) operations.
    
    This class provides basic CRUD operations for any entity type. It uses generic types
    to ensure type safety across different entity types.
    
    Type Parameters:
        EntityCreate: Type for creating new entities
        EntityUpdate: Type for updating existing entities
        EntityRead: Type for reading entity data
    
    Attributes:
        _entity_create (Type[EntityCreate]): Class reference for entity creation
        _entity_update (Type[EntityUpdate]): Class reference for entity updates
        _entity_read (Type[EntityRead]): Class reference for entity reading
        repository (BaseRepositoryInterface): Repository instance for data operations
    """
    _entity_create: Type[EntityCreate]
    _entity_update: Type[EntityUpdate]
    _entity_read: Type[EntityRead]

    def __init__(self, repository: BaseRepositoryInterface):
        """Initialize the use case with a repository.
        
        Args:
            repository (BaseRepositoryInterface): Repository instance for data operations
        """
        self.repository = repository

    async def add_one(self, data: EntityCreate) -> EntityRead:
        """Create a new entity.
        
        Args:
            data (EntityCreate): Data for creating the entity
            
        Returns:
            EntityRead: Created entity with full data
        """
        instance = await self.repository.add_one(
            data.model_dump(exclude_unset=True, exclude_defaults=True)
        )
        return self._entity_read.model_validate(instance)

    async def delete_one(self, instance_id: int) -> bool:
        """Delete an entity by its ID.
        
        Args:
            instance_id (int): ID of the entity to delete
            
        Returns:
            bool: True if deletion was successful, False otherwise
        """
        return await self.repository.delete_one(instance_id)

    async def get_one_by_id(self, instance_id: int) -> EntityRead:
        """Get an entity by its ID.
        
        Args:
            instance_id (int): ID of the entity to retrieve
            
        Returns:
            EntityRead: Entity with full data
        """
        instance = await self.repository.get_one_by_id(instance_id)
        return self._entity_read.model_validate(instance)

    async def get_list(
        self,
        page: int = 1,
        page_size: int = 25,
        order_by: str = "id",
        desc_order: bool = True,
        random_order: bool = False,
        **filter_by,
    ) -> tuple[list[EntityRead], int]:
        """Get a paginated list of entities with optional filtering.
        
        Args:
            page (int, optional): Page number. Defaults to 1.
            page_size (int, optional): Number of items per page. Defaults to 25.
            order_by (str, optional): Field to order by. Defaults to "id".
            desc_order (bool, optional): Whether to order in descending order. Defaults to True.
            random_order (bool): If True, ignore order_by and use random order
            **filter_by: Additional filters to apply
            
        Returns:
            tuple[list[EntityRead], int]: List of entities and total count
        """
        offset = (page - 1) * page_size
        filter_by = {k: v for k, v in filter_by.items() if v is not None}
        instances, total = await self.repository.get_list(
            offset, page_size, order_by, desc_order, random_order, **filter_by
        )
        return [
            self._entity_read.model_validate(instance) for instance in instances
        ], total

    async def get_list_by_ids(self, ids: list[int]) -> list[EntityRead]:
        """Get a list of entities by their IDs.
        
        Args:
            ids (list[int]): List of entity IDs to retrieve
            
        Returns:
            list[EntityRead]: List of entities with full data
        """
        clothes = await self.repository.get_list_by_ids(ids)
        return [self._entity_read.model_validate(item) for item in clothes]

    async def update_one(self, instance_id: int, data: EntityUpdate) -> EntityRead:
        """Update an existing entity.
        
        Args:
            instance_id (int): ID of the entity to update
            data (EntityUpdate): New data for the entity
            
        Returns:
            EntityRead: Updated entity with full data
        """
        instance = await self.repository.update_one(
            instance_id, data.model_dump(exclude_unset=True)
        )
        return self._entity_read.model_validate(instance)
