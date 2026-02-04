"""
Test configuration and shared fixtures.

Provides pytest fixtures for database sessions, sample data,
and common test utilities.
"""

import pytest
import asyncio
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import NullPool

from app.db.session import Base
from app.models.section import Section
from app.models.room import Room
from app.models.time_slot import TimeSlot
from app.models.semester import Semester
from app.models.department import Department
from app.models.user import User, UserRole
from app.models.timetable import Timetable, TimetableSlot, Conflict


# Test database URL
TEST_DATABASE_URL = "postgresql+asyncpg://postgres:postgres@localhost/timeweaver_test"


@pytest.fixture(scope="session")
def event_loop():
    """Create an event loop for the test session"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="function")
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Create a fresh database session for each test.
    
    The database is created and dropped for each test to ensure isolation.
    """
    # Create async engine
    engine = create_async_engine(
        TEST_DATABASE_URL,
        poolclass=NullPool,  # Disable pooling for tests
        echo=False
    )
    
    # Create all tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    
    # Create session factory
    async_session_factory = async_sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False
    )
    
    # Provide session to test
    async with async_session_factory() as session:
        yield session
    
    # Cleanup
    await engine.dispose()


@pytest.fixture
async def sample_department(db_session: AsyncSession):
    """Create a sample department"""
    dept = Department(
        id=1,
        name="Computer Science",
        code="CSE"
    )
    db_session.add(dept)
    await db_session.commit()
    await db_session.refresh(dept)
    return dept


@pytest.fixture
async def sample_semester(db_session: AsyncSession):
    """Create a sample semester"""
    semester = Semester(
        id=1,
        name="Fall 2024",
        start_date="2024-08-01",
        end_date="2024-12-15",
        is_active=True
    )
    db_session.add(semester)
    await db_session.commit()
    await db_session.refresh(semester)
    return semester


@pytest.fixture
async def sample_sections(db_session: AsyncSession, sample_department, sample_semester):
    """Create sample sections"""
    sections = [
        Section(id=1, name="CSE-A", year=1, student_count=60, semester_id=sample_semester.id, department_id=sample_department.id),
        Section(id=2, name="CSE-B", year=1, student_count=55, semester_id=sample_semester.id, department_id=sample_department.id),
        Section(id=3, name="ECE-A", year=2, student_count=50, semester_id=sample_semester.id, department_id=sample_department.id),
    ]
    db_session.add_all(sections)
    await db_session.commit()
    for section in sections:
        await db_session.refresh(section)
    return sections


@pytest.fixture
async def sample_rooms(db_session: AsyncSession):
    """Create sample rooms"""
    rooms = [
        Room(id=1, room_number="101", room_type="classroom", capacity=70),
        Room(id=2, room_number="102", room_type="lab", capacity=50, has_lab_equipment=True),
        Room(id=3, room_number="103", room_type="classroom", capacity=40),
    ]
    db_session.add_all(rooms)
    await db_session.commit()
    for room in rooms:
        await db_session.refresh(room)
    return rooms


@pytest.fixture
async def sample_time_slots(db_session: AsyncSession):
    """Create sample time slots"""
    time_slots = [
        TimeSlot(id=1, start_time="09:00", end_time="10:00"),
        TimeSlot(id=2, start_time="10:00", end_time="11:00"),
        TimeSlot(id=3, start_time="11:00", end_time="12:00"),
    ]
    db_session.add_all(time_slots)
    await db_session.commit()
    for ts in time_slots:
        await db_session.refresh(ts)
    return time_slots


@pytest.fixture
async def sample_admin_user(db_session: AsyncSession):
    """Create a sample admin user"""
    user = User(
        id=1,
        username="admin",
        email="admin@test.com",
        hashed_password="$2b$12$test_hash",
        full_name="Admin User",
        role=UserRole.ADMIN,
        is_active=True
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest.fixture
async def sample_timetable(db_session: AsyncSession, sample_semester, sample_admin_user):
    """Create a sample timetable"""
    timetable = Timetable(
        id=1,
        semester_id=sample_semester.id,
        name="Fall 2024 - Test Timetable",
        status="completed",
        quality_score=0.85,
        conflict_count=0,
        is_published=False,
        generation_algorithm="GA",
        generation_time_seconds=15.5,
        created_by_user_id=sample_admin_user.id
    )
    db_session.add(timetable)
    await db_session.commit()
    await db_session.refresh(timetable)
    return timetable
