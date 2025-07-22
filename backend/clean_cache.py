#!/usr/bin/env python3
"""
Script para limpar cache Python e arquivos temporários
"""
import os
import shutil
import sys

def clean_pycache():
    """Limpar todos os arquivos __pycache__"""
    print("🧹 Limpando cache Python...")
    
    removed_count = 0
    for root, dirs, files in os.walk('.'):
        if '__pycache__' in dirs:
            pycache_path = os.path.join(root, '__pycache__')
            try:
                shutil.rmtree(pycache_path)
                print(f"✅ Removido: {pycache_path}")
                removed_count += 1
            except Exception as e:
                print(f"⚠️ Erro ao remover {pycache_path}: {e}")
    
    print(f"\n🎉 Limpeza concluída! {removed_count} diretórios __pycache__ removidos")
    return True

if __name__ == "__main__":
    clean_pycache()
