"""Difficulty level enum for LogicBoost questions."""
from enum import Enum


class DifficultyLevel(Enum):
    """Question difficulty levels from 1 (very easy) to 5 (very hard)."""
    
    VERY_EASY = 1      # 🟢 Very Easy
    EASY = 2           # 🟡 Easy
    MEDIUM = 3         # 🟠 Medium
    HARD = 4           # 🔴 Hard
    VERY_HARD = 5      # ⚫ Very Hard
    
    def __int__(self):
        """Convert enum to integer value."""
        return self.value
    
    def __str__(self):
        """Convert enum to readable string."""
        names = {
            1: "Very Easy",
            2: "Easy",
            3: "Medium",
            4: "Hard",
            5: "Very Hard"
        }
        return names.get(self.value, "Unknown")
    
    @classmethod
    def from_value(cls, value):
        """Create enum from integer value."""
        if isinstance(value, cls):
            return value
        try:
            return cls(int(value))
        except (ValueError, KeyError):
            raise ValueError(f"Invalid difficulty value: {value}. Must be 1-5")
    
    @property
    def emoji(self):
        """Get emoji representation."""
        emojis = {
            1: "🟢",
            2: "🟡",
            3: "🟠",
            4: "🔴",
            5: "⚫"
        }
        return emojis.get(self.value, "❓")
    
    @classmethod
    def all_values(cls):
        """Get all valid difficulty values (1-5)."""
        return [1, 2, 3, 4, 5]
