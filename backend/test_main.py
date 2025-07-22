#!/usr/bin/env python3
"""
Script simples para testar se o main.py está funcionando
"""
import subprocess
import sys
import time

def test_main():
    """Testar se main.py inicia sem erros críticos"""
    print("🧪 Testando main.py...")
    print("=" * 40)
    
    try:
        # Executar main.py e capturar output
        process = subprocess.Popen([
            sys.executable, "main.py"
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        
        # Aguardar alguns segundos para inicialização
        time.sleep(3)
        
        # Verificar se ainda está rodando
        if process.poll() is None:
            print("✅ main.py iniciou com sucesso!")
            print("✅ Servidor está rodando")
            
            # Terminar processo
            process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
            
            return True
        else:
            # Processo terminou, capturar erros
            stdout, stderr = process.communicate()
            print("❌ main.py falhou ao iniciar")
            print("\nSTDOUT:")
            print(stdout)
            print("\nSTDERR:")
            print(stderr)
            return False
            
    except Exception as e:
        print(f"💥 Erro ao testar: {e}")
        return False

if __name__ == "__main__":
    success = test_main()
    if success:
        print("\n🎉 main.py está funcionando corretamente!")
        print("Execute: python main.py")
    else:
        print("\n❌ main.py tem problemas")
