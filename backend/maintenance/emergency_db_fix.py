#!/usr/bin/env python3
"""
Emergency database fix - execute this in the backend directory
"""
import pymysql
import os
from urllib.parse import unquote_plus

def fix_database():
    """Direct MySQL connection to add missing columns"""
    
    # Database connection parameters
    db_host = os.getenv("DB_HOST", "localhost")
    db_port = int(os.getenv("DB_PORT", "3306"))
    db_user = os.getenv("DB_USER", "root") 
    db_password = os.getenv("DB_PASSWORD", "Evo@000#!")
    db_name = os.getenv("DB_NAME", "vibe")
    
    print(f"🔌 Connecting to MySQL database: {db_name}")
    
    try:
        # Direct MySQL connection
        connection = pymysql.connect(
            host=db_host,
            port=db_port,
            user=db_user,
            password=db_password,
            database=db_name,
            charset='utf8mb4'
        )
        
        cursor = connection.cursor()
        
        # Check if columns exist
        cursor.execute("SHOW COLUMNS FROM posts LIKE 'is_profile_update'")
        if cursor.fetchone():
            print("✅ Column is_profile_update already exists")
        else:
            print("➕ Adding is_profile_update column...")
            cursor.execute("ALTER TABLE posts ADD COLUMN is_profile_update BOOLEAN DEFAULT FALSE")
            print("✅ Added is_profile_update column")
        
        cursor.execute("SHOW COLUMNS FROM posts LIKE 'is_cover_update'")
        if cursor.fetchone():
            print("✅ Column is_cover_update already exists") 
        else:
            print("➕ Adding is_cover_update column...")
            cursor.execute("ALTER TABLE posts ADD COLUMN is_cover_update BOOLEAN DEFAULT FALSE")
            print("✅ Added is_cover_update column")
        
        connection.commit()
        print("🎉 Database fixed successfully!")
        
        # Verify the fix
        cursor.execute("DESCRIBE posts")
        columns = cursor.fetchall()
        has_profile_update = any('is_profile_update' in col for col in columns)
        has_cover_update = any('is_cover_update' in col for col in columns)
        
        print(f"✅ Verification - is_profile_update exists: {has_profile_update}")
        print(f"✅ Verification - is_cover_update exists: {has_cover_update}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    finally:
        if 'connection' in locals():
            connection.close()
    
    return True

if __name__ == "__main__":
    print("🚨 EMERGENCY DATABASE FIX")
    print("=" * 40)
    fix_database()
