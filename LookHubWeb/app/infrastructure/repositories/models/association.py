from sqlalchemy import Table, Column, ForeignKey

from app.infrastructure.repositories.models.base_model import Base

"""Association table for many-to-many relationship between clothes and categories.

This module defines the association table that manages the many-to-many relationship
between clothes items and their categories in the database.
"""
clothescategory_clothes = Table(
    "clothescategory_clothes",
    Base.metadata,
    Column("clothescategory_id", ForeignKey("clothescategory.id", ondelete="CASCADE")),
    Column("clothes_id", ForeignKey("clothes.id", ondelete="CASCADE")),
)
