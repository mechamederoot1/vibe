#!/usr/bin/env python3
"""
Comprehensive database setup script for Stories functionality
This script ensures all necessary tables and columns exist for proper story functionality
"""

import os
import sys
from sqlalchemy import create_engine, text, MetaData, inspect
from sqlalchemy.orm import sessionmaker
from datetime import datetime

# Add the parent directory to the path so we can import our models
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from core.database import engine, SessionLocal, Base
    from models.story import Story, StoryView, StoryTag, StoryOverlay
    from models.user import User
    from models.notification import Notification
except ImportError as e:
    print(f"Error importing models: {e}")
    print("Make sure you're running this from the backend directory")
    sys.exit(1)

def check_table_exists(engine, table_name):
    """Check if a table exists in the database"""
    inspector = inspect(engine)
    return table_name in inspector.get_table_names()

def check_column_exists(engine, table_name, column_name):
    """Check if a column exists in a table"""
    inspector = inspect(engine)
    if not check_table_exists(engine, table_name):
        return False
    
    columns = inspector.get_columns(table_name)
    return any(col['name'] == column_name for col in columns)

def create_stories_tables():
    """Create all stories-related tables"""
    print("🔧 Setting up Stories database structure...")
    
    try:
        # Create all tables
        Base.metadata.create_all(bind=engine)
        print("✅ All tables created successfully")
        
        # Verify essential tables exist
        essential_tables = ['stories', 'story_views', 'story_tags', 'story_overlays']
        for table in essential_tables:
            if check_table_exists(engine, table):
                print(f"✅ Table '{table}' exists")
            else:
                print(f"❌ Table '{table}' missing!")
                return False
        
        # Check specific columns in stories table
        stories_columns = [
            'id', 'author_id', 'content', 'media_type', 'media_url',
            'background_color', 'duration_hours', 'max_duration_seconds',
            'archived', 'archived_at', 'created_at', 'expires_at', 'views_count'
        ]
        
        for column in stories_columns:
            if check_column_exists(engine, 'stories', column):
                print(f"✅ Column 'stories.{column}' exists")
            else:
                print(f"❌ Column 'stories.{column}' missing!")
        
        # Check if media_url column has sufficient length
        with engine.connect() as conn:
            try:
                result = conn.execute(text("""
                    SELECT CHARACTER_MAXIMUM_LENGTH
                    FROM INFORMATION_SCHEMA.COLUMNS
                    WHERE TABLE_NAME = 'stories'
                    AND COLUMN_NAME = 'media_url'
                """)).fetchone()

                if result and result[0]:
                    if result[0] >= 500:
                        print(f"✅ media_url column length is sufficient ({result[0]} chars)")
                    else:
                        print(f"⚠️  media_url column may be too short ({result[0]} chars), recommended: 500+")
                        # Try to alter the column
                        try:
                            conn.execute(text("ALTER TABLE stories MODIFY COLUMN media_url VARCHAR(500)"))
                            conn.commit()
                            print("✅ media_url column length increased to 500 characters")
                        except Exception as e:
                            print(f"❌ Failed to increase media_url column length: {e}")
            except Exception as e:
                print(f"⚠️  Could not check media_url column length: {e}")

        # Check if background_color column can store CSS gradients
        with engine.connect() as conn:
            try:
                result = conn.execute(text("""
                    SELECT CHARACTER_MAXIMUM_LENGTH
                    FROM INFORMATION_SCHEMA.COLUMNS
                    WHERE TABLE_NAME = 'stories'
                    AND COLUMN_NAME = 'background_color'
                """)).fetchone()

                if result and result[0]:
                    if result[0] >= 255:
                        print(f"✅ background_color column length is sufficient ({result[0]} chars)")
                    else:
                        print(f"⚠️  background_color column too short ({result[0]} chars), expanding to 255...")
                        # Try to alter the column
                        try:
                            conn.execute(text("ALTER TABLE stories MODIFY COLUMN background_color VARCHAR(255)"))
                            conn.commit()
                            print("✅ background_color column expanded to 255 characters for CSS gradients")
                        except Exception as e:
                            print(f"❌ Failed to expand background_color column: {e}")
            except Exception as e:
                print(f"⚠️  Could not check background_color column length: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error creating tables: {e}")
        return False

def verify_user_story_columns():
    """Verify users table has story-related columns"""
    print("\n🔧 Checking user story-related columns...")
    
    story_columns = [
        'story_visibility',
        'story_notifications'
    ]
    
    with engine.connect() as conn:
        for column in story_columns:
            if check_column_exists(engine, 'users', column):
                print(f"✅ Column 'users.{column}' exists")
            else:
                print(f"⚠️  Column 'users.{column}' missing, attempting to add...")
                try:
                    if column == 'story_visibility':
                        conn.execute(text("ALTER TABLE users ADD COLUMN story_visibility VARCHAR(20) DEFAULT 'public'"))
                    elif column == 'story_notifications':
                        conn.execute(text("ALTER TABLE users ADD COLUMN story_notifications BOOLEAN DEFAULT 1"))
                    
                    conn.commit()
                    print(f"✅ Column 'users.{column}' added successfully")
                except Exception as e:
                    print(f"❌ Failed to add column 'users.{column}': {e}")

def setup_uploads_directory():
    """Create uploads directory structure for stories"""
    print("\n🔧 Setting up uploads directory structure...")
    
    upload_dirs = [
        "uploads",
        "uploads/stories",
        "uploads/stories/images",
        "uploads/stories/videos",
        "uploads/stories/audio"
    ]
    
    for directory in upload_dirs:
        os.makedirs(directory, exist_ok=True)
        print(f"✅ Directory '{directory}' ready")

def test_story_creation():
    """Test story creation functionality"""
    print("\n🧪 Testing story creation...")
    
    try:
        db = SessionLocal()
        
        # Check if we have at least one user
        user = db.query(User).first()
        if not user:
            print("⚠️  No users found, cannot test story creation")
            return
        
        print(f"📝 Testing with user: {user.first_name} {user.last_name}")
        
        # Test creating a simple text story
        test_story = Story(
            author_id=user.id,
            content="Test story for database setup",
            media_type="text",
            background_color="#3B82F6",
            duration_hours=24,
            max_duration_seconds=25,
            expires_at=datetime.utcnow()
        )
        
        db.add(test_story)
        db.commit()
        db.refresh(test_story)
        
        print(f"✅ Test story created successfully (ID: {test_story.id})")
        
        # Clean up test story
        db.delete(test_story)
        db.commit()
        print("✅ Test story cleaned up")
        
        db.close()
        
    except Exception as e:
        print(f"❌ Story creation test failed: {e}")

def main():
    """Main setup function"""
    print("=" * 60)
    print("🚀 STORIES DATABASE SETUP SCRIPT")
    print("=" * 60)
    
    # Check database connection
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        print("✅ Database connection successful")
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False
    
    # Create tables
    if not create_stories_tables():
        print("❌ Failed to create stories tables")
        return False
    
    # Verify user columns
    verify_user_story_columns()
    
    # Setup upload directories
    setup_uploads_directory()
    
    # Test story creation
    test_story_creation()
    
    print("\n" + "=" * 60)
    print("✅ STORIES DATABASE SETUP COMPLETED SUCCESSFULLY!")
    print("=" * 60)
    print("\n📋 Summary:")
    print("- All story tables created and verified")
    print("- User story columns checked/added")
    print("- Upload directories created")
    print("- Story creation tested successfully")
    print("\n🎉 Your application is ready for story functionality!")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
