from sqlalchemy.orm import Session
from models import TaxSlab, TaxParameter, StatutoryRate

def calculate_income_tax(db: Session, taxable_income: float) -> float:
    """Calculates income tax dynamically based on database tax slabs."""
    slabs = db.query(TaxSlab).order_by(TaxSlab.min_income).all()
    total_tax = 0.0
    
    for slab in slabs:
        if taxable_income > slab.min_income:
            upper = slab.max_income if slab.max_income else taxable_income
            taxable_in_slab = min(taxable_income, upper) - slab.min_income
            if taxable_in_slab > 0:
                total_tax += taxable_in_slab * (slab.tax_rate / 100.0)
                
    return round(total_tax, 2)

def get_standard_deduction(db: Session) -> float:
    """Fetches the configurable standard deduction from parameters."""
    param = db.query(TaxParameter).filter(TaxParameter.parameter_name == "standard_deduction").first()
    return float(param.value) if param else 50000.0

def process_payroll_calculation(db: Session, employee_id: str, basic_monthly: float, allowances: float):
    gross_monthly = basic_monthly + allowances
    annual_gross = gross_monthly * 12
    
    std_deduction = get_standard_deduction(db)
    taxable_income = max(0.0, annual_gross - std_deduction)
    
    annual_tax = calculate_income_tax(db, taxable_income)
    monthly_tax = round(annual_tax / 12, 2)
    
    net_monthly = gross_monthly - monthly_tax
    
    return {
        "employee_id": employee_id,
        "gross_pay": gross_monthly,
        "standard_deduction": std_deduction,
        "taxable_income": taxable_income,
        "monthly_income_tax": monthly_tax,
        "employee_pf": 0.0,
        "employer_pf": 0.0,
        "total_deductions": monthly_tax,
        "net_pay": net_monthly
    }