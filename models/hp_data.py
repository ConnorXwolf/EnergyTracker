"""
HP data model for monthly tracker.

Represents daily HP metrics with Physical/Mental/Sleepiness breakdown.
"""

from pydantic import BaseModel, Field
from typing import Optional


class HPData(BaseModel):
    """
    Daily HP data point.
    
    Attributes:
        hp: Calculated HP value (0-100)
        physical: Physical energy points (0-10)
        mental: Mental energy points (0-10)
        sleepiness: Sleepiness level (0-10)
        date_str: ISO date string (YYYY-MM-DD)
    """
    hp: int = Field(ge=0, le=100)
    physical: int = Field(ge=0, le=10)
    mental: int = Field(ge=0, le=10)
    sleepiness: int = Field(ge=0, le=10)
    date_str: str = Field(pattern=r'^\d{4}-\d{2}-\d{2}$')
    
    def get_category(self) -> str:
        """
        Determine HP category based on thresholds.
        
        Returns:
            Category name string
        """
        if self.hp < 33:
            return "None"
        elif 33 <= self.hp < 44:
            return "Very Low"
        elif 44 <= self.hp < 55:
            return "Low"
        elif 55 <= self.hp < 66:
            return "Moderate"
        elif 66 <= self.hp < 77:
            return "High"
        elif 77 <= self.hp < 88:
            return "Very High"
        else:  # 88-100
            return "Maximum"
    
    def format_display(self) -> str:
        """
        Generate formatted display string.
        
        Returns:
            Multi-line string with HP breakdown
        """
        return (
            f"HP: {self.hp} ({self.get_category()})\n"
            f"Physical: {self.physical} | "
            f"Mental: {self.mental} | "
            f"Sleepiness: {self.sleepiness}"
        )