"""
Database manager for SQLite operations.

Implements the singleton pattern to manage database connections,
schema initialization, and provides transactional CRUD operations
for all data models.
"""

import sqlite3
import os
from pathlib import Path
from typing import List, Optional, Dict, Any, Tuple
from contextlib import contextmanager

from models import Exercise, ExerciseLog, Task, CalendarEvent
from utils import DATABASE_NAME


class DatabaseManager:
    """
    Singleton database manager for SQLite operations.
    
    Provides thread-safe database access with automatic schema
    initialization and transaction management.
    
    Attributes:
        _instance: Singleton instance
        _connection: Active SQLite connection
        _db_path: Path to database file
    """
    
    _instance: Optional['DatabaseManager'] = None
    
    def __new__(cls) -> 'DatabaseManager':
        """Ensure only one instance exists (Singleton pattern)."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        """Initialize database manager and create connection."""
        if self._initialized:
            return
        
        self._db_path = Path.cwd() / DATABASE_NAME
        self._connection: Optional[sqlite3.Connection] = None
        self._initialize_database()
        self._initialized = True
    
    def _initialize_database(self) -> None:
        """
        Create database and initialize schema if not exists.
        
        Raises:
            sqlite3.Error: If database initialization fails
        """
        try:
            self._connection = sqlite3.connect(
                self._db_path,
                check_same_thread=False
            )
            self._connection.row_factory = sqlite3.Row
            
            # Read and execute schema
            # Handle both normal execution and PyInstaller bundled execution
            import sys
            if getattr(sys, 'frozen', False):
                # Running as PyInstaller bundle
                base_path = Path(sys._MEIPASS)
            else:
                # Running as normal Python script
                base_path = Path(__file__).parent
            
            schema_path = base_path / 'database' / 'schema.sql'
            
            # If still not found, try current directory
            if not schema_path.exists():
                schema_path = Path(__file__).parent / 'schema.sql'
            
            with open(schema_path, 'r', encoding='utf-8') as f:
                schema_sql = f.read()
            
            self._connection.executescript(schema_sql)
            self._connection.commit()
            
        except sqlite3.Error as e:
            raise sqlite3.Error(f"Failed to initialize database: {e}") from e
        except FileNotFoundError as e:
            raise FileNotFoundError(f"Schema file not found at {schema_path}: {e}") from e
    
    @contextmanager
    def transaction(self):
        """
        Context manager for database transactions.
        
        Automatically commits on success or rolls back on exception.
        
        Yields:
            sqlite3.Cursor: Database cursor for operations
            
        Example:
            with db.transaction() as cursor:
                cursor.execute("INSERT INTO ...")
        """
        cursor = self._connection.cursor()
        try:
            yield cursor
            self._connection.commit()
        except Exception as e:
            self._connection.rollback()
            raise sqlite3.Error(f"Transaction failed: {e}") from e
        finally:
            cursor.close()
    
    def execute(self, query: str, params: tuple = ()) -> None:
        """
        Execute a query without returning results.
        
        Args:
            query: SQL query string
            params: Query parameters tuple
            
        Raises:
            sqlite3.Error: If execution fails
        """
        try:
            with self.transaction() as cursor:
                cursor.execute(query, params)
        except sqlite3.Error as e:
            raise sqlite3.Error(f"Query execution failed: {e}") from e
    
    def fetch_one(self, query: str, params: tuple = ()) -> Optional[tuple]:
        """
        Execute query and fetch single result.
        
        Args:
            query: SQL query string
            params: Query parameters tuple
            
        Returns:
            Single result tuple or None
            
        Raises:
            sqlite3.Error: If query fails
        """
        try:
            cursor = self._connection.cursor()
            cursor.execute(query, params)
            return cursor.fetchone()
        except sqlite3.Error as e:
            raise sqlite3.Error(f"Fetch one failed: {e}") from e
    
    # ==================== Exercise Operations ====================
    
    def create_exercise(self, exercise: Exercise) -> int:
        """
        Insert new exercise definition.
        
        Args:
            exercise: Exercise model to insert
            
        Returns:
            Generated exercise ID
            
        Raises:
            sqlite3.IntegrityError: If exercise name already exists
        """
        try:
            with self.transaction() as cursor:
                cursor.execute(
                    """
                    INSERT INTO exercises (name, category, color, target_value, unit)
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (
                        exercise.name,
                        exercise.category,
                        exercise.color,
                        exercise.target_value,
                        exercise.unit
                    )
                )
                return cursor.lastrowid
        except sqlite3.IntegrityError as e:
            raise sqlite3.IntegrityError(
                f"Exercise '{exercise.name}' already exists"
            ) from e
    
    def get_all_exercises(self) -> List[Exercise]:
        """
        Retrieve all exercise definitions.
        
        Returns:
            List of Exercise models ordered by creation date
            
        Raises:
            sqlite3.Error: If query fails
        """
        try:
            cursor = self._connection.cursor()
            cursor.execute(
                """
                SELECT id, name, category, color, target_value, unit
                FROM exercises
                ORDER BY created_at ASC
                """
            )
            
            rows = cursor.fetchall()
            return [
                Exercise(
                    id=row['id'],
                    name=row['name'],
                    category=row['category'],
                    color=row['color'],
                    target_value=row['target_value'],
                    unit=row['unit']
                )
                for row in rows
            ]
        except sqlite3.Error as e:
            raise sqlite3.Error(f"Failed to retrieve exercises: {e}") from e
    
    def get_exercise_by_id(self, exercise_id: int) -> Optional[Exercise]:
        """
        Retrieve exercise by ID.
        
        Args:
            exercise_id: Unique exercise identifier
            
        Returns:
            Exercise model or None if not found
            
        Raises:
            sqlite3.Error: If query fails
        """
        try:
            cursor = self._connection.cursor()
            cursor.execute(
                """
                SELECT id, name, category, color, target_value, unit
                FROM exercises
                WHERE id = ?
                """,
                (exercise_id,)
            )
            
            row = cursor.fetchone()
            if row is None:
                return None
            
            return Exercise(
                id=row['id'],
                name=row['name'],
                category=row['category'],
                color=row['color'],
                target_value=row['target_value'],
                unit=row['unit']
            )
        except sqlite3.Error as e:
            raise sqlite3.Error(
                f"Failed to retrieve exercise {exercise_id}: {e}"
            ) from e
    
    def update_exercise(self, exercise: Exercise) -> bool:
        """
        Update existing exercise definition.
        
        Args:
            exercise: Exercise model with updated values
            
        Returns:
            True if exercise was updated, False if not found
            
        Raises:
            sqlite3.Error: If update fails
        """
        try:
            with self.transaction() as cursor:
                cursor.execute(
                    """
                    UPDATE exercises
                    SET name = ?, category = ?, color = ?, 
                        target_value = ?, unit = ?
                    WHERE id = ?
                    """,
                    (
                        exercise.name,
                        exercise.category,
                        exercise.color,
                        exercise.target_value,
                        exercise.unit,
                        exercise.id
                    )
                )
                return cursor.rowcount > 0
        except sqlite3.Error as e:
            raise sqlite3.Error(f"Failed to update exercise: {e}") from e
    
    def delete_exercise(self, exercise_id: int) -> bool:
        """
        Delete exercise and all associated logs (CASCADE).
        
        Args:
            exercise_id: Unique exercise identifier
            
        Returns:
            True if exercise was deleted, False if not found
            
        Raises:
            sqlite3.Error: If deletion fails
        """
        try:
            with self.transaction() as cursor:
                cursor.execute(
                    "DELETE FROM exercises WHERE id = ?",
                    (exercise_id,)
                )
                return cursor.rowcount > 0
        except sqlite3.Error as e:
            raise sqlite3.Error(f"Failed to delete exercise: {e}") from e
    
    # ==================== Exercise Log Operations ====================
    
    def create_or_update_log(
        self,
        exercise_id: int,
        date: str,
        actual_value: int,
        completed: bool,
        notes: str = ""
    ) -> int:
        """
        Create new log or update existing for exercise on date.
        
        Uses UPSERT pattern (INSERT OR REPLACE) to handle duplicates.
        
        Args:
            exercise_id: Reference to exercise
            date: Log date in ISO format
            actual_value: Performance achieved
            completed: Completion status
            notes: Optional workout notes
            
        Returns:
            Log ID (new or existing)
            
        Raises:
            sqlite3.Error: If operation fails
        """
        try:
            with self.transaction() as cursor:
                cursor.execute(
                    """
                    INSERT INTO exercise_logs 
                        (exercise_id, date, completed, actual_value, notes)
                    VALUES (?, ?, ?, ?, ?)
                    ON CONFLICT(exercise_id, date) 
                    DO UPDATE SET
                        completed = excluded.completed,
                        actual_value = excluded.actual_value,
                        notes = excluded.notes,
                        logged_at = CURRENT_TIMESTAMP
                    """,
                    (exercise_id, date, completed, actual_value, notes)
                )
                return cursor.lastrowid
        except sqlite3.Error as e:
            raise sqlite3.Error(f"Failed to create/update log: {e}") from e
    
    def get_logs_by_date(self, date: str) -> List[ExerciseLog]:
        """
        Retrieve all exercise logs for specific date.
        
        Args:
            date: Date in ISO format (YYYY-MM-DD)
            
        Returns:
            List of ExerciseLog models with denormalized exercise data
            
        Raises:
            sqlite3.Error: If query fails
        """
        try:
            cursor = self._connection.cursor()
            cursor.execute(
                """
                SELECT 
                    el.id,
                    el.exercise_id,
                    el.date,
                    el.completed,
                    el.actual_value,
                    el.notes,
                    e.target_value,
                    e.unit,
                    e.category
                FROM exercise_logs el
                JOIN exercises e ON el.exercise_id = e.id
                WHERE el.date = ?
                ORDER BY e.created_at ASC
                """,
                (date,)
            )
            
            rows = cursor.fetchall()
            return [
                ExerciseLog(
                    id=row['id'],
                    exercise_id=row['exercise_id'],
                    date=row['date'],
                    completed=bool(row['completed']),
                    actual_value=row['actual_value'],
                    target_value=row['target_value'],
                    unit=row['unit'],
                    category=row['category'],
                    notes=row['notes'] or ""
                )
                for row in rows
            ]
        except sqlite3.Error as e:
            raise sqlite3.Error(f"Failed to retrieve logs for {date}: {e}") from e
    
    def get_logs_by_date_range(
        self,
        start_date: str,
        end_date: str
    ) -> List[ExerciseLog]:
        """
        Retrieve logs within date range (inclusive).
        
        Args:
            start_date: Range start in ISO format
            end_date: Range end in ISO format
            
        Returns:
            List of ExerciseLog models ordered by date
            
        Raises:
            sqlite3.Error: If query fails
        """
        try:
            cursor = self._connection.cursor()
            cursor.execute(
                """
                SELECT 
                    el.id,
                    el.exercise_id,
                    el.date,
                    el.completed,
                    el.actual_value,
                    el.notes,
                    e.target_value,
                    e.unit,
                    e.category
                FROM exercise_logs el
                JOIN exercises e ON el.exercise_id = e.id
                WHERE el.date BETWEEN ? AND ?
                ORDER BY el.date DESC, e.created_at ASC
                """,
                (start_date, end_date)
            )
            
            rows = cursor.fetchall()
            return [
                ExerciseLog(
                    id=row['id'],
                    exercise_id=row['exercise_id'],
                    date=row['date'],
                    completed=bool(row['completed']),
                    actual_value=row['actual_value'],
                    target_value=row['target_value'],
                    unit=row['unit'],
                    category=row['category'],
                    notes=row['notes'] or ""
                )
                for row in rows
            ]
        except sqlite3.Error as e:
            raise sqlite3.Error(
                f"Failed to retrieve logs for range {start_date}-{end_date}: {e}"
            ) from e
    
    # ==================== Task Operations ====================
    
    def create_task(self, task: Task, date: str = None) -> int:
        """
        Insert new task with optional date assignment.
        
        Args:
            task: Task model to insert
            date: Task creation date in ISO format (defaults to today if None)
            
        Returns:
            Generated task ID
            
        Raises:
            sqlite3.Error: If insertion fails
        """
        try:
            # Import here to avoid circular dependency
            from utils import get_today
            
            # Use provided date or default to today
            task_date = date if date is not None else get_today()
            
            with self.transaction() as cursor:
                cursor.execute(
                    """
                    INSERT INTO tasks 
                        (title, is_completed, date, due_date, priority, category)
                    VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    (
                        task.title,
                        task.is_completed,
                        task_date,
                        task.due_date,
                        task.priority,
                        task.category
                    )
                )
                return cursor.lastrowid
        except sqlite3.Error as e:
            raise sqlite3.Error(f"Failed to create task: {e}") from e
    
    def get_all_tasks(self) -> List[Task]:
        """
        Retrieve all tasks.
        
        Returns:
            List of Task models ordered by priority (high to low) then creation
            
        Raises:
            sqlite3.Error: If query fails
        """
        try:
            cursor = self._connection.cursor()
            cursor.execute(
                """
                SELECT id, title, is_completed, date, due_date, priority, category
                FROM tasks
                ORDER BY priority DESC, created_at ASC
                """
            )
            
            rows = cursor.fetchall()
            return [
                Task(
                    id=row['id'],
                    title=row['title'],
                    is_completed=bool(row['is_completed']),
                    date=row['date'],
                    due_date=row['due_date'],
                    priority=row['priority'],
                    category=row['category']
                )
                for row in rows
            ]
        except sqlite3.Error as e:
            raise sqlite3.Error(f"Failed to retrieve tasks: {e}") from e
    
    def get_tasks_by_category(self, category: str) -> List[Task]:
        """
        Retrieve tasks filtered by category.
        
        Args:
            category: Category name to filter by
            
        Returns:
            List of Task models in category
            
        Raises:
            sqlite3.Error: If query fails
        """
        try:
            cursor = self._connection.cursor()
            cursor.execute(
                """
                SELECT id, title, is_completed, date, due_date, priority, category
                FROM tasks
                WHERE category = ?
                ORDER BY priority DESC, created_at ASC
                """,
                (category,)
            )
            
            rows = cursor.fetchall()
            return [
                Task(
                    id=row['id'],
                    title=row['title'],
                    is_completed=bool(row['is_completed']),
                    date=row['date'],
                    due_date=row['due_date'],
                    priority=row['priority'],
                    category=row['category']
                )
                for row in rows
            ]
        except sqlite3.Error as e:
            raise sqlite3.Error(
                f"Failed to retrieve tasks for category '{category}': {e}"
            ) from e
    
    def get_tasks_by_date(self, date: str) -> List[Task]:
        """
        Retrieve tasks created on specific date.
        
        Args:
            date: Task date in ISO format (YYYY-MM-DD)
            
        Returns:
            List of Task models for the specified date
            
        Raises:
            sqlite3.Error: If query fails
            ValueError: If date format is invalid
        """
        try:
            # Validate date format
            from datetime import datetime
            try:
                datetime.fromisoformat(date)
            except ValueError as e:
                raise ValueError(f"Invalid date format '{date}': Expected YYYY-MM-DD") from e
            
            cursor = self._connection.cursor()
            cursor.execute(
                """
                SELECT id, title, is_completed, date, due_date, priority, category
                FROM tasks
                WHERE date = ?
                ORDER BY priority DESC, created_at ASC
                """,
                (date,)
            )
            
            rows = cursor.fetchall()
            return [
                Task(
                    id=row['id'],
                    title=row['title'],
                    is_completed=bool(row['is_completed']),
                    date=row['date'],
                    due_date=row['due_date'],
                    priority=row['priority'],
                    category=row['category']
                )
                for row in rows
            ]
        except sqlite3.Error as e:
            raise sqlite3.Error(
                f"Failed to retrieve tasks for date '{date}': {e}"
            ) from e
        except ValueError:
            # Re-raise validation errors
            raise
    
    def get_tasks_by_month(self, year: int, month: int) -> List[Task]:
        """
        Retrieve tasks with due dates in specified month.
        
        Args:
            year: Target year (e.g., 2026)
            month: Target month (1-12)
            
        Returns:
            List of Task models with due_date in specified month
            
        Raises:
            sqlite3.Error: If query fails
            ValueError: If month is invalid
        """
        try:
            # Validate month range
            if not 1 <= month <= 12:
                raise ValueError(f"Invalid month: {month}. Must be 1-12")
            
            # Construct date pattern for LIKE query
            date_pattern = f"{year:04d}-{month:02d}-%"
            
            cursor = self._connection.cursor()
            cursor.execute(
                """
                SELECT id, title, is_completed, date, due_date, priority, category
                FROM tasks
                WHERE due_date LIKE ?
                ORDER BY due_date ASC, priority DESC, created_at ASC
                """,
                (date_pattern,)
            )
            
            rows = cursor.fetchall()
            return [
                Task(
                    id=row['id'],
                    title=row['title'],
                    is_completed=bool(row['is_completed']),
                    date=row['date'],
                    due_date=row['due_date'],
                    priority=row['priority'],
                    category=row['category']
                )
                for row in rows
            ]
        except sqlite3.Error as e:
            raise sqlite3.Error(
                f"Failed to retrieve tasks for {year}-{month:02d}: {e}"
            ) from e
        except ValueError:
            # Re-raise validation errors
            raise
    
    def update_task(self, task: Task) -> bool:
        """
        Update existing task.
        
        Args:
            task: Task model with updated values
            
        Returns:
            True if task was updated, False if not found
            
        Raises:
            sqlite3.Error: If update fails
        """
        try:
            with self.transaction() as cursor:
                # Update completed_at timestamp if completion status changed
                completed_at = "CURRENT_TIMESTAMP" if task.is_completed else "NULL"
                
                cursor.execute(
                    f"""
                    UPDATE tasks
                    SET title = ?,
                        is_completed = ?,
                        date = ?,
                        due_date = ?,
                        priority = ?,
                        category = ?,
                        completed_at = {completed_at}
                    WHERE id = ?
                    """,
                    (
                        task.title,
                        task.is_completed,
                        task.date,
                        task.due_date,
                        task.priority,
                        task.category,
                        task.id
                    )
                )
                return cursor.rowcount > 0
        except sqlite3.Error as e:
            raise sqlite3.Error(f"Failed to update task: {e}") from e
    
    def delete_task(self, task_id: int) -> bool:
        """
        Delete task by ID.
        
        Args:
            task_id: Unique task identifier
            
        Returns:
            True if task was deleted, False if not found
            
        Raises:
            sqlite3.Error: If deletion fails
        """
        try:
            with self.transaction() as cursor:
                cursor.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
                return cursor.rowcount > 0
        except sqlite3.Error as e:
            raise sqlite3.Error(f"Failed to delete task: {e}") from e
    
    # ==================== Event Operations ====================
    
    def create_event(self, event: CalendarEvent) -> int:
        """
        Insert new calendar event.
        
        Args:
            event: CalendarEvent model to insert
            
        Returns:
            Generated event ID
            
        Raises:
            sqlite3.Error: If insertion fails
        """
        try:
            with self.transaction() as cursor:
                cursor.execute(
                    """
                    INSERT INTO events (title, event_date, description)
                    VALUES (?, ?, ?)
                    """,
                    (event.title, event.event_date, event.description)
                )
                return cursor.lastrowid
        except sqlite3.Error as e:
            raise sqlite3.Error(f"Failed to create event: {e}") from e
    
    def get_events_by_date(self, date: str) -> List[CalendarEvent]:
        """
        Retrieve events for specific date.
        
        Args:
            date: Date in ISO format (YYYY-MM-DD)
            
        Returns:
            List of CalendarEvent models for the date
            
        Raises:
            sqlite3.Error: If query fails
        """
        try:
            cursor = self._connection.cursor()
            cursor.execute(
                """
                SELECT id, title, event_date, description
                FROM events
                WHERE event_date = ?
                ORDER BY created_at ASC
                """,
                (date,)
            )
            
            rows = cursor.fetchall()
            return [
                CalendarEvent(
                    id=row['id'],
                    title=row['title'],
                    event_date=row['event_date'],
                    description=row['description']
                )
                for row in rows
            ]
        except sqlite3.Error as e:
            raise sqlite3.Error(f"Failed to retrieve events for {date}: {e}") from e
    
    def get_events_by_month(self, year: int, month: int) -> List[CalendarEvent]:
        """
        Retrieve all events in a month.
        
        Args:
            year: Year (e.g., 2026)
            month: Month (1-12)
            
        Returns:
            List of CalendarEvent models in the month
            
        Raises:
            sqlite3.Error: If query fails
        """
        try:
            # Construct date pattern for LIKE query
            date_pattern = f"{year:04d}-{month:02d}-%"
            
            cursor = self._connection.cursor()
            cursor.execute(
                """
                SELECT id, title, event_date, description
                FROM events
                WHERE event_date LIKE ?
                ORDER BY event_date ASC, created_at ASC
                """,
                (date_pattern,)
            )
            
            rows = cursor.fetchall()
            return [
                CalendarEvent(
                    id=row['id'],
                    title=row['title'],
                    event_date=row['event_date'],
                    description=row['description']
                )
                for row in rows
            ]
        except sqlite3.Error as e:
            raise sqlite3.Error(
                f"Failed to retrieve events for {year}-{month:02d}: {e}"
            ) from e
    
    def update_event(self, event: CalendarEvent) -> bool:
        """
        Update existing event.
        
        Args:
            event: CalendarEvent model with updated values
            
        Returns:
            True if event was updated, False if not found
            
        Raises:
            sqlite3.Error: If update fails
        """
        try:
            with self.transaction() as cursor:
                cursor.execute(
                    """
                    UPDATE events
                    SET title = ?, event_date = ?, description = ?
                    WHERE id = ?
                    """,
                    (event.title, event.event_date, event.description, event.id)
                )
                return cursor.rowcount > 0
        except sqlite3.Error as e:
            raise sqlite3.Error(f"Failed to update event: {e}") from e
    
    def delete_event(self, event_id: int) -> bool:
        """
        Delete event by ID.
        
        Args:
            event_id: Unique event identifier
            
        Returns:
            True if event was deleted, False if not found
            
        Raises:
            sqlite3.Error: If deletion fails
        """
        try:
            with self.transaction() as cursor:
                cursor.execute("DELETE FROM events WHERE id = ?", (event_id,))
                return cursor.rowcount > 0
        except sqlite3.Error as e:
            raise sqlite3.Error(f"Failed to delete event: {e}") from e
    
    # ==================== Utility Methods ====================
    
    def close(self) -> None:
        """
        Close database connection gracefully.
        
        Should be called on application shutdown.
        """
        if self._connection:
            self._connection.close()
            self._connection = None
    
    def __del__(self):
        """Ensure connection is closed on object destruction."""
        self.close()
