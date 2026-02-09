"""
Daily Report Generator.

Generates and saves daily reports including HP, tasks, and exercises.
"""

import os
from datetime import datetime
from pathlib import Path
from typing import Dict, Any


class ReportGenerator:
    """
    Generate daily reports with HP, tasks, and exercise data.
    
    Reports are saved to data/history directory.
    """
    
    def __init__(
        self,
        exercise_manager,  # Type hint removed to avoid circular import
        task_manager,      # Type hint removed to avoid circular import
        output_dir: str = "data/history"
    ):
        """
        Initialize report generator.
        
        Args:
            exercise_manager: Manager for exercise operations
            task_manager: Manager for task operations
            output_dir: Directory to save reports
        """
        self._exercise_manager = exercise_manager
        self._task_manager = task_manager
        self._output_dir = Path(output_dir)
        
        # Create output directory if it doesn't exist
        self._output_dir.mkdir(parents=True, exist_ok=True)
    
    def generate_daily_report(
        self,
        hp_value: float,
        points: Dict[str, int],
        date: str = None
    ) -> str:
        """
        Generate and save daily report.
        
        Args:
            hp_value: Current HP value
            points: Dictionary with physical, mental, sleepiness points
            date: Date for report (defaults to today)
            
        Returns:
            Path to saved report file
        """
        # Lazy import to avoid circular dependency
        from utils import get_today
        
        if date is None:
            date = get_today()
        
        # Generate timestamp
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Collect data
        report_data = {
            'date': date,
            'timestamp': timestamp,
            'hp': hp_value,
            'points': points,
            'tasks': self._get_task_data(),
            'exercises': self._get_exercise_data(date)
        }
        
        # Generate report content
        report_content = self._format_report(report_data)
        
        # Save report
        filename = f"report_{date}_{datetime.now().strftime('%H%M%S')}.txt"
        filepath = self._output_dir / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(report_content)
        
        return str(filepath)
    
    def _get_task_data(self) -> Dict[str, Any]:
        """
        Get task completion data.
        
        Returns:
            Dictionary with task statistics and list
        """
        try:
            stats = self._task_manager.get_completion_statistics()
            groups = self._task_manager.get_task_groups()
            
            task_list = []
            for group in groups:
                for task in group.tasks:
                    task_list.append({
                        'title': task.title,
                        'completed': task.is_completed,
                        'category': group.category
                    })
            
            return {
                'total': stats['total'],
                'completed': stats['completed'],
                'completion_rate': stats['completion_rate'],
                'tasks': task_list
            }
        except Exception as e:
            print(f"Error getting task data: {e}")
            return {
                'total': 0,
                'completed': 0,
                'completion_rate': 0,
                'tasks': []
            }
    
    def _get_exercise_data(self, date: str) -> Dict[str, Any]:
        """
        Get exercise completion data.
        
        Args:
            date: Date for exercise data
            
        Returns:
            Dictionary with exercise statistics and list
        """
        try:
            summary = self._exercise_manager.get_summary_for_date(date)
            exercises_data = self._exercise_manager.get_logs_for_date(date)
            
            exercise_list = []
            for exercise, log in exercises_data:
                exercise_list.append({
                    'name': exercise.name,
                    'completed': log.completed,
                    'actual': log.actual_value,
                    'target': log.target_value,
                    'unit': log.unit,
                    'progress': log.progress_percentage
                })
            
            return {
                'total': summary.total,
                'completed': summary.completed,
                'completion_rate': summary.completion_rate,
                'progress_rate': summary.progress_rate,
                'exercises': exercise_list
            }
        except Exception as e:
            print(f"Error getting exercise data: {e}")
            return {
                'total': 0,
                'completed': 0,
                'completion_rate': 0,
                'progress_rate': 0,
                'exercises': []
            }
    
    def _format_report(self, data: Dict[str, Any]) -> str:
        """
        Format report data as text.
        
        Args:
            data: Report data dictionary
            
        Returns:
            Formatted report text
        """
        lines = []
        
        # Header
        lines.append("=" * 60)
        lines.append(f"Daily Report - {data['date']}")
        lines.append(f"Generated: {data['timestamp']}")
        lines.append("=" * 60)
        lines.append("")
        
        # HP and Points
        lines.append("HP & POINTS")
        lines.append("-" * 60)
        lines.append(f"HP: {data['hp']:.0f}")
        lines.append(f"Physical: {data['points']['physical']} pts")
        lines.append(f"Mental: {data['points']['mental']} pts")
        lines.append(f"Sleepiness: {data['points']['sleepiness']} pts")
        lines.append("")
        
        # Tasks
        lines.append("TASKS")
        lines.append("-" * 60)
        task_data = data['tasks']
        lines.append(f"Completed: {task_data['completed']}/{task_data['total']} ({task_data['completion_rate']:.0f}%)")
        lines.append("")
        
        if task_data['tasks']:
            for task in task_data['tasks']:
                status = "✓" if task['completed'] else "○"
                lines.append(f"  {status} [{task['category']}] {task['title']}")
        else:
            lines.append("  No tasks")
        lines.append("")
        
        # Exercises
        lines.append("EXERCISES")
        lines.append("-" * 60)
        exercise_data = data['exercises']
        lines.append(f"Completed: {exercise_data['completed']}/{exercise_data['total']} ({exercise_data['completion_rate']:.0f}%)")
        lines.append(f"Progress: {exercise_data['progress_rate']:.0f}%")
        lines.append("")
        
        if exercise_data['exercises']:
            for exercise in exercise_data['exercises']:
                status = "✓" if exercise['completed'] else "○"
                lines.append(f"  {status} {exercise['name']}: {exercise['actual']}/{exercise['target']} {exercise['unit']} ({exercise['progress']:.0f}%)")
        else:
            lines.append("  No exercises")
        lines.append("")
        
        # Footer
        lines.append("=" * 60)
        lines.append("End of Report")
        lines.append("=" * 60)
        
        return "\n".join(lines)