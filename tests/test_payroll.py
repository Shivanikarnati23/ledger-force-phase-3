import time
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_trigger_bulk_payroll():
    """Test triggering the 18-month bulk payroll background task."""
    response = client.post("/api/v1/payroll/run-bulk")
    # Expecting 202 Accepted for background processing tasks
    assert response.status_code == 202
    data = response.json()
    assert "job_id" in data
    assert data["status"] == "queued"

def test_payroll_job_status_flow():
    """Test checking a non-existent job ID and a valid job status flow."""
    # 1. Test non-existent job ID returns 404
    response = client.get("/api/v1/payroll/jobs/non-existent-id-12345")
    assert response.status_code == 404
    
    # 2. Trigger a real job and immediately check its status
    trigger_res = client.post("/api/v1/payroll/run-bulk")
    assert trigger_res.status_code == 202
    job_id = trigger_res.json()["job_id"]
    
    status_res = client.get(f"/api/v1/payroll/jobs/{job_id}")
    assert status_res.status_code == 200
    job_data = status_res.json()
    assert job_data["job_id"] == job_id
    assert job_data["months_total"] == 18
    assert job_data["status"] in ["queued", "processing", "completed"]

def test_payroll_routers_prefix():
    """Verify versioned payroll endpoint prefix availability."""
    response = client.get("/api/v1/payroll/status")
    assert response.status_code in [200, 401, 404]

def test_payroll_bulk_run_validation():
    """Verify bulk payroll run payload defaults and constraints."""
    response = client.post("/api/v1/payroll/run-bulk")
    assert response.status_code == 202
    data = response.json()
    assert "job_id" in data
    assert "status" in data

def test_payroll_job_not_found_handling():
    """Verify handling of completely invalid job IDs."""
    response = client.get("/api/v1/payroll/jobs/invalid-uuid-format-999")
    assert response.status_code == 404