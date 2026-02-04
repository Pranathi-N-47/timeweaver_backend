"""
Module: Testing Timetable Models (Module 3)
Repository: timeweaver_backend
Owner: Student C
Epic: 3 - AI/Backend Optimization & Conflict Detection

Unit tests for Timetable, TimetableSlot, and Conflict models.
Tests model creation, validation, constraints, and database operations.

Test Coverage:
    - Model creation and field validation
    - Database constraints (CHECK, FOREIGN KEY)
    - Relationships
    - Edge cases and error handling

Run with: pytest tests/test_timetable_models.py -v
"""

import pytest
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from app.models.timetable import Timetable, TimetableSlot, Conflict


class TestTimetableModel:
    """Test cases for Timetable model"""
    
    @pytest.mark.asyncio
    async def test_create_timetable_success(self, db_session, sample_semester, sample_admin_user):
        """Test successful timetable creation with valid data"""
        timetable = Timetable(
            semester_id=sample_semester.id,
            name="Fall 2024 - GA v1",
            status="completed",
            quality_score=0.92,
            conflict_count=0,
            is_published=False,
            generation_algorithm="GA",
            generation_time_seconds=25.5,
            created_by_user_id=sample_admin_user.id
        )
        
        db_session.add(timetable)
        await db_session.commit()
        await db_session.refresh(timetable)
        
        assert timetable.id is not None
        assert timetable.name == "Fall 2024 - GA v1"
        assert timetable.status == "completed"
        assert timetable.quality_score == 0.92
        assert timetable.conflict_count == 0
        assert timetable.is_published is False
        assert timetable.created_at is not None
    
    @pytest.mark.asyncio
    async def test_timetable_default_status(self, db_session, sample_semester):
        """Test that default status is 'generating'"""
        timetable = Timetable(
            semester_id=sample_semester.id,
            name="Test"
        )
        
        db_session.add(timetable)
        await db_session.commit()
        await db_session.refresh(timetable)
        
        assert timetable.status == "generating"
        assert timetable.conflict_count == 0
        assert timetable.is_published is False
    
    @pytest.mark.asyncio
    async def test_timetable_invalid_status(self, db_session, sample_semester):
        """Test that invalid status value raises constraint error"""
        timetable = Timetable(
            semester_id=sample_semester.id,
            name="Test",
            status="invalid_status"  # Not in: generating, completed, failed, archived
        )
        
        db_session.add(timetable)
        
        with pytest.raises(IntegrityError) as exc_info:
            await db_session.commit()
        
        assert "check_status_valid" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_timetable_quality_score_range_validation(self, db_session, sample_semester):
        """Test that quality_score must be between 0 and 1"""
        # Test invalid score > 1
        timetable = Timetable(
            semester_id=sample_semester.id,
            name="Test",
            quality_score=1.5  # Invalid: > 1
        )
        
        db_session.add(timetable)
        
        with pytest.raises(IntegrityError) as exc_info:
            await db_session.commit()
        
        assert "check_quality_score_range" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_timetable_negative_conflict_count(self, db_session, sample_semester):
        """Test that conflict_count cannot be negative"""
        timetable = Timetable(
            semester_id=sample_semester.id,
            name="Test",
            conflict_count=-1  # Invalid
        )
        
        db_session.add(timetable)
        
        with pytest.raises(IntegrityError) as exc_info:
            await db_session.commit()
        
        assert "check_conflict_count_positive" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_timetable_invalid_algorithm(self, db_session, sample_semester):
        """Test that invalid algorithm raises constraint error"""
        timetable = Timetable(
            semester_id=sample_semester.id,
            name="Test",
            generation_algorithm="INVALID_ALGO"
        )
        
        db_session.add(timetable)
        
        with pytest.raises(IntegrityError) as exc_info:
            await db_session.commit()
        
        assert "check_algorithm_valid" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_timetable_cascade_delete_on_semester(self, db_session, sample_semester, sample_timetable):
        """Test that deleting semester deletes timetables"""
        timetable_id = sample_timetable.id
        
        # Delete semester
        await db_session.delete(sample_semester)
        await db_session.commit()
        
        # Timetable should be deleted
        result = await db_session.execute(
            select(Timetable).where(Timetable.id == timetable_id)
        )
        assert result.scalar_one_or_none() is None


class TestTimetableSlotModel:
    """Test cases for TimetableSlot model"""
    
    @pytest.mark.asyncio
    async def test_create_slot_success(self, db_session, sample_timetable, sample_sections, sample_rooms, sample_time_slots):
        """Test successful slot creation"""
        slot = TimetableSlot(
            timetable_id=sample_timetable.id,
            section_id=sample_sections[0].id,
            room_id=sample_rooms[0].id,
            time_slot_id=sample_time_slots[0].id,
            day_of_week=0,  # Monday
            is_locked=False
        )
        
        db_session.add(slot)
        await db_session.commit()
        await db_session.refresh(slot)
        
        assert slot.id is not None
        assert slot.timetable_id == sample_timetable.id
        assert slot.section_id == sample_sections[0].id
        assert slot.room_id == sample_rooms[0].id
        assert slot.day_of_week == 0
        assert slot.is_locked is False
        assert slot.created_at is not None
    
    @pytest.mark.asyncio
    async def test_slot_day_of_week_validation(self, db_session, sample_timetable, sample_sections, sample_rooms, sample_time_slots):
        """Test that day_of_week must be 0-6"""
        # Test invalid day > 6
        slot = TimetableSlot(
            timetable_id=sample_timetable.id,
            section_id=sample_sections[0].id,
            room_id=sample_rooms[0].id,
            time_slot_id=sample_time_slots[0].id,
            day_of_week=7  # Invalid: must be 0-6
        )
        
        db_session.add(slot)
        
        with pytest.raises(IntegrityError) as exc_info:
            await db_session.commit()
        
        assert "check_day_of_week_valid" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_slot_negative_day(self, db_session, sample_timetable, sample_sections, sample_rooms, sample_time_slots):
        """Test that day_of_week cannot be negative"""
        slot = TimetableSlot(
            timetable_id=sample_timetable.id,
            section_id=sample_sections[0].id,
            room_id=sample_rooms[0].id,
            time_slot_id=sample_time_slots[0].id,
            day_of_week=-1  # Invalid
        )
        
        db_session.add(slot)
        
        with pytest.raises(IntegrityError) as exc_info:
            await db_session.commit()
        
        assert "check_day_of_week_valid" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_slot_locked_flag(self, db_session, sample_timetable, sample_sections, sample_rooms, sample_time_slots):
        """Test slot locking functionality (User Story 3.2)"""
        slot = TimetableSlot(
            timetable_id=sample_timetable.id,
            section_id=sample_sections[0].id,
            room_id=sample_rooms[0].id,
            time_slot_id=sample_time_slots[0].id,
            day_of_week=0,
            is_locked=True  # Locked slot
        )
        
        db_session.add(slot)
        await db_session.commit()
        await db_session.refresh(slot)
        
        assert slot.is_locked is True
    
    @pytest.mark.asyncio
    async def test_slot_cascade_delete_on_timetable(self, db_session, sample_timetable, sample_sections, sample_rooms, sample_time_slots):
        """Test that deleting timetable deletes slots"""
        slot = TimetableSlot(
            timetable_id=sample_timetable.id,
            section_id=sample_sections[0].id,
            room_id=sample_rooms[0].id,
            time_slot_id=sample_time_slots[0].id,
            day_of_week=0
        )
        
        db_session.add(slot)
        await db_session.commit()
        slot_id = slot.id
        
        # Delete timetable
        await db_session.delete(sample_timetable)
        await db_session.commit()
        
        # Slot should be deleted
        result = await db_session.execute(
            select(TimetableSlot).where(TimetableSlot.id == slot_id)
        )
        assert result.scalar_one_or_none() is None


class TestConflictModel:
    """Test cases for Conflict model"""
    
    @pytest.mark.asyncio
    async def test_create_conflict_success(self, db_session, sample_timetable):
        """Test successful conflict creation"""
        conflict = Conflict(
            timetable_id=sample_timetable.id,
            conflict_type="ROOM_CLASH",
            severity="HIGH",
            slot_ids=[1, 2],
            description="Room 101 double-booked on Monday 9:00 AM",
            is_resolved=False
        )
        
        db_session.add(conflict)
        await db_session.commit()
        await db_session.refresh(conflict)
        
        assert conflict.id is not None
        assert conflict.timetable_id == sample_timetable.id
        assert conflict.conflict_type == "ROOM_CLASH"
        assert conflict.severity == "HIGH"
        assert conflict.slot_ids == [1, 2]
        assert conflict.is_resolved is False
        assert conflict.detected_at is not None
    
    @pytest.mark.asyncio
    async def test_conflict_default_severity(self, db_session, sample_timetable):
        """Test that default severity is HIGH"""
        conflict = Conflict(
            timetable_id=sample_timetable.id,
            conflict_type="FACULTY_CLASH",
            slot_ids=[1, 2],
            description="Test"
        )
        
        db_session.add(conflict)
        await db_session.commit()
        await db_session.refresh(conflict)
        
        assert conflict.severity == "HIGH"
        assert conflict.is_resolved is False
    
    @pytest.mark.asyncio
    async def test_conflict_invalid_type(self, db_session, sample_timetable):
        """Test that invalid conflict type raises error"""
        conflict = Conflict(
            timetable_id=sample_timetable.id,
            conflict_type="INVALID_TYPE",
            slot_ids=[1, 2],
            description="Test"
        )
        
        db_session.add(conflict)
        
        with pytest.raises(IntegrityError) as exc_info:
            await db_session.commit()
        
        assert "check_conflict_type_valid" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_conflict_invalid_severity(self, db_session, sample_timetable):
        """Test that invalid severity raises error"""
        conflict = Conflict(
            timetable_id=sample_timetable.id,
            conflict_type="ROOM_CLASH",
            severity="CRITICAL",  # Invalid: not in HIGH, MEDIUM, LOW
            slot_ids=[1, 2],
            description="Test"
        )
        
        db_session.add(conflict)
        
        with pytest.raises(IntegrityError) as exc_info:
            await db_session.commit()
        
        assert "check_severity_valid" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_conflict_resolution_tracking(self, db_session, sample_timetable):
        """Test conflict resolution tracking"""
        from datetime import datetime
        
        conflict = Conflict(
            timetable_id=sample_timetable.id,
            conflict_type="STUDENT_CLASH",
            severity="MEDIUM",
            slot_ids=[1, 2],
            description="Elective overlap",
            is_resolved=True,
            resolution_notes="Manually rescheduled Section B",
            resolved_at=datetime.utcnow()
        )
        
        db_session.add(conflict)
        await db_session.commit()
        await db_session.refresh(conflict)
        
        assert conflict.is_resolved is True
        assert conflict.resolution_notes == "Manually rescheduled Section B"
        assert conflict.resolved_at is not None
    
    @pytest.mark.asyncio
    async def test_conflict_multiple_slots(self, db_session, sample_timetable):
        """Test conflict with multiple conflicting slots"""
        conflict = Conflict(
            timetable_id=sample_timetable.id,
            conflict_type="CAPACITY_VIOLATION",
            severity="HIGH",
            slot_ids=[1, 2, 3, 4],  # Multiple slots
            description="Auditorium over-capacity"
        )
        
        db_session.add(conflict)
        await db_session.commit()
        await db_session.refresh(conflict)
        
        assert len(conflict.slot_ids) == 4
        assert conflict.slot_ids == [1, 2, 3, 4]
