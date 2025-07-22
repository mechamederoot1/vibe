# Database Schema Fix

## Problem

The application was experiencing a database schema error: `no such column: users.username`. This was caused by conflicting User model definitions between `main.py` and `models/user.py`, which resulted in the database being created with an incomplete schema.

## Root Cause

1. **Multiple User model definitions**:
   - `main.py` contained a complete User model with all fields including `username`
   - `models/user.py` contained an incomplete User model missing many fields
   - `models/notification.py` had conflicting Notification model

2. **Different Base classes**:
   - `main.py` used `DeclarativeBase`
   - `models/base.py` used `declarative_base()`

3. **Schema mismatch**: The database was created using the incomplete model, but the application code expected the complete model.

## Solution Applied

### 1. Fixed Model Conflicts

- **Updated `models/user.py`**: Now imports User from main.py instead of defining its own
- **Updated `models/notification.py`**: Now imports Notification from main.py instead of defining its own
- **Removed database files**: Deleted `test.db` and `vibe.db` to force recreation with correct schema

### 2. Files Modified

- `backend/models/user.py` - Now imports from main.py
- `backend/models/notification.py` - Now imports from main.py
- Removed old database files

### 3. Additional Scripts Created

- `recreate_db.py` - Script to manually remove database files
- `start_clean.py` - Clean startup script with proper initialization
- `fix_database.py` - Database testing script
- `test_db.py` - Schema verification script

## How to Start the Backend

### Option 1: Normal startup (recommended)

```bash
cd backend
python main.py
```

### Option 2: Clean startup with explicit initialization

```bash
cd backend
python start_clean.py
```

### Option 3: Using the run script

```bash
cd backend
python run.py
```

## Verification

When you start the backend, you should see:

1. ✅ Database tables created successfully
2. ✅ Sample data initialized
3. ✅ Server running on port 8000
4. No more "no such column" errors

## Notes

- The database will be automatically recreated with the correct schema on first run
- Sample user will be created: email `joao@exemplo.com`, password `123456`
- All model definitions are now centralized in `main.py`
- The models directory now only contains import redirects to avoid conflicts
