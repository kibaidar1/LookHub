from typing import Any

from sqlalchemy import select, insert, update, delete

from app.application.interfaces import LooksRepositoryInterface
from app.infrastructure.repositories.models.association import clothescategory_clothes
from app.infrastructure.repositories.models.clothes_categories import ClothesCategory
from app.infrastructure.repositories.models.looks import Look
from app.infrastructure.repositories.sqlalchemy import SQLAlchemyRepository


class LooksRepository(SQLAlchemyRepository[Look], LooksRepositoryInterface):
    """Repository implementation for looks.
    
    This class extends the base SQLAlchemy repository with look-specific
    operations and implements the LooksRepositoryInterface.
    """

    _model = Look

    async def add_clothes_category(
        self, look_id: int, clothes_category: dict[str, Any]
    ) -> dict[str, Any]:
        """Add a new clothes category to a look.
        
        Args:
            look_id (int): ID of the look to add the category to
            clothes_category (dict): Category data including name and clothes IDs
            
        Returns:
            dict: Updated look data as dictionary
        """
        async with self.session() as session:
            stmt = (
                insert(ClothesCategory)
                .values(name=clothes_category.get("name"), look_id=look_id)
                .returning(ClothesCategory.id)
            )
            res = await session.execute(stmt)
            clothescategory_id = res.scalar_one()
            for clothes_id in clothes_category.get("clothes"):
                stmt = insert(clothescategory_clothes).values(
                    clothescategory_id=clothescategory_id, clothes_id=clothes_id
                )
                await session.execute(stmt)
            await session.commit()
            stmt = select(self._model).where(self._model.id == look_id)
            res = await session.execute(stmt)
            ans = res.unique().scalar_one()
        return ans.__dict__

    async def add_clothes_to_clothes_category(
        self, category_id: int, clothes_id: int
    ) -> dict[str, Any]:
        """Add a clothes item to an existing category.
        
        Args:
            category_id (int): ID of the category to add clothes to
            clothes_id (int): ID of the clothes item to add
            
        Returns:
            dict: Updated look data as dictionary
        """
        async with self.session() as session:
            stmt = select(ClothesCategory).where(ClothesCategory.id == category_id)
            res = await session.execute(stmt)
            category = res.unique().scalar_one()
            category.clothes.append(clothes_id)
            await session.commit()
            stmt = select(self._model).where(self._model.id == category.look_id)
            res = await session.execute(stmt)
            ans = res.unique().scalar_one()
        return ans.__dict__

    async def delete_clothes_category(
        self, look_id: int, clothes_category_id: int
    ) -> dict[str, Any]:
        """Delete a clothes category from a look.
        
        Args:
            look_id (int): ID of the look containing the category
            clothes_category_id (int): ID of the category to delete
            
        Returns:
            dict: Updated look data as dictionary
        """
        async with self.session() as session:
            stmt = delete(ClothesCategory).where(
                ClothesCategory.id == clothes_category_id
            )
            await session.execute(stmt)
            await session.commit()
            stmt = select(self._model).where(self._model.id == look_id)
            res = await session.execute(stmt)
            ans = res.unique().scalar_one()
        return ans.__dict__

    async def delete_clothes_from_clothes_category(
        self, category_id: int, clothes_id: int
    ) -> dict[str, Any]:
        """Remove a clothes item from a category.
        
        Args:
            category_id (int): ID of the category to remove clothes from
            clothes_id (int): ID of the clothes item to remove
            
        Returns:
            dict: Updated look data as dictionary
        """
        async with self.session() as session:
            stmt = select(ClothesCategory).where(ClothesCategory.id == category_id)
            res = await session.execute(stmt)
            category = res.unique().scalar_one()
            category.clothes = [c for c in category.clothes if c.id != clothes_id]
            await session.commit()
            stmt = select(self._model).where(self._model.id == category.look_id)
            res = await session.execute(stmt)
            ans = res.unique().scalar_one()
        return ans.__dict__
