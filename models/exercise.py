"""
Exercise data models with validation.

Defines Pydantic models for exercise definitions and daily logs,
including progress calculation and validation logic.
"""

from pydantic import BaseModel, Field, field_validator, computed_field
from typing import Literal


class Exercise(BaseModel):
    """
    Exercise definition model.
    
    Represents a single exercise type in the tracking system with
    associated metadata for visualization and progress tracking.
    
    Attributes:
        id: Unique identifier (0 for unsaved exercises)
        name: Display name of the exercise
        category: Classification (cardio/muscle/stretch)
        color: Hex color code for UI visualization
        target_value: Daily goal quantity
        unit: Measurement unit for progress tracking
    """
    id: int = Field(default=0, ge=0)
    name: str = Field(min_length=1, max_length=100)
    category: Literal['cardio', 'muscle', 'stretch']
    color: str = Field(pattern=r'^#[0-9A-Fa-f]{6}$')
    target_value: int = Field(gt=0)
    unit: Literal['reps', 'sets', 'minutes', 'km', 'hours']
    
    @field_validator('name')
    @classmethod
    def validate_name(cls, value: str) -> str:
        """
        Ensure exercise name is not just whitespace.
        
        Args:
            value: Exercise name to validate
            
        Returns:
            Trimmed exercise name
            
        Raises:
            ValueError: If name is empty after trimming
        """
        trimmed = value.strip()
        if not trimmed:
            raise ValueError("Exercise name cannot be empty or whitespace")
        return trimmed
    
    @field_validator('color')
    @classmethod
    def validate_color(cls, value: str) -> str:
        """
        Ensure color is uppercase hex format.
        
        Args:
            value: Hex color code
            
        Returns:
            Uppercase hex color code
        """
        return value.upper()


class ExerciseLog(BaseModel):
    """
    Daily exercise completion record.
    
    Tracks actual performance against target goals with automatic
    progress percentage calculation and achievement status.
    
    Attributes:
        id: Unique log identifier (0 for unsaved logs)
        exercise_id: Reference to parent exercise
        date: Workout date in ISO format (YYYY-MM-DD)
        completed: Binary completion flag
        actual_value: Actual performance achieved
        target_value: Goal quantity (denormalized for quick access)
        unit: Measurement unit (denormalized)
        category: Exercise category (denormalized for aggregations)
        notes: Optional workout observations
    """
    id: int = Field(default=0, ge=0)
    exercise_id: int = Field(gt=0)
    date: str = Field(pattern=r'^\d{4}-\d{2}-\d{2}$')
    completed: bool = False
    actual_value: int = Field(ge=0)
    target_value: int = Field(gt=0)
    unit: Literal['reps', 'sets', 'minutes', 'km', 'hours']
    category: Literal['cardio', 'muscle', 'stretch']
    notes: str = Field(default="", max_length=500)
    
    @field_validator('date')
    @classmethod
    def validate_date_format(cls, value: str) -> str:
        """
        Validate ISO date format.
        
        Args:
            value: Date string to validate
            
        Returns:
            Validated date string
            
        Raises:
            ValueError: If date format is invalid
        """
        from datetime import datetime
        try:
            datetime.fromisoformat(value)
            return value
        except ValueError as e:
            raise ValueError(f"Invalid date format: {value}. Expected YYYY-MM-DD") from e
    
    @computed_field
    @property
    def progress_percentage(self) -> float:
        """
        Calculate progress as percentage (can exceed 100%).
        
        Returns:
            Progress ratio as percentage (e.g., 120.5 for over-achievement)
        """
        if self.target_value == 0:
            return 0.0
        return round((self.actual_value / self.target_value) * 100, 1)
    
    @computed_field
    @property
    def display_percentage(self) -> float:
        """
        Calculate capped percentage for progress bar display.
        
        Returns:
            Progress percentage capped at 100.0
        """
        return min(self.progress_percentage, 100.0)
    
    @computed_field
    @property
    def is_over_achieved(self) -> bool:
        """
        Check if actual performance exceeds target.
        
        Returns:
            True if actual > target, False otherwise
        """
        return self.actual_value > self.target_value
    
    @computed_field
    @property
    def is_target_met(self) -> bool:
        """
        Check if target goal was met or exceeded.
        
        Returns:
            True if actual >= target, False otherwise
        """
        return self.actual_value >= self.target_value
    
    def format_progress_text(self) -> str:
        """
        Generate formatted progress display text.
        
        Returns:
            Formatted string like "30/30 reps (100.0%)"
        """
        return (
            f"{self.actual_value}/{self.target_value} {self.unit} "
            f"({self.progress_percentage:.1f}%)"
        )


class ExerciseSummary(BaseModel):
    """
    Aggregated exercise statistics for a date range.
    
    Attributes:
        total_exercises: Number of exercises tracked
        completed_count: Number completed
        completion_rate: Percentage of exercises completed
        total_actual: Sum of all actual values
        total_target: Sum of all target values
        progress_rate: Overall progress percentage
    """
    total_exercises: int = Field(ge=0)
    completed_count: int = Field(ge=0)
    completion_rate: float = Field(ge=0.0, le=100.0)
    total_actual: int = Field(ge=0)
    total_target: int = Field(gt=0)
    progress_rate: float = Field(ge=0.0)
    
    @field_validator('completion_rate', 'progress_rate')
    @classmethod
    def round_percentage(cls, value: float) -> float:
        """Round percentage to one decimal place."""
        return round(value, 1)
