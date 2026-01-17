"""
Script de teste de extração para Goiana 2025
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from extraction.extracao import process_raw_excel_to_parquet

def test_extraction():
    print("Testando extracao de Goiana 2025...\n")
    
    def progress_callback(current, total, message, step):
        print(f"[{current}%] {step}: {message}")
    
    try:
        sucesso, mensagem, registros = process_raw_excel_to_parquet(
            'Goiana',
            2025,
            mode='all',
            progress_callback=progress_callback
        )
        
        print(f"\n{'='*60}")
        print(f"Resultado: {'SUCESSO' if sucesso else 'ERRO'}")
        print(f"Mensagem: {mensagem}")
        print(f"Registros: {registros:,}")
        print(f"{'='*60}")
        
        # Verificar logs
        from extraction.logger import load_extraction_history
        history = load_extraction_history()
        if history:
            ultima = history[-1]
            print(f"\n📊 Última sessão de log:")
            print(f"   Status: {ultima['status']}")
            print(f"   Arquivos processados: {ultima['arquivos_sucesso']}/{ultima['total_arquivos']}")
            print(f"   Total de registros: {ultima['total_registros']:,}")
            if ultima['erros']:
                print(f"\n❌ Erros encontrados:")
                for erro in ultima['erros']:
                    print(f"   - {erro['message']}")
                    if 'exception_message' in erro:
                        print(f"     Exceção: {erro['exception_message']}")
        
        return sucesso
    except Exception as e:
        print(f"\n❌ ERRO CRÍTICO: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_extraction()
    sys.exit(0 if success else 1)
