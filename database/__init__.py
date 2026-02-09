"""
Database layer package.

Provides SQLite database management with schema initialization
and comprehensive CRUD operations for all data models.
"""

from .db_manager import DatabaseManager

__all__ = ['DatabaseManager']
