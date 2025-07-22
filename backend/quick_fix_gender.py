#!/usr/bin/env python3
"""
Correção rápida para o problema da coluna gender
"""

import mysql.connector
import os
from dotenv import load_dotenv

load_dotenv()

try:
    # Conectar ao banco
    connection = mysql.connector.connect(
        host=os.getenv('DB_HOST', 'localhost'),
        port=int(os.getenv('DB_PORT', 3306)),
        user=os.getenv('DB_USER', 'vibe_user'),
        password=os.getenv('DB_PASSWORD', 'Dashwoodi@1995'),
        database=os.getenv('DB_NAME', 'vibe_social'),
        charset='utf8mb4'
    )
    
    cursor = connection.cursor()
    
    # Corrigir a coluna gender
    print("🔧 Corrigindo coluna gender...")
    cursor.execute("""
        ALTER TABLE users 
        MODIFY COLUMN gender ENUM('male', 'female', 'other', 'prefer_not_to_say') 
        DEFAULT NULL
    """)
    
    connection.commit()
    print("✅ Coluna gender corrigida com sucesso!")
    
    # Verificar a correção
    cursor.execute("SHOW COLUMNS FROM users LIKE 'gender'")
    result = cursor.fetchone()
    print(f"📋 Nova definição: {result[1]}")
    
    cursor.close()
    connection.close()
    
    print("\n🎉 Problema resolvido! Agora você pode criar contas normalmente.")
    
except Exception as e:
    print(f"❌ Erro: {e}")
