from datetime import datetime

from sqlalchemy import Integer, func, inspect
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import (
    DeclarativeBase,
    mapped_column,
    Mapped,
    declared_attr,
    InstrumentedAttribute,
)


class Base(AsyncAttrs, DeclarativeBase):
    """Base class for all database models.
    
    This abstract class provides common fields and functionality for all models:
    - Automatic ID generation
    - Created and updated timestamps
    - Automatic table naming
    - Dictionary serialization with relationship handling
    """

    __abstract__ = True  # Abstract class to prevent table creation

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        server_default=func.now(), onupdate=func.now()
    )

    @declared_attr.directive
    def __tablename__(cls) -> str:
        """Generate table name from class name.
        
        Returns:
            str: Lowercase class name as table name
        """
        return cls.__name__.lower()

    def to_dict(self):
        """Convert model instance to dictionary.
        
        This method handles:
        - Basic field conversion
        - Relationship serialization
        - Nested object serialization
        - Special field type conversions (e.g., ID to string)
        
        Returns:
            dict: Dictionary representation of the model instance
        """
        convert_fields = {"id": str}
        data = {
            c.name: (
                convert_fields[c.name](getattr(self, c.name))
                if c.name in convert_fields
                else getattr(self, c.name)
            )
            for c in self.__table__.columns
        }

        for key, value in self.__class__.__dict__.items():
            if isinstance(value, InstrumentedAttribute):
                related_value = getattr(self, key)

                if isinstance(related_value, list):
                    data[key] = [
                        item.to_dict()
                        for item in related_value
                        if inspect(item, raiseerr=False)
                    ]
                elif inspect(related_value, raiseerr=False):
                    data[key] = related_value.to_dict()

        return data
