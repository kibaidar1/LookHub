import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from PIL import Image
from io import BytesIO
import os

from app.application.utils import save_image, delete_image
from app.domain.entities.clothes import Clothes
from app.domain.entities.enums import GenderEnum, ColourEnum


class TestImageUtils:
    """Test cases for image utility functions."""

    @pytest.mark.asyncio
    async def test_save_image_success(self):
        """Test successful image saving."""
        # Arrange
        test_image = Image.new('RGB', (100, 100), color='red')
        filename = "test_image"
        
        # Act
        with patch('app.application.utils.os.path.exists', return_value=False):
            with patch('app.application.utils.os.makedirs'):
                with patch('app.application.utils.Image', return_value=test_image):
                    result = await save_image(test_image, filename)
        
        # Assert
        assert result is not None
        assert isinstance(result, str)

    @pytest.mark.asyncio
    async def test_save_image_with_existing_directory(self):
        """Test image saving when directory already exists."""
        # Arrange
        test_image = Image.new('RGB', (100, 100), color='blue')
        filename = "test_image"
        
        # Act
        with patch('app.application.utils.os.path.exists', return_value=True):
            with patch('app.application.utils.Image', return_value=test_image):
                result = await save_image(test_image, filename)
        
        # Assert
        assert result is not None
        assert isinstance(result, str)

    from unittest.mock import patch

    @pytest.mark.asyncio
    async def test_delete_image_success(self):
        """Test successful image deletion."""
        image_path = "test_image.jpg"

        with patch("app.application.utils.UPLOAD_IMAGES_DIR") as mock_dir:
            mock_path = mock_dir.__truediv__.return_value
            mock_path.exists.return_value = True
            with patch("app.application.utils.os.remove") as mock_remove:
                await delete_image(image_path)
                mock_remove.assert_called_once_with(mock_path)

    @pytest.mark.asyncio
    async def test_delete_image_file_not_found(self):
        """Test image deletion when file doesn't exist."""
        # Arrange
        image_path = "nonexistent_image.jpg"
        
        # Act & Assert
        with patch('app.application.utils.os.remove', side_effect=FileNotFoundError):
            # Should not raise an exception
            await delete_image(image_path)

    @pytest.mark.asyncio
    async def test_delete_image_permission_error(self):
        """Test image deletion with permission error."""
        # Arrange
        image_path = "protected_image.jpg"
        
        # Act & Assert
        with patch('app.application.utils.os.remove', side_effect=PermissionError):
            # Should not raise an exception
            await delete_image(image_path)


class TestValidationUtils:
    """Test cases for validation utility functions."""

    def test_validate_enum_values(self):
        """Test enum value validation."""
        from app.domain.entities.enums import GenderEnum, ColourEnum
        
        # Test valid enum values
        assert GenderEnum.male.value == "мужской"
        assert GenderEnum.female.value == "женский"
        assert GenderEnum.unisex.value == "унисекс"
        
        assert ColourEnum.black.value == "черный"
        assert ColourEnum.white.value == "белый"
        assert ColourEnum.red.value == "красный"

    def test_validate_model_config(self):
        """Test Pydantic model configuration."""
        from app.domain.entities.clothes import Clothes
        from app.domain.entities.looks import Look
        
        # Test that models have correct configuration
        clothes = Clothes(
            name="Test",
            colours=[ColourEnum.black],
            gender=GenderEnum.unisex,
            link="https://example.com",
            image_url="test.jpg"
        )
        
        look = Look(
            name="Test Look",
            gender=GenderEnum.unisex,
            description="Test description",
            image_prompts=["test"],
            image_urls=[]
        )
        
        # Models should be created without errors
        assert clothes.name == "Test"
        assert look.name == "Test Look"


class TestDataTransformation:
    """Test cases for data transformation utilities."""

    def test_model_dump_exclude_unset(self):
        """Test model_dump with exclude_unset parameter."""
        from app.domain.entities.clothes import ClothesCreate
        
        # Create model with some fields set
        clothes = ClothesCreate(
            name="Test T-Shirt",
            colours=[ColourEnum.black],
            gender=GenderEnum.unisex,
            link="https://example.com",
            image_url="test.jpg"
        )
        
        # Test exclude_unset=True
        data = clothes.model_dump(exclude_unset=True)
        assert "name" in data
        assert "colours" in data
        assert "gender" in data
        assert "link" in data
        assert "image_url" in data
        # description should not be in data since it's None
        assert "description" not in data

    def test_model_dump_exclude_defaults(self):
        """Test model_dump with exclude_defaults parameter."""
        from app.domain.entities.looks import LookCreate
        
        # Create model with default values
        look = LookCreate(
            name="Test Look",
            gender=GenderEnum.unisex,
            description="Test description",
            clothes_categories=[],
            image_prompts=["test"],
            image_urls=[],
            content_json=None,
            checked=False,
            pushed=False
        )
        
        # Test exclude_defaults=True
        data = look.model_dump(exclude_defaults=True)
        assert "name" in data
        assert "gender" in data
        assert "description" in data
        assert "clothes_categories" in data
        assert "image_prompts" in data
        # Default values should be excluded
        assert "image_urls" not in data
        assert "content_json" not in data
        assert "checked" not in data
        assert "pushed" not in data

    def test_model_validate(self):
        """Test model_validate method."""
        from app.domain.entities.clothes import ClothesRead
        
        # Test data
        data = {
            "id": 1,
            "name": "Test T-Shirt",
            "description": "A comfortable cotton t-shirt",
            "colours": [ColourEnum.black, ColourEnum.white],
            "gender": GenderEnum.unisex,
            "link": "https://example.com/tshirt",
            "image_url": "test_tshirt.jpg"
        }
        
        # Validate data
        clothes = ClothesRead.model_validate(data)
        
        assert clothes.id == 1
        assert clothes.name == "Test T-Shirt"
        assert clothes.colours == [ColourEnum.black.value, ColourEnum.white.value]


class TestErrorHandling:
    """Test cases for error handling utilities."""

    def test_invalid_enum_value(self):
        """Test handling of invalid enum values."""
        from app.domain.entities.enums import GenderEnum
        
        # Test that invalid enum values raise ValueError
        with pytest.raises(ValueError):
            GenderEnum("invalid_value")

    def test_invalid_model_data(self):
        """Test handling of invalid model data."""
        from app.domain.entities.clothes import ClothesCreate
        
        # Test that missing required fields raise ValidationError
        with pytest.raises(Exception):  # Pydantic validation error
            ClothesCreate(
                # Missing required fields
                name="Test"
                # Missing colours, gender, link, image_url
            )

    def test_invalid_image_data(self):
        """Test handling of invalid image data."""
        # Test with invalid image data
        invalid_image_data = b"invalid_image_data"
        
        with pytest.raises(Exception):  # PIL should raise an error
            Image.open(BytesIO(invalid_image_data))


class TestPerformanceUtils:
    """Test cases for performance-related utilities."""

    def test_large_data_handling(self):
        """Test handling of large data sets."""
        from app.domain.entities.enums import ColourEnum
        
        # Test with large list of colours
        large_colours_list = [ColourEnum.black] * 1000
        
        clothes = Clothes(
            name="Test",
            colours=large_colours_list,
            gender=GenderEnum.unisex,
            link="https://example.com",
            image_url="test.jpg"
        )
        
        # Should handle large data without issues
        assert len(clothes.colours) == 1000

    def test_memory_efficient_processing(self):
        """Test memory-efficient data processing."""
        from app.domain.entities.looks import Look
        
        # Test with large image URLs list
        large_image_urls = [f"image_{i}.jpg" for i in range(100)]
        
        look = Look(
            name="Test Look",
            gender=GenderEnum.unisex,
            description="Test description",
            image_prompts=["test"],
            image_urls=large_image_urls
        )
        
        # Should handle large lists without memory issues
        assert len(look.image_urls) == 100
        assert len(look.get_storage_paths()) == 100 