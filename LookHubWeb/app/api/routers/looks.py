from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from starlette import status
import json
import uuid
from celery import Celery

from app.api.dependencies import LooksUseCaseDep, SecurityDep
from app.api.routers.utils import create_enum_from_model
from app.api.schemas import Paginated, ClothesData
from app.domain.entities.categories import ClothesCategoryCreate
from app.domain.entities.looks import LookRead, LookCreate, LookUpdate
from app.config import REDIS_HOST, REDIS_PORT

# Router for looks-related endpoints
router = APIRouter(prefix="/looks")

# Create enum for look fields to use in ordering
LOOK_FIELDS_ENUM = create_enum_from_model(LookRead, "LookFieldsEnum")


@router.post('/{look_id}/add_clothes_categories',
             response_model=LookRead,
             status_code=status.HTTP_201_CREATED,
             dependencies=[SecurityDep])
async def add_clothes_categories_to_look(looks_use_case: LooksUseCaseDep,
                                         look_id: int,
                                         clothes_categories: list[ClothesCategoryCreate]):
    """Add new clothes categories to the look.

        Args:
            looks_use_case (LooksUseCaseDep): Injected looks use case
            look_id (int): ID of the look
            clothes_categories: list[ClothesCategoryCreate]: Clothes categories to add to the look

        Returns:
            LookRead: Created look
        """
    return await looks_use_case.add_clothes_categories(look_id, clothes_categories)


@router.post('/{look_id}/add_images',
             response_model=LookRead,
             status_code=status.HTTP_201_CREATED,
             dependencies=[SecurityDep])
async def add_images_to_look(looks_use_case: LooksUseCaseDep,
                             look_id: int,
                             image_files: list[UploadFile] = File(...)):
    """Create a new look.

        Args:
            looks_use_case (LooksUseCaseDep): Injected looks use case
            look_id (int): ID of the look
            image_files (list[UploadFile]): Image files to add to the look

        Returns:
            LookRead: Created look
        """
    images = [image.file.read() for image in image_files]
    return await looks_use_case.add_images(look_id, images)


@router.post("/", response_model=LookRead, status_code=status.HTTP_201_CREATED, dependencies=[SecurityDep])
async def create_look(looks_use_case: LooksUseCaseDep,
                      look: LookCreate):
    """Create a new look.
    
    Args:
        looks_use_case (LooksUseCaseDep): Injected looks use case
        look (LookCreate): Data for the new-look
        
    Returns:
        LookRead: Created look
    """
    return await looks_use_case.add_one(look)


@router.get("/", response_model=Paginated[LookRead], status_code=status.HTTP_200_OK)
async def get_looks_list(
    looks_use_case: LooksUseCaseDep,
    page: int = 1,
    page_size: int = 25,
    order_by: LOOK_FIELDS_ENUM = "id",
    desc_order: bool = True,
    random_order: bool = False,
    checked: bool | None = None,
    pushed: bool | None = None,
):
    """Get a paginated list of looks.
    
    Args:
        looks_use_case (LooksUseCaseDep): Injected looks use case
        page (int, optional): Page number. Defaults to 1.
        page_size (int, optional): Items per page. Defaults to 25.
        order_by (LOOK_FIELDS_ENUM, optional): Field to order by. Defaults to "id".
        desc_order (bool, optional): Order descending. Defaults to True.
        random_order (bool): If True, ignore order_by and use random order
        checked (bool | None, optional): Filter by checked status. Defaults to None.
        pushed (bool | None, optional): Filter by pushed status. Defaults to None.
        
    Returns:
        Paginated[LookRead]: Paginated list of looks
    """
    looks, total = await looks_use_case.get_list(
        page,
        page_size,
        order_by.value if order_by else None,
        desc_order,
        random_order,
        checked=checked,
        pushed=pushed,
    )
    return Paginated[LookRead](results=looks, count=total)


@router.get("/{look_id}", response_model=LookRead, status_code=status.HTTP_200_OK)
async def get_look_detail(looks_use_case: LooksUseCaseDep, look_id: int):
    """Get a specific look by ID.
    
    Args:
        looks_use_case (LooksUseCaseDep): Injected looks use case
        look_id (int): ID of the look
        
    Returns:
        LookRead: Look details
    """
    return await looks_use_case.get_one_by_id(look_id)


@router.patch("/{look_id}", response_model=LookRead, status_code=status.HTTP_200_OK, dependencies=[SecurityDep])
async def update_look(looks_use_case: LooksUseCaseDep, look_id: int, look: LookUpdate):
    """Update a look.
    
    Args:
        looks_use_case (LooksUseCaseDep): Injected looks use case
        look_id (int): ID of the look to update
        look (LookUpdate): New data for the look
        
    Returns:
        LookRead: Updated look
    """
    print(look)
    return await looks_use_case.update_one(look_id, look)


@router.delete("/{look_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[SecurityDep])
async def delete_look(looks_use_case: LooksUseCaseDep, look_id: int):
    """Delete a look.
    
    Args:
        looks_use_case (LooksUseCaseDep): Injected looks use case
        look_id (int): ID of the look to delete
        
    Raises:
        ValueError: If deletion fails
    """
    if not await looks_use_case.delete_one(look_id):
        raise ValueError("Could not delete")


@router.delete("/{look_id}/categories/{category_id}", dependencies=[SecurityDep])
async def delete_clothes_category(
    looks_use_case: LooksUseCaseDep, look_id: int, category_id: int
):
    """Delete a clothes category from a look.
    
    Args:
        looks_use_case (LooksUseCaseDep): Injected looks use case
        look_id (int): ID of the look
        category_id (int): ID of the category to delete
        
    Returns:
        dict: Success message
    """
    await looks_use_case.delete_clothes_category(look_id, category_id)
    return {"message": "Категория успешно удалена"}


@router.post("/{look_id}/categories/{category_id}/clothes", dependencies=[SecurityDep])
async def add_clothes_to_category(
    looks_use_case: LooksUseCaseDep,
    look_id: int,
    category_id: int,
    clothes_data: ClothesData,
):
    """Add clothes to a category in a look.
    
    Args:
        looks_use_case (LooksUseCaseDep): Injected looks use case
        look_id (int): ID of the look
        category_id (int): ID of the category
        clothes_data (ClothesData): Data containing clothes ID to add
        
    Returns:
        dict: Success message
    """
    await looks_use_case.add_clothes_to_category(
        look_id, category_id, clothes_data.clothes_id
    )
    return {"message": "Вещь успешно добавлена в категорию"}


@router.delete("/{look_id}/categories/{category_id}/clothes/{clothes_id}", dependencies=[SecurityDep])
async def remove_clothes_from_category(
    looks_use_case: LooksUseCaseDep, look_id: int, category_id: int, clothes_id: int
):
    """Remove clothes from a category in a look.
    
    Args:
        looks_use_case (LooksUseCaseDep): Injected looks use case
        look_id (int): ID of the look
        category_id (int): ID of the category
        clothes_id (int): ID of the clothes to remove
        
    Returns:
        dict: Success message
    """
    await looks_use_case.delete_clothes_from_category(look_id, category_id, clothes_id)
    return {"message": "Вещь успешно удалена из категории"}


@router.post("/{look_id}/publish", dependencies=[SecurityDep])
async def publish_look_to_social_media(looks_use_case: LooksUseCaseDep, look_id: int):
    """Publish a look to social media platforms.
    
    Args:
        looks_use_case (LooksUseCaseDep): Injected looks use case
        look_id (int): ID of the look to publish
        
    Returns:
        dict: Success message with task_id
    """
    # Get the look data
    look = await looks_use_case.get_one_by_id(look_id)
    
    # Check if look is ready for publishing
    if not look.checked:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Look must be checked before publishing"
        )
    
    if not look.image_urls:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Look must have images before publishing"
        )
    
    # Create Celery app for SocialMediaPoster
    social_media_celery = Celery(
        "social_media_poster",
        broker=f"redis://{REDIS_HOST}:{REDIS_PORT}/0",
        backend=f"redis://{REDIS_HOST}:{REDIS_PORT}/1"
    )
    
    # Prepare look data for SocialMediaPoster
    look_data = look.model_dump()
    task_id = str(uuid.uuid4())
    look_data['task_id'] = task_id
    
    # Send task to SocialMediaPoster
    social_media_celery.send_task(
        "src.tasks.post_to_social_media",
        args=[look_data]
    )
    
    return {
        "message": "Look sent to social media queue",
        "task_id": task_id,
        "look_id": look_id
    }
