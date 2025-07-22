#!/usr/bin/env python3
"""
Migração para adicionar campos is_profile_update e is_cover_update na tabela posts
"""
import os
from sqlalchemy import create_engine, text
from urllib.parse import quote_plus
from dotenv import load_dotenv

# Carrega variáveis de ambiente
load_dotenv()

def get_database_url():
    """Create database URL from environment variables"""
    database_url = os.getenv("DATABASE_URL")
    if database_url:
        return database_url

    db_host = os.getenv("DB_HOST", "localhost")
    db_port = os.getenv("DB_PORT", "3306")
    db_user = os.getenv("DB_USER", "root")
    db_password = os.getenv("DB_PASSWORD", "Evo@000#!")
    db_name = os.getenv("DB_NAME", "vibe")

    encoded_password = quote_plus(db_password)
    return f"mysql+pymysql://{db_user}:{encoded_password}@{db_host}:{db_port}/{db_name}"

def migrate_profile_fields():
    """Add is_profile_update and is_cover_update columns to posts table"""
    
    print("🔧 Executando migração para adicionar campos de atualização de perfil...")
    
    engine = create_engine(get_database_url())
    
    with engine.connect() as conn:
        try:
            # Verificar se as colunas já existem
            result = conn.execute(text("SHOW COLUMNS FROM posts LIKE 'is_profile_update'"))
            if result.fetchone():
                print('✅ Coluna is_profile_update já existe')
            else:
                conn.execute(text('ALTER TABLE posts ADD COLUMN is_profile_update BOOLEAN DEFAULT FALSE'))
                conn.commit()
                print('✅ Adicionada coluna is_profile_update')
            
            result = conn.execute(text("SHOW COLUMNS FROM posts LIKE 'is_cover_update'"))
            if result.fetchone():
                print('✅ Coluna is_cover_update já existe')
            else:
                conn.execute(text('ALTER TABLE posts ADD COLUMN is_cover_update BOOLEAN DEFAULT FALSE'))
                conn.commit()
                print('✅ Adicionada coluna is_cover_update')

            print('🎉 Migração concluída com sucesso!')
            
        except Exception as e:
            print(f'❌ Erro durante a migração: {e}')
            raise

if __name__ == "__main__":
    migrate_profile_fields()
