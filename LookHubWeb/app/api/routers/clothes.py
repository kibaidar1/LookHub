from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from starlette import status

from app.api.dependencies import ClothesUseCaseDep, SecurityDep
from app.api.routers.utils import create_enum_from_model
from app.api.schemas import Paginated
from app.domain.entities.clothes import ClothesRead, ClothesUpdate, ClothesCreate
from app.domain.entities.enums import GenderEnum

# Router for clothes-related endpoints
router = APIRouter(prefix="/clothes")

# Create enum for clothes fields to use in ordering
ClothesFieldsEnum = create_enum_from_model(ClothesRead, "ClothesFieldsEnum")


class ClothesAICreate(BaseModel):
    """Schema for creating clothes using AI.
    
    Attributes:
        link (str): URL to parse clothes data from
    """
    link: str


@router.post("/", response_model=ClothesRead, status_code=status.HTTP_201_CREATED, dependencies=[SecurityDep])
async def add_clothes(clothes_use_case: ClothesUseCaseDep, clothes: ClothesCreate):
    """Create a new clothing item.
    
    Args:
        clothes_use_case (ClothesUseCaseDep): Injected clothes use case
        clothes (ClothesCreate): Data for the new clothing item
        
    Returns:
        ClothesRead: Created clothing item
    """
    return await clothes_use_case.add_one(clothes)


@router.post("/ai", response_model=ClothesRead, status_code=status.HTTP_201_CREATED, dependencies=[SecurityDep])
async def add_clothes_with_ai(
    clothes_use_case: ClothesUseCaseDep, clothes: ClothesAICreate
):
    """Create a new clothing item using AI to parse data from a URL.
    
    Args:
        clothes_use_case (ClothesUseCaseDep): Injected clothes use case
        clothes (ClothesAICreate): URL to parse clothes data from
        
    Returns:
        ClothesRead: Created clothing item with AI-generated description
    """
    return await clothes_use_case.add_one_with_ai(clothes.link)


@router.get("/", response_model=Paginated[ClothesRead], status_code=status.HTTP_200_OK)
async def get_clothes_list(
    clothes_use_case: ClothesUseCaseDep,
    page: int = 1,
    page_size: int = 25,
    order_by: ClothesFieldsEnum = "id",
    desc_order: bool = True,
    random_order: bool = False,
    gender: GenderEnum | None = None,
):
    """Get a paginated list of clothing items.
    
    Args:
        clothes_use_case (ClothesUseCaseDep): Injected clothes use case
        page (int, optional): Page number. Defaults to 1.
        page_size (int, optional): Items per page. Defaults to 25.
        order_by (ClothesFieldsEnum, optional): Field to order by. Defaults to "id".
        desc_order (bool, optional): Order descending. Defaults to True.
        random_order (bool): If True, ignore order_by and use random order
        gender (GenderEnum, optional): Filter by gender. Defaults to GenderEnum.unisex.
        
    Returns:
        Paginated[ClothesRead]: Paginated list of clothing items
    """
    clothes, total = await clothes_use_case.get_list(page,
                                                     page_size,
                                                     order_by.value if order_by else None,
                                                     desc_order,
                                                     random_order,
                                                     gender=gender.value if gender else None)
    return Paginated[ClothesRead](results=clothes, count=total)


@router.get("/{clothes_id}", response_model=ClothesRead, status_code=status.HTTP_200_OK)
async def get_clothes_detail(clothes_use_case: ClothesUseCaseDep, clothes_id: int):
    """Get a specific clothing item by ID.
    
    Args:
        clothes_use_case (ClothesUseCaseDep): Injected clothes use case
        clothes_id (int): ID of the clothing item
        
    Returns:
        ClothesRead: Clothing item details
    """
    return await clothes_use_case.get_one_by_id(clothes_id)


@router.patch(
    "/{clothes_id}", response_model=ClothesRead, status_code=status.HTTP_201_CREATED, dependencies=[SecurityDep]
)
async def update_clothes(clothes_use_case: ClothesUseCaseDep, clothes_id: int, clothes: ClothesUpdate):
    """Update a clothing item.
    
    Args:
        clothes_use_case (ClothesUseCaseDep): Injected clothes use case
        clothes_id (int): ID of the clothing item to update
        clothes (ClothesUpdate): New data for the clothing item
        
    Returns:
        ClothesRead: Updated clothing item
    """
    return await clothes_use_case.update_one(clothes_id, clothes)


@router.delete("/{clothes_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[SecurityDep])
async def delete_clothes(clothes_use_case: ClothesUseCaseDep, clothes_id: int):
    """Delete a clothing item.
    
    Args:
        clothes_use_case (ClothesUseCaseDep): Injected clothes use case
        clothes_id (int): ID of the clothing item to delete
        
    Raises:
        ValueError: If deletion fails
    """
    if not await clothes_use_case.delete_one(clothes_id):
        raise ValueError("Could not delete")
