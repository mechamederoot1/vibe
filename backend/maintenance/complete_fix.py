#!/usr/bin/env python3
"""
Complete fix for profile photo upload issues
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    # Method 1: Try using main.py connection
    from main import engine
    from sqlalchemy import text
    
    print("🔧 Method 1: Using SQLAlchemy from main.py")
    
    with engine.connect() as conn:
        # Check current table structure
        result = conn.execute(text("DESCRIBE posts"))
        columns = [row[0] for row in result.fetchall()]
        
        print(f"📋 Current posts table columns: {len(columns)} columns")
        print(f"🔍 Looking for profile update columns...")
        
        has_profile_update = 'is_profile_update' in columns
        has_cover_update = 'is_cover_update' in columns
        
        print(f"   - is_profile_update: {'✅ EXISTS' if has_profile_update else '❌ MISSING'}")
        print(f"   - is_cover_update: {'✅ EXISTS' if has_cover_update else '❌ MISSING'}")
        
        if not has_profile_update:
            print("➕ Adding is_profile_update column...")
            conn.execute(text("ALTER TABLE posts ADD COLUMN is_profile_update BOOLEAN DEFAULT FALSE"))
            conn.commit()
            print("✅ Added is_profile_update")
        
        if not has_cover_update:
            print("➕ Adding is_cover_update column...")
            conn.execute(text("ALTER TABLE posts ADD COLUMN is_cover_update BOOLEAN DEFAULT FALSE"))
            conn.commit()
            print("✅ Added is_cover_update")
        
        # Verify the fix
        result = conn.execute(text("DESCRIBE posts"))
        columns = [row[0] for row in result.fetchall()]
        
        final_profile = 'is_profile_update' in columns
        final_cover = 'is_cover_update' in columns
        
        print("\n🎯 FINAL VERIFICATION:")
        print(f"   - is_profile_update: {'✅ OK' if final_profile else '❌ FAILED'}")
        print(f"   - is_cover_update: {'✅ OK' if final_cover else '❌ FAILED'}")
        
        if final_profile and final_cover:
            print("\n🎉 DATABASE SUCCESSFULLY FIXED!")
            print("🔄 Please restart the backend server for changes to take effect.")
        else:
            print("\n❌ Fix failed. Manual intervention required.")

except Exception as e:
    print(f"❌ Error with Method 1: {e}")
    print("\n🔧 Trying Method 2: Direct PyMySQL connection...")
    
    try:
        import pymysql
        
        # Database credentials
        connection = pymysql.connect(
            host='localhost',
            port=3306,
            user='root',
            password='Evo@000#!',
            database='vibe',
            charset='utf8mb4'
        )
        
        cursor = connection.cursor()
        
        # Check and add columns
        cursor.execute("SHOW COLUMNS FROM posts")
        columns = [row[0] for row in cursor.fetchall()]
        
        if 'is_profile_update' not in columns:
            cursor.execute("ALTER TABLE posts ADD COLUMN is_profile_update BOOLEAN DEFAULT FALSE")
            print("✅ Added is_profile_update")
        
        if 'is_cover_update' not in columns:
            cursor.execute("ALTER TABLE posts ADD COLUMN is_cover_update BOOLEAN DEFAULT FALSE") 
            print("✅ Added is_cover_update")
        
        connection.commit()
        connection.close()
        
        print("🎉 DATABASE FIXED WITH DIRECT CONNECTION!")
        
    except Exception as e2:
        print(f"❌ Method 2 also failed: {e2}")
        print("\n💡 MANUAL FIX REQUIRED:")
        print("Execute these SQL commands directly in your MySQL console:")
        print("   ALTER TABLE posts ADD COLUMN is_profile_update BOOLEAN DEFAULT FALSE;")
        print("   ALTER TABLE posts ADD COLUMN is_cover_update BOOLEAN DEFAULT FALSE;")
