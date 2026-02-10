"""
Academic Setup Backend - Standalone API Server
Handles: Departments, Semesters, Courses, and Sections

Run: python main.py
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, field_validator
from typing import Optional, Literal
import uvicorn

app = FastAPI(title="Academic Setup API", version="1.0.0")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory storage
departments_db = []
semesters_db = []
courses_db = []
sections_db = []

# Pydantic Models
class Department(BaseModel):
    id: Optional[int] = None
    code: str
    name: str
    description: Optional[str] = None

class Semester(BaseModel):
    id: Optional[int] = None
    name: str
    academic_year: str
    semester_type: str  # ODD or EVEN
    start_date: str
    end_date: str
    is_active: bool = True

class Course(BaseModel):
    id: Optional[int] = None
    code: str
    name: str
    credits: int = Field(..., gt=0)
    department_id: int
    theory_hours: int = 0
    lab_hours: int = 0
    tutorial_hours: int = 0
    is_elective: bool = False
    requires_lab: bool = False
    
    @field_validator('credits')
    @classmethod
    def validate_credits(cls, v):
        if v <= 0:
            raise ValueError('Credits must be positive')
        return v

class Section(BaseModel):
    id: Optional[int] = None
    department_id: int
    name: str
    batch_year_start: int
    batch_year_end: int
    student_count: int = Field(..., gt=0)
    
    @field_validator('student_count')
    @classmethod
    def validate_student_count(cls, v):
        if v <= 0:
            raise ValueError('Student count must be positive')
        return v

# Initialize with mock data
def init_data():
    global departments_db, semesters_db, courses_db, sections_db
    
    departments_db = [
        {"id": 1, "code": "CSE", "name": "Computer Science & Engineering", "description": "CS Department"},
        {"id": 2, "code": "ECE", "name": "Electronics & Communication Engineering", "description": "ECE Department"},
        {"id": 3, "code": "ME", "name": "Mechanical Engineering", "description": "ME Department"},
        {"id": 4, "code": "CE", "name": "Civil Engineering", "description": "CE Department"},
        {"id": 5, "code": "EEE", "name": "Electrical & Electronics Engineering", "description": "EEE Department"},
    ]
    
    semesters_db = [
        {"id": 1, "name": "Fall 2024", "academic_year": "2024-2025", "semester_type": "ODD", 
         "start_date": "2024-08-01", "end_date": "2024-12-15", "is_active": True},
        {"id": 2, "name": "Spring 2025", "academic_year": "2024-2025", "semester_type": "EVEN",
         "start_date": "2025-01-10", "end_date": "2025-05-20", "is_active": False},
        {"id": 3, "name": "Fall 2025", "academic_year": "2025-2026", "semester_type": "ODD",
         "start_date": "2025-08-01", "end_date": "2025-12-15", "is_active": False},
        {"id": 4, "name": "Spring 2026", "academic_year": "2025-2026", "semester_type": "EVEN",
         "start_date": "2026-01-10", "end_date": "2026-05-20", "is_active": True},
    ]
    
    courses_db = [
        {"id": 1, "code": "CS101", "name": "Introduction to Computer Science", "credits": 4,
         "department_id": 1, "theory_hours": 3, "lab_hours": 2, "tutorial_hours": 0,
         "is_elective": False, "requires_lab": True},
        {"id": 2, "code": "CS201", "name": "Data Structures and Algorithms", "credits": 4,
         "department_id": 1, "theory_hours": 3, "lab_hours": 2, "tutorial_hours": 0,
         "is_elective": False, "requires_lab": True},
        {"id": 3, "code": "CS301", "name": "Database Management Systems", "credits": 3,
         "department_id": 1, "theory_hours": 3, "lab_hours": 0, "tutorial_hours": 0,
         "is_elective": False, "requires_lab": False},
        {"id": 4, "code": "CS302", "name": "Web Development", "credits": 3,
         "department_id": 1, "theory_hours": 2, "lab_hours": 2, "tutorial_hours": 0,
         "is_elective": True, "requires_lab": True},
        {"id": 5, "code": "ECE101", "name": "Electronics Fundamentals", "credits": 4,
         "department_id": 2, "theory_hours": 3, "lab_hours": 2, "tutorial_hours": 0,
         "is_elective": False, "requires_lab": True},
        {"id": 6, "code": "ME101", "name": "Engineering Mechanics", "credits": 4,
         "department_id": 3, "theory_hours": 4, "lab_hours": 0, "tutorial_hours": 1,
         "is_elective": False, "requires_lab": False},
    ]
    
    sections_db = [
        {"id": 1, "department_id": 1, "name": "CSE-A", "batch_year_start": 2023, 
         "batch_year_end": 2027, "student_count": 60},
        {"id": 2, "department_id": 1, "name": "CSE-B", "batch_year_start": 2023,
         "batch_year_end": 2027, "student_count": 58},
        {"id": 3, "department_id": 2, "name": "ECE-A", "batch_year_start": 2024,
         "batch_year_end": 2028, "student_count": 55},
        {"id": 4, "department_id": 3, "name": "ME-A", "batch_year_start": 2023,
         "batch_year_end": 2027, "student_count": 50},
    ]

# Initialize data on startup
@app.on_event("startup")
def startup_event():
    init_data()

# ========== DEPARTMENT ENDPOINTS ==========

@app.get("/api/v1/departments/")
def list_departments():
    """Get all departments"""
    return departments_db

@app.get("/api/v1/departments/{dept_id}")
def get_department(dept_id: int):
    """Get a specific department"""
    dept = next((d for d in departments_db if d["id"] == dept_id), None)
    if not dept:
        raise HTTPException(status_code=404, detail="Department not found")
    return dept

@app.post("/api/v1/departments/")
def create_department(dept: Department):
    """Create a new department"""
    new_id = max([d["id"] for d in departments_db], default=0) + 1
    new_dept = dept.dict()
    new_dept["id"] = new_id
    departments_db.append(new_dept)
    return new_dept

@app.put("/api/v1/departments/{dept_id}")
def update_department(dept_id: int, dept: Department):
    """Update an existing department"""
    for i, d in enumerate(departments_db):
        if d["id"] == dept_id:
            updated = dept.dict()
            updated["id"] = dept_id
            departments_db[i] = updated
            return updated
    raise HTTPException(status_code=404, detail="Department not found")

@app.delete("/api/v1/departments/{dept_id}")
def delete_department(dept_id: int):
    """Delete a department"""
    global departments_db
    departments_db = [d for d in departments_db if d["id"] != dept_id]
    return {"message": "Department deleted successfully"}

# ========== SEMESTER ENDPOINTS ==========

@app.get("/api/v1/semesters/")
def list_semesters():
    """Get all semesters"""
    return semesters_db

@app.get("/api/v1/semesters/{sem_id}")
def get_semester(sem_id: int):
    """Get a specific semester"""
    sem = next((s for s in semesters_db if s["id"] == sem_id), None)
    if not sem:
        raise HTTPException(status_code=404, detail="Semester not found")
    return sem

@app.post("/api/v1/semesters/")
def create_semester(sem: Semester):
    """Create a new semester"""
    new_id = max([s["id"] for s in semesters_db], default=0) + 1
    new_sem = sem.dict()
    new_sem["id"] = new_id
    semesters_db.append(new_sem)
    return new_sem

@app.put("/api/v1/semesters/{sem_id}")
def update_semester(sem_id: int, sem: Semester):
    """Update an existing semester"""
    for i, s in enumerate(semesters_db):
        if s["id"] == sem_id:
            updated = sem.dict()
            updated["id"] = sem_id
            semesters_db[i] = updated
            return updated
    raise HTTPException(status_code=404, detail="Semester not found")

@app.delete("/api/v1/semesters/{sem_id}")
def delete_semester(sem_id: int):
    """Delete a semester"""
    global semesters_db
    semesters_db = [s for s in semesters_db if s["id"] != sem_id]
    return {"message": "Semester deleted successfully"}

# ========== COURSE ENDPOINTS ==========

@app.get("/api/v1/courses/")
def list_courses():
    """Get all courses"""
    return courses_db

@app.get("/api/v1/courses/{course_id}")
def get_course(course_id: int):
    """Get a specific course"""
    course = next((c for c in courses_db if c["id"] == course_id), None)
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    return course

@app.post("/api/v1/courses/")
def create_course(course: Course):
    """Create a new course"""
    new_id = max([c["id"] for c in courses_db], default=0) + 1
    new_course = course.dict()
    new_course["id"] = new_id
    courses_db.append(new_course)
    return new_course

@app.put("/api/v1/courses/{course_id}")
def update_course(course_id: int, course: Course):
    """Update an existing course"""
    for i, c in enumerate(courses_db):
        if c["id"] == course_id:
            updated = course.dict()
            updated["id"] = course_id
            courses_db[i] = updated
            return updated
    raise HTTPException(status_code=404, detail="Course not found")

@app.delete("/api/v1/courses/{course_id}")
def delete_course(course_id: int):
    """Delete a course"""
    global courses_db
    courses_db = [c for c in courses_db if c["id"] != course_id]
    return {"message": "Course deleted successfully"}

# ========== SECTION ENDPOINTS ==========

@app.get("/api/v1/sections/")
def list_sections():
    """Get all sections"""
    return sections_db

@app.get("/api/v1/sections/{section_id}")
def get_section(section_id: int):
    """Get a specific section"""
    section = next((s for s in sections_db if s["id"] == section_id), None)
    if not section:
        raise HTTPException(status_code=404, detail="Section not found")
    return section

@app.post("/api/v1/sections/")
def create_section(section: Section):
    """Create a new section"""
    new_id = max([s["id"] for s in sections_db], default=0) + 1
    new_section = section.dict()
    new_section["id"] = new_id
    sections_db.append(new_section)
    return new_section

@app.put("/api/v1/sections/{section_id}")
def update_section(section_id: int, section: Section):
    """Update an existing section"""
    for i, s in enumerate(sections_db):
        if s["id"] == section_id:
            updated = section.dict()
            updated["id"] = section_id
            sections_db[i] = updated
            return updated
    raise HTTPException(status_code=404, detail="Section not found")

@app.delete("/api/v1/sections/{section_id}")
def delete_section(section_id: int):
    """Delete a section"""
    global sections_db
    sections_db = [s for s in sections_db if s["id"] != section_id]
    return {"message": "Section deleted successfully"}

# ========== HEALTH CHECK ==========

@app.get("/")
def root():
    """Root endpoint - API info"""
    return {
        "message": "Academic Setup API",
        "version": "1.0.0",
        "endpoints": {
            "departments": "/api/v1/departments/",
            "semesters": "/api/v1/semesters/",
            "courses": "/api/v1/courses/",
            "sections": "/api/v1/sections/"
        },
        "docs": "/docs"
    }

@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}

# Run the server
if __name__ == "__main__":
    print("=" * 60)
    print("🚀 Academic Setup Backend API Server")
    print("=" * 60)
    print(f"📍 API Base URL: http://localhost:8000/api/v1")
    print(f"📖 API Documentation: http://localhost:8000/docs")
    print(f"🏥 Health Check: http://localhost:8000/health")
    print()
    print("✅ Pre-loaded Data:")
    print(f"   - {len(departments_db)} departments")
    print(f"   - {len(semesters_db)} semesters")
    print(f"   - {len(courses_db)} courses")
    print(f"   - {len(sections_db)} sections")
    print()
    print("Press CTRL+C to stop")
    print("=" * 60)
    print()
    
    uvicorn.run(app, host="0.0.0.0", port=8000)
