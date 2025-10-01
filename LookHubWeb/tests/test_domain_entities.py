import pytest
from app.domain.entities.clothes import Clothes, ClothesCreate, ClothesUpdate, ClothesRead
from app.domain.entities.looks import Look, LookCreate, LookUpdate, LookRead
from app.domain.entities.enums import GenderEnum, ColourEnum
from app.domain.entities.categories import ClothesCategoryCreate
from app.config import API_HOST


class TestClothesEntity:
    """Test cases for Clothes domain entities."""

    def test_clothes_create_valid_data(self):
        """Test creating ClothesCreate with valid data."""
        data = {
            "name": "Test T-Shirt",
            "description": "A comfortable cotton t-shirt",
            "colours": [ColourEnum.black, ColourEnum.white],
            "gender": GenderEnum.unisex,
            "link": "https://example.com/tshirt",
            "image_url": "test_tshirt.jpg"
        }
        
        clothes = ClothesCreate(**data)
        
        assert clothes.name == "Test T-Shirt"
        assert clothes.description == "A comfortable cotton t-shirt"
        assert clothes.colours == [ColourEnum.black.value, ColourEnum.white.value]
        assert clothes.gender == GenderEnum.unisex.value
        assert clothes.link == "https://example.com/tshirt"
        assert clothes.image_url == "test_tshirt.jpg"

    def test_clothes_update_with_defaults(self):
        """Test ClothesUpdate with default values."""
        clothes = ClothesUpdate()
        
        assert clothes.clothes_id == ""
        assert clothes.name == ""
        assert clothes.description == ""
        assert clothes.colours == [ColourEnum.black]
        assert clothes.gender == GenderEnum.unisex
        assert clothes.link == ""
        assert clothes.image_url == ""

    def test_clothes_read_with_id(self):
        """Test ClothesRead with ID field."""
        data = {
            "id": 1,
            "name": "Test T-Shirt",
            "description": "A comfortable cotton t-shirt",
            "colours": [ColourEnum.black, ColourEnum.white],
            "gender": GenderEnum.unisex,
            "link": "https://example.com/tshirt",
            "image_url": "test_tshirt.jpg"
        }
        
        clothes = ClothesRead(**data)
        
        assert clothes.id == 1
        assert clothes.name == "Test T-Shirt"
        assert clothes.colours == [ColourEnum.black.value, ColourEnum.white.value]

    def test_clothes_model_config(self):
        """Test that Clothes model configuration is correct."""
        clothes = Clothes(
            name="Test",
            colours=[ColourEnum.black],
            gender=GenderEnum.unisex,
            link="https://example.com",
            image_url="test.jpg"
        )
        
        # Test that enum values are used
        assert clothes.gender == "унисекс"
        assert clothes.colours[0] == "черный"


class TestLookEntity:
    """Test cases for Look domain entities."""

    def test_look_create_valid_data(self):
        """Test creating LookCreate with valid data."""
        data = {
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
        
        look = LookCreate(**data)
        
        assert look.name == "Casual Summer Look"
        assert look.gender == GenderEnum.unisex.value
        assert look.description == "A comfortable summer outfit"
        assert look.image_prompts == ["casual summer outfit"]
        assert look.image_urls == []
        assert look.checked is False
        assert look.pushed is False

    def test_look_update_with_defaults(self):
        """Test LookUpdate with default values."""
        look = LookUpdate()
        
        assert look.name == ""
        assert look.gender == GenderEnum.unisex
        assert look.description == ""
        assert look.clothes_categories == []
        assert look.image_prompts == []

    def test_look_read_with_id(self):
        """Test LookRead with ID field."""
        data = {
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
        
        look = LookRead(**data)
        
        assert look.id == 1
        assert look.name == "Casual Summer Look"
        assert look.gender == GenderEnum.unisex.value

    def test_look_image_urls_processing(self):
        """Test image URL processing in Look entity."""
        # Test adding API_HOST prefix
        look = Look(
            name="Test Look",
            gender=GenderEnum.unisex,
            description="Test description",
            image_prompts=["test"],
            image_urls=["image1.jpg", "image2.jpg"]
        )
        
        expected_urls = [f"{API_HOST}/images/image1.jpg", f"{API_HOST}/images/image2.jpg"]
        assert look.image_urls == expected_urls

    def test_look_get_storage_paths(self):
        """Test get_storage_paths method."""
        look = Look(
            name="Test Look",
            gender=GenderEnum.unisex,
            description="Test description",
            image_prompts=["test"],
            image_urls=[f"{API_HOST}/images/image1.jpg", f"{API_HOST}/images/image2.jpg"]
        )
        
        storage_paths = look.get_storage_paths()
        assert storage_paths == ["image1.jpg", "image2.jpg"]

    def test_look_image_urls_with_existing_http(self):
        """Test image URLs that already have http prefix."""
        look = Look(
            name="Test Look",
            gender=GenderEnum.unisex,
            description="Test description",
            image_prompts=["test"],
            image_urls=["https://external.com/image1.jpg", "image2.jpg"]
        )
        
        expected_urls = ["https://external.com/image1.jpg", f"{API_HOST}/images/image2.jpg"]
        assert look.image_urls == expected_urls


class TestEnums:
    """Test cases for enum classes."""

    def test_gender_enum_values(self):
        """Test GenderEnum values."""
        assert GenderEnum.male.value == "мужской"
        assert GenderEnum.female.value == "женский"
        assert GenderEnum.unisex.value == "унисекс"

    def test_gender_enum_str(self):
        """Test GenderEnum string representation."""
        assert str(GenderEnum.male) == "male"
        assert str(GenderEnum.female) == "female"
        assert str(GenderEnum.unisex) == "unisex"

    def test_colour_enum_values(self):
        """Test ColourEnum values."""
        assert ColourEnum.black.value == "черный"
        assert ColourEnum.white.value == "белый"
        assert ColourEnum.red.value == "красный"
        assert ColourEnum.blue.value == "синий"

    def test_colour_enum_str(self):
        """Test ColourEnum string representation."""
        assert str(ColourEnum.black) == "black"
        assert str(ColourEnum.white) == "white"
        assert str(ColourEnum.red) == "red"


class TestClothesCategoryCreate:
    """Test cases for ClothesCategoryCreate entity."""

    def test_clothes_category_create_valid_data(self):
        """Test creating ClothesCategoryCreate with valid data."""
        data = {
            "name": "Tops",
            "clothes": []
        }
        
        category = ClothesCategoryCreate(**data)
        
        assert category.name == "Tops"
        assert category.clothes == [] 