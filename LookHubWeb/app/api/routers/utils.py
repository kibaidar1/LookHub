from enum import Enum
from typing import get_origin, get_args

from pydantic import BaseModel


def create_enum_from_model(model: type[BaseModel], enum_name: str) -> type[Enum]:
    """Create an Enum class from a Pydantic model's fields.

    This utility function creates an Enum class where each value is the same as its name,
    using the field names from a Pydantic model. This is useful for creating enums for
    field selection in API endpoints. Fields that cannot be used for sorting (like lists,
    complex objects, JSON fields, and booleans) are excluded.

    Args:
        model (type[BaseModel]): Pydantic model class to create enum from
        enum_name (str): Name for the created Enum class

    Returns:
        type[Enum]: New Enum class with model field names as values

    Example:
        >>> class MyModel(BaseModel):
        ...     name: str
        ...     age: int
        ...     tags: list[str]
        >>> MyEnum = create_enum_from_model(MyModel, "MyEnum")
        >>> MyEnum.name.value == "name"  # True
        >>> MyEnum.tags  # AttributeError: 'MyEnum' has no attribute 'tags'
    """
    sortable_fields = {}

    for field_name, field_info in model.model_fields.items():
        field_type = field_info.annotation

        # Skip if field type is None
        if field_type is None:
            continue

        # Get the origin type (e.g., list, dict) and its arguments
        origin = get_origin(field_type)
        args = get_args(field_type)

        # Skip fields that cannot be sorted
        if (origin is list or  # Skip list types
                origin is dict or  # Skip dict types
                (hasattr(field_type, "__origin__") and field_type.__origin__ is dict) or  # Skip JSON fields
                (origin is not None and any(arg.__name__ == "BaseModel" for arg in args))):  # Skip complex objects
            continue

        sortable_fields[field_name] = field_name

    return Enum(enum_name, sortable_fields)
