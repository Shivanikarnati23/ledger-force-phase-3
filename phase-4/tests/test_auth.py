from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_login_invalid_credentials():
    """Verify that logging in with incorrect credentials returns 401 Unauthorized."""
    response = client.post(
        "/api/v1/auth/login",
        data={"username": "wronguser", "password": "wrongpassword"}
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Incorrect username or password"

def test_login_missing_fields():
    """Verify validation error when login form data is empty."""
    response = client.post("/api/v1/auth/login", data={})
    assert response.status_code == 422

def test_admin_dashboard_unauthorized():
    """Verify that accessing the admin dashboard without a token returns 401 or 403."""
    response = client.get("/api/v1/admin/dashboard")
    assert response.status_code in [401, 403]

def test_payslip_access_control():
    """Verify that unauthenticated access to payslips is restricted."""
    response = client.get("/api/v1/payslips/E0001")
    assert response.status_code in [401, 403]

def test_root_health_check():
    """Verify root health check endpoint directly."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}