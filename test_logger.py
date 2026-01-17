"""
Script de teste para verificar o sistema de logging.
"""

import sys
from pathlib import Path

# Adicionar diretório raiz ao path
sys.path.insert(0, str(Path(__file__).parent))

from extraction.logger import ExtractionLogger, load_extraction_history
import time

def test_logger():
    """Testa o sistema de logging."""
    print("🧪 Testando sistema de logging...\n")
    
    # Criar logger de teste
    logger = ExtractionLogger("TesteLog", 2026)
    
    # Simular processamento
    logger.info("Iniciando teste de logging")
    
    # Simular arquivos
    for i in range(3):
        filename = f"teste_{i+1}.xlsx"
        logger.log_file_start(filename, 1.5)
        time.sleep(0.1)
        
        if i == 1:
            # Simular erro em um arquivo
            logger.log_file_error(filename, "Erro de teste", 0.1)
        else:
            # Simular sucesso
            logger.log_file_success(filename, 1000 * (i+1), 0.1)
    
    # Adicionar warnings
    logger.warning("Este é um aviso de teste")
    
    # Finalizar
    logger.finalize(status="parcial")
    
    print("\n✅ Logger finalizado!")
    print(f"📄 Log salvo em: {logger.log_file}")
    print(f"📊 Histórico salvo em: {logger.history_file}")
    
    # Verificar se foi salvo
    if logger.log_file.exists():
        print("\n📝 Conteúdo do log:")
        with open(logger.log_file, 'r', encoding='utf-8') as f:
            print(f.read())
    
    # Verificar histórico
    history = load_extraction_history()
    if history:
        print(f"\n📚 Histórico contém {len(history)} sessões")
        ultima = history[-1]
        print(f"   Última sessão: {ultima['session_id']}")
        print(f"   Status: {ultima['status']}")
        print(f"   Arquivos: {ultima['arquivos_sucesso']}/{ultima['total_arquivos']}")
    
    print("\n🎉 Teste concluído com sucesso!")

if __name__ == "__main__":
    test_logger()
