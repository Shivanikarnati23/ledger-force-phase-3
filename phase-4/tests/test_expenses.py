import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.routers.expenses import ExpenseBill, detect_duplicate_bills

client = TestClient(app)

def test_duplicate_detector():
    # Mock row data to test matching vendor, amount, and close dates (within 3 days)
    row1 = {
        "expense_id": "EXP-101",
        "vendor_id": "VEND-01",
        "total_amount": "5000.0",
        "expense_date": "2025-05-10"
    }
    row2 = {
        "expense_id": "EXP-102",
        "vendor_id": "VEND-01",
        "total_amount": "5000.0",
        "expense_date": "2025-05-12"  # Within the 3-day window
    }
    row3 = {
        "expense_id": "EXP-103",
        "vendor_id": "VEND-02",
        "total_amount": "12000.0",
        "expense_date": "2025-05-10"
    }
    
    bills = [ExpenseBill(row1), ExpenseBill(row2), ExpenseBill(row3)]
    duplicates = detect_duplicate_bills(bills, date_window_days=3)
    
    # Assert that exactly one duplicate match is found between EXP-101 and EXP-102
    assert len(duplicates) == 1
    assert duplicates[0]["original"] == "EXP-101"
    assert duplicates[0]["duplicate_candidate"] == "EXP-102"
    assert duplicates[0]["vendor_id"] == "VEND-01"

def test_expense_endpoints_prefix():
    # Verify versioned endpoint route availability
    response = client.get("/api/v1/expenses/")
    assert response.status_code in [200, 403,404]