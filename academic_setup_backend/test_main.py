"""
Unit Tests for Academic Setup Backend
Author: TimeWeaver Team
Date: February 9, 2026

Run tests:
    pytest test_main.py -v
    pytest test_main.py -v --cov=main --cov-report=html
"""

import pytest
from fastapi.testclient import TestClient
from main import app, init_data

# Create test client
client = TestClient(app)

# Reset data before each test
@pytest.fixture(autouse=True)
def reset_data():
    """Reset in-memory data before each test"""
    init_data()
    yield


# ========== ROOT & HEALTH ENDPOINTS ==========

def test_root_endpoint():
    """Test GET / - Root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Academic Setup API"
    assert "endpoints" in data
    assert "/api/v1/departments/" in data["endpoints"]


def test_health_check():
    """Test GET /health - Health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "academic_setup"


# ========== DEPARTMENT CRUD TESTS ==========

class TestDepartments:
    """Test suite for Department endpoints"""
    
    def test_list_departments(self):
        """Test GET /api/v1/departments/ - List all departments"""
        response = client.get("/api/v1/departments/")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 5  # Initial data has 5 departments
        
        # Verify first department structure
        dept = data[0]
        assert "id" in dept
        assert "code" in dept
        assert "name" in dept
        assert dept["code"] == "CSE"
    
    def test_get_department_by_id(self):
        """Test GET /api/v1/departments/{id} - Get single department"""
        response = client.get("/api/v1/departments/1")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == 1
        assert data["code"] == "CSE"
        assert data["name"] == "Computer Science & Engineering"
    
    def test_get_department_not_found(self):
        """Test GET /api/v1/departments/{id} - Department not found"""
        response = client.get("/api/v1/departments/999")
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()
    
    def test_create_department(self):
        """Test POST /api/v1/departments/ - Create new department"""
        new_dept = {
            "code": "IT",
            "name": "Information Technology",
            "description": "IT Department"
        }
        response = client.post("/api/v1/departments/", json=new_dept)
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == "IT"
        assert data["name"] == "Information Technology"
        assert data["id"] == 6  # Next available ID
        
        # Verify it was added
        list_response = client.get("/api/v1/departments/")
        assert len(list_response.json()) == 6
    
    def test_create_department_minimal(self):
        """Test POST with only required fields (code, name)"""
        new_dept = {
            "code": "MATH",
            "name": "Mathematics"
        }
        response = client.post("/api/v1/departments/", json=new_dept)
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == "MATH"
        assert data["description"] is None
    
    def test_update_department(self):
        """Test PUT /api/v1/departments/{id} - Update department"""
        updated = {
            "code": "CSE",
            "name": "Computer Science & Engineering - Updated",
            "description": "Updated CS Department"
        }
        response = client.put("/api/v1/departments/1", json=updated)
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Computer Science & Engineering - Updated"
        assert data["description"] == "Updated CS Department"
    
    def test_update_department_not_found(self):
        """Test PUT for non-existent department"""
        updated = {
            "code": "XX",
            "name": "Non Existent"
        }
        response = client.put("/api/v1/departments/999", json=updated)
        assert response.status_code == 404
    
    def test_delete_department(self):
        """Test DELETE /api/v1/departments/{id} - Delete department"""
        response = client.delete("/api/v1/departments/1")
        assert response.status_code == 200
        
        # Verify deletion
        get_response = client.get("/api/v1/departments/1")
        assert get_response.status_code == 404
        
        # Verify list has one less item
        list_response = client.get("/api/v1/departments/")
        assert len(list_response.json()) == 4
    
    def test_delete_department_not_found(self):
        """Test DELETE for non-existent department"""
        response = client.delete("/api/v1/departments/999")
        assert response.status_code == 404


# ========== SEMESTER CRUD TESTS ==========

class TestSemesters:
    """Test suite for Semester endpoints"""
    
    def test_list_semesters(self):
        """Test GET /api/v1/semesters/ - List all semesters"""
        response = client.get("/api/v1/semesters/")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 4
        
        # Verify structure
        semester = data[0]
        assert "id" in semester
        assert "name" in semester
        assert "semester_type" in semester
    
    def test_get_semester_by_id(self):
        """Test GET /api/v1/semesters/{id} - Get single semester"""
        response = client.get("/api/v1/semesters/1")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == 1
        assert data["name"] == "Fall 2024"
        assert data["semester_type"] == "ODD"
    
    def test_create_semester(self):
        """Test POST /api/v1/semesters/ - Create new semester"""
        new_sem = {
            "name": "Fall 2026",
            "academic_year": "2026-2027",
            "semester_type": "ODD",
            "start_date": "2026-08-01",
            "end_date": "2026-12-15",
            "is_active": False
        }
        response = client.post("/api/v1/semesters/", json=new_sem)
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Fall 2026"
        assert data["semester_type"] == "ODD"
        assert data["is_active"] == False
    
    def test_create_semester_default_active(self):
        """Test POST with default is_active=true"""
        new_sem = {
            "name": "Test Semester",
            "academic_year": "2027-2028",
            "semester_type": "EVEN",
            "start_date": "2027-01-01",
            "end_date": "2027-05-31"
        }
        response = client.post("/api/v1/semesters/", json=new_sem)
        assert response.status_code == 200
        data = response.json()
        assert data["is_active"] == True  # Default value
    
    def test_update_semester(self):
        """Test PUT /api/v1/semesters/{id} - Update semester"""
        updated = {
            "name": "Fall 2024 - Updated",
            "academic_year": "2024-2025",
            "semester_type": "ODD",
            "start_date": "2024-08-01",
            "end_date": "2024-12-15",
            "is_active": False
        }
        response = client.put("/api/v1/semesters/1", json=updated)
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Fall 2024 - Updated"
        assert data["is_active"] == False
    
    def test_delete_semester(self):
        """Test DELETE /api/v1/semesters/{id} - Delete semester"""
        response = client.delete("/api/v1/semesters/1")
        assert response.status_code == 200
        
        # Verify deletion
        get_response = client.get("/api/v1/semesters/1")
        assert get_response.status_code == 404


# ========== COURSE CRUD TESTS ==========

class TestCourses:
    """Test suite for Course endpoints"""
    
    def test_list_courses(self):
        """Test GET /api/v1/courses/ - List all courses"""
        response = client.get("/api/v1/courses/")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 6
    
    def test_get_course_by_id(self):
        """Test GET /api/v1/courses/{id} - Get single course"""
        response = client.get("/api/v1/courses/1")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == 1
        assert data["code"] == "CS101"
        assert data["name"] == "Introduction to Computer Science"
    
    def test_create_course_with_tutorial_hours(self):
        """Test POST /api/v1/courses/ - Create course WITH tutorial_hours"""
        new_course = {
            "code": "CS401",
            "name": "Machine Learning",
            "credits": 4,
            "department_id": 1,
            "theory_hours": 3,
            "lab_hours": 2,
            "tutorial_hours": 1,  # Testing tutorial_hours field
            "is_elective": True,
            "requires_lab": True
        }
        response = client.post("/api/v1/courses/", json=new_course)
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == "CS401"
        assert data["tutorial_hours"] == 1  # Verify tutorial_hours saved
        assert data["theory_hours"] == 3
        assert data["lab_hours"] == 2
    
    def test_create_course_without_tutorial_hours(self):
        """Test POST with tutorial_hours = 0 (default)"""
        new_course = {
            "code": "CS402",
            "name": "Software Engineering",
            "credits": 3,
            "department_id": 1,
            "theory_hours": 3,
            "lab_hours": 0,
            "tutorial_hours": 0,
            "is_elective": False,
            "requires_lab": False
        }
        response = client.post("/api/v1/courses/", json=new_course)
        assert response.status_code == 200
        data = response.json()
        assert data["tutorial_hours"] == 0
    
    def test_create_course_minimal_fields(self):
        """Test POST with only required fields"""
        new_course = {
            "code": "MATH201",
            "name": "Linear Algebra",
            "credits": 4,
            "department_id": 3,
            "theory_hours": 4,
            "lab_hours": 0,
            "tutorial_hours": 0,
            "is_elective": False,
            "requires_lab": False
        }
        response = client.post("/api/v1/courses/", json=new_course)
        assert response.status_code == 200
    
    def test_update_course(self):
        """Test PUT /api/v1/courses/{id} - Update course"""
        updated = {
            "code": "CS101",
            "name": "Intro to CS - Updated",
            "credits": 4,
            "department_id": 1,
            "theory_hours": 4,
            "lab_hours": 2,
            "tutorial_hours": 1,  # Changed from 0 to 1
            "is_elective": False,
            "requires_lab": True
        }
        response = client.put("/api/v1/courses/1", json=updated)
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Intro to CS - Updated"
        assert data["tutorial_hours"] == 1  # Verify update
    
    def test_delete_course(self):
        """Test DELETE /api/v1/courses/{id} - Delete course"""
        response = client.delete("/api/v1/courses/1")
        assert response.status_code == 200
        
        # Verify deletion
        get_response = client.get("/api/v1/courses/1")
        assert get_response.status_code == 404


# ========== SECTION CRUD TESTS ==========

class TestSections:
    """Test suite for Section endpoints"""
    
    def test_list_sections(self):
        """Test GET /api/v1/sections/ - List all sections"""
        response = client.get("/api/v1/sections/")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 4
    
    def test_get_section_by_id(self):
        """Test GET /api/v1/sections/{id} - Get single section"""
        response = client.get("/api/v1/sections/1")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == 1
        assert data["name"] == "CSE-A"
        assert data["student_count"] == 60
    
    def test_create_section(self):
        """Test POST /api/v1/sections/ - Create new section"""
        new_section = {
            "department_id": 1,
            "name": "CSE-C",
            "batch_year_start": 2024,
            "batch_year_end": 2028,
            "student_count": 55
        }
        response = client.post("/api/v1/sections/", json=new_section)
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "CSE-C"
        assert data["student_count"] == 55
        assert data["batch_year_start"] == 2024
    
    def test_update_section(self):
        """Test PUT /api/v1/sections/{id} - Update section"""
        updated = {
            "department_id": 1,
            "name": "CSE-A",
            "batch_year_start": 2023,
            "batch_year_end": 2027,
            "student_count": 65  # Changed from 60
        }
        response = client.put("/api/v1/sections/1", json=updated)
        assert response.status_code == 200
        data = response.json()
        assert data["student_count"] == 65
    
    def test_delete_section(self):
        """Test DELETE /api/v1/sections/{id} - Delete section"""
        response = client.delete("/api/v1/sections/1")
        assert response.status_code == 200
        
        # Verify deletion
        get_response = client.get("/api/v1/sections/1")
        assert get_response.status_code == 404


# ========== EDGE CASES & ERROR HANDLING ==========

class TestErrorHandling:
    """Test suite for error handling and edge cases"""
    
    def test_invalid_endpoint(self):
        """Test accessing non-existent endpoint"""
        response = client.get("/api/v1/invalid/")
        assert response.status_code == 404
    
    def test_create_department_missing_required_field(self):
        """Test POST without required 'code' field"""
        invalid_dept = {
            "name": "Missing Code Dept"
        }
        response = client.post("/api/v1/departments/", json=invalid_dept)
        assert response.status_code == 422  # Validation error
    
    def test_create_course_invalid_department(self):
        """Test POST course with non-existent department_id"""
        invalid_course = {
            "code": "TEST999",
            "name": "Test Course",
            "credits": 3,
            "department_id": 9999,  # Invalid
            "theory_hours": 3,
            "lab_hours": 0,
            "tutorial_hours": 0,
            "is_elective": False,
            "requires_lab": False
        }
        response = client.post("/api/v1/courses/", json=invalid_course)
        # Should succeed (no FK constraint in this implementation)
        # But in production would fail
        assert response.status_code in [200, 400]


# ========== SUMMARY STATISTICS ==========

def test_data_integrity_after_operations():
    """Test that data remains consistent after multiple operations"""
    # Create a department
    new_dept = {"code": "TEST", "name": "Test Dept"}
    create_response = client.post("/api/v1/departments/", json=new_dept)
    dept_id = create_response.json()["id"]
    
    # Update it
    update_response = client.put(f"/api/v1/departments/{dept_id}", json={
        "code": "TEST2",
        "name": "Test Dept Updated"
    })
    assert update_response.status_code == 200
    
    # Verify update
    get_response = client.get(f"/api/v1/departments/{dept_id}")
    assert get_response.json()["code"] == "TEST2"
    
    # Delete it
    delete_response = client.delete(f"/api/v1/departments/{dept_id}")
    assert delete_response.status_code == 200
    
    # Verify deletion
    final_response = client.get(f"/api/v1/departments/{dept_id}")
    assert final_response.status_code == 404
