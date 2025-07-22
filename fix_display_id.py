#!/usr/bin/env python3
"""
Quick fix to add missing display_id column to users table
"""
import sys
import os
sys.path.append('backend')

from backend.main import engine
from sqlalchemy import text
import random

print("🔧 Adding missing display_id column to users table...")

with engine.connect() as conn:
    # Check if display_id column exists
    result = conn.execute(text("SHOW COLUMNS FROM users LIKE 'display_id'"))
    if result.fetchone():
        print("✅ display_id column already exists")
    else:
        # Add display_id column
        print("➕ Adding display_id column...")
        conn.execute(text("ALTER TABLE users ADD COLUMN display_id VARCHAR(20) UNIQUE AFTER id"))
        conn.commit()
        print("✅ Added display_id column")
        
        # Generate display_id for existing users
        print("🔄 Generating display_id for existing users...")
        result = conn.execute(text("SELECT id FROM users WHERE display_id IS NULL"))
        users = result.fetchall()
        
        for user in users:
            # Generate unique random display_id
            while True:
                random_display_id = str(random.randint(1000000000, 9999999999))
                check = conn.execute(text("SELECT id FROM users WHERE display_id = :display_id"), 
                                   {"display_id": random_display_id})
                if not check.fetchone():
                    break
            
            conn.execute(text("UPDATE users SET display_id = :display_id WHERE id = :user_id"), 
                       {"display_id": random_display_id, "user_id": user[0]})
            print(f"   ✅ User {user[0]} -> display_id: {random_display_id}")
        
        conn.commit()
        
    # Add index if it doesn't exist
    try:
        conn.execute(text("CREATE INDEX idx_display_id ON users (display_id)"))
        conn.commit()
        print("✅ Added index for display_id")
    except:
        print("✅ Index for display_id already exists")
    
    print("\n🎉 DISPLAY_ID COLUMN FIX COMPLETE!")
    print("🔄 Backend should now work properly")
