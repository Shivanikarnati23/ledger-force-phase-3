from sqlalchemy import Column, Integer, String, Float
from app.database import Base

class TaxSlab(Base):
    __tablename__ = "tax_slabs"
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True, index=True)
    min_income = Column(Float, nullable=False)
    max_income = Column(Float, nullable=True)
    tax_rate = Column(Float, nullable=False)

class TaxParameter(Base):
    __tablename__ = "tax_parameters"
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True, index=True)
    parameter_name = Column(String, unique=True, index=True)
    value = Column(String, nullable=False)

class StatutoryRate(Base):
    __tablename__ = "statutory_rates"
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True, index=True)
    statutory_type = Column(String, unique=True, index=True, nullable=False)
    employee_share = Column(Float, nullable=False)
    employer_share = Column(Float, nullable=False)
    wage_ceiling = Column(Float, nullable=False)