"""
Database reset script for Energy Tracker.

Deletes all existing exercises and resets to new default (拉筋).
Run this after updating to the new version with Physical/Mental/Sleepiness categories.

Usage:
    python reset_exercises.py
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database import DatabaseManager
from managers import ExerciseManager

def main():
    """Reset exercises to new defaults."""
    print("=" * 60)
    print("Energy Tracker - Exercise Reset")
    print("=" * 60)
    print()
    
    response = input("This will DELETE ALL exercises and create new default. Continue? (yes/no): ")
    if response.lower() != 'yes':
        print("Aborted.")
        return
    
    print()
    print("Resetting exercises...")
    
    try:
        # Initialize managers
        db = DatabaseManager()
        em = ExerciseManager()
        
        # Get all exercises
        exercises = em.get_all_exercises()
        print(f"Found {len(exercises)} existing exercises")
        
        # Delete all exercises
        for exercise in exercises:
            em.delete_exercise(exercise.id)
            print(f"  Deleted: {exercise.name}")
        
        print()
        print("Creating new default exercise...")
        
        # Create new default: 拉筋
        exercise_id = em.create_exercise(
            name='拉筋',
            category='physical',
            target_value=30,
            unit='minutes'
        )
        
        if exercise_id:
            print(f"  Created: 拉筋 (30 minutes/day)")
        
        print()
        print("=" * 60)
        print("✓ RESET COMPLETE")
        print("=" * 60)
        print()
        print("You can now run the application:")
        print("  python main.py")
        print()
        
    except Exception as e:
        print(f"✗ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
