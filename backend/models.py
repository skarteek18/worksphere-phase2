
from sqlalchemy import (
    Column, Integer, String, Boolean, Date, DateTime,
    Float, ForeignKey, Text, UniqueConstraint
)
from sqlalchemy.orm import relationship
from datetime import datetime

from Database import Base


# 1. Users Table
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), unique=True, nullable=False)
    email = Column(String(150), unique=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)

    # EMPLOYEE, HR or ADMIN
    role = Column(String(20), default="EMPLOYEE", nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)


# 2. Employees Table
class Employee(Base):
    __tablename__ = "employees"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True)
    full_name = Column(String(150), nullable=False)
    department = Column(String(100))
    designation = Column(String(100))
    phone = Column(String(20))
    joining_date = Column(Date)
    basic_salary = Column(Float, default=0.0)


# 3. Attendance Table
class Attendance(Base):
    __tablename__ = "attendance"

    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(
        Integer, ForeignKey("employees.id"), nullable=False
    )
    attendance_date = Column(Date, nullable=False)
    check_in = Column(DateTime)
    check_out = Column(DateTime)
    status = Column(String(20), default="PRESENT")
    late_minutes = Column(Integer, default=0)
    overtime_hours = Column(Float, default=0.0)

    __table_args__ = (
        UniqueConstraint(
            "employee_id",
            "attendance_date",
            name="unique_employee_attendance_per_day"
        ),
    )


# 4. Leaves Table
class Leave(Base):
    __tablename__ = "leaves"

    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(
        Integer, ForeignKey("employees.id"), nullable=False
    )
    leave_type = Column(String(50), nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    reason = Column(Text)
    status = Column(String(20), default="PENDING")
    approved_by = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)


# 5. Leave Policies Table
class LeavePolicy(Base):
    __tablename__ = "leave_policies"

    id = Column(Integer, primary_key=True, index=True)
    leave_type = Column(String(50), unique=True, nullable=False)
    total_days_allowed = Column(Integer, nullable=False)


# 6. Leave Balance Table
class LeaveBalance(Base):
    __tablename__ = "leave_balance"

    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(
        Integer, ForeignKey("employees.id"), nullable=False
    )
    leave_type = Column(String(50), nullable=False)
    remaining_days = Column(Integer, default=0, nullable=False)

    __table_args__ = (
        UniqueConstraint(
            "employee_id",
            "leave_type",
            name="unique_employee_leave_type"
        ),
    )


# 7. Payroll Table
class Payroll(Base):
    __tablename__ = "payroll"

    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(
        Integer, ForeignKey("employees.id"), nullable=False
    )
    month = Column(Integer, nullable=False)
    year = Column(Integer, nullable=False)
    basic_salary = Column(Float, default=0.0)
    allowances = Column(Float, default=0.0)
    deductions = Column(Float, default=0.0)
    net_salary = Column(Float, default=0.0)
    payment_status = Column(String(20), default="PENDING")
    generated_at = Column(DateTime, default=datetime.utcnow)


# 8. Notifications Table
class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    message = Column(Text, nullable=False)
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
