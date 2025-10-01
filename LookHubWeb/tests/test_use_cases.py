import pytest
from unittest.mock import AsyncMock, MagicMock
from app.application.use_cases import ClothesUseCase, LooksUseCase
from app.domain.entities.clothes import ClothesCreate, ClothesUpdate, ClothesRead
from app.domain.entities.looks import LookCreate, LookUpdate, LookRead
from app.domain.entities.enums import GenderEnum, ColourEnum
from app.domain.entities.categories import ClothesCategoryCreate


class TestClothesUseCase:
    """Test cases for ClothesUseCase."""

    @pytest.mark.asyncio
    async def test_add_one_success(self, clothes_use_case, mock_clothes_repository, sample_clothes_data, sample_clothes_instance):
        """Test successful clothes creation."""
        # Arrange
        clothes_data = ClothesCreate(**sample_clothes_data)
        mock_clothes_repository.add_one.return_value = sample_clothes_instance
        
        # Act
        result = await clothes_use_case.add_one(clothes_data)
        
        # Assert
        assert isinstance(result, ClothesRead)
        assert result.id == 1
        assert result.name == "Test T-Shirt"
        mock_clothes_repository.add_one.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_one_by_id_success(self, clothes_use_case, mock_clothes_repository, sample_clothes_instance):
        """Test successful clothes retrieval by ID."""
        # Arrange
        mock_clothes_repository.get_one_by_id.return_value = sample_clothes_instance
        
        # Act
        result = await clothes_use_case.get_one_by_id(1)
        
        # Assert
        assert isinstance(result, ClothesRead)
        assert result.id == 1
        assert result.name == "Test T-Shirt"
        mock_clothes_repository.get_one_by_id.assert_called_once_with(1)

    @pytest.mark.asyncio
    async def test_update_one_success(self, clothes_use_case, mock_clothes_repository, sample_clothes_instance):
        """Test successful clothes update."""
        # Arrange
        update_data = ClothesUpdate(name="Updated T-Shirt")
        mock_clothes_repository.update_one.return_value = sample_clothes_instance
        
        # Act
        result = await clothes_use_case.update_one(1, update_data)
        
        # Assert
        assert isinstance(result, ClothesRead)
        assert result.id == 1
        mock_clothes_repository.update_one.assert_called_once_with(1, {"name": "Updated T-Shirt"})

    @pytest.mark.asyncio
    async def test_delete_one_success(self, clothes_use_case, mock_clothes_repository):
        """Test successful clothes deletion."""
        # Arrange
        mock_clothes_repository.delete_one.return_value = True
        
        # Act
        result = await clothes_use_case.delete_one(1)
        
        # Assert
        assert result is True
        mock_clothes_repository.delete_one.assert_called_once_with(1)

    @pytest.mark.asyncio
    async def test_get_list_success(self, clothes_use_case, mock_clothes_repository, sample_clothes_instance):
        """Test successful clothes list retrieval."""
        # Arrange
        mock_clothes_repository.get_list.return_value = ([sample_clothes_instance], 1)
        
        # Act
        result, total = await clothes_use_case.get_list(page=1, page_size=10)
        
        # Assert
        assert len(result) == 1
        assert total == 1
        assert isinstance(result[0], ClothesRead)
        mock_clothes_repository.get_list.assert_called_once_with(0, 10, "id", True, **{})

    @pytest.mark.asyncio
    async def test_get_list_by_ids_success(self, clothes_use_case, mock_clothes_repository, sample_clothes_instance):
        """Test successful clothes retrieval by IDs."""
        # Arrange
        mock_clothes_repository.get_list_by_ids.return_value = [sample_clothes_instance]
        
        # Act
        result = await clothes_use_case.get_list_by_ids([1, 2])
        
        # Assert
        assert len(result) == 1
        assert isinstance(result[0], ClothesRead)
        mock_clothes_repository.get_list_by_ids.assert_called_once_with([1, 2])


class TestLooksUseCase:
    """Test cases for LooksUseCase."""

    @pytest.mark.asyncio
    async def test_add_one_success(self, looks_use_case, mock_looks_repository, sample_look_data, sample_look_instance):
        """Test successful look creation."""
        # Arrange
        look_data = LookCreate(**sample_look_data)
        mock_looks_repository.add_one.return_value = sample_look_instance
        
        # Act
        result = await looks_use_case.add_one(look_data)
        
        # Assert
        assert isinstance(result, LookRead)
        assert result.id == 1
        assert result.name == "Casual Summer Look"
        mock_looks_repository.add_one.assert_called_once()

    @pytest.mark.asyncio
    async def test_add_clothes_categories_success(self, looks_use_case, mock_looks_repository, sample_look_instance):
        """Test successful addition of clothes categories to a look."""
        # Arrange
        categories = [
            ClothesCategoryCreate(name="Tops", description="Upper body", clothes=[]),
            ClothesCategoryCreate(name="Bottoms", description="Lower body", clothes=[])
        ]
        mock_looks_repository.add_clothes_category.return_value = sample_look_instance
        
        # Act
        result = await looks_use_case.add_clothes_categories(1, categories)
        
        # Assert
        assert isinstance(result, LookRead)
        assert mock_looks_repository.add_clothes_category.call_count == 2

    @pytest.mark.asyncio
    async def test_add_clothes_to_category_success(self, looks_use_case, mock_looks_repository, sample_look_instance):
        """Test successful addition of clothes to a category."""
        # Arrange
        mock_looks_repository.add_clothes_to_clothes_category.return_value = sample_look_instance
        
        # Act
        result = await looks_use_case.add_clothes_to_category(1, 1, 1)
        
        # Assert
        assert isinstance(result, LookRead)
        mock_looks_repository.add_clothes_to_clothes_category.assert_called_once_with(1, 1)

    @pytest.mark.asyncio
    async def test_delete_clothes_category_success(self, looks_use_case, mock_looks_repository, sample_look_instance):
        """Test successful deletion of clothes category."""
        # Arrange
        mock_looks_repository.delete_clothes_category.return_value = sample_look_instance
        
        # Act
        result = await looks_use_case.delete_clothes_category(1, 1)
        
        # Assert
        assert isinstance(result, LookRead)
        mock_looks_repository.delete_clothes_category.assert_called_once_with(1, 1)

    @pytest.mark.asyncio
    async def test_delete_clothes_from_category_success(self, looks_use_case, mock_looks_repository, sample_look_instance):
        """Test successful deletion of clothes from category."""
        # Arrange
        mock_looks_repository.delete_clothes_from_clothes_category.return_value = sample_look_instance
        
        # Act
        result = await looks_use_case.delete_clothes_from_category(1, 1, 1)
        
        # Assert
        assert isinstance(result, LookRead)
        mock_looks_repository.delete_clothes_from_clothes_category.assert_called_once_with(1, 1)

    @pytest.mark.asyncio
    async def test_get_one_by_id_success(self, looks_use_case, mock_looks_repository, sample_look_instance):
        """Test successful look retrieval by ID."""
        # Arrange
        mock_looks_repository.get_one_by_id.return_value = sample_look_instance
        
        # Act
        result = await looks_use_case.get_one_by_id(1)
        
        # Assert
        assert isinstance(result, LookRead)
        assert result.id == 1
        assert result.name == "Casual Summer Look"
        mock_looks_repository.get_one_by_id.assert_called_once_with(1)

    @pytest.mark.asyncio
    async def test_update_one_success(self, looks_use_case, mock_looks_repository, sample_look_instance):
        """Test successful look update."""
        # Arrange
        update_data = LookUpdate(name="Casual Summer Look")
        mock_looks_repository.update_one.return_value = sample_look_instance
        mock_looks_repository.get_one_by_id.return_value = sample_look_instance  # <--- ВАЖНО

        # Act
        result = await looks_use_case.update_one(1, update_data)

        # Assert
        assert isinstance(result, LookRead)
        assert result.id == 1
        assert result.name == "Casual Summer Look"
        mock_looks_repository.update_one.assert_called_once_with(1, {"name": "Casual Summer Look"})

    @pytest.mark.asyncio
    async def test_delete_one_success(self, looks_use_case, mock_looks_repository, sample_look_instance):
        """Test successful look deletion."""
        # Arrange
        mock_looks_repository.delete_one.return_value = True
        mock_looks_repository.get_one_by_id.return_value = sample_look_instance  # <--- ВАЖНО

        # Act
        result = await looks_use_case.delete_one(1)

        # Assert
        assert result is True
        mock_looks_repository.delete_one.assert_called_once_with(1)

    @pytest.mark.asyncio
    async def test_get_list_success(self, looks_use_case, mock_looks_repository, sample_look_instance):
        """Test successful look list retrieval."""
        # Arrange
        mock_looks_repository.get_list.return_value = ([sample_look_instance], 1)
        
        # Act
        result, total = await looks_use_case.get_list(page=1, page_size=10)
        
        # Assert
        assert len(result) == 1
        assert total == 1
        assert isinstance(result[0], LookRead)
        mock_looks_repository.get_list.assert_called_once_with(0, 10, "id", True, **{})

    @pytest.mark.asyncio
    async def test_get_list_by_ids_success(self, looks_use_case, mock_looks_repository, sample_look_instance):
        """Test successful look retrieval by IDs."""
        # Arrange
        mock_looks_repository.get_list_by_ids.return_value = [sample_look_instance]
        
        # Act
        result = await looks_use_case.get_list_by_ids([1, 2])
        
        # Assert
        assert len(result) == 1
        assert isinstance(result[0], LookRead)
        mock_looks_repository.get_list_by_ids.assert_called_once_with([1, 2])


class TestBaseUseCase:
    """Test cases for base CRUD use case functionality."""

    @pytest.mark.asyncio
    async def test_entity_type_attributes(self, clothes_use_case):
        """Test that use case has correct entity type attributes."""
        assert clothes_use_case._entity_create == ClothesCreate
        assert clothes_use_case._entity_update == ClothesUpdate
        assert clothes_use_case._entity_read == ClothesRead

    @pytest.mark.asyncio
    async def test_repository_injection(self, clothes_use_case, mock_clothes_repository):
        """Test that repository is properly injected."""
        assert clothes_use_case.repository == mock_clothes_repository
        assert clothes_use_case.clothes_repository == mock_clothes_repository 