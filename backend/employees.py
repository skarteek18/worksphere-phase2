
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from Database import get_db
from Models import Employee, User
from Schemas import EmployeeCreate, EmployeeUpdate, EmployeeResponse
from Security import get_current_user, hr_or_admin


router = APIRouter()


# Create employee (HR or Admin)
@router.post("/", response_model=EmployeeResponse, status_code=201)
def create_employee(
    employee_data: EmployeeCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(hr_or_admin)
):
    # Check whether the user exists
    user = db.query(User).filter(
        User.id == employee_data.user_id
    ).first()

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    # Check whether an employee record already exists
    existing_employee = db.query(Employee).filter(
        Employee.user_id == employee_data.user_id
    ).first()

    if existing_employee:
        raise HTTPException(
            status_code=400,
            detail="Employee record already exists"
        )

    new_employee = Employee(**employee_data.model_dump())

    db.add(new_employee)
    db.commit()
    db.refresh(new_employee)

    return new_employee


# View employees
@router.get("/", response_model=list[EmployeeResponse])
def get_employees(
    db: Session = Depends(get_db),
    current_user: User = Depends(hr_or_admin)
):
    return db.query(Employee).all()


# View employee by ID
@router.get("/{employee_id}", response_model=EmployeeResponse)
def get_employee(
    employee_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    employee = db.query(Employee).filter(
        Employee.id == employee_id
    ).first()

    if not employee:
        raise HTTPException(
            status_code=404,
            detail="Employee not found"
        )

    # Employees can view only their own records
    if current_user.role == "EMPLOYEE":
        if employee.user_id != current_user.id:
            raise HTTPException(
                status_code=403,
                detail="You can only view your own profile"
            )

    return employee


# Update employee (HR or Admin)
@router.put("/{employee_id}", response_model=EmployeeResponse)
def update_employee(
    employee_id: int,
    employee_data: EmployeeUpdate,
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

    update_data = employee_data.model_dump(exclude_unset=True)

    for key, value in update_data.items():
        setattr(employee, key, value)

    db.commit()
    db.refresh(employee)

    return employee


# Delete employee (Admin only)
@router.delete("/{employee_id}")
def delete_employee(
    employee_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role != "ADMIN":
        raise HTTPException(
            status_code=403,
            detail="Only Admin can delete employee records"
        )

    employee = db.query(Employee).filter(
        Employee.id == employee_id
    ).first()

    if not employee:
        raise HTTPException(
            status_code=404,
            detail="Employee not found"
        )

    db.delete(employee)
    db.commit()

    return {"message": "Employee deleted successfully"}
