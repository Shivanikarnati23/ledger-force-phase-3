import csv
from app.database import SessionLocal, engine, Base
from app.models import TaxSlab, TaxParameter, StatutoryRate

def seed_data():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    
    db.query(TaxSlab).delete()
    db.query(TaxParameter).delete()
    db.query(StatutoryRate).delete()
    
    # Load Tax Slabs (Columns: Slab_id, regime, financial_year, income_from, income_to, rate_percent, effective_from, note)
    with open("tax_slabs.csv", mode="r", encoding="utf-8-sig") as f:
        reader = csv.reader(f)
        next(reader, None) # Skip header row
        for row in reader:
            if not row or len(row) < 6:
                continue
            try:
                min_inc = float(row[3])  # income_from
                max_inc = float(row[4])  # income_to
                rate = float(row[5]) / 100.0 if float(row[5]) > 1 else float(row[5]) # rate_percent (handles both percentage and decimal format)
            except ValueError:
                continue
                
            db.add(TaxSlab(
                min_income=min_inc,
                max_income=max_inc,
                tax_rate=rate
            ))
            
    # Load Tax Parameters
    with open("tax_parameters.csv", mode="r", encoding="utf-8-sig") as f:
        reader = csv.reader(f)
        next(reader, None)
        for row in reader:
            if not row or len(row) < 2:
                continue
            try:
                val = float(row[1])
            except ValueError:
                continue
            db.add(TaxParameter(
                parameter_name=row[0].strip(),
                value=val,
                description=row[2].strip() if len(row) > 2 else ""
            ))
            
    # Load Statutory Rates
    with open("statutory_rates.csv", mode="r", encoding="utf-8-sig") as f:
        reader = csv.reader(f)
        next(reader, None)
        for row in reader:
            if not row or len(row) < 4:
                continue
            try:
                emp_share = float(row[1])
                empr_share = float(row[2])
                ceiling = float(row[3])
            except ValueError:
                continue
            db.add(StatutoryRate(
                statutory_type=row[0].strip(),
                employee_share=emp_share,
                employer_share=empr_share,
                wage_ceiling=ceiling
            ))
            
    db.commit()
    db.close()
    print("Tax configuration data seeded successfully from CSV files!")

if __name__ == "__main__":
    seed_data()