"""
Task data model with validation.

Defines the Pydantic model for checklist tasks with due dates
and priority levels.
"""

from pydantic import BaseModel, Field, field_validator
from typing import Optional


class Task(BaseModel):
    """
    Task/checklist item model.
    
    Represents a single task in the daily checklist system with
    completion tracking and optional due dates.
    
    Attributes:
        id: Unique identifier (0 for unsaved tasks)
        title: Task description
        is_completed: Completion status flag
        date: Task creation/assignment date in ISO format
        due_date: Optional due date in ISO format
        priority: Priority level (0=low, 1=medium, 2=high)
        category: Optional categorization (e.g., "收拾書包")
    """
    id: int = Field(default=0, ge=0)
    title: str = Field(min_length=1, max_length=200)
    is_completed: bool = False
    date: str = Field(pattern=r'^\d{4}-\d{2}-\d{2}$')
    due_date: Optional[str] = Field(
        default=None,
        pattern=r'^\d{4}-\d{2}-\d{2}$'
    )
    priority: int = Field(default=0, ge=0, le=2)
    category: Optional[str] = Field(default=None, max_length=50)
    
    @field_validator('title')
    @classmethod
    def validate_title(cls, value: str) -> str:
        """
        Ensure task title is not just whitespace.
        
        Args:
            value: Task title to validate
            
        Returns:
            Trimmed task title
            
        Raises:
            ValueError: If title is empty after trimming
        """
        trimmed = value.strip()
        if not trimmed:
            raise ValueError("Task title cannot be empty or whitespace")
        return trimmed
    
    @field_validator('date', 'due_date')
    @classmethod
    def validate_dates(cls, value: Optional[str]) -> Optional[str]:
        """
        Validate date formats if provided.
        
        Args:
            value: Date string or None
            
        Returns:
            Validated date string or None
            
        Raises:
            ValueError: If date format is invalid
        """
        if value is None:
            return None
        
        from datetime import datetime
        try:
            datetime.fromisoformat(value)
            return value
        except ValueError as e:
            raise ValueError(
                f"Invalid date format: {value}. Expected YYYY-MM-DD"
            ) from e
    
    def is_overdue(self, current_date: str) -> bool:
        """
        Check if task is overdue.
        
        Args:
            current_date: Current date in ISO format
            
        Returns:
            True if task has due date and is past due, False otherwise
        """
        if self.due_date is None or self.is_completed:
            return False
        
        from datetime import datetime
        try:
            due = datetime.fromisoformat(self.due_date).date()
            current = datetime.fromisoformat(current_date).date()
            return current > due
        except ValueError:
            return False
    
    def get_priority_label(self) -> str:
        """
        Get human-readable priority label.
        
        Returns:
            Priority level as string ("Low", "Medium", "High")
        """
        priority_map = {0: "Low", 1: "Medium", 2: "High"}
        return priority_map.get(self.priority, "Unknown")


class TaskGroup(BaseModel):
    """
    Grouped collection of related tasks.
    
    Used for organizing tasks into categories like "收拾書包"
    with aggregate completion tracking.
    
    Attributes:
        category: Group name
        tasks: List of tasks in this group
        required_count: Number of tasks required for group completion
    """
    category: str = Field(min_length=1, max_length=50)
    tasks: list[Task] = Field(default_factory=list)
    required_count: Optional[int] = None
    
    @property
    def completed_count(self) -> int:
        """
        Count completed tasks in group.
        
        Returns:
            Number of completed tasks
        """
        return sum(1 for task in self.tasks if task.is_completed)
    
    @property
    def total_count(self) -> int:
        """
        Get total number of tasks in group.
        
        Returns:
            Total task count
        """
        return len(self.tasks)
    
    @property
    def is_group_completed(self) -> bool:
        """
        Check if required tasks are completed.
        
        Returns:
            True if required count is met or all tasks completed
        """
        if self.required_count is None:
            return self.completed_count == self.total_count
        return self.completed_count >= self.required_count
    
    def format_progress(self) -> str:
        """
        Generate progress display text.
        
        Returns:
            Formatted string like "必帶 4 樣 (4/4)"
        """
        if self.required_count is not None:
            return f"必帶 {self.required_count} 樣 ({self.completed_count}/{self.total_count})"
        return f"{self.completed_count}/{self.total_count}"
