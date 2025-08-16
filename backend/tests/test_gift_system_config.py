import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock

from app.core.enhanced_settings import get_settings
from app.schemas.gift_system import (
    GiftSystemConfig,
    GiftIntegrationSettings,
    GiftSystemPermissions,
    GiftSystemStatus,
    GiftPrivacyMode,
    GiftSuggestionEngine
)

class TestGiftSystemConfiguration:
    """Test gift system configuration and validation"""
    
    def test_gift_system_config_defaults(self):
        """Test default gift system configuration values"""
        settings = get_settings()
        
        # Test default values are set
        assert settings.GIFT_SYSTEM_ENABLED is True
        assert settings.GIFT_DEFAULT_CURRENCY == "USD"
        assert settings.GIFT_MAX_BUDGET == 10000  # Development default
        assert settings.GIFT_SUGGESTION_ENGINE == "basic"
        assert settings.GIFT_AUTO_CREATE_TASKS is True
        assert settings.GIFT_PRIVACY_MODE == "personal"
        assert settings.GIFT_IMAGE_STORAGE is True
        assert settings.GIFT_EXTERNAL_LINKS is True
    
    def test_gift_reminder_days_parsing(self):
        """Test parsing of gift reminder days from configuration"""
        settings = get_settings()
        
        reminder_days = settings.get_gift_reminder_days()
        assert isinstance(reminder_days, list)
        assert len(reminder_days) > 0
        assert all(isinstance(day, int) for day in reminder_days)
        assert all(day > 0 for day in reminder_days)
    
    @patch.dict('os.environ', {
        'GIFT_REMINDER_DAYS': '14,7,3,1',
        'GIFT_MAX_BUDGET': '5000'
    })
    def test_gift_config_environment_override(self):
        """Test that environment variables override default configuration"""
        settings = get_settings(reload=True)
        
        reminder_days = settings.get_gift_reminder_days()
        assert reminder_days == [14, 7, 3, 1]
        assert settings.GIFT_MAX_BUDGET == 5000
    
    def test_gift_system_schema_validation(self):
        """Test gift system configuration schema validation"""
        # Valid configuration
        config = GiftSystemConfig(
            enabled=True,
            default_budget_currency="USD",
            max_budget_amount=1000,
            suggestion_engine=GiftSuggestionEngine.BASIC,
            reminder_advance_days=[7, 3, 1],
            auto_create_tasks=True,
            privacy_mode=GiftPrivacyMode.PERSONAL,
            image_storage_enabled=True,
            external_links_enabled=True
        )
        
        assert config.enabled is True
        assert config.max_budget_amount == 1000
        assert config.reminder_advance_days == [7, 3, 1]
    
    def test_gift_budget_validation(self):
        """Test gift budget amount validation"""
        # Invalid budget: zero
        with pytest.raises(ValueError, match="Maximum budget must be greater than 0"):
            GiftSystemConfig(max_budget_amount=0)
        
        # Invalid budget: negative
        with pytest.raises(ValueError, match="Maximum budget must be greater than 0"):
            GiftSystemConfig(max_budget_amount=-100)
        
        # Invalid budget: too high
        with pytest.raises(ValueError, match="Maximum budget cannot exceed"):
            GiftSystemConfig(max_budget_amount=200000)
    
    def test_gift_reminder_days_validation(self):
        """Test gift reminder days validation and normalization"""
        # Empty list should get default
        config = GiftSystemConfig(reminder_advance_days=[])
        assert config.reminder_advance_days == [7, 3, 1]
        
        # Negative/zero values should be filtered out
        config = GiftSystemConfig(reminder_advance_days=[14, 0, -1, 7, 3])
        assert config.reminder_advance_days == [14, 7, 3]
        
        # Duplicates should be removed and sorted
        config = GiftSystemConfig(reminder_advance_days=[7, 14, 7, 3, 14, 1])
        assert config.reminder_advance_days == [14, 7, 3, 1]
    
    def test_gift_image_extensions(self):
        """Test gift allowed image extensions parsing"""
        settings = get_settings()
        
        # When image storage is enabled
        settings.GIFT_IMAGE_STORAGE = True
        settings.ALLOWED_EXTENSIONS = "jpg,jpeg,png,gif,pdf,txt"
        
        allowed = settings.get_gift_allowed_extensions()
        expected_image_extensions = ['jpg', 'jpeg', 'png', 'gif']
        assert all(ext in allowed for ext in expected_image_extensions)
        assert 'pdf' not in allowed  # Non-image extension should be filtered
        assert 'txt' not in allowed  # Non-image extension should be filtered
        
        # When image storage is disabled
        settings.GIFT_IMAGE_STORAGE = False
        allowed = settings.get_gift_allowed_extensions()
        assert allowed == []

class TestGiftSystemAPI:
    """Test gift system API endpoints"""
    
    def test_get_gift_system_config(self, client: TestClient, auth_headers: dict):
        """Test GET /api/v1/config/gift-system/config endpoint"""
        response = client.get("/api/v1/config/gift-system/config", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        
        # Validate response structure
        assert "enabled" in data
        assert "default_budget_currency" in data
        assert "max_budget_amount" in data
        assert "suggestion_engine" in data
        assert "reminder_advance_days" in data
        assert "auto_create_tasks" in data
        assert "privacy_mode" in data
        assert "image_storage_enabled" in data
        assert "external_links_enabled" in data
        
        # Validate data types
        assert isinstance(data["enabled"], bool)
        assert isinstance(data["max_budget_amount"], int)
        assert isinstance(data["reminder_advance_days"], list)
    
    def test_get_gift_integration_settings(self, client: TestClient, auth_headers: dict):
        """Test GET /api/v1/config/gift-system/integration-settings endpoint"""
        response = client.get("/api/v1/config/gift-system/integration-settings", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        
        # Validate integration settings structure
        integration_fields = [
            "contact_integration_enabled",
            "auto_suggest_from_relationships", 
            "use_contact_preferences",
            "financial_integration_enabled",
            "track_gift_expenses",
            "budget_alerts_enabled",
            "reminder_integration_enabled",
            "create_occasion_reminders",
            "create_shopping_reminders",
            "task_integration_enabled",
            "create_shopping_tasks",
            "create_wrapping_tasks"
        ]
        
        for field in integration_fields:
            assert field in data
            assert isinstance(data[field], bool)
    
    def test_get_gift_system_permissions(self, client: TestClient, auth_headers: dict):
        """Test GET /api/v1/config/gift-system/permissions endpoint"""
        response = client.get("/api/v1/config/gift-system/permissions", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        
        # Validate permissions structure
        permission_fields = [
            "can_view_gifts",
            "can_create_gifts",
            "can_edit_gifts", 
            "can_delete_gifts",
            "can_manage_budgets",
            "can_view_others_gifts",
            "can_export_gift_data",
            "can_configure_system"
        ]
        
        for field in permission_fields:
            assert field in data
            assert isinstance(data[field], bool)
        
        # Basic security checks
        if data["can_view_gifts"]:
            # If user can view gifts, they should also be able to create them
            assert data["can_create_gifts"] is True
        
        # Users should not have system configuration access by default
        assert data["can_configure_system"] is False
    
    def test_get_gift_system_status(self, client: TestClient, auth_headers: dict):
        """Test GET /api/v1/config/gift-system/status endpoint"""
        response = client.get("/api/v1/config/gift-system/status", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        
        # Validate status structure
        assert "is_enabled" in data
        assert "configuration_valid" in data
        assert "integration_status" in data
        assert "version" in data
        
        # Validate integration status
        integration_status = data["integration_status"]
        expected_integrations = ["contacts", "financial", "reminders", "tasks", "storage", "external_links"]
        
        for integration in expected_integrations:
            assert integration in integration_status
            assert isinstance(integration_status[integration], bool)
    
    def test_get_gift_categories(self, client: TestClient, auth_headers: dict):
        """Test GET /api/v1/config/gift-system/reference-data/categories endpoint"""
        response = client.get("/api/v1/config/gift-system/reference-data/categories", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        
        assert isinstance(data, list)
        assert len(data) > 0
        
        # Validate category structure
        category = data[0]
        required_fields = ["key", "display_name", "description", "tags"]
        
        for field in required_fields:
            assert field in category
        
        assert isinstance(category["tags"], list)
    
    def test_get_gift_occasions(self, client: TestClient, auth_headers: dict):
        """Test GET /api/v1/config/gift-system/reference-data/occasions endpoint"""
        response = client.get("/api/v1/config/gift-system/reference-data/occasions", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        
        assert isinstance(data, list)
        assert len(data) > 0
        
        # Validate occasion structure
        occasion = data[0]
        required_fields = ["key", "display_name", "frequency", "advance_reminder_days"]
        
        for field in required_fields:
            assert field in occasion
        
        assert isinstance(occasion["advance_reminder_days"], list)
    
    def test_get_gift_budget_ranges(self, client: TestClient, auth_headers: dict):
        """Test GET /api/v1/config/gift-system/reference-data/budget-ranges endpoint"""
        response = client.get("/api/v1/config/gift-system/reference-data/budget-ranges", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        
        assert isinstance(data, list)
        assert len(data) > 0
        
        # Validate budget range structure
        budget_range = data[0]
        required_fields = ["key", "display_name", "min_amount", "currency"]
        
        for field in required_fields:
            assert field in budget_range
        
        assert isinstance(budget_range["min_amount"], int)
        assert budget_range["min_amount"] >= 0
    
    @patch('app.core.enhanced_settings.get_settings')
    def test_disabled_gift_system_access(self, mock_settings, client: TestClient, auth_headers: dict):
        """Test API responses when gift system is disabled"""
        # Mock disabled gift system
        mock_settings.return_value.GIFT_SYSTEM_ENABLED = False
        
        endpoints = [
            "/api/v1/config/gift-system/reference-data/categories",
            "/api/v1/config/gift-system/reference-data/occasions", 
            "/api/v1/config/gift-system/reference-data/budget-ranges"
        ]
        
        for endpoint in endpoints:
            response = client.get(endpoint, headers=auth_headers)
            assert response.status_code == 404
            assert "Gift system is not enabled" in response.json()["detail"]

class TestGiftSystemIntegration:
    """Test gift system integration with other modules"""
    
    def test_contact_integration_config(self):
        """Test gift system integration with contact module"""
        settings = GiftIntegrationSettings()
        
        assert settings.contact_integration_enabled is True
        assert settings.auto_suggest_from_relationships is True
        assert settings.use_contact_preferences is True
    
    def test_financial_integration_config(self):
        """Test gift system integration with financial module"""
        settings = GiftIntegrationSettings()
        
        assert settings.financial_integration_enabled is True
        assert settings.track_gift_expenses is True
        assert settings.budget_alerts_enabled is True
    
    def test_reminder_integration_config(self):
        """Test gift system integration with reminder module"""
        settings = GiftIntegrationSettings()
        
        assert settings.reminder_integration_enabled is True
        assert settings.create_occasion_reminders is True
        assert settings.create_shopping_reminders is True
    
    def test_task_integration_config(self):
        """Test gift system integration with task module"""
        settings = GiftIntegrationSettings()
        
        assert settings.task_integration_enabled is True
        assert settings.create_shopping_tasks is True
        # Wrapping tasks are optional
        assert settings.create_wrapping_tasks is False

class TestGiftSystemSecurity:
    """Test gift system security and privacy configurations"""
    
    def test_privacy_mode_personal(self):
        """Test personal privacy mode configuration"""
        config = GiftSystemConfig(privacy_mode=GiftPrivacyMode.PERSONAL)
        assert config.privacy_mode == "personal"
    
    def test_privacy_mode_strict(self):
        """Test strict privacy mode configuration"""
        config = GiftSystemConfig(privacy_mode=GiftPrivacyMode.STRICT)
        assert config.privacy_mode == "strict"
    
    def test_default_permissions_security(self):
        """Test that default permissions follow security best practices"""
        permissions = GiftSystemPermissions()
        
        # Users should not have access to others' gifts by default
        assert permissions.can_view_others_gifts is False
        
        # Users should not have system configuration access by default
        assert permissions.can_configure_system is False
        
        # Users should have basic gift management permissions
        assert permissions.can_view_gifts is True
        assert permissions.can_create_gifts is True
        assert permissions.can_edit_gifts is True
    
    def test_production_vs_development_security(self):
        """Test security differences between production and development"""
        # Development settings (more permissive)
        dev_config = GiftSystemConfig(
            privacy_mode=GiftPrivacyMode.PERSONAL,
            image_storage_enabled=True,
            external_links_enabled=True
        )
        
        # Production settings (more restrictive)
        prod_config = GiftSystemConfig(
            privacy_mode=GiftPrivacyMode.STRICT,
            image_storage_enabled=False,
            external_links_enabled=False
        )
        
        # Production should be more restrictive
        assert prod_config.privacy_mode == "strict"
        assert dev_config.privacy_mode == "personal"
        assert prod_config.image_storage_enabled is False
        assert prod_config.external_links_enabled is False