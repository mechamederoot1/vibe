#!/usr/bin/env python3
"""
Script master para configurar completamente o banco de dados da rede social
Executa criação de estrutura + sistema de qualidade de mídia
"""
import os
import sys
import subprocess
from pathlib import Path

def run_script(script_name, description):
    """Executar um script Python e capturar resultado"""
    print(f"\n🚀 Executando: {description}")
    print("=" * 60)
    
    try:
        # Executar o script
        result = subprocess.run([
            sys.executable, script_name
        ], capture_output=True, text=True, cwd=Path(__file__).parent)
        
        # Mostrar output
        if result.stdout:
            print(result.stdout)
        
        if result.stderr:
            print("⚠️ Avisos/Erros:")
            print(result.stderr)
        
        if result.returncode == 0:
            print(f"✅ {description} - CONCLUÍDO COM SUCESSO")
            return True
        else:
            print(f"❌ {description} - FALHOU")
            return False
            
    except Exception as e:
        print(f"💥 Erro ao executar {script_name}: {e}")
        return False

def main():
    """Executar setup completo do banco de dados"""
    
    print("🎯 SETUP COMPLETO DO BANCO DE DADOS DA REDE SOCIAL")
    print("=" * 60)
    print("Este script irá:")
    print("1. Criar toda a estrutura de tabelas")
    print("2. Configurar sistema de qualidade de mídia")
    print("3. Otimizar performance")
    print("4. Configurar índices e views")
    print("=" * 60)
    
    # Confirmar execução
    response = input("\n🤔 Continuar com o setup? (y/N): ").strip().lower()
    if response != 'y':
        print("⏹️ Setup cancelado pelo usuário.")
        return False
    
    success_count = 0
    total_scripts = 2
    
    # 1. Criar estrutura do banco
    if run_script("create_database_structure.py", "Criação da estrutura do banco"):
        success_count += 1
    
    # 2. Configurar sistema de mídia
    if run_script("setup_media_quality.py", "Sistema de qualidade de mídia"):
        success_count += 1
    
    # Resultado final
    print("\n" + "=" * 60)
    if success_count == total_scripts:
        print("🎉 SETUP COMPLETO REALIZADO COM SUCESSO!")
        print("=" * 60)
        print("\n✅ O que foi configurado:")
        print("📊 16 tabelas principais criadas")
        print("📸 Sistema de mídia com múltiplas qualidades")
        print("🎨 Configurações de qualidade para cada tipo")
        print("⚡ Índices de performance otimizados")
        print("👀 Views úteis para consultas")
        print("🔍 Sistema de metadados avançado")
        
        print("\n🚀 Sua rede social está pronta para:")
        print("• Upload de fotos de perfil em alta qualidade")
        print("• Fotos de capa otimizadas")
        print("• Posts com imagens/vídeos")
        print("• Stories temporários")
        print("• Sistema de comentários")
        print("• Reações estilo Facebook")
        print("• Chat privado e em grupo")
        print("• Notificações em tempo real")
        print("• Álbuns organizados")
        print("• Sistema de amizades completo")
        
        print(f"\n📋 Próximos passos:")
        print("1. Execute sua aplicação: python main.py")
        print("2. Teste o upload de imagens")
        print("3. Configure processamento de mídia se necessário")
        
        return True
    else:
        print(f"⚠️ SETUP PARCIALMENTE CONCLUÍDO ({success_count}/{total_scripts})")
        print("Verifique os erros acima e execute novamente se necessário.")
        return False

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n⏹️ Setup interrompido pelo usuário")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Erro fatal: {e}")
        sys.exit(1)
