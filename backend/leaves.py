
from datetime import date

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from Database import get_db
from Models import Leave, Employee, User, LeaveBalance
from Schemas import LeaveCreate, LeaveResponse, LeaveStatusUpdate
from Security import get_current_user, hr_or_admin


router = APIRouter()


# Find the employee linked to the logged-in user
def get_employee(db: Session, user: User):
    employee = db.query(Employee).filter(
        Employee.user_id == user.id
    ).first()

    if not employee:
        raise HTTPException(
            status_code=404,
            detail="Employee record not found"
        )

    return employee


# Apply for leave
@router.post("/", response_model=LeaveResponse, status_code=201)
def apply_leave(
    leave_data: LeaveCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    employee = get_employee(db, current_user)

    # Validate leave dates
    if leave_data.start_date < date.today():
        raise HTTPException(
            status_code=400,
            detail="Leave cannot start in the past"
        )

    if leave_data.end_date < leave_data.start_date:
        raise HTTPException(
            status_code=400,
            detail="End date cannot be before start date"
        )

    # Prevent employees from applying on behalf of others
    if employee.id != leave_data.employee_id:
        raise HTTPException(
            status_code=403,
            detail="You can apply for leave only for yourself"
        )

    # Check available leave balance
    balance = db.query(LeaveBalance).filter(
        LeaveBalance.employee_id == employee.id,
        LeaveBalance.leave_type == leave_data.leave_type
    ).first()

    if not balance:
        raise HTTPException(
            status_code=400,
            detail="Leave balance not configured for this leave type"
        )

    requested_days = (
        leave_data.end_date - leave_data.start_date
    ).days + 1

    if requested_days > balance.remaining_days:
        raise HTTPException(
            status_code=400,
            detail="Insufficient leave balance"
        )

    # Create pending leave request
    new_leave = Leave(
        employee_id=employee.id,
        leave_type=leave_data.leave_type,
        start_date=leave_data.start_date,
        end_date=leave_data.end_date,
        reason=leave_data.reason,
        status="PENDING"
    )

    db.add(new_leave)
    db.commit()
    db.refresh(new_leave)

    return new_leave


# View own leave requests
@router.get("/my-leaves", response_model=list[LeaveResponse])
def get_my_leaves(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    employee = get_employee(db, current_user)

    return db.query(Leave).filter(
        Leave.employee_id == employee.id
    ).order_by(Leave.created_at.desc()).all()


# HR/Admin: View all leave requests
@router.get("/", response_model=list[LeaveResponse])
def get_all_leaves(
    db: Session = Depends(get_db),
    current_user: User = Depends(hr_or_admin)
):
    return db.query(Leave).order_by(
        Leave.created_at.desc()
    ).all()


# HR/Admin: Approve or reject leave
@router.put("/{leave_id}/status", response_model=LeaveResponse)
def update_leave_status(
    leave_id: int,
    status_data: LeaveStatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(hr_or_admin)
):
    leave = db.query(Leave).filter(
        Leave.id == leave_id
    ).with_for_update().first()

    if not leave:
        raise HTTPException(
            status_code=404,
            detail="Leave request not found"
        )

    if leave.status != "PENDING":
        raise HTTPException(
            status_code=400,
            detail="This leave request has already been processed"
        )

    # Deduct balance only when approved
    if status_data.status == "APPROVED":
        balance = db.query(LeaveBalance).filter(
            LeaveBalance.employee_id == leave.employee_id,
            LeaveBalance.leave_type == leave.leave_type
        ).with_for_update().first()

        if not balance:
            raise HTTPException(
                status_code=400,
                detail="Leave balance not found"
            )

        requested_days = (
            leave.end_date - leave.start_date
        ).days + 1

        if requested_days > balance.remaining_days:
            raise HTTPException(
                status_code=400,
                detail="Insufficient leave balance for approval"
            )

        balance.remaining_days -= requested_days

    leave.status = status_data.status
    leave.approved_by = current_user.id

    db.commit()
    db.refresh(leave)

    return leave


# View an employee's leave requests (HR/Admin)
@router.get(
    "/employee/{employee_id}",
    response_model=list[LeaveResponse]
)
def get_employee_leaves(
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

    return db.query(Leave).filter(
        Leave.employee_id == employee_id
    ).order_by(Leave.created_at.desc()).all()
