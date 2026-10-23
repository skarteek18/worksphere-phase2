
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from Database import get_db
from Models import LeavePolicy, LeaveBalance, Employee, User
from Schemas import (
    LeavePolicyCreate,
    LeavePolicyResponse,
    LeaveBalanceCreate,
    LeaveBalanceResponse
)
from Security import hr_or_admin


router = APIRouter()


# Create a leave policy (HR/Admin)
@router.post("/policies", response_model=LeavePolicyResponse, status_code=201)
def create_leave_policy(
    policy_data: LeavePolicyCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(hr_or_admin)
):
    existing_policy = db.query(LeavePolicy).filter(
        LeavePolicy.leave_type == policy_data.leave_type
    ).first()

    if existing_policy:
        raise HTTPException(
            status_code=400,
            detail="Leave policy already exists"
        )

    policy = LeavePolicy(
        leave_type=policy_data.leave_type,
        total_days_allowed=policy_data.total_days_allowed
    )

    db.add(policy)
    db.commit()
    db.refresh(policy)

    return policy


# View all leave policies
@router.get("/policies", response_model=list[LeavePolicyResponse])
def get_leave_policies(
    db: Session = Depends(get_db),
    current_user: User = Depends(hr_or_admin)
):
    return db.query(LeavePolicy).all()


# Update a leave policy
@router.put("/policies/{policy_id}", response_model=LeavePolicyResponse)
def update_leave_policy(
    policy_id: int,
    policy_data: LeavePolicyCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(hr_or_admin)
):
    policy = db.query(LeavePolicy).filter(
        LeavePolicy.id == policy_id
    ).first()

    if not policy:
        raise HTTPException(
            status_code=404,
            detail="Leave policy not found"
        )

    duplicate = db.query(LeavePolicy).filter(
        LeavePolicy.leave_type == policy_data.leave_type,
        LeavePolicy.id != policy_id
    ).first()

    if duplicate:
        raise HTTPException(
            status_code=400,
            detail="Another policy already uses this leave type"
        )

    policy.leave_type = policy_data.leave_type
    policy.total_days_allowed = policy_data.total_days_allowed

    db.commit()
    db.refresh(policy)

    return policy


# Create a leave balance for an employee
@router.post("/balances", response_model=LeaveBalanceResponse, status_code=201)
def create_leave_balance(
    balance_data: LeaveBalanceCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(hr_or_admin)
):
    employee = db.query(Employee).filter(
        Employee.id == balance_data.employee_id
    ).first()

    if not employee:
        raise HTTPException(
            status_code=404,
            detail="Employee not found"
        )

    policy = db.query(LeavePolicy).filter(
        LeavePolicy.leave_type == balance_data.leave_type
    ).first()

    if not policy:
        raise HTTPException(
            status_code=404,
            detail="Leave policy not found"
        )

    if balance_data.remaining_days > policy.total_days_allowed:
        raise HTTPException(
            status_code=400,
            detail="Balance cannot exceed the policy allowance"
        )

    existing_balance = db.query(LeaveBalance).filter(
        LeaveBalance.employee_id == balance_data.employee_id,
        LeaveBalance.leave_type == balance_data.leave_type
    ).first()

    if existing_balance:
        raise HTTPException(
            status_code=400,
            detail="Leave balance already exists"
        )

    balance = LeaveBalance(
        employee_id=balance_data.employee_id,
        leave_type=balance_data.leave_type,
        remaining_days=balance_data.remaining_days
    )

    db.add(balance)
    db.commit()
    db.refresh(balance)

    return balance


# View all employee leave balances (HR/Admin)
@router.get("/balances", response_model=list[LeaveBalanceResponse])
def get_all_leave_balances(
    db: Session = Depends(get_db),
    current_user: User = Depends(hr_or_admin)
):
    return db.query(LeaveBalance).all()


# View leave balances for a specific employee (HR/Admin)
@router.get(
    "/balances/{employee_id}",
    response_model=list[LeaveBalanceResponse]
)
def get_employee_leave_balances(
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

    return db.query(LeaveBalance).filter(
        LeaveBalance.employee_id == employee_id
    ).all()


# Update an employee's remaining leave balance
@router.put("/balances/{balance_id}", response_model=LeaveBalanceResponse)
def update_leave_balance(
    balance_id: int,
    balance_data: LeaveBalanceCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(hr_or_admin)
):
    balance = db.query(LeaveBalance).filter(
        LeaveBalance.id == balance_id
    ).first()

    if not balance:
        raise HTTPException(
            status_code=404,
            detail="Leave balance not found"
        )

    if balance_data.employee_id != balance.employee_id:
        raise HTTPException(
            status_code=400,
            detail="Employee ID cannot be changed"
        )

    policy = db.query(LeavePolicy).filter(
        LeavePolicy.leave_type == balance_data.leave_type
    ).first()

    if not policy:
        raise HTTPException(
            status_code=404,
            detail="Leave policy not found"
        )

    if balance_data.remaining_days > policy.total_days_allowed:
        raise HTTPException(
            status_code=400,
            detail="Balance cannot exceed the policy allowance"
        )

    balance.leave_type = balance_data.leave_type
    balance.remaining_days = balance_data.remaining_days

    db.commit()
    db.refresh(balance)

    return balance
