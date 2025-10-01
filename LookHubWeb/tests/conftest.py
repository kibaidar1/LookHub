import pytest
from unittest.mock import AsyncMock, MagicMock
from typing import Generator

from app.application.interfaces import (
    LooksRepositoryInterface,
    ClothesRepositoryInterface,
    BaseRepositoryInterface,
)
from app.application.use_cases import ClothesUseCase, LooksUseCase
from app.domain.entities.clothes import ClothesCreate, ClothesUpdate, ClothesRead
from app.domain.entities.looks import LookCreate, LookUpdate, LookRead
from app.domain.entities.enums import GenderEnum, ColourEnum
from app.domain.entities.categories import ClothesCategoryCreate


@pytest.fixture
def mock_clothes_repository() -> ClothesRepositoryInterface:
    """Mock repository for clothes operations."""
    mock = AsyncMock(spec=ClothesRepositoryInterface)
    return mock


@pytest.fixture
def mock_looks_repository() -> LooksRepositoryInterface:
    """Mock repository for looks operations."""
    mock = AsyncMock(spec=LooksRepositoryInterface)
    return mock


@pytest.fixture
def clothes_use_case(mock_clothes_repository) -> ClothesUseCase:
    """Clothes use case with mocked repository."""
    return ClothesUseCase(mock_clothes_repository)


@pytest.fixture
def looks_use_case(mock_looks_repository, mock_clothes_repository) -> LooksUseCase:
    """Looks use case with mocked repositories."""
    return LooksUseCase(mock_looks_repository, mock_clothes_repository)


@pytest.fixture
def sample_clothes_data() -> dict:
    """Sample data for creating clothes."""
    return {
        "name": "Test T-Shirt",
        "description": "A comfortable cotton t-shirt",
        "colours": [ColourEnum.black, ColourEnum.white],
        "gender": GenderEnum.unisex,
        "link": "https://example.com/tshirt",
        "image_url": "test_tshirt.jpg"
    }


@pytest.fixture
def sample_look_data() -> dict:
    """Sample data for creating looks."""
    return {
        "name": "Casual Summer Look",
        "gender": GenderEnum.unisex,
        "description": "A comfortable summer outfit",
        "clothes_categories": [],
        "image_prompts": ["casual summer outfit"],
        "image_urls": [],
        "content_json": None,
        "checked": False,
        "pushed": False
    }


@pytest.fixture
def sample_clothes_category_data() -> dict:
    """Sample data for creating clothes categories."""
    return {
        "name": "Tops",
        "clothes": []
    }


@pytest.fixture
def sample_clothes_instance() -> dict:
    """Sample clothes instance as returned by repository."""
    return {
        "id": 1,
        "name": "Test T-Shirt",
        "description": "A comfortable cotton t-shirt",
        "colours": [ColourEnum.black, ColourEnum.white],
        "gender": GenderEnum.unisex,
        "link": "https://example.com/tshirt",
        "image_url": "test_tshirt.jpg"
    }


@pytest.fixture
def sample_look_instance() -> dict:
    """Sample look instance as returned by repository."""
    return {
        "id": 1,
        "name": "Casual Summer Look",
        "gender": GenderEnum.unisex,
        "description": "A comfortable summer outfit",
        "clothes_categories": [],
        "image_prompts": ["casual summer outfit"],
        "image_urls": [],
        "content_json": None,
        "checked": False,
        "pushed": False
    } 