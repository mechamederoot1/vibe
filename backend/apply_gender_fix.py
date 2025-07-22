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
        print("🔧 Corrigindo coluna gender...")
        
        # Executar ALTER TABLE
        connection.execute(text("""
            ALTER TABLE users 
            MODIFY COLUMN gender VARCHAR(20) DEFAULT NULL
        """))
        
        connection.commit()
        
        print("✅ Coluna gender corrigida para VARCHAR(20)!")
        print("🎉 Agora o cadastro deve funcionar normalmente.")
        
except Exception as e:
    print(f"❌ Erro: {e}")
    print("💡 Tente executar manualmente no MySQL:")
    print("   ALTER TABLE users MODIFY COLUMN gender VARCHAR(20) DEFAULT NULL;")
