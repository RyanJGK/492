"""API endpoint tests."""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timedelta

from main import app
from database import get_db
from models.database import Base, User, AuthenticationEvent, AIAnalysis
from routers.auth import get_password_hash


# Test database
SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    """Override database dependency for testing."""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)


@pytest.fixture(scope="function")
def test_db():
    """Create test database for each test."""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    
    # Create test users
    test_admin = User(
        username="test_admin",
        email="admin@test.com",
        hashed_password=get_password_hash("admin123"),
        role="admin",
        is_active=True
    )
    
    test_analyst = User(
        username="test_analyst",
        email="analyst@test.com",
        hashed_password=get_password_hash("analyst123"),
        role="analyst",
        is_active=True
    )
    
    test_observer = User(
        username="test_observer",
        email="observer@test.com",
        hashed_password=get_password_hash("observer123"),
        role="observer",
        is_active=True
    )
    
    db.add_all([test_admin, test_analyst, test_observer])
    db.commit()
    
    yield db
    
    db.close()
    Base.metadata.drop_all(bind=engine)


def get_auth_token(username: str, password: str) -> str:
    """Helper function to get authentication token."""
    response = client.post(
        "/api/auth/login",
        json={"username": username, "password": password}
    )
    return response.json()["access_token"]


class TestAuthentication:
    """Authentication endpoint tests."""
    
    def test_login_success(self, test_db):
        """Test successful login."""
        response = client.post(
            "/api/auth/login",
            json={"username": "test_admin", "password": "admin123"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"
    
    def test_login_invalid_credentials(self, test_db):
        """Test login with invalid credentials."""
        response = client.post(
            "/api/auth/login",
            json={"username": "test_admin", "password": "wrongpassword"}
        )
        
        assert response.status_code == 401
    
    def test_login_nonexistent_user(self, test_db):
        """Test login with nonexistent user."""
        response = client.post(
            "/api/auth/login",
            json={"username": "nonexistent", "password": "password"}
        )
        
        assert response.status_code == 401


class TestRBAC:
    """Role-Based Access Control tests."""
    
    def test_observer_access_events(self, test_db):
        """Test observer can access event endpoints."""
        token = get_auth_token("test_observer", "observer123")
        
        response = client.get(
            "/api/events/auth",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
    
    def test_observer_cannot_access_admin(self, test_db):
        """Test observer cannot access admin endpoints."""
        token = get_auth_token("test_observer", "observer123")
        
        response = client.get(
            "/api/config/model-weights",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 403
    
    def test_analyst_can_submit_feedback(self, test_db):
        """Test analyst can submit feedback."""
        token = get_auth_token("test_analyst", "analyst123")
        
        # Create a test analysis
        analysis = AIAnalysis(
            timestamp=datetime.now(),
            analysis_type="test",
            confidence_score=0.85,
            threat_level="high",
            affected_systems=["system1"],
            recommendation="Test recommendation"
        )
        test_db.add(analysis)
        test_db.commit()
        
        response = client.post(
            "/api/analyze/feedback",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "analysis_id": analysis.id,
                "is_false_positive": True,
                "notes": "This is a false positive"
            }
        )
        
        assert response.status_code == 200
    
    def test_admin_can_update_weights(self, test_db):
        """Test admin can update model weights."""
        token = get_auth_token("test_admin", "admin123")
        
        response = client.put(
            "/api/config/model-weights",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "config_key": "authentication_weights",
                "weights": {
                    "failed_login_rate": 0.4,
                    "geo_velocity": 0.3,
                    "time_anomaly": 0.2,
                    "enumeration_score": 0.1
                }
            }
        )
        
        assert response.status_code == 200


class TestEventEndpoints:
    """Event query endpoint tests."""
    
    def test_get_authentication_events_empty(self, test_db):
        """Test getting authentication events when none exist."""
        token = get_auth_token("test_analyst", "analyst123")
        
        response = client.get(
            "/api/events/auth",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        assert response.json() == []
    
    def test_get_authentication_events_with_data(self, test_db):
        """Test getting authentication events with data."""
        # Add test events
        event = AuthenticationEvent(
            timestamp=datetime.now(),
            source_ip="192.168.1.1",
            username="testuser",
            event_type="failed_login",
            geolocation="US",
            is_suspicious=True
        )
        test_db.add(event)
        test_db.commit()
        
        token = get_auth_token("test_analyst", "analyst123")
        
        response = client.get(
            "/api/events/auth",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["source_ip"] == "192.168.1.1"
    
    def test_get_events_with_filters(self, test_db):
        """Test filtering authentication events."""
        # Add test events
        event1 = AuthenticationEvent(
            timestamp=datetime.now(),
            source_ip="192.168.1.1",
            username="user1",
            event_type="failed_login",
            is_suspicious=True
        )
        event2 = AuthenticationEvent(
            timestamp=datetime.now(),
            source_ip="192.168.1.2",
            username="user2",
            event_type="successful_login",
            is_suspicious=False
        )
        test_db.add_all([event1, event2])
        test_db.commit()
        
        token = get_auth_token("test_analyst", "analyst123")
        
        # Filter by suspicious flag
        response = client.get(
            "/api/events/auth?is_suspicious=true",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["is_suspicious"] is True


class TestAnalysisEndpoints:
    """Analysis endpoint tests."""
    
    def test_get_dashboard_data(self, test_db):
        """Test getting dashboard data."""
        token = get_auth_token("test_analyst", "analyst123")
        
        response = client.get(
            "/api/analyze/dashboard",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "threat_level" in data
        assert "confidence_score" in data
        assert "active_threats" in data
    
    def test_get_threats(self, test_db):
        """Test getting threat analysis results."""
        # Add test analysis
        analysis = AIAnalysis(
            timestamp=datetime.now(),
            analysis_type="authentication_anomaly",
            confidence_score=0.85,
            threat_level="high",
            affected_systems=["system1", "system2"],
            recommendation="Block suspicious IPs"
        )
        test_db.add(analysis)
        test_db.commit()
        
        token = get_auth_token("test_analyst", "analyst123")
        
        response = client.get(
            "/api/analyze/threats",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["threat_level"] == "high"


class TestHealthEndpoints:
    """Health check endpoint tests."""
    
    def test_root_endpoint(self):
        """Test root endpoint."""
        response = client.get("/")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "operational"
    
    def test_health_check(self):
        """Test health check endpoint."""
        response = client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
