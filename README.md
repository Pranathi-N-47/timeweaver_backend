# TimeWeaver Backend - Quick Reference

**For complete setup guide**, see: [../SETUP_GUIDE.md](../SETUP_GUIDE.md)  
**For module specifications**, see: [../MODULE_SPECIFICATIONS.md](../MODULE_SPECIFICATIONS.md)

---

## 🚀 Quick Start

### 1. Database Setup (PostgreSQL)

```powershell
# Create database
psql -U postgres
CREATE DATABASE timeweaver_db;
\q
```

**Current Configuration**:
- Database: `timeweaver_db`
- User: `postgres`
- Host: `localhost`
- Port: `5432`
- Password: Check `.env` file

### 2. Backend Setup

```powershell
# Create and activate virtual environment
python -m venv venv
.\venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run migrations
alembic upgrade head

# Create admin user
python -m app.scripts.create_admin

# Start server
uvicorn app.main:app --reload
```

✅ Backend running at: http://localhost:8000  
✅ API Docs: http://localhost:8000/docs

---

## 📊 Database Connection

**Connection String** (in `.env`):
```
DATABASE_URL=postgresql://postgres:[YOUR_PASSWORD]@localhost:5432/timeweaver_db
```

**Verify Connection**:
```powershell
# Test connection
psql -U postgres -d timeweaver_db

# List tables
\dt

# View users
SELECT * FROM users;

# Exit
\q
```

---

## 📁 Project Structure

```
backend/
├── app/
│   ├── api/v1/endpoints/      # API endpoints (your code here)
│   │   ├── auth.py            # Module 1
│   │   ├── users.py           # Module 1
│   │   ├── courses.py         # Module 2
│   │   ├── departments.py     # Module 2
│   │   ├── timetables.py      # Module 3 (TO BUILD)
│   │   ├── faculty.py         # Module 4 (TO BUILD)
│   │   └── audit_logs.py      # Module 5
│   ├── models/                # SQLAlchemy models
│   ├── schemas/               # Pydantic schemas
│   ├── services/              # Business logic
│   ├── middleware/            # Audit logging
│   └── core/                  # Auth, security, config
├── tests/                     # Backend tests
├── alembic/                   # Database migrations
└── requirements.txt           # Python dependencies
```

---

## ✅ Current Status

### Completed (64 endpoints)

**Authentication** (6):
- Login, Logout, Me, Refresh,  Forgot/Reset Password

**User Management** (8):
- Full CRUD (admin) + Self-service profile/password

**Academic Entities** (48):
- Semesters, Departments, Courses, Sections, Rooms, Time Slots, Constraints
- All with RBAC protection

**Audit Logging** (2):
- Query logs with filters (admin only)

### To Build

**Module 3** (Student C):
- Timetable generation algorithm
- `app/services/timetable_generator.py`
- `app/api/v1/endpoints/timetables.py`

**Module 4** (Student D):
- Faculty management
- Workload calculator
- `app/api/v1/endpoints/faculty.py`
- `app/services/workload_calculator.py`

---

## 🧪 Testing

```powershell
# Run all tests
pytest

# Run specific test file
pytest tests/test_auth.py -v

# With coverage
pytest --cov=app --cov-report=html

# View coverage
# Open htmlcov/index.html
```

---

## 🔧 Useful Commands

### Development

```powershell
# Activate venv
.\venv\Scripts\activate

# Start server
uvicorn app.main:app --reload

# Start on different port
uvicorn app.main:app --reload --port 8001
```

### Database Migrations

```powershell
# Create new migration
alembic revision -m "description"

# Apply migrations
alembic upgrade head

# Rollback one
alembic downgrade -1

# View history
alembic history
```

### Database Operations

```powershell
# Connect
psql -U postgres -d timeweaver_db

# Common queries
SELECT * FROM users;
SELECT COUNT(*) FROM courses;
\dt  # List tables
\d users  # Describe users table
\q  # Exit
```

---

## 🔒 Default Credentials

```
Username: admin
Password: Admin@123
Email: admin@timeweaver.com
Role: ADMIN
```

---

## 🐛 Troubleshooting

**Database connection error**:
- Check PostgreSQL is running: `Get-Service postgresql*`
- Verify `.env` has correct password
- Test: `psql -U postgres -d timeweaver_db`

**Module not found**:
- Activate venv: `.\venv\Scripts\activate`
- Reinstall: `pip install -r requirements.txt`

**Port in use**:
```powershell
netstat -ano | findstr :8000
taskkill /PID [PID] /F
```

---

## 📚 Documentation

- **API Docs**: http://localhost:8000/docs (Swagger)
- **Alternative Docs**: http://localhost:8000/redoc
- **Setup Guide**: [../SETUP_GUIDE.md](../SETUP_GUIDE.md)
- **Module Specs**: [../MODULE_SPECIFICATIONS.md](../MODULE_SPECIFICATIONS.md)

---

## 🎯 For Students

Choose your module from MODULE_SPECIFICATIONS.md:
- **Module 1** (Student A): Frontend for Auth & Users
- **Module 2** (Student B): Frontend for Academic Data
- **Module 3** (Student C): Timetable Generation (backend + frontend)
- **Module 4** (Student D): Faculty Management (backend + frontend)
- **Module 5** (Student E): Frontend for Dashboard & Audit Logs

Backend for Modules 1, 2, and 5 is **already complete**!

---

**Questions?** Check SETUP_GUIDE.md or MODULE_SPECIFICATIONS.md
