from typing import Generic, TypeVar, Type, Any, Callable, AsyncContextManager

from sqlalchemy import insert, delete, select, update, func, asc, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.exceptions import EntityNotFoundError
from app.application.interfaces import BaseRepositoryInterface
from app.infrastructure.repositories.models.base_model import Base

Model = TypeVar("Model", bound=Base)


class SQLAlchemyRepository(BaseRepositoryInterface, Generic[Model]):
    """Generic base repository implementation using SQLAlchemy.
    
    This class provides common database operations for all models:
    - Create, read, update, delete operations
    - Pagination and filtering
    - Sorting and ordering
    - Batch operations
    """

    _model: Type[Model] = None

    def __init__(self, session: Callable[[], AsyncContextManager[AsyncSession]]):
        """Initialize repository with session factory.
        
        Args:
            session: Async context manager factory for database sessions
        """
        self.session = session

    async def add_one(self, data: dict) -> dict[str, Any]:
        """Add a new record to the database.
        
        Args:
            data (dict): Dictionary of field values for the new record
            
        Returns:
            dict: Dictionary representation of the created record
        """
        async with self.session() as session:
            stmt = insert(self._model).values(**data).returning(self._model)
            res = await session.execute(stmt)
            await session.commit()
            ans = res.unique().scalar_one()
        return ans.__dict__

    async def delete_one(self, instance_id: int) -> bool:
        """Delete a record from the database.
        
        Args:
            instance_id (int): ID of the record to delete
            
        Returns:
            bool: True if record was deleted, False otherwise
        """
        async with self.session() as session:
            stmt = delete(self._model).where(self._model.id == instance_id)
            res = await session.execute(stmt)
            await session.commit()
            if res.rowcount == 0:
                raise EntityNotFoundError(self._model.__name__)
        return bool(res.rowcount)

    async def get_count(self):
        """Get total count of records.
        
        Returns:
            int: Total number of records in the table
        """
        async with self.session() as session:
            result = await session.scalar(select(func.count(self._model.id)))
        return result

    async def get_one_by_id(self, instance_id: int) -> dict[str, Any]:
        """Get a single record by ID.
        
        Args:
            instance_id (int): ID of the record to retrieve
            
        Returns:
            dict: Dictionary representation of the record
        """
        async with self.session() as session:
            stmt = select(self._model).where(self._model.id == instance_id)
            res = await session.execute(stmt)
            ans = res.unique().scalar_one_or_none()
            if not ans:
                raise EntityNotFoundError(self._model.__name__)
        return ans.__dict__

    async def get_list(
            self,
            offset: int | None = None,
            limit: int | None = None,
            order_by: str = "created_at",
            desc_order: bool = True,
            random_order: bool = False,
            **filter_by,
    ) -> tuple[list[dict[str, Any]], int]:
        """Get a paginated list of records with filtering and sorting.

        Args:
            offset (int, optional): Number of records to skip
            limit (int, optional): Maximum number of records to return
            order_by (str): Field to sort by
            desc_order (bool): Whether to sort in descending order
            random_order (bool): If True, ignore order_by and use random order
            **filter_by: Additional filters to apply

        Returns:
            tuple: (List of records as dictionaries, total count)
        """
        async with self.session() as session:
            if random_order:
                order_clause = func.random()
            else:
                order_field = getattr(self._model, order_by)
                order_clause = desc(order_field) if desc_order else asc(order_field)

            query = select(self._model).filter_by(**filter_by).order_by(order_clause)
            paginated_query = query.offset(offset).limit(limit)
            res = await session.execute(paginated_query)
            ans = res.unique().scalars().all()

            count_query = select(func.count(self._model.id)).filter_by(**filter_by)
            total = await session.scalar(count_query)

        return [a.__dict__ for a in ans], total

    async def get_list_by_ids(self, instance_ids: list[int]) -> list[dict[str, Any]]:
        """Get multiple records by their IDs.
        
        Args:
            instance_ids (list[int]): List of record IDs to retrieve
            
        Returns:
            list[dict]: List of records as dictionaries
        """
        async with self.session() as session:
            query = select(self._model).where(self._model.id.in_(instance_ids))
            res = await session.execute(query)
            ans = res.unique().scalars().all()
        return [a.__dict__ for a in ans]

    async def update_one(self, instance_id: int, data: dict) -> dict[str, Any]:
        """Update a record in the database.
        
        Args:
            instance_id (int): ID of the record to update
            data (dict): Dictionary of field values to update
            
        Returns:
            dict: Dictionary representation of the updated record
        """
        async with self.session() as session:
            stmt = (
                update(self._model)
                .where(self._model.id == instance_id)
                .values(**data)
                .returning(self._model)
            )
            res = await session.execute(stmt)
            ans = res.unique().scalar_one_or_none()
            if not ans:
                raise EntityNotFoundError(self._model.__name__)
            await session.commit()
        return ans.__dict__
