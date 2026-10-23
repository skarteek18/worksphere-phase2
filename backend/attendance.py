
from datetime import datetime, date, time
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from Database import get_db
from Models import Attendance, Employee, User
from Schemas import AttendanceResponse
from Security import get_current_user, hr_or_admin


router = APIRouter()


# Find the employee record for the logged-in user
def get_employee_for_user(db: Session, user: User):
    employee = db.query(Employee).filter(
        Employee.user_id == user.id
    ).first()

    if not employee:
        raise HTTPException(
            status_code=404,
            detail="Employee record not found"
        )

    return employee


# Mark attendance / check in
@router.post("/check-in", response_model=AttendanceResponse)
def check_in(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    employee = get_employee_for_user(db, current_user)

    today = date.today()

    existing = db.query(Attendance).filter(
        Attendance.employee_id == employee.id,
        Attendance.attendance_date == today
    ).first()

    if existing:
        raise HTTPException(
            status_code=400,
            detail="Attendance already marked for today"
        )

    now = datetime.now()

    # Employees arriving after 9:15 AM are marked late
    office_start = datetime.combine(today, time(9, 15))
    late_minutes = max(
        0, int((now - office_start).total_seconds() // 60)
    )

    attendance = Attendance(
        employee_id=employee.id,
        attendance_date=today,
        check_in=now,
        status="LATE" if late_minutes > 0 else "PRESENT",
        late_minutes=late_minutes,
        overtime_hours=0
    )

    db.add(attendance)
    db.commit()
    db.refresh(attendance)

    return attendance


# Check out
@router.post("/check-out", response_model=AttendanceResponse)
def check_out(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    employee = get_employee_for_user(db, current_user)

    today = date.today()

    attendance = db.query(Attendance).filter(
        Attendance.employee_id == employee.id,
        Attendance.attendance_date == today
    ).first()

    if not attendance:
        raise HTTPException(
            status_code=400,
            detail="Please check in before checking out"
        )

    if attendance.check_out:
        raise HTTPException(
            status_code=400,
            detail="You have already checked out today"
        )

    now = datetime.now()

    attendance.check_out = now

    # Calculate overtime after 8 working hours
    if attendance.check_in:
        working_hours = (
            now - attendance.check_in
        ).total_seconds() / 3600

        attendance.overtime_hours = round(
            max(0, working_hours - 8), 2
        )

    db.commit()
    db.refresh(attendance)

    return attendance


# View own attendance history
@router.get("/my-history", response_model=list[AttendanceResponse])
def my_attendance_history(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    employee = get_employee_for_user(db, current_user)

    return db.query(Attendance).filter(
        Attendance.employee_id == employee.id
    ).order_by(
        Attendance.attendance_date.desc()
    ).all()


# HR/Admin: View all attendance records
@router.get("/", response_model=list[AttendanceResponse])
def get_all_attendance(
    db: Session = Depends(get_db),
    current_user: User = Depends(hr_or_admin)
):
    return db.query(Attendance).order_by(
        Attendance.attendance_date.desc()
    ).all()


# HR/Admin: View attendance for a specific employee
@router.get(
    "/employee/{employee_id}",
    response_model=list[AttendanceResponse]
)
def get_employee_attendance(
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

    return db.query(Attendance).filter(
        Attendance.employee_id == employee_id
    ).order_by(
        Attendance.attendance_date.desc()
    ).all()


# HR/Admin: Mark absent for a past date when no record exists
@router.post("/mark-absent/{employee_id}")
def mark_absent(
    employee_id: int,
    attendance_date: date,
    db: Session = Depends(get_db),
    current_user: User = Depends(hr_or_admin)
):
    if attendance_date >= date.today():
        raise HTTPException(
            status_code=400,
            detail="Only past dates can be marked absent"
        )

    employee = db.query(Employee).filter(
        Employee.id == employee_id
    ).first()

    if not employee:
        raise HTTPException(
            status_code=404,
            detail="Employee not found"
        )

    existing = db.query(Attendance).filter(
        Attendance.employee_id == employee_id,
        Attendance.attendance_date == attendance_date
    ).first()

    if existing:
        raise HTTPException(
            status_code=400,
            detail="Attendance record already exists"
        )

    attendance = Attendance(
        employee_id=employee_id,
        attendance_date=attendance_date,
        status="ABSENT",
        late_minutes=0,
        overtime_hours=0
    )

    db.add(attendance)
    db.commit()

    return {"message": "Employee marked absent successfully"}
