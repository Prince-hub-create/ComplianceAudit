from sqlalchemy.ext.declarative import declarative_base
from backend.models.employee import EmployeeRecord  # ✅ Ensure this file exists

Base = declarative_base()  # ✅ Make sure this line is present
