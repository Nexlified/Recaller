def test_root_endpoint(client):
    """Test the root endpoint returns correct response"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Welcome to Recaller API!"
    assert data["documentation"] == "/docs"

def test_openapi_endpoint(client):
    """Test the OpenAPI endpoint is accessible"""
    response = client.get("/api/v1/openapi.json")
    assert response.status_code == 200
    data = response.json()
    assert "openapi" in data
    assert data["info"]["title"] == "Recaller"