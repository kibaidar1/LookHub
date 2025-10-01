from typing import Annotated
from fastapi import Depends, Security

from app.api.security import verify_api_token
from app.application.use_cases import LooksUseCase, ClothesUseCase
from app.infrastructure.database import get_async_session, scoped_session
from app.infrastructure.repositories.clothes import ClothesRepository
from app.infrastructure.repositories.looks import LooksRepository


# Dependency factories for use cases
async def get_looks_use_case() -> LooksUseCase:
    looks_repo = LooksRepository(scoped_session)
    clothes_repo = ClothesRepository(scoped_session)
    return LooksUseCase(looks_repo, clothes_repo)


async def get_clothes_use_case() -> ClothesUseCase:
    clothes_repo = ClothesRepository(scoped_session)
    return ClothesUseCase(clothes_repo)

# Type aliases for FastAPI dependency injection
LooksUseCaseDep = Annotated[LooksUseCase, Depends(get_looks_use_case)]
ClothesUseCaseDep = Annotated[ClothesUseCase, Depends(get_clothes_use_case)]
SecurityDep = Security(verify_api_token)
