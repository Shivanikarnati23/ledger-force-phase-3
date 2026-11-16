from fastapi import APIRouter, HTTPException
import csv
import os
from datetime import datetime, timedelta
from collections import defaultdict

router = APIRouter(prefix="/expenses", tags=["Expenses & Vendors"])

def format_indian_currency(amount):
    """Formats numeric values into Indian numbering style (e.g., 1,23,456.00)."""
    try:
        val = float(amount)
    except (TypeError, ValueError):
        return "0.00"
    
    s = f"{val:.2f}"
    parts = s.split(".")
    integer_part = parts[0]
    decimal_part = parts[1]
    
    if len(integer_part) <= 3:
        formatted_int = integer_part
    else:
        last_three = integer_part[-3:]
        remaining = integer_part[:-3]
        groups = []
        while len(remaining) > 0:
            groups.insert(0, remaining[-2:])
            remaining = remaining[:-2]
        formatted_int = ",".join(groups) + "," + last_three if groups else last_three
        
    return f"{formatted_int}.{decimal_part}"


class ExpenseBill:
    def __init__(self, row):
        self.expense_id = row.get("expense_id")
        self.expense_date = row.get("expense_date")
        self.category_account = row.get("category_account")
        self.vendor_id = row.get("vendor_id")
        self.bill_reference = row.get("bill_reference")
        self.description = row.get("description")
        self.department_id = row.get("department_id")
        self.amount_excl_gst = float(row.get("amount_excl_gst", 0))
        self.gst_rate_percent = float(row.get("gst_rate_percent", 0))
        self.gst_amount = float(row.get("gst_amount", 0))
        self.total_amount = float(row.get("total_amount", 0))
        self.due_date = row.get("due_date")
        self.paid_date = row.get("paid_date")
        self.status = row.get("status", "SUBMITTED").upper()
        self.payment_mode = row.get("payment_mode")
        self.submitted_by = row.get("submitted_by")
        self.approved_by = row.get("approved_by")

    def validate_workflow(self):
        """Enforces Task 11 security controls: Separation of Duties and approval before payment."""
        if self.status in ["APPROVED", "PAID"]:
            if not self.submitted_by or not self.approved_by:
                raise HTTPException(status_code=400, detail=f"Bill {self.expense_id}: Missing submitter or approver.")
            
            # Separation of Duties Control: The person who creates cannot approve
            if self.submitted_by == self.approved_by:
                raise HTTPException(
                    status_code=403, 
                    detail=f"Security Violation for {self.expense_id}: The person who creates a bill cannot approve it!"
                )
        
        if self.status == "PAID" and not self.approved_by:
            raise HTTPException(status_code=400, detail=f"Bill {self.expense_id}: Cannot be paid before approval.")
        
        return True


@router.get("/")
def get_expenses():
    """Loads expenses from CSV and validates workflow security rules (Separation of Duties)."""
    csv_file = "expenses.csv"
    if not os.path.exists(csv_file):
        raise HTTPException(status_code=404, detail="expenses.csv not found in root directory.")
    
    expenses_list = []
    with open(csv_file, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            bill = ExpenseBill(row)
            bill.validate_workflow()
            expenses_list.append({
                "expense_id": bill.expense_id,
                "vendor_id": bill.vendor_id,
                "description": bill.description,
                "total_amount": format_indian_currency(bill.total_amount),
                "status": bill.status,
                "submitted_by": bill.submitted_by,
                "approved_by": bill.approved_by
            })
            
    return {
        "status": "success",
        "total_expenses": len(expenses_list),
        "expenses": expenses_list
    }


def detect_duplicate_bills(expenses_list, date_window_days=3):
    """Flags bills with the same vendor_id, total_amount, and date within a 3-day window."""
    duplicates = []
    seen = []

    for bill in expenses_list:
        try:
            current_date = datetime.strptime(bill.expense_date, "%Y-%m-%d")
        except (ValueError, TypeError):
            continue

        for seen_bill in seen:
            if bill.vendor_id == seen_bill.vendor_id and bill.total_amount == seen_bill.total_amount:
                try:
                    seen_date = datetime.strptime(seen_bill.expense_date, "%Y-%m-%d")
                    if abs((current_date - seen_date).days) <= date_window_days:
                        duplicates.append({
                            "original": seen_bill.expense_id,
                            "duplicate_candidate": bill.expense_id,
                            "vendor_id": bill.vendor_id,
                            "amount": format_indian_currency(bill.total_amount)
                        })
                except ValueError:
                    continue
        seen.append(bill)
        
    return duplicates


@router.get("/duplicates")
def check_duplicate_expenses():
    """API endpoint to detect duplicate bills within a 3-day window."""
    csv_file = "expenses.csv"
    if not os.path.exists(csv_file):
        raise HTTPException(status_code=404, detail="expenses.csv not found.")
    
    bills = []
    with open(csv_file, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            bills.append(ExpenseBill(row))
            
    duplicates = detect_duplicate_bills(bills)
    return {
        "status": "success",
        "duplicate_count": len(duplicates),
        "duplicates": duplicates
    }


@router.get("/monthly-comparison")
def get_monthly_comparison():
    """Aggregates expenses by month to provide a month-over-month comparison table (Evidence 1)."""
    csv_file = "expenses.csv"
    if not os.path.exists(csv_file):
        raise HTTPException(status_code=404, detail="expenses.csv not found.")
    
    monthly_data = defaultdict(lambda: {"total_amount": 0.0, "bill_count": 0})
    
    with open(csv_file, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            bill = ExpenseBill(row)
            if not bill.expense_date:
                continue
            try:
                month_key = bill.expense_date[:7]
            except Exception:
                continue
            
            monthly_data[month_key]["total_amount"] += bill.total_amount
            monthly_data[month_key]["bill_count"] += 1
            
    comparison_table = []
    for month in sorted(monthly_data.keys()):
        data = monthly_data[month]
        comparison_table.append({
            "month": month,
            "total_bills": data["bill_count"],
            "total_spend": format_indian_currency(data["total_amount"])
        })
        
    return {
        "status": "success",
        "monthly_comparison": comparison_table
    }