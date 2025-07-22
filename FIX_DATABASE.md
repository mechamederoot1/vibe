# Database Fix Instructions

## Problem
The backend is failing because the `users` table is missing the `display_id` column that the code expects.

## Solution
Run one of these commands in the backend directory:

### Option 1: Run the existing maintenance script
```bash
cd backend
python maintenance/add_display_id.py
```

### Option 2: Recreate the database structure (if you don't mind losing existing data)
```bash
cd backend
python create_database_structure.py
```

### Option 3: Manual SQL fix (if you prefer direct database access)
```sql
USE vibe;
ALTER TABLE users ADD COLUMN display_id VARCHAR(20) UNIQUE AFTER id;
CREATE INDEX idx_display_id ON users (display_id);
```

## After fixing
1. Restart the backend server
2. The backend should now start without errors and create sample data successfully

## Expected output after fix
```
🎉 Banco de dados MySQL inicializado com sucesso!
✅ Sample data created successfully
```

The frontend should then be able to connect to the backend properly.
