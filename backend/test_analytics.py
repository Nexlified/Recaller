import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.api.deps import get_db

# Create test database without creating tables (since we have JSONB issues with SQLite)
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

# Create minimal test tables compatible with SQLite
with engine.connect() as conn:
    conn.execute(text("CREATE TABLE IF NOT EXISTS tenants (id INTEGER PRIMARY KEY, name TEXT, slug TEXT UNIQUE, is_active BOOLEAN DEFAULT TRUE, created_at DATETIME DEFAULT CURRENT_TIMESTAMP)"))
    conn.execute(text("INSERT OR IGNORE INTO tenants (id, name, slug) VALUES (1, 'Test Tenant', 'test')"))
    conn.commit()

client = TestClient(app)

def test_analytics_overview():
    """Test analytics overview endpoint"""
    response = client.get("/api/v1/analytics/overview")
    assert response.status_code == 200
    
    data = response.json()
    assert "summary" in data
    assert "network_health" in data
    assert "recent_activity" in data
    assert "top_insights" in data
    
    # Check summary structure
    summary = data["summary"]
    assert "total_contacts" in summary
    assert "active_contacts" in summary
    assert "strong_relationships" in summary

def test_analytics_summary():
    """Test analytics summary endpoint"""
    response = client.get("/api/v1/analytics/summary")
    assert response.status_code == 200
    
    data = response.json()
    assert "total_contacts" in data
    assert "active_contacts" in data
    assert "avg_connection_strength" in data
    assert isinstance(data["total_contacts"], int)
    assert isinstance(data["avg_connection_strength"], float)

def test_analytics_trends():
    """Test analytics trends endpoint"""
    response = client.get("/api/v1/analytics/trends?period=30")
    assert response.status_code == 200
    
    data = response.json()
    assert isinstance(data, list)
    # Should return empty list when no data

def test_analytics_kpis():
    """Test KPIs endpoint"""
    response = client.get("/api/v1/analytics/kpis")
    assert response.status_code == 200
    
    data = response.json()
    assert "network_size" in data
    assert "network_health_score" in data
    assert "engagement_rate" in data
    assert "growth_rate" in data

def test_network_overview():
    """Test network overview endpoint"""
    response = client.get("/api/v1/analytics/network/overview")
    assert response.status_code == 200
    
    data = response.json()
    assert "network_size" in data
    assert "active_contacts" in data
    assert "network_health" in data

def test_network_growth():
    """Test network growth endpoint"""
    response = client.get("/api/v1/analytics/network/growth?period=90")
    assert response.status_code == 200
    
    data = response.json()
    assert "growth_metrics" in data
    assert "growth_timeline" in data
    assert "growth_sources" in data
    assert "predictions" in data

def test_relationship_health():
    """Test relationship health endpoint"""
    response = client.get("/api/v1/analytics/network/health")
    assert response.status_code == 200
    
    data = response.json()
    assert "overall_health" in data
    assert "health_factors" in data
    assert "recommendations" in data

def test_interactions_overview():
    """Test interactions overview endpoint"""
    response = client.get("/api/v1/analytics/interactions/overview")
    assert response.status_code == 200
    
    data = response.json()
    assert "total_interactions" in data
    assert "avg_quality" in data
    assert "recent_activity" in data

def test_interaction_types():
    """Test interaction types breakdown endpoint"""
    response = client.get("/api/v1/analytics/interactions/types")
    assert response.status_code == 200
    
    data = response.json()
    assert "meetings" in data
    assert "calls" in data
    assert "emails" in data
    assert "texts" in data

def test_insights_endpoint():
    """Test insights endpoint"""
    response = client.get("/api/v1/analytics/insights?limit=5")
    assert response.status_code == 200
    
    data = response.json()
    assert isinstance(data, list)
    # Should return empty list when no insights

def test_insights_generation():
    """Test insights generation endpoint"""
    response = client.post("/api/v1/analytics/insights/generate", json={
        "insight_types": ["network_growth", "relationship_health"],
        "force_regenerate": False
    })
    assert response.status_code == 200
    
    data = response.json()
    assert isinstance(data, list)

def test_recommendations():
    """Test recommendations endpoint"""
    response = client.get("/api/v1/analytics/recommendations")
    assert response.status_code == 200
    
    data = response.json()
    assert isinstance(data, list)

if __name__ == "__main__":
    # Run basic tests
    print("Running analytics API tests...")
    
    try:
        test_analytics_overview()
        print("✓ Analytics overview test passed")
        
        test_analytics_summary()
        print("✓ Analytics summary test passed")
        
        test_analytics_trends()
        print("✓ Analytics trends test passed")
        
        test_analytics_kpis()
        print("✓ Analytics KPIs test passed")
        
        test_network_overview()
        print("✓ Network overview test passed")
        
        test_network_growth()
        print("✓ Network growth test passed")
        
        test_relationship_health()
        print("✓ Relationship health test passed")
        
        test_interactions_overview()
        print("✓ Interactions overview test passed")
        
        test_interaction_types()
        print("✓ Interaction types test passed")
        
        test_insights_endpoint()
        print("✓ Insights endpoint test passed")
        
        test_insights_generation()
        print("✓ Insights generation test passed")
        
        test_recommendations()
        print("✓ Recommendations test passed")
        
        print("\n🎉 All analytics API tests passed!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        raise