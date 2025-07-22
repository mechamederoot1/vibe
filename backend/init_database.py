#!/usr/bin/env python3
"""
Script para inicializar o banco de dados MySQL com as tabelas necessárias
"""
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from core.database import Base
from core.config import get_database_url
import os
from dotenv import load_dotenv

# Carrega variáveis de ambiente
load_dotenv()

def init_database():
    """Inicializa o banco de dados com as tabelas necessárias"""
    try:
        print("🔍 Inicializando banco de dados...")
        
        # Conectar ao MySQL (sem especificar banco)
        db_host = os.getenv("DB_HOST", "127.0.0.1")
        db_port = os.getenv("DB_PORT", "3306")
        db_user = os.getenv("DB_USER", "root")
        db_password = os.getenv("DB_PASSWORD", "Evo@000#!")
        db_name = os.getenv("DB_NAME", "vibe")
        
        # URL encode da senha para caracteres especiais
        from urllib.parse import quote_plus
        encoded_password = quote_plus(db_password)
        
        # Conectar sem especificar banco primeiro
        root_url = f"mysql+pymysql://{db_user}:{encoded_password}@{db_host}:{db_port}/"
        root_engine = create_engine(root_url)
        
        # Criar banco se não existir
        with root_engine.connect() as conn:
            conn.execute(text(f"CREATE DATABASE IF NOT EXISTS {db_name}"))
            print(f"✅ Banco de dados '{db_name}' criado/verificado!")
        
        root_engine.dispose()
        
        # Agora conectar ao banco específico
        database_url = get_database_url()
        engine = create_engine(database_url)
        
        # Criar todas as tabelas
        Base.metadata.create_all(bind=engine)
        print("✅ Todas as tabelas foram criadas com sucesso!")
        
        # Verificar tabelas criadas
        with engine.connect() as conn:
            result = conn.execute(text("SHOW TABLES"))
            tables = [row[0] for row in result]
            print(f"📋 Tabelas criadas: {', '.join(tables)}")
        
        engine.dispose()
        print("🎉 Inicialização do banco de dados concluída!")
        
    except Exception as e:
        print(f"❌ Erro na inicialização: {e}")
        return False
    
    return True

if __name__ == "__main__":
    success = init_database()
    if not success:
        exit(1)
