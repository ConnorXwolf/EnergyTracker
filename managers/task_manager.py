"""
Task checklist business logic manager.

Handles task CRUD operations, completion tracking, and provides
grouped task statistics for checklist widgets.
"""

from typing import List, Dict, Optional
from PyQt6.QtCore import QObject, pyqtSignal

from database import DatabaseManager
from models import Task, TaskGroup
from utils import get_today


class TaskManager(QObject):
    """
    Business logic manager for task checklists.
    
    Manages task definitions, completion status, and provides
    grouped task collections for UI display.
    
    Signals:
        data_changed: Emitted when task data is modified
        task_completed: Emitted with task_id when task is completed
    """
    
    data_changed = pyqtSignal()
    task_completed = pyqtSignal(int)  # Emits task_id
    
    def __init__(self):
        """Initialize manager with database connection."""
        super().__init__()
        self._db = DatabaseManager()
    
    # ==================== Task CRUD Operations ====================
    
    def create_task(
        self,
        title: str,
        date: Optional[str] = None,
        due_date: Optional[str] = None,
        priority: int = 0,
        category: Optional[str] = None
    ) -> Optional[int]:
        """
        Create new task.
        
        Args:
            title: Task description
            date: Task assignment date in ISO format (defaults to today)
            due_date: Optional due date in ISO format
            priority: Priority level (0=low, 1=medium, 2=high)
            category: Optional category for grouping
            
        Returns:
            Task ID if created, None if failed
        """
        try:
            # Default to today if no date provided
            task_date = date if date is not None else get_today()
            
            task = Task(
                title=title,
                is_completed=False,
                date=task_date,
                due_date=due_date,
                priority=priority,
                category=category
            )
            
            task_id = self._db.create_task(task, date=task_date)
            
            self.data_changed.emit()
            
            return task_id
            
        except Exception as e:
            print(f"Error creating task: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def get_all_tasks(self) -> List[Task]:
        """
        Retrieve all tasks.
        
        Returns:
            List of Task models ordered by priority
        """
        try:
            return self._db.get_all_tasks()
        except Exception as e:
            print(f"Error retrieving tasks: {e}")
            return []
    
    def get_tasks_by_category(self, category: str) -> List[Task]:
        """
        Retrieve tasks in specific category.
        
        Args:
            category: Category name
            
        Returns:
            List of Task models in category
        """
        try:
            return self._db.get_tasks_by_category(category)
        except Exception as e:
            print(f"Error retrieving tasks for category '{category}': {e}")
            return []
    
    def get_tasks_by_date(self, date: str) -> List[Task]:
        """
        Retrieve tasks for specific date.
        
        Args:
            date: Date in ISO format (YYYY-MM-DD)
            
        Returns:
            List of Task models for the specified date
        """
        try:
            return self._db.get_tasks_by_date(date)
        except ValueError as e:
            print(f"Invalid date format: {e}")
            return []
        except Exception as e:
            print(f"Error retrieving tasks for date '{date}': {e}")
            import traceback
            traceback.print_exc()
            return []
    
    def get_task_groups(self) -> List[TaskGroup]:
        """
        Retrieve tasks organized into groups by category.
        
        Returns:
            List of TaskGroup models with aggregated statistics
        """
        try:
            all_tasks = self._db.get_all_tasks()
            
            # Group tasks by category
            category_map: Dict[str, List[Task]] = {}
            uncategorized = []
            
            for task in all_tasks:
                if task.category:
                    if task.category not in category_map:
                        category_map[task.category] = []
                    category_map[task.category].append(task)
                else:
                    uncategorized.append(task)
            
            # Build TaskGroup objects
            groups = []
            for category, tasks in category_map.items():
                groups.append(TaskGroup(
                    category=category,
                    tasks=tasks
                ))
            
            # Add uncategorized tasks as separate group if exists
            if uncategorized:
                groups.append(TaskGroup(
                    category="其他",
                    tasks=uncategorized
                ))
            
            return groups
            
        except Exception as e:
            print(f"Error retrieving task groups: {e}")
            return []
    
    def update_task(
        self,
        task_id: int,
        title: Optional[str] = None,
        is_completed: Optional[bool] = None,
        date: Optional[str] = None,
        due_date: Optional[str] = None,
        priority: Optional[int] = None,
        category: Optional[str] = None
    ) -> bool:
        """
        Update existing task with partial updates.
        
        Args:
            task_id: Task to update
            title: New title (if provided)
            is_completed: New completion status (if provided)
            date: New date (if provided)
            due_date: New due date (if provided)
            priority: New priority (if provided)
            category: New category (if provided)
            
        Returns:
            True if updated successfully
        """
        try:
            # Retrieve existing task
            existing_tasks = [t for t in self._db.get_all_tasks() if t.id == task_id]
            if not existing_tasks:
                return False
            
            existing = existing_tasks[0]
            
            # Apply updates
            updated_task = Task(
                id=task_id,
                title=title if title is not None else existing.title,
                is_completed=is_completed if is_completed is not None else existing.is_completed,
                date=date if date is not None else existing.date,
                due_date=due_date if due_date is not None else existing.due_date,
                priority=priority if priority is not None else existing.priority,
                category=category if category is not None else existing.category
            )
            
            success = self._db.update_task(updated_task)
            
            if success:
                self.data_changed.emit()
                
                # Emit completion signal if task was just completed
                if is_completed and not existing.is_completed:
                    self.task_completed.emit(task_id)
            
            return success
            
        except Exception as e:
            print(f"Error updating task: {e}")
            return False
    
    def toggle_task_completion(self, task_id: int) -> bool:
        """
        Toggle task completion status.
        
        Args:
            task_id: Task to toggle
            
        Returns:
            True if toggled successfully
        """
        try:
            # Get current task
            existing_tasks = [t for t in self._db.get_all_tasks() if t.id == task_id]
            if not existing_tasks:
                return False
            
            existing = existing_tasks[0]
            new_status = not existing.is_completed
            
            return self.update_task(task_id, is_completed=new_status)
            
        except Exception as e:
            print(f"Error toggling task completion: {e}")
            return False
    
    def delete_task(self, task_id: int) -> bool:
        """
        Delete task by ID.
        
        Args:
            task_id: Task to delete
            
        Returns:
            True if deleted successfully
        """
        try:
            success = self._db.delete_task(task_id)
            
            if success:
                self.data_changed.emit()
            
            return success
            
        except Exception as e:
            print(f"Error deleting task: {e}")
            return False
    
    # ==================== Statistics & Queries ====================
    
    def get_completion_statistics(self) -> Dict[str, int]:
        """
        Calculate overall task completion statistics.
        
        Returns:
            Dictionary with keys: total, completed, pending, overdue
        """
        try:
            tasks = self._db.get_all_tasks()
            today = get_today()
            
            total = len(tasks)
            completed = sum(1 for t in tasks if t.is_completed)
            pending = sum(1 for t in tasks if not t.is_completed)
            overdue = sum(1 for t in tasks if t.is_overdue(today))
            
            return {
                'total': total,
                'completed': completed,
                'pending': pending,
                'overdue': overdue,
                'completion_rate': (completed / total * 100) if total > 0 else 0
            }
            
        except Exception as e:
            print(f"Error calculating statistics: {e}")
            return {'total': 0, 'completed': 0, 'pending': 0, 'overdue': 0, 'completion_rate': 0}
    
    def get_overdue_tasks(self) -> List[Task]:
        """
        Retrieve all overdue tasks.
        
        Returns:
            List of Task models that are past due
        """
        try:
            tasks = self._db.get_all_tasks()
            today = get_today()
            
            return [t for t in tasks if t.is_overdue(today)]
            
        except Exception as e:
            print(f"Error retrieving overdue tasks: {e}")
            return []
    
    def get_high_priority_tasks(self) -> List[Task]:
        """
        Retrieve tasks with high priority (priority=2).
        
        Returns:
            List of high-priority Task models
        """
        try:
            tasks = self._db.get_all_tasks()
            return [t for t in tasks if t.priority == 2]
            
        except Exception as e:
            print(f"Error retrieving high priority tasks: {e}")
            return []
    
    def get_pending_tasks(self) -> List[Task]:
        """
        Retrieve all incomplete tasks.
        
        Returns:
            List of incomplete Task models
        """
        try:
            tasks = self._db.get_all_tasks()
            return [t for t in tasks if not t.is_completed]
            
        except Exception as e:
            print(f"Error retrieving pending tasks: {e}")
            return []
    
    def clear_completed_tasks(self) -> int:
        """
        Delete all completed tasks.
        
        Returns:
            Number of tasks deleted
        """
        try:
            completed_tasks = [t for t in self._db.get_all_tasks() if t.is_completed]
            
            deleted_count = 0
            for task in completed_tasks:
                if self._db.delete_task(task.id):
                    deleted_count += 1
            
            if deleted_count > 0:
                self.data_changed.emit()
            
            return deleted_count
            
        except Exception as e:
            print(f"Error clearing completed tasks: {e}")
            return 0
