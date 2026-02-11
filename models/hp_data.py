"""
HP data model for monthly tracker.

Represents daily HP metrics with Physical/Mental breakdown.
Updated: 2026-02-11 - Stamina/Mana model with internal score conversion
Formula: Display Score = 20 + (Stamina + Mana) * 4
Input Range: Stamina (0-10), Mana (0-10)
Output Range: Score (20-100)
"""

from pydantic import BaseModel, Field, field_validator
from typing import Optional


class HPData(BaseModel):
    """
    Daily HP data point.
    
    Attributes:
        hp: Display score (20-100, calculated from raw inputs)
        physical: Physical energy points (Stamina, 0-10)
        mental: Mental energy points (Mana, 0-10)
        date_str: ISO date string (YYYY-MM-DD)
    """
    hp: int = Field(ge=20, le=100)
    physical: int = Field(ge=0, le=10)
    mental: int = Field(ge=0, le=10)
    date_str: str = Field(pattern=r'^\d{4}-\d{2}-\d{2}$')
    
    @field_validator('hp')
    @classmethod
    def validate_hp_range(cls, value: int) -> int:
        """
        Ensure HP is within valid display range.
        
        Args:
            value: HP value to validate
            
        Returns:
            Validated HP value
            
        Raises:
            ValueError: If HP is outside 20-100 range
        """
        if not 20 <= value <= 100:
            raise ValueError(f"HP must be between 20 and 100, got {value}")
        return value
    
    def get_category(self) -> str:
        """
        Determine HP category based on thresholds.
        
        Display Score Thresholds:
        - = 20: None (minimum possible)
        - 21-40: Very Low
        - 41-55: Low
        - 56-75: Moderate
        - 76-83: High
        - 84-100: Maximum
        
        Returns:
            Category name string
        """
        if self.hp == 20:
            return "None"
        elif 21 <= self.hp <= 40:
            return "Very Low"
        elif 41 <= self.hp <= 55:
            return "Low"
        elif 56 <= self.hp <= 75:
            return "Moderate"
        elif 76 <= self.hp <= 83:
            return "High"
        else:  # 84-100
            return "Maximum"
    
    def get_raw_hp(self) -> int:
        """
        Calculate raw HP from physical and mental inputs.
        
        Returns:
            Raw HP value (0-20)
        """
        return self.physical + self.mental
    
    def format_display(self) -> str:
        """
        Generate formatted display string.
        
        Returns:
            Multi-line string with HP breakdown
        """
        raw_hp = self.get_raw_hp()
        return (
            f"Score: {self.hp}/100 ({self.get_category()})\n"
            f"Stamina: {self.physical}/10 | Mana: {self.mental}/10\n"
            f"Raw HP: {raw_hp}/20"
        )
