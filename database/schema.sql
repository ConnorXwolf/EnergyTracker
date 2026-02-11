-- Energy Tracker Database Schema
-- SQLite schema for exercise tracking, tasks, and calendar events

-- Exercise definitions table
CREATE TABLE IF NOT EXISTS exercises (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    category TEXT NOT NULL CHECK(category IN ('cardio', 'muscle', 'stretch')),
    color TEXT NOT NULL CHECK(length(color) = 7 AND color LIKE '#%'),
    target_value INTEGER NOT NULL CHECK(target_value > 0),
    unit TEXT NOT NULL CHECK(unit IN ('reps', 'sets', 'minutes', 'km', 'hours')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(name)
);

-- Daily exercise completion logs
CREATE TABLE IF NOT EXISTS exercise_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    exercise_id INTEGER NOT NULL,
    date DATE NOT NULL CHECK(date LIKE '____-__-__'),
    completed BOOLEAN NOT NULL DEFAULT 0,
    actual_value INTEGER NOT NULL DEFAULT 0 CHECK(actual_value >= 0),
    notes TEXT DEFAULT '',
    logged_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (exercise_id) REFERENCES exercises(id) ON DELETE CASCADE,
    UNIQUE(exercise_id, date)
);

-- Task checklist table
CREATE TABLE IF NOT EXISTS tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    is_completed BOOLEAN NOT NULL DEFAULT 0,
    date DATE NOT NULL DEFAULT (date('now')) CHECK(date LIKE '____-__-__'),
    due_date DATE CHECK(due_date IS NULL OR due_date LIKE '____-__-__'),
    priority INTEGER NOT NULL DEFAULT 0 CHECK(priority BETWEEN 0 AND 2),
    category TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP
);

-- Calendar events table
CREATE TABLE IF NOT EXISTS events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    event_date DATE NOT NULL CHECK(event_date LIKE '____-__-__'),
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Daily points tracking table
-- UPDATED: Stamina (0-10) + Mana (0-10) → Score (20-100)
-- Formula: hp = 20 + (physical + mental) * 4
CREATE TABLE IF NOT EXISTS daily_points (
    date DATE PRIMARY KEY CHECK(date LIKE '____-__-__'),
    physical INTEGER NOT NULL DEFAULT 0 CHECK(physical BETWEEN 0 AND 10),
    mental INTEGER NOT NULL DEFAULT 0 CHECK(mental BETWEEN 0 AND 10),
    hp INTEGER NOT NULL DEFAULT 20 CHECK(hp BETWEEN 20 AND 100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for performance optimization
CREATE INDEX IF NOT EXISTS idx_exercise_logs_date ON exercise_logs(date);
CREATE INDEX IF NOT EXISTS idx_exercise_logs_exercise_id ON exercise_logs(exercise_id);
CREATE INDEX IF NOT EXISTS idx_tasks_date ON tasks(date);
CREATE INDEX IF NOT EXISTS idx_tasks_due_date ON tasks(due_date);
CREATE INDEX IF NOT EXISTS idx_tasks_category ON tasks(category);
CREATE INDEX IF NOT EXISTS idx_events_date ON events(event_date);

-- Application metadata table
CREATE TABLE IF NOT EXISTS app_metadata (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insert initial metadata
INSERT OR IGNORE INTO app_metadata (key, value) VALUES ('db_version', '1.2.0');
INSERT OR IGNORE INTO app_metadata (key, value) VALUES ('initialized_at', datetime('now'));
INSERT OR IGNORE INTO app_metadata (key, value) VALUES ('last_update', '2026-02-11_stamina_mana_conversion');
