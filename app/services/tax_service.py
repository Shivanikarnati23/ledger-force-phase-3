from sqlalchemy.orm import Session
from sqlalchemy import select
from decimal import Decimal
from app.models.tax import TaxSlab, TaxParameter, StatutoryRate

def get_tax_parameter(db: Session, parameter_name: str, default: float = 0.0) -> float:
    """Fetches a specific tax parameter value from the database."""
    param = db.execute(
        select(TaxParameter).where(TaxParameter.parameter_name == parameter_name)
    ).scalars().first()
    return param.value if param else default

def calculate_income_tax(annual_taxable_income: float, db: Session) -> float:
    """Calculates income tax dynamically based on database tax slabs."""
    slabs = db.execute(
        select(TaxSlab).order_by(TaxSlab.min_income.asc())
    ).scalars().all()
    
    total_tax = 0.0
    for slab in slabs:
        if annual_taxable_income > slab.min_income:
            taxable_in_slab = min(annual_taxable_income, slab.max_income) - slab.min_income
            if taxable_in_slab > 0:
                total_tax += taxable_in_slab * slab.tax_rate
                
    return round(total_tax, 2)

def calculate_statutory_deductions(basic_salary: float, db: Session) -> dict:
    """Calculates statutory contributions (PF, etc.) using database ceiling and rates."""
    pf_rate = db.execute(
        select(StatutoryRate).where(StatutoryRate.statutory_type == "PF")
    ).scalars().first()
    
    if not pf_rate:
        return {"employee_pf": 0.0, "employer_pf": 0.0}
        
    # Apply wage ceiling if applicable
    applicable_wage = min(basic_salary, pf_rate.wage_ceiling) if pf_rate.wage_ceiling > 0 else basic_salary
    
    employee_pf = applicable_wage * pf_rate.employee_share
    employer_pf = applicable_wage * pf_rate.employer_share
    
    return {
        "employee_pf": round(employee_pf, 2),
        "employer_pf": round(employer_pf, 2)
    }