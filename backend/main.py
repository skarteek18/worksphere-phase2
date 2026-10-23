
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from Database import Base, engine
from Auth import router as auth_router
from Employees import router as employees_router
from Attendance import router as attendance_router
from Leaves import router as leaves_router
from LeavePolicies import router as leave_policies_router
from Payroll import router as payroll_router
from Admin import router as admin_router

# Create FastAPI application
app = FastAPI(
    title="WorkSphere HRMS API",
    description="Phase 2 - RBAC and Advanced HR Features",
    version="2.0.0"
)

# Create database tables
Base.metadata.create_all(bind=engine)

# Enable frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API routers
app.include_router(auth_router, prefix="/auth", tags=["Authentication"])
app.include_router(employees_router, prefix="/employees", tags=["Employees"])
app.include_router(attendance_router, prefix="/attendance", tags=["Attendance"])
app.include_router(leaves_router, prefix="/leaves", tags=["Leave Management"])
app.include_router(
    leave_policies_router,
    prefix="/leave-policies",
    tags=["Leave Policies"]
)
app.include_router(payroll_router, prefix="/payroll", tags=["Payroll"])
app.include_router(admin_router, prefix="/admin", tags=["Admin Management"])


# Home endpoint
@app.get("/")
def home():
    return {
        "message": "Welcome to WorkSphere HRMS API",
        "phase": "Phase 2",
        "features": [
            "Role-Based Access Control",
            "Employee Self-Service Portal",
            "Advanced Attendance",
            "Leave Policies and Balances",
            "Enhanced Payroll",
            "Admin User Management"
        ]
    }


# Health check endpoint
@app.get("/health")
def health_check():
    return {
        "status": "running",
        "application": "WorkSphere HRMS"
    }
