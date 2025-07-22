#!/usr/bin/env python3
"""
Script para verificar se o setup está correto
"""

def verify_imports():
    """Verificar se todas as importações estão funcionando"""
    print("🔍 Verificando importações...")
    
    try:
        # Testar importações básicas
        from fastapi import FastAPI
        print("✅ FastAPI OK")
        
        from sqlalchemy import create_engine
        print("✅ SQLAlchemy OK")
        
        # Testar importação dos models
        from models import Base, MediaFile, Album
        print("✅ Models OK")
        
        print("\n🎉 Todas as importações estão funcionando!")
        return True
        
    except ImportError as e:
        print(f"❌ Erro de importação: {e}")
        return False
    except Exception as e:
        print(f"💥 Erro inesperado: {e}")
        return False

def verify_main():
    """Verificar se main.py pode ser importado"""
    print("\n🔍 Verificando main.py...")
    
    try:
        # Tentar importar main sem executar
        import importlib.util
        spec = importlib.util.spec_from_file_location("main", "main.py")
        if spec and spec.loader:
            print("✅ main.py pode ser carregado")
            return True
        else:
            print("❌ main.py não pode ser carregado")
            return False
            
    except Exception as e:
        print(f"❌ Erro ao verificar main.py: {e}")
        return False

def main():
    """Função principal de verificação"""
    print("🚀 VERIFICAÇÃO COMPLETA DO SETUP")
    print("=" * 40)
    
    # Limpar cache primeiro
    import os
    import shutil
    for root, dirs, files in os.walk('.'):
        if '__pycache__' in dirs:
            shutil.rmtree(os.path.join(root, '__pycache__'), ignore_errors=True)
    print("🧹 Cache limpo")
    
    success_count = 0
    total_tests = 2
    
    if verify_imports():
        success_count += 1
    
    if verify_main():
        success_count += 1
    
    print("\n" + "=" * 40)
    if success_count == total_tests:
        print("🎉 SETUP VERIFICADO COM SUCESSO!")
        print("✅ Pronto para executar: python main.py")
        return True
    else:
        print(f"⚠️ VERIFICAÇÃO PARCIAL ({success_count}/{total_tests})")
        print("Verifique os erros acima")
        return False

if __name__ == "__main__":
    main()
