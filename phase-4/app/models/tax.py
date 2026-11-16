from sqlalchemy import Column, Integer, String, Float
from app.database import Base

class TaxSlab(Base):
    __tablename__ = "tax_slabs"
    id = Column(Integer, primary_key=True, index=True)
    min_income = Column(Float, nullable=False)
    max_income = Column(Float, nullable=False)
    tax_rate = Column(Float, nullable=False)

class TaxParameter(Base):
    __tablename__ = "tax_parameters"
    id = Column(Integer, primary_key=True, index=True)
    parameter_name = Column(String, unique=True, index=True, nullable=False)
    value = Column(Float, nullable=False)
    description = Column(String, nullable=True)

class StatutoryRate(Base):
    __tablename__ = "statutory_rates"
    id = Column(Integer, primary_key=True, index=True)
    statutory_type = Column(String, unique=True, index=True, nullable=False)
    employee_share = Column(Float, nullable=False)
    employer_share = Column(Float, nullable=False)
    wage_ceiling = Column(Float, nullable=False)