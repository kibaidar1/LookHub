from app.infrastructure.repositories.models.clothes import Clothes
from app.infrastructure.repositories.sqlalchemy import SQLAlchemyRepository


class ClothesRepository(SQLAlchemyRepository[Clothes]):
    """Repository implementation for clothes items.
    
    This class extends the base SQLAlchemy repository with clothes-specific
    operations and implements the ClothesRepositoryInterface.
    """

    _model = Clothes

