#!/usr/bin/env python3
import sqlite3
import os

def migrate_database():
    """Add is_profile_update and is_cover_update columns to posts table"""
    db_path = "backend/database.db"
    
    if not os.path.exists(db_path):
        print("Database file not found. Creating columns when database is created.")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Add is_profile_update column
        cursor.execute("ALTER TABLE posts ADD COLUMN is_profile_update BOOLEAN DEFAULT 0")
        print("✓ Added is_profile_update column")
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e):
            print("Column is_profile_update already exists")
        else:
            print(f"Error adding is_profile_update: {e}")
    
    try:
        # Add is_cover_update column  
        cursor.execute("ALTER TABLE posts ADD COLUMN is_cover_update BOOLEAN DEFAULT 0")
        print("✓ Added is_cover_update column")
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e):
            print("Column is_cover_update already exists")
        else:
            print(f"Error adding is_cover_update: {e}")
    
    conn.commit()
    conn.close()
    print("Database migration completed successfully!")

if __name__ == "__main__":
    migrate_database()
