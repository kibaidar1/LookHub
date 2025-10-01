from typing import TypeVar, Type

from pydantic import BaseModel

# Type variable for create models
EntityCreate = TypeVar("EntityCreate", bound=BaseModel)
"""Type variable for create models that inherit from BaseModel."""

# Type variable for update models
EntityUpdate = TypeVar("EntityUpdate", bound=BaseModel)
"""Type variable for update models that inherit from BaseModel."""

# Type variable for read models
EntityRead = TypeVar("EntityRead", bound=BaseModel)
"""Type variable for read models that inherit from BaseModel."""
