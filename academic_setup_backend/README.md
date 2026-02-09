# Academic Setup Backend

Standalone backend API server for the Academic Setup frontend module.

## Features

- ✅ Departments Management
- ✅ Semesters Management
- ✅ Courses Management
- ✅ Sections Management
- ✅ In-memory storage (no database required)
- ✅ CORS enabled for all origins
- ✅ Auto-generated API documentation

## Requirements

```bash
pip install fastapi uvicorn
```

## Running the Server

```bash
python main.py
```

The server will start on `http://localhost:8000`

## API Endpoints

### Departments
- `GET /api/v1/departments/` - List all departments
- `GET /api/v1/departments/{id}` - Get specific department
- `POST /api/v1/departments/` - Create new department
- `PUT /api/v1/departments/{id}` - Update department
- `DELETE /api/v1/departments/{id}` - Delete department

### Semesters
- `GET /api/v1/semesters/` - List all semesters
- `GET /api/v1/semesters/{id}` - Get specific semester
- `POST /api/v1/semesters/` - Create new semester
- `PUT /api/v1/semesters/{id}` - Update semester
- `DELETE /api/v1/semesters/{id}` - Delete semester

### Courses
- `GET /api/v1/courses/` - List all courses
- `GET /api/v1/courses/{id}` - Get specific course
- `POST /api/v1/courses/` - Create new course
- `PUT /api/v1/courses/{id}` - Update course
- `DELETE /api/v1/courses/{id}` - Delete course

### Sections
- `GET /api/v1/sections/` - List all sections
- `GET /api/v1/sections/{id}` - Get specific section
- `POST /api/v1/sections/` - Create new section
- `PUT /api/v1/sections/{id}` - Update section
- `DELETE /api/v1/sections/{id}` - Delete section

## API Documentation

Once the server is running, visit:
- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

## Default Data

The server comes pre-loaded with:
- 5 departments (CSE, ECE, ME, CE, EEE)
- 4 semesters (Fall 2024, Spring 2025, Fall 2025, Spring 2026)
- 6 courses across different departments
- 4 sections

## Note

All data is stored in-memory and will be reset when the server restarts.
