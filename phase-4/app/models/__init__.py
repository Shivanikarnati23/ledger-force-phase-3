from app.database import Base
from app.models.employee import Employee
from app.models.salary import SalaryComponent, SalaryStructure, SalaryRevision
from app.models.attendance import Attendance
from app.models.leave import LeaveBalance
from .user import User  # This makes 'from app.models import User' work seamlessly!
from .tax import TaxSlab, TaxParameter, StatutoryRate