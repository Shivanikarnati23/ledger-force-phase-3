import importlib.util
import os
from fastapi.testclient import TestClient

# Load root-level app.py directly by file path
current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.dirname(current_dir)
app_path = os.path.join(root_dir, "app.py")

spec = importlib.util.spec_from_file_location("root_app", app_path)
root_app = importlib.util.module_from_spec(spec)
spec.loader.exec_module(root_app)

app = root_app.app
client = TestClient(app)


def test_trial_balance_endpoint():
  response = client.get("/reports/trial-balance")
  assert response.status_code == 200
  data = response.json()
  assert data["status"] == "success"
  assert data["mismatches"] == 0


def test_profit_and_loss_endpoint():
  response = client.get("/reports/profit-and-loss")
  assert response.status_code == 200
  data = response.json()
  assert data["status"] == "success"


def test_balance_sheet_endpoint():
  response = client.get("/reports/balance-sheet")
  assert response.status_code == 200
  data = response.json()
  assert data["status"] == "success"
  assert data["balanced"] is True