
from pydantic import BaseModel, EmailStr, Field, ConfigDict
from datetime import date, datetime
from typing import Optional, Literal


# Allowed user roles
UserRole = Literal["EMPLOYEE", "HR", "ADMIN"]


# 1. User Schemas
class UserCreate(BaseModel):
    username: str = Field(min_length=3, max_length=100)
    email: EmailStr
    password: str = Field(min_length=8)
    role: UserRole = "EMPLOYEE"


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: int
    username: str
    email: EmailStr
    role: UserRole
    is_active: bool

    model_config = ConfigDict(from_attributes=True)


class UserRoleUpdate(BaseModel):
    role: UserRole


class UserStatusUpdate(BaseModel):
    is_active: bool


# 2. Employee Schemas
class EmployeeCreate(BaseModel):
    user_id: int
    full_name: str = Field(min_length=2, max_length=150)
    department: Optional[str] = None
    designation: Optional[str] = None
    phone: Optional[str] = None
    joining_date: Optional[date] = None
    basic_salary: float = Field(default=0, ge=0)


class EmployeeUpdate(BaseModel):
    full_name: Optional[str] = None
    department: Optional[str] = None
    designation: Optional[str] = None
    phone: Optional[str] = None
    joining_date: Optional[date] = None
    basic_salary: Optional[float] = Field(default=None, ge=0)


class EmployeeResponse(BaseModel):
    id: int
    user_id: Optional[int] = None
    full_name: str
    department: Optional[str] = None
    designation: Optional[str] = None
    phone: Optional[str] = None
    joining_date: Optional[date] = None
    basic_salary: float

    model_config = ConfigDict(from_attributes=True)


# 3. Attendance Schemas
class AttendanceCheckIn(BaseModel):
    employee_id: int


class AttendanceCheckOut(BaseModel):
    employee_id: int


class AttendanceResponse(BaseModel):
    id: int
    employee_id: int
    attendance_date: date
    check_in: Optional[datetime] = None
    check_out: Optional[datetime] = None
    status: str
    late_minutes: int
    overtime_hours: float

    model_config = ConfigDict(from_attributes=True)


# 4. Leave Schemas
class LeaveCreate(BaseModel):
    employee_id: int
    leave_type: str = Field(min_length=2, max_length=50)
    start_date: date
    end_date: date
    reason: Optional[str] = None


class LeaveStatusUpdate(BaseModel):
    status: Literal["APPROVED", "REJECTED"]


class LeaveResponse(BaseModel):
    id: int
    employee_id: int
    leave_type: str
    start_date: date
    end_date: date
    reason: Optional[str] = None
    status: str
    approved_by: Optional[int] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# 5. Leave Policy Schemas
class LeavePolicyCreate(BaseModel):
    leave_type: str = Field(min_length=2, max_length=50)
    total_days_allowed: int = Field(ge=0)


class LeavePolicyResponse(BaseModel):
    id: int
    leave_type: str
    total_days_allowed: int

    model_config = ConfigDict(from_attributes=True)


# 6. Leave Balance Schemas
class LeaveBalanceCreate(BaseModel):
    employee_id: int
    leave_type: str
    remaining_days: int = Field(ge=0)


class LeaveBalanceResponse(BaseModel):
    id: int
    employee_id: int
    leave_type: str
    remaining_days: int

    model_config = ConfigDict(from_attributes=True)


# 7. Payroll Schemas
class PayrollCreate(BaseModel):
    employee_id: int
    month: int = Field(ge=1, le=12)
    year: int = Field(ge=2000, le=2100)
    basic_salary: float = Field(ge=0)
    allowances: float = Field(default=0, ge=0)
    deductions: float = Field(default=0, ge=0)


class PayrollResponse(BaseModel):
    id: int
    employee_id: int
    month: int
    year: int
    basic_salary: float
    allowances: float
    deductions: float
    net_salary: float
    payment_status: str
    generated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# 8. Notification Schemas
class NotificationCreate(BaseModel):
    user_id: int
    message: str = Field(min_length=1)


class NotificationResponse(BaseModel):
    id: int
    user_id: int
    message: str
    is_read: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
