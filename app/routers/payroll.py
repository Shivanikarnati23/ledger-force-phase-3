from fastapi import APIRouter, Depends, HTTPException, status, Header
from sqlalchemy.orm import Session
from app.database import get_db
from app.services.payroll import process_payroll_calculation
from models import TaxParameter

router = APIRouter(prefix="/payroll", tags=["Payroll Integration"])

def verify_admin_role(x_user_role: str = Header(default="Admin")):
    """Ensures only users with an 'Admin' role can modify tax/statutory rules."""
    if x_user_role != "Admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied. Only administrators can modify tax and statutory rules."
        )
    return {"role": "Admin"}

@router.post("/calculate-payroll/{employee_id}")
def calculate_payroll_endpoint(
    employee_id: str,
    basic_monthly: float,
    allowances: float,
    db: Session = Depends(get_db)
):
    """Calculates payroll before and after adjustments for a given employee."""
    try:
        result = process_payroll_calculation(db, employee_id, basic_monthly, allowances)
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/statutory-report")
def get_statutory_report(db: Session = Depends(get_db)):
    """Fetches statutory compliance parameters seeded from CSV."""
    try:
        params = db.query(TaxParameter).all()
        statutory_data = {p.parameter_name: p.value for p in params}
        
        return {
            "report_type": "Statutory Compliance & Rates Summary",
            "status": "Active",
            "statutory_rates": statutory_data
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.put("/tax-parameters/{param_id}")
def update_tax_parameter(
    param_id: int, 
    new_value: float, 
    db: Session = Depends(get_db), 
    admin = Depends(verify_admin_role)
):
    """Admin-only endpoint to modify tax rules/slabs and verify dynamic recalculation."""
    try:
        param = db.query(TaxParameter).filter(TaxParameter.id == param_id).first()
        if not param:
            raise HTTPException(status_code=404, detail="Tax parameter not found")
        
        param.value = new_value
        db.commit()
        db.refresh(param)
        
        return {
            "message": "Tax parameter updated successfully by Admin",
            "parameter_name": param.parameter_name,
            "new_value": param.value
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))