import asyncio

from PIL import Image, UnidentifiedImageError
from io import BytesIO

from app.application.base_use_cases import CRUDUseCase
from app.application.exceptions import InvalidFileError, UnknownError
from app.application.interfaces import (
    LooksRepositoryInterface, BaseRepositoryInterface,
)
from app.application.utils import save_image, delete_image
from app.domain.entities.categories import ClothesCategory, ClothesCategoryCreate
from app.domain.entities.clothes import (
    ClothesCreate,
    ClothesUpdate,
    ClothesRead,
    Clothes,
)
from app.domain.entities.enums import GenderEnum
from app.domain.entities.looks import LookCreate, LookUpdate, LookRead

import logging

logger = logging.getLogger(__name__)


class ClothesUseCase(CRUDUseCase[ClothesCreate, ClothesUpdate, ClothesRead]):
    """Use case for managing clothing items.
    
    This class handles all operations related to clothing items
    
    Attributes:
        _entity_create (Type[ClothesCreate]): Class reference for creating clothes
        _entity_update (Type[ClothesUpdate]): Class reference for updating clothes
        _entity_read (Type[ClothesRead]): Class reference for reading clothes
    """
    _entity_create = ClothesCreate
    _entity_update = ClothesUpdate
    _entity_read = ClothesRead

    def __init__(
        self,
        clothes_repository: BaseRepositoryInterface,
    ):
        """Initialize the clothes use case.
        
        Args:
            clothes_repository (ClothesRepositoryInterface): Repository for clothes data
        """
        super().__init__(clothes_repository)
        self.clothes_repository = clothes_repository


class LooksUseCase(CRUDUseCase[LookCreate, LookUpdate, LookRead]):
    """Use case for managing fashion looks.
    
    This class handles all operations related to fashion looks, including category management.
    
    Attributes:
        _entity_create (Type[LookCreate]): Class reference for creating looks
        _entity_update (Type[LookUpdate]): Class reference for updating looks
        _entity_read (Type[LookRead]): Class reference for reading looks
    """
    _entity_create = LookCreate
    _entity_update = LookUpdate
    _entity_read = LookRead

    def __init__(
        self,
        look_repository: LooksRepositoryInterface,
        clothes_repository: BaseRepositoryInterface,
    ):
        """Initialize the looks use case.
        
        Args:
            look_repository (LooksRepositoryInterface): Repository for looks data
            clothes_repository (ClothesRepositoryInterface): Repository for clothes data
        """
        super().__init__(look_repository)
        self.looks_repository = look_repository
        self.clothes_repository = clothes_repository

    async def add_one(self, data: LookCreate) -> LookRead:
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

    async def add_clothes_categories(
        self, look_id: int, clothes_categories: list[ClothesCategoryCreate]
    ) -> LookRead:
        """Add multiple clothes categories to a look.
        
        Args:
            look_id (int): ID of the look to add categories to
            clothes_categories (list[ClothesCategoryCreate]): Categories to add
            
        Returns:
            LookRead: Updated look with new categories
        """
        updated_look = None
        for category in clothes_categories:
            updated_look = await self.looks_repository.add_clothes_category(
                look_id, category.model_dump()
            )
        return LookRead.model_validate(updated_look)

    async def add_clothes_to_category(
        self, look_id: int, category_id: int, clothes_id: int
    ) -> LookRead:
        """Add clothes to a category in a look.
        
        Args:
            look_id (int): ID of the look
            category_id (int): ID of the category to add clothes to
            clothes_id (int): ID of the clothes to add
            
        Returns:
            LookRead: Updated look with new clothes in the category
        """
        look = await self.looks_repository.add_clothes_to_clothes_category(
            category_id, clothes_id
        )
        return LookRead.model_validate(look)

    async def add_images(
            self, look_id: int, images: list[bytes]) -> LookRead:
        """Add images to look.

        Args:
            look_id (int): ID of the look
            images (list[bytes]): list of image files

        Returns:
            LookRead: Updated look with added images
        """
        look = await self.get_one_by_id(look_id)
        look_images = look.get_storage_paths()

        async def process_image(image_data: bytes) -> str:
            try:
                valid_image = await asyncio.to_thread(Image.open, BytesIO(image_data))
                return await save_image(valid_image, str(look_id))
            except UnidentifiedImageError as e:
                raise InvalidFileError from e
            except Exception as e:
                raise UnknownError from e

        # Параллельная обработка всех изображений
        results = await asyncio.gather(*(process_image(img) for img in images))
        look_images.extend(results)

        updated_look = await self.update_one(
            look_id, data=LookUpdate(image_urls=look_images)
        )
        return updated_look

    async def delete_clothes_category(
        self, look_id: int, clothes_category_id: int
    ) -> LookRead:
        """Delete a clothes category from a look.
        
        Args:
            look_id (int): ID of the look
            clothes_category_id (int): ID of the category to delete
            
        Returns:
            LookRead: Updated look without the deleted category
        """
        updated_look = await self.looks_repository.delete_clothes_category(
            look_id, clothes_category_id
        )
        return LookRead.model_validate(updated_look)

    async def delete_clothes_from_category(
        self, look_id: int, category_id: int, clothes_id: int
    ) -> LookRead:
        """Delete clothes from a category in a look.
        
        Args:
            look_id (int): ID of the look
            category_id (int): ID of the category
            clothes_id (int): ID of the clothes to delete
            
        Returns:
            LookRead: Updated look without the deleted clothes
        """
        look = await self.looks_repository.delete_clothes_from_clothes_category(
            category_id, clothes_id
        )
        return LookRead.model_validate(look)

    @staticmethod
    async def _delete_images(image_paths: list[str]) -> None:
        """Delete image files from storage.
        
        Args:
            image_paths (list[str]): List of image paths to delete
        """
        for image_path in image_paths:
            await delete_image(image_path)

    async def delete_one(self, instance_id: int) -> bool:
        """Delete a look and its associated images.
        
        Args:
            instance_id (int): ID of the look to delete
            
        Returns:
            bool: True if deletion was successful, False otherwise
        """
        look = await self.get_one_by_id(instance_id)
        if look.image_urls:
            await self._delete_images(look.get_storage_paths())
        return await super().delete_one(instance_id)

    async def update_one(self, instance_id: int, data: LookUpdate) -> LookRead:
        """Update a look and handle associated image changes.
        
        Args:
            instance_id (int): ID of the look to update
            data (LookUpdate): New look data
            
        Returns:
            LookRead: Updated look with new data
        """
        # Get current look data
        current_look = await self.get_one_by_id(instance_id)

        # Get updated look data
        updated_data = data.model_dump(exclude_unset=True, exclude_defaults=True)
        updated_look = await self.repository.update_one(instance_id, updated_data)
        valid_look = LookRead.model_validate(updated_look)

        # Handle image deletion
        if "image_urls" in updated_data:
            current_paths = set(current_look.get_storage_paths())
            new_paths = set(valid_look.get_storage_paths())
            deleted_paths = current_paths - new_paths
            if deleted_paths:
                await self._delete_images(list(deleted_paths))

        return valid_look
