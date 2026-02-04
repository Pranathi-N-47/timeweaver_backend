"""
Module: Timetable Generation & Scheduling (Module 3)
Repository: timeweaver_backend
Owner: Pranathi Nibhanipudi
Epic: 3 - Timetable Generation / Re-generation

Slot Locking Service - User Story 3.2

Handles locking and unlocking of timetable slots to protect critical
assignments during re-optimization and incremental updates.

Locked slots are:
- Protected from modification during generation
- Preserved during re-optimization
- Used for manual overrides and fixes

Dependencies:
    - app.models.timetable (TimetableSlot model)

User Stories: 3.2.2 (Slot Locking)
"""

from sqlalchemy.orm import Session
from sqlalchemy import select, update
from app.models.timetable import TimetableSlot


class SlotLockingService:
    """Service for slot locking operations"""
    
    @staticmethod
    def lock_slots(db: Session, slot_ids: list[int]) -> int:
        """
        Lock specified timetable slots.
        
        Args:
            db: Database session
            slot_ids: List of slot IDs to lock
            
        Returns:
            Number of slots locked
        """
        stmt = (
            update(TimetableSlot)
            .where(TimetableSlot.id.in_(slot_ids))
            .values(is_locked=True)
        )
        
        result = db.execute(stmt)
        db.commit()
        
        return result.rowcount
    
    @staticmethod
    def unlock_slots(db: Session, slot_ids: list[int]) -> int:
        """
        Unlock specified timetable slots.
        
        Args:
            db: Database session
            slot_ids: List of slot IDs to unlock
            
        Returns:
            Number of slots unlocked
        """
        stmt = (
            update(TimetableSlot)
            .where(TimetableSlot.id.in_(slot_ids))
            .values(is_locked=False)
        )
        
        result = db.execute(stmt)
        db.commit()
        
        return result.rowcount
    
    @staticmethod
    def lock_all_slots_for_timetable(db: Session, timetable_id: int) -> int:
        """
        Lock ALL slots in a timetable (for publishing).
        
        Args:
            db: Database session
            timetable_id: Timetable ID
            
        Returns:
            Number of slots locked
        """
        stmt = (
            update(TimetableSlot)
            .where(TimetableSlot.timetable_id == timetable_id)
            .values(is_locked=True)
        )
        
        result = db.execute(stmt)
        db.commit()
        
        return result.rowcount
    
    @staticmethod
    def unlock_all_slots_for_timetable(db: Session, timetable_id: int) -> int:
        """
        Unlock ALL slots in a timetable (for re-generation).
        
        Args:
            db: Database session
            timetable_id: Timetable ID
            
        Returns:
            Number of slots unlocked
        """
        stmt = (
            update(TimetableSlot)
            .where(TimetableSlot.timetable_id == timetable_id)
            .values(is_locked=False)
        )
        
        result = db.execute(stmt)
        db.commit()
        
        return result.rowcount
    
    @staticmethod
    def get_locked_slots(db: Session, timetable_id: int) -> list[TimetableSlot]:
        """
        Get all locked slots for a timetable.
        
        Args:
            db: Database session
            timetable_id: Timetable ID
            
        Returns:
            List of locked TimetableSlot objects
        """
        stmt = select(TimetableSlot).where(
            TimetableSlot.timetable_id == timetable_id,
            TimetableSlot.is_locked == True
        )
        
        result = db.execute(stmt)
        return list(result.scalars().all())
    
    @staticmethod
    def get_unlocked_slots(db: Session, timetable_id: int) -> list[TimetableSlot]:
        """
        Get all unlocked (modifiable) slots for a timetable.
        
        Args:
            db: Database session
            timetable_id: Timetable ID
            
        Returns:
            List of unlocked TimetableSlot objects
        """
        stmt = select(TimetableSlot).where(
            TimetableSlot.timetable_id == timetable_id,
            TimetableSlot.is_locked == False
        )
        
        result = db.execute(stmt)
        return list(result.scalars().all())
    
    @staticmethod
    def get_lock_statistics(db: Session, timetable_id: int) -> dict[str, any]:
        """
        Get locking statistics for a timetable.
        
        Args:
            db: Database session
            timetable_id: Timetable ID
            
        Returns:
            Dict with lock statistics
        """
        # Get all slots
        stmt = select(TimetableSlot).where(TimetableSlot.timetable_id == timetable_id)
        all_slots = list(db.execute(stmt).scalars().all())
        
        locked_count = sum(1 for slot in all_slots if slot.is_locked)
        unlocked_count = len(all_slots) - locked_count
        
        return {
            "total_slots": len(all_slots),
            "locked_slots": locked_count,
            "unlocked_slots": unlocked_count,
            "lock_percentage": (locked_count / len(all_slots) * 100) if all_slots else 0
        }
    
    @staticmethod
    def is_slot_modifiable(db: Session, slot_id: int) -> bool:
        """
        Check if a slot can be modified (is not locked).
        
        Args:
            db: Database session
            slot_id: Slot ID to check
            
        Returns:
            True if slot is unlocked and modifiable
        """
        stmt = select(TimetableSlot.is_locked).where(TimetableSlot.id == slot_id)
        result = db.execute(stmt).scalar_one_or_none()
        
        if result is None:
            return False  # Slot doesn't exist
        
        return not result  # True if is_locked is False
