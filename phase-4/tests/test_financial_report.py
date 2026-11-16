from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_trial_balance_endpoint():
    response = client.get("/api/v1/reports/trial-balance")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["mismatches"] == 0

def test_profit_and_loss_endpoint():
    response = client.get("/api/v1/reports/profit-and-loss")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"

def test_balance_sheet_endpoint():
    response = client.get("/api/v1/reports/balance-sheet")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["balanced"] is True