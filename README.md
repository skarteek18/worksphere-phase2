# worksphere-phase2


WorkSphere – HR Management System

Phase 2: Role-Based Access Control & Advanced HR Features

Project Overview

WorkSphere is a full-stack Human Resource Management System developed to simplify employee management, attendance tracking, leave management, payroll processing, and user administration.

Phase 2 introduces Role-Based Access Control (RBAC), an Employee Self-Service Portal, advanced attendance validations, leave policies, enhanced payroll, and admin user management.

Technologies Used

Backend

- Python
- FastAPI
- SQLAlchemy
- SQLite
- JWT Authentication
- Pydantic

Frontend

- React.js
- Vite
- JavaScript
- CSS
- Axios

User Roles

Role| Permissions
EMPLOYEE| View own profile, mark attendance, apply for leave, view payroll
HR| Manage employees, approve leaves, view attendance, generate payroll
ADMIN| Manage users and roles, control access, view analytics

Modules Implemented

Module 8: Role-Based Access Control

- JWT authentication
- Role validation
- Protected API endpoints
- Ownership validation

Module 9: Employee Self-Service Portal

- Employee dashboard
- Personal profile
- Attendance history
- Leave application and status tracking
- Salary details

Module 10: Advanced Attendance Controls

- Daily check-in validation
- Attendance status tracking
- Late entry identification
- Automatic absence processing

Module 11: Leave Policies & Balances

- Leave policy management
- Employee leave balances
- Leave approval and rejection
- Automatic balance deduction
- Leave limit validation

Module 12: Payroll Enhancements

- Basic salary
- Allowances
- Deductions
- Net salary calculation
- Monthly payroll history

Module 13: Admin Controls & User Management

- Create and update users
- Assign roles
- Activate or deactivate accounts
- Delete users where permitted

Database Tables

- Users
- Employees
- Attendance
- Leaves
- Leave_Policies
- Leave_Balance
- Payroll
- Notifications

Installation and Setup

1. Clone the repository

git clone YOUR_GITHUB_REPOSITORY_URL
cd WorkSphere

2. Set up the backend

cd backend
python -m venv venv

Activate the environment on Windows:

venv\Scripts\activate

Install dependencies:

pip install -r Requirements.txt

Create a ".env" file based on ".env.example" and configure a strong secret key.

3. Run the backend

uvicorn Main:app --reload

Open the API documentation at:
"http://127.0.0.1:8000/docs"

4. Set up the frontend

Open a new terminal:

cd frontend
npm install
npm run dev

Open the local frontend URL displayed by Vite.

Security Features

- JWT-based authentication
- Role-based authorization
- Password hashing
- Pydantic request validation
- Employee data ownership checks
- Environment-based secret configuration

Project Duration

2 Days

Expected Outcome

A secure, role-driven HR management application with employee self-service, attendance controls, leave balance management, payroll details, and administrative user management.

Author

WorkSphere Development Team
