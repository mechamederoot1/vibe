#!/usr/bin/env python3
"""
Auto-fix reactions table - add missing updated_at column
This script will run automatically when the backend starts
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import create_engine, text, inspect
from core.database import SQLALCHEMY_DATABASE_URL

def auto_fix_reactions_table():
    """Automatically fix reactions table if updated_at column is missing"""
    
    print("🔧 Checking reactions table schema...")
    
    try:
        # Create engine
        engine = create_engine(SQLALCHEMY_DATABASE_URL)
        
        with engine.connect() as conn:
            # Check if updated_at column exists
            inspector = inspect(engine)
            columns = inspector.get_columns('reactions')
            column_names = [col['name'] for col in columns]
            
            if 'updated_at' not in column_names:
                print("❌ Missing updated_at column in reactions table")
                print("🔧 Adding updated_at column...")
                
                # Add updated_at column
                conn.execute(text('''
                    ALTER TABLE reactions 
                    ADD COLUMN updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
                '''))
                conn.commit()
                print('✅ Added updated_at column to reactions table')
                
                # Update existing records
                conn.execute(text('''
                    UPDATE reactions 
                    SET updated_at = created_at 
                    WHERE updated_at IS NULL
                '''))
                conn.commit()
                print('✅ Updated existing records with created_at values')
                
            else:
                print('✅ reactions.updated_at column already exists')
                
            # Verify the fix
            columns = inspector.get_columns('reactions')
            print("📋 Current reactions table columns:")
            for col in columns:
                print(f"   - {col['name']} ({col['type']})")
                
            return True
                
    except Exception as e:
        print(f"❌ Error fixing reactions table: {e}")
        return False

if __name__ == "__main__":
    auto_fix_reactions_table()
