#!/usr/bin/env python3

# Importar a configuração do banco do main.py
import sys
import os
sys.path.append(os.path.dirname(__file__))

from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()

# Configurar engine do banco
DATABASE_URL = f"mysql+pymysql://{os.getenv('DB_USER', 'vibe_user')}:{os.getenv('DB_PASSWORD', 'Dashwoodi@1995')}@{os.getenv('DB_HOST', 'localhost')}:{os.getenv('DB_PORT', 3306)}/{os.getenv('DB_NAME', 'vibe_social')}"

try:
    engine = create_engine(DATABASE_URL)
    
    with engine.connect() as connection:
        print("🔧 Corrigindo estrutura da tabela users...")
        
        # Verificar se a coluna gender existe e corrigir
        try:
            connection.execute(text("""
                ALTER TABLE users 
                MODIFY COLUMN gender VARCHAR(50) DEFAULT NULL
            """))
            print("✅ Coluna gender corrigida para VARCHAR(50)!")
        except Exception as e:
            print(f"⚠️ Aviso gender: {e}")
        
        # Verificar se a coluna username existe
        result = connection.execute(text("""
            SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS 
            WHERE TABLE_NAME = 'users' AND COLUMN_NAME = 'username'
        """)).fetchone()
        
        if not result:
            print("🔧 Adicionando coluna username...")
            connection.execute(text("""
                ALTER TABLE users 
                ADD COLUMN username VARCHAR(50) UNIQUE AFTER email
            """))
            print("✅ Coluna username adicionada!")
        else:
            print("✅ Coluna username já existe!")
        
        # Verificar se a coluna display_id existe
        result = connection.execute(text("""
            SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS 
            WHERE TABLE_NAME = 'users' AND COLUMN_NAME = 'display_id'
        """)).fetchone()
        
        if not result:
            print("🔧 Adicionando coluna display_id...")
            connection.execute(text("""
                ALTER TABLE users 
                ADD COLUMN display_id VARCHAR(20) UNIQUE AFTER id
            """))
            print("✅ Coluna display_id adicionada!")
        else:
            print("✅ Coluna display_id já existe!")
        
        # Verificar se a coluna is_verified existe
        result = connection.execute(text("""
            SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS 
            WHERE TABLE_NAME = 'users' AND COLUMN_NAME = 'is_verified'
        """)).fetchone()
        
        if not result:
            print("🔧 Adicionando coluna is_verified...")
            connection.execute(text("""
                ALTER TABLE users 
                ADD COLUMN is_verified BOOLEAN DEFAULT FALSE AFTER is_active
            """))
            print("✅ Coluna is_verified adicionada!")
        else:
            print("✅ Coluna is_verified já existe!")
        
        connection.commit()
        print("🎉 Todas as correções aplicadas com sucesso!")
        
except Exception as e:
    print(f"❌ Erro: {e}")
    print("💡 Tente executar manualmente no MySQL:")
    print("   ALTER TABLE users MODIFY COLUMN gender VARCHAR(50) DEFAULT NULL;")
    print("   ALTER TABLE users ADD COLUMN username VARCHAR(50) UNIQUE AFTER email;")
    print("   ALTER TABLE users ADD COLUMN display_id VARCHAR(20) UNIQUE AFTER id;")
    print("   ALTER TABLE users ADD COLUMN is_verified BOOLEAN DEFAULT FALSE AFTER is_active;")