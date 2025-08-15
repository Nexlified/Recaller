import pytest
from decimal import Decimal
from datetime import date
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture
def client():
    """Create a test client."""
    with TestClient(app) as test_client:
        yield test_client


def test_personal_debt_endpoints_structure(client):
    """Test that personal debt endpoints are properly defined and accessible."""
    # Test GET /personal-debts/ endpoint exists (will return 401 without auth)
    response = client.get("/api/v1/personal-debts/")
    # We expect 401 Unauthorized since we're not authenticated
    assert response.status_code == 401
    
    # Test POST /personal-debts/ endpoint exists (will return 401 without auth)
    response = client.post("/api/v1/personal-debts/", json={})
    assert response.status_code == 401
    
    # Test GET /personal-debts/summary endpoint exists
    response = client.get("/api/v1/personal-debts/summary")
    assert response.status_code == 401
    
    # Test GET /personal-debts/overdue endpoint exists
    response = client.get("/api/v1/personal-debts/overdue")
    assert response.status_code == 401
    
    # Test GET /personal-debts/owed-to-me endpoint exists
    response = client.get("/api/v1/personal-debts/owed-to-me")
    assert response.status_code == 401
    
    # Test GET /personal-debts/i-owe endpoint exists
    response = client.get("/api/v1/personal-debts/i-owe")
    assert response.status_code == 401


def test_openapi_schema_includes_personal_debts(client):
    """Test that the OpenAPI schema includes personal debt endpoints."""
    response = client.get("/openapi.json")
    assert response.status_code == 200
    
    openapi_spec = response.json()
    paths = openapi_spec.get("paths", {})
    
    # Check that personal debt endpoints are in the OpenAPI spec
    assert "/api/v1/personal-debts/" in paths
    assert "/api/v1/personal-debts/summary" in paths
    assert "/api/v1/personal-debts/overdue" in paths
    assert "/api/v1/personal-debts/owed-to-me" in paths
    assert "/api/v1/personal-debts/i-owe" in paths
    assert "/api/v1/personal-debts/{debt_id}" in paths
    assert "/api/v1/personal-debts/{debt_id}/payments" in paths
    assert "/api/v1/personal-debts/payments/{payment_id}" in paths
    
    # Check that the endpoints have proper HTTP methods
    personal_debts_path = paths["/api/v1/personal-debts/"]
    assert "get" in personal_debts_path  # List debts
    assert "post" in personal_debts_path  # Create debt
    
    debt_detail_path = paths["/api/v1/personal-debts/{debt_id}"]
    assert "get" in debt_detail_path  # Get debt
    assert "put" in debt_detail_path  # Update debt
    assert "delete" in debt_detail_path  # Delete debt
    
    payments_path = paths["/api/v1/personal-debts/{debt_id}/payments"]
    assert "get" in payments_path  # List payments
    assert "post" in payments_path  # Create payment


def test_personal_debt_schemas_in_openapi(client):
    """Test that personal debt schemas are properly defined in OpenAPI."""
    response = client.get("/openapi.json")
    assert response.status_code == 200
    
    openapi_spec = response.json()
    components = openapi_spec.get("components", {})
    schemas = components.get("schemas", {})
    
    # Check that our schemas are defined
    assert "PersonalDebt" in schemas
    assert "PersonalDebtCreate" in schemas
    assert "PersonalDebtUpdate" in schemas
    assert "PersonalDebtWithPayments" in schemas
    assert "PersonalDebtSummary" in schemas
    assert "DebtPayment" in schemas
    assert "DebtPaymentCreate" in schemas
    assert "DebtPaymentUpdate" in schemas
    
    # Check PersonalDebt schema has required fields
    personal_debt_schema = schemas["PersonalDebt"]
    properties = personal_debt_schema.get("properties", {})
    
    expected_fields = [
        "id", "user_id", "tenant_id", "creditor_contact_id", "debtor_contact_id",
        "debt_type", "amount", "currency", "status", "payment_status", "created_at"
    ]
    
    for field in expected_fields:
        assert field in properties, f"Field {field} missing from PersonalDebt schema"


def test_personal_debt_tags_in_openapi(client):
    """Test that personal debt endpoints are properly tagged."""
    response = client.get("/openapi.json")
    assert response.status_code == 200
    
    openapi_spec = response.json()
    paths = openapi_spec.get("paths", {})
    
    # Check that personal debt endpoints have the right tag
    personal_debts_path = paths["/api/v1/personal-debts/"]
    get_operation = personal_debts_path.get("get", {})
    post_operation = personal_debts_path.get("post", {})
    
    assert "Personal Debts" in get_operation.get("tags", [])
    assert "Personal Debts" in post_operation.get("tags", [])