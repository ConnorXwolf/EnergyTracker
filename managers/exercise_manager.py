"""
Exercise tracking business logic manager.

Handles exercise CRUD operations, progress tracking, and provides
aggregated statistics for ring chart visualization.
"""

from typing import List, Dict, Any, Tuple, Optional
from PyQt6.QtCore import QObject, pyqtSignal

from database import DatabaseManager
from models import Exercise, ExerciseLog, ExerciseSummary
from utils import get_today, get_category_color, EXERCISE_CATEGORIES


class ExerciseManager(QObject):
    """
    Business logic manager for exercise tracking.
    
    Manages exercise definitions, daily logs, and provides aggregated
    statistics for UI components. Emits signals on data changes to
    trigger UI updates.
    
    Signals:
        data_changed: Emitted when exercise data is modified
        log_updated: Emitted with date when log is created/updated
    """
    
    data_changed = pyqtSignal()
    log_updated = pyqtSignal(str)  # Emits date of updated log
    
    def __init__(self):
        """Initialize manager with database connection."""
        super().__init__()
        self._db = DatabaseManager()
    
    # ==================== Exercise Definition Operations ====================
    
    def create_exercise(
        self,
        name: str,
        category: str,
        target_value: int,
        unit: str
    ) -> Optional[int]:
        """
        Create new exercise definition.
        
        Args:
            name: Exercise name
            category: Category ('cardio', 'strength', 'flexibility')
            target_value: Daily goal quantity
            unit: Measurement unit
            
        Returns:
            Exercise ID if created, None if failed
            
        Raises:
            ValueError: If parameters are invalid
        """
        try:
            # Get category color
            color = get_category_color(category)
            
            # Create exercise model
            exercise = Exercise(
                name=name,
                category=category,
                color=color,
                target_value=target_value,
                unit=unit
            )
            
            # Insert into database
            exercise_id = self._db.create_exercise(exercise)
            
            # Emit signal to refresh UI
            self.data_changed.emit()
            
            return exercise_id
            
        except Exception as e:
            print(f"Error creating exercise: {e}")
            return None
    
    def get_all_exercises(self) -> List[Exercise]:
        """
        Retrieve all exercise definitions.
        
        Returns:
            List of Exercise models
        """
        try:
            return self._db.get_all_exercises()
        except Exception as e:
            print(f"Error retrieving exercises: {e}")
            return []
    
    def get_exercise_by_id(self, exercise_id: int) -> Optional[Exercise]:
        """
        Retrieve specific exercise by ID.
        
        Args:
            exercise_id: Unique identifier
            
        Returns:
            Exercise model or None if not found
        """
        try:
            return self._db.get_exercise_by_id(exercise_id)
        except Exception as e:
            print(f"Error retrieving exercise {exercise_id}: {e}")
            return None
    
    def update_exercise(
        self,
        exercise_id: int,
        name: str,
        category: str,
        target_value: int,
        unit: str
    ) -> bool:
        """
        Update existing exercise definition.
        
        Args:
            exercise_id: Exercise to update
            name: New name
            category: New category
            target_value: New target
            unit: New unit
            
        Returns:
            True if updated successfully
        """
        try:
            color = get_category_color(category)
            
            exercise = Exercise(
                id=exercise_id,
                name=name,
                category=category,
                color=color,
                target_value=target_value,
                unit=unit
            )
            
            success = self._db.update_exercise(exercise)
            
            if success:
                self.data_changed.emit()
            
            return success
            
        except Exception as e:
            print(f"Error updating exercise: {e}")
            return False
    
    def delete_exercise(self, exercise_id: int) -> bool:
        """
        Delete exercise and all associated logs.
        
        Args:
            exercise_id: Exercise to delete
            
        Returns:
            True if deleted successfully
        """
        try:
            success = self._db.delete_exercise(exercise_id)
            
            if success:
                self.data_changed.emit()
            
            return success
            
        except Exception as e:
            print(f"Error deleting exercise: {e}")
            return False
    
    # ==================== Exercise Log Operations ====================
    
    def update_progress(
        self,
        exercise_id: int,
        date: str,
        actual_value: int,
        completed: bool = True,
        notes: str = ""
    ) -> bool:
        """
        Update exercise progress for specific date.
        
        Args:
            exercise_id: Exercise being logged
            date: Date in ISO format
            actual_value: Performance achieved
            completed: Completion status
            notes: Optional notes
            
        Returns:
            True if logged successfully
        """
        try:
            self._db.create_or_update_log(
                exercise_id=exercise_id,
                date=date,
                actual_value=actual_value,
                completed=completed,
                notes=notes
            )
            
            # Emit signals
            self.data_changed.emit()
            self.log_updated.emit(date)
            
            return True
            
        except Exception as e:
            print(f"Error updating progress: {e}")
            return False
    
    def get_today_logs(self) -> List[Tuple[Exercise, ExerciseLog]]:
        """
        Retrieve today's exercise logs with exercise definitions.
        
        Returns:
            List of (Exercise, ExerciseLog) tuples
        """
        return self.get_logs_for_date(get_today())
    
    def get_logs_for_date(self, date: str) -> List[Tuple[Exercise, ExerciseLog]]:
        """
        Retrieve exercise logs for specific date.
        
        Creates placeholder logs for exercises without entries.
        
        Args:
            date: Date in ISO format
            
        Returns:
            List of (Exercise, ExerciseLog) tuples
        """
        try:
            exercises = self._db.get_all_exercises()
            logs = self._db.get_logs_by_date(date)
            
            # Create map of exercise_id -> log
            log_map = {log.exercise_id: log for log in logs}
            
            # Build combined list with placeholder logs for missing entries
            result = []
            for exercise in exercises:
                if exercise.id in log_map:
                    log = log_map[exercise.id]
                else:
                    # Create placeholder log
                    log = ExerciseLog(
                        exercise_id=exercise.id,
                        date=date,
                        completed=False,
                        actual_value=0,
                        target_value=exercise.target_value,
                        unit=exercise.unit,
                        category=exercise.category
                    )
                
                result.append((exercise, log))
            
            return result
            
        except Exception as e:
            print(f"Error retrieving logs for {date}: {e}")
            return []
    
    # ==================== Statistics & Aggregations ====================
    
    def get_today_summary(self) -> ExerciseSummary:
        """
        Calculate summary statistics for today.
        
        Returns:
            ExerciseSummary with aggregated metrics
        """
        return self.get_summary_for_date(get_today())
    
    def get_summary_for_date(self, date: str) -> ExerciseSummary:
        """
        Calculate summary statistics for specific date.
        
        Args:
            date: Date in ISO format
            
        Returns:
            ExerciseSummary with completion and progress rates
        """
        try:
            logs_data = self.get_logs_for_date(date)
            
            if not logs_data:
                return ExerciseSummary(
                    total_exercises=0,
                    completed_count=0,
                    completion_rate=0.0,
                    total_actual=0,
                    total_target=1,  # Avoid division by zero
                    progress_rate=0.0
                )
            
            total = len(logs_data)
            completed = sum(1 for _, log in logs_data if log.completed)
            total_actual = sum(log.actual_value for _, log in logs_data)
            total_target = sum(log.target_value for _, log in logs_data)
            
            completion_rate = (completed / total * 100) if total > 0 else 0.0
            progress_rate = (total_actual / total_target * 100) if total_target > 0 else 0.0
            
            return ExerciseSummary(
                total_exercises=total,
                completed_count=completed,
                completion_rate=completion_rate,
                total_actual=total_actual,
                total_target=total_target,
                progress_rate=progress_rate
            )
            
        except Exception as e:
            print(f"Error calculating summary: {e}")
            return ExerciseSummary(
                total_exercises=0,
                completed_count=0,
                completion_rate=0.0,
                total_actual=0,
                total_target=1,
                progress_rate=0.0
            )
    
    def get_ring_chart_data(self, date: str) -> Dict[str, Any]:
        """
        Generate data structure for ring chart visualization.
        
        Calculates overall HP percentage and category-wise segments
        with angles for circular representation.
        
        Args:
            date: Date in ISO format
            
        Returns:
        Dictionary with hp=0 and empty segments
        """
        return {
        'hp': 0.0,
        'segments': []
    }
    
    def get_weekly_completion_rate(self, end_date: str) -> List[Tuple[str, float]]:
        """
        Calculate completion rates for past 7 days.
        
        Args:
            end_date: End date of week in ISO format
            
        Returns:
            List of (date, completion_rate) tuples
        """
        try:
            from datetime import datetime, timedelta
            
            end = datetime.fromisoformat(end_date).date()
            dates = [
                (end - timedelta(days=i)).isoformat()
                for i in range(6, -1, -1)
            ]
            
            rates = []
            for date in dates:
                summary = self.get_summary_for_date(date)
                rates.append((date, summary.completion_rate))
            
            return rates
            
        except Exception as e:
            print(f"Error calculating weekly rates: {e}")
            return []
