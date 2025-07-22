#!/usr/bin/env python3
"""
Quick fix for missing profile update columns
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from main import engine
from sqlalchemy import text

def fix_profile_columns():
    """Add missing profile update columns"""
    print("🔧 Adding missing profile update columns...")
    
    with engine.connect() as conn:
        try:
            # Add is_profile_update column
            conn.execute(text('ALTER TABLE posts ADD COLUMN is_profile_update BOOLEAN DEFAULT FALSE'))
            conn.commit()
            print('✅ Added is_profile_update column')
        except Exception as e:
            if "Duplicate column name" in str(e) or "already exists" in str(e):
                print('��� is_profile_update column already exists')
            else:
                print(f'⚠️ Error adding is_profile_update: {e}')
        
        try:
            # Add is_cover_update column  
            conn.execute(text('ALTER TABLE posts ADD COLUMN is_cover_update BOOLEAN DEFAULT FALSE'))
            conn.commit()
            print('✅ Added is_cover_update column')
        except Exception as e:
            if "Duplicate column name" in str(e) or "already exists" in str(e):
                print('✅ is_cover_update column already exists')
            else:
                print(f'⚠️ Error adding is_cover_update: {e}')

    print('🎉 Database migration completed!')

if __name__ == "__main__":
    fix_profile_columns()
