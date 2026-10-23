
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from Database import get_db
from Models import Payroll, Employee, User
from Schemas import PayrollCreate, PayrollResponse
from Security import get_current_user, hr_or_admin


router = APIRouter()


# Generate monthly payroll (HR/Admin)
@router.post(
    "/generate",
    response_model=PayrollResponse,
    status_code=201
)
def generate_payroll(
    payroll_data: PayrollCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(hr_or_admin)
):
    # Check employee exists
    employee = db.query(Employee).filter(
        Employee.id == payroll_data.employee_id
    ).first()

    if not employee:
        raise HTTPException(
            status_code=404,
            detail="Employee not found"
        )

    # Prevent duplicate payroll for the same month
    existing_payroll = db.query(Payroll).filter(
        Payroll.employee_id == payroll_data.employee_id,
        Payroll.month == payroll_data.month,
        Payroll.year == payroll_data.year
    ).first()

    if existing_payroll:
        raise HTTPException(
            status_code=400,
            detail="Payroll already generated for this month"
        )

    # Calculate net salary
    net_salary = (
        payroll_data.basic_salary
        + payroll_data.allowances
        - payroll_data.deductions
    )

    if net_salary < 0:
        raise HTTPException(
            status_code=400,
            detail="Net salary cannot be negative"
        )

    payroll = Payroll(
        employee_id=payroll_data.employee_id,
        month=payroll_data.month,
        year=payroll_data.year,
        basic_salary=payroll_data.basic_salary,
        allowances=payroll_data.allowances,
        deductions=payroll_data.deductions,
        net_salary=net_salary,
        payment_status="PENDING"
    )

    db.add(payroll)
    db.commit()
    db.refresh(payroll)

    return payroll


# View own payroll history
@router.get("/my-payroll", response_model=list[PayrollResponse])
def get_my_payroll(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    employee = db.query(Employee).filter(
        Employee.user_id == current_user.id
    ).first()

    if not employee:
        raise HTTPException(
            status_code=404,
            detail="Employee record not found"
        )

    return db.query(Payroll).filter(
        Payroll.employee_id == employee.id
    ).order_by(
        Payroll.year.desc(),
        Payroll.month.desc()
    ).all()


# HR/Admin: View all payroll records
@router.get("/", response_model=list[PayrollResponse])
def get_all_payroll(
    db: Session = Depends(get_db),
    current_user: User = Depends(hr_or_admin)
):
    return db.query(Payroll).order_by(
        Payroll.year.desc(),
        Payroll.month.desc()
    ).all()


# HR/Admin: View payroll for a specific employee
@router.get(
    "/employee/{employee_id}",
    response_model=list[PayrollResponse]
)
def get_employee_payroll(
    employee_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(hr_or_admin)
):
    employee = db.query(Employee).filter(
        Employee.id == employee_id
    ).first()

    if not employee:
        raise HTTPException(
            status_code=404,
            detail="Employee not found"
        )

    return db.query(Payroll).filter(
        Payroll.employee_id == employee_id
    ).order_by(
        Payroll.year.desc(),
        Payroll.month.desc()
    ).all()


# HR/Admin: Update payroll payment status
@router.put("/{payroll_id}/status")
def update_payroll_status(
    payroll_id: int,
    payment_status: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(hr_or_admin)
):
    payroll = db.query(Payroll).filter(
        Payroll.id == payroll_id
    ).first()

    if not payroll:
        raise HTTPException(
            status_code=404,
            detail="Payroll record not found"
        )

    if payment_status not in ["PENDING", "PAID", "FAILED"]:
        raise HTTPException(
            status_code=400,
            detail="Invalid payment status"
        )

    payroll.payment_status = payment_status

    db.commit()
    db.refresh(payroll)

    return {
        "message": "Payroll status updated successfully",
        "payroll_id": payroll.id,
        "payment_status": payroll.payment_status
    }
