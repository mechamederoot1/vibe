#!/usr/bin/env python3
"""
Migration script to fix background_color column size in stories table
"""

import os
import sys
from sqlalchemy import create_engine, text

# Add the parent directory to the path so we can import our models
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from core.database import engine
except ImportError as e:
    print(f"Error importing database: {e}")
    print("Make sure you're running this from the backend directory")
    sys.exit(1)

def fix_background_color_column():
    """Fix the background_color column size to support CSS gradients"""
    print("🔧 Fixing background_color column size...")
    
    try:
        with engine.connect() as conn:
            # Check current column definition
            result = conn.execute(text("""
                SELECT CHARACTER_MAXIMUM_LENGTH, DATA_TYPE 
                FROM INFORMATION_SCHEMA.COLUMNS 
                WHERE TABLE_NAME = 'stories' 
                AND COLUMN_NAME = 'background_color'
            """)).fetchone()
            
            if result:
                current_length = result[0]
                data_type = result[1]
                print(f"📊 Current column: {data_type}({current_length})")
                
                if current_length and current_length < 255:
                    print("🔄 Updating column size to VARCHAR(255)...")
                    
                    # Alter the column
                    conn.execute(text("""
                        ALTER TABLE stories 
                        MODIFY COLUMN background_color VARCHAR(255)
                    """))
                    conn.commit()
                    
                    print("✅ Column updated successfully!")
                    
                    # Verify the change
                    result = conn.execute(text("""
                        SELECT CHARACTER_MAXIMUM_LENGTH 
                        FROM INFORMATION_SCHEMA.COLUMNS 
                        WHERE TABLE_NAME = 'stories' 
                        AND COLUMN_NAME = 'background_color'
                    """)).fetchone()
                    
                    if result:
                        new_length = result[0]
                        print(f"✅ Verified: Column is now VARCHAR({new_length})")
                    
                else:
                    print(f"✅ Column already has sufficient size ({current_length})")
                    
            else:
                print("❌ Could not find background_color column in stories table")
                return False
                
    except Exception as e:
        print(f"❌ Error updating column: {e}")
        return False
    
    return True

def test_gradient_storage():
    """Test storing a CSS gradient in the background_color column"""
    print("\n🧪 Testing gradient storage...")
    
    test_gradient = "linear-gradient(135deg, #667eea 0%, #764ba2 100%)"
    print(f"📝 Test gradient: {test_gradient}")
    print(f"📏 Length: {len(test_gradient)} characters")
    
    try:
        with engine.connect() as conn:
            # Try to insert a test record with gradient
            conn.execute(text("""
                INSERT INTO stories (author_id, content, background_color, duration_hours, expires_at, created_at, views_count)
                VALUES (1, 'Test gradient story', :gradient, 24, NOW() + INTERVAL 24 HOUR, NOW(), 0)
            """), {"gradient": test_gradient})
            
            # Get the inserted record ID
            result = conn.execute(text("""
                SELECT id, background_color FROM stories 
                WHERE content = 'Test gradient story' 
                ORDER BY id DESC 
                LIMIT 1
            """)).fetchone()
            
            if result:
                story_id, stored_gradient = result
                print(f"✅ Test gradient stored successfully!")
                print(f"📄 Stored value: {stored_gradient}")
                
                # Clean up test record
                conn.execute(text("DELETE FROM stories WHERE id = :id"), {"id": story_id})
                conn.commit()
                print("🧹 Test record cleaned up")
                
                return True
            else:
                print("❌ Could not retrieve test record")
                return False
                
    except Exception as e:
        print(f"❌ Error testing gradient storage: {e}")
        return False

def main():
    """Main migration function"""
    print("=" * 60)
    print("🔧 BACKGROUND COLOR COLUMN MIGRATION")
    print("=" * 60)
    
    # Check database connection
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        print("✅ Database connection successful")
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False
    
    # Fix the column
    if not fix_background_color_column():
        print("❌ Failed to fix background_color column")
        return False
    
    # Test gradient storage
    if not test_gradient_storage():
        print("❌ Failed to test gradient storage")
        return False
    
    print("\n" + "=" * 60)
    print("✅ MIGRATION COMPLETED SUCCESSFULLY!")
    print("=" * 60)
    print("\n📋 Summary:")
    print("- background_color column expanded to VARCHAR(255)")
    print("- CSS gradients can now be stored properly")
    print("- Stories with gradients should work now")
    print("\n🎉 Your stories functionality is now fully working!")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
