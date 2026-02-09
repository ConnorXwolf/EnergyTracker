"""
Database migration script for adding 'date' column to tasks table.

This script handles the migration for existing databases that don't have
the 'date' column in the tasks table. It adds the column and populates
it with the current date for all existing tasks.

Usage:
    python migrate_task_dates.py
"""

import sqlite3
import sys
from pathlib import Path
from datetime import date


def migrate_database(db_path: Path) -> bool:
    """
    Perform database migration to add 'date' column to tasks table.
    
    Args:
        db_path: Path to SQLite database file
        
    Returns:
        True if migration successful, False otherwise
    """
    try:
        # Connect to database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if 'date' column already exists
        cursor.execute("PRAGMA table_info(tasks)")
        columns = [row[1] for row in cursor.fetchall()]
        
        if 'date' in columns:
            print("✓ Migration already applied - 'date' column exists")
            conn.close()
            return True
        
        print("Starting migration...")
        
        # Begin transaction
        cursor.execute("BEGIN TRANSACTION")
        
        try:
            # Add 'date' column with default value
            today = date.today().isoformat()
            cursor.execute(f"""
                ALTER TABLE tasks 
                ADD COLUMN date DATE NOT NULL DEFAULT '{today}' 
                CHECK(date LIKE '____-__-__')
            """)
            
            print(f"✓ Added 'date' column with default value '{today}'")
            
            # Create index for performance
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_tasks_date ON tasks(date)
            """)
            
            print("✓ Created index on 'date' column")
            
            # Update metadata
            cursor.execute("""
                INSERT OR REPLACE INTO app_metadata (key, value, updated_at)
                VALUES ('last_migration', '2026-02-10_add_task_date', datetime('now'))
            """)
            
            cursor.execute("""
                UPDATE app_metadata 
                SET value = '1.1.0', updated_at = datetime('now')
                WHERE key = 'db_version'
            """)
            
            print("✓ Updated database metadata")
            
            # Commit transaction
            conn.commit()
            
            # Verify migration
            cursor.execute("SELECT COUNT(*) FROM tasks")
            task_count = cursor.fetchone()[0]
            
            print(f"\n✓ Migration completed successfully")
            print(f"  - {task_count} existing tasks now have date '{today}'")
            
            conn.close()
            return True
            
        except sqlite3.Error as e:
            # Rollback on error
            conn.rollback()
            print(f"✗ Migration failed: {e}")
            conn.close()
            return False
            
    except sqlite3.Error as e:
        print(f"✗ Database connection failed: {e}")
        return False
    except Exception as e:
        print(f"✗ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Execute migration script."""
    print("=" * 60)
    print("Energy Tracker - Database Migration")
    print("Adding 'date' column to tasks table")
    print("=" * 60)
    print()
    
    # Locate database
    db_path = Path.cwd() / "energy_tracker.db"
    
    if not db_path.exists():
        print(f"✗ Database not found at: {db_path}")
        print("  Please run the application first to create the database")
        sys.exit(1)
    
    print(f"Database location: {db_path}")
    print()
    
    # Confirm migration
    response = input("Proceed with migration? (yes/no): ")
    if response.lower() != 'yes':
        print("Migration cancelled")
        sys.exit(0)
    
    print()
    
    # Execute migration
    success = migrate_database(db_path)
    
    print()
    print("=" * 60)
    if success:
        print("✓ MIGRATION COMPLETE")
        print("=" * 60)
        print()
        print("You can now run the application:")
        print("  python main.py")
        sys.exit(0)
    else:
        print("✗ MIGRATION FAILED")
        print("=" * 60)
        print()
        print("Please check the error messages above and try again")
        print("If the issue persists, consider backing up your database")
        print("and recreating it from scratch")
        sys.exit(1)


if __name__ == "__main__":
    main()