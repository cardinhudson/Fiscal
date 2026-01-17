"""
Script de teste para extração de Porto Real 2025
"""
import sys
from pathlib import Path

# Adiciona o diretório raiz ao path
sys.path.insert(0, str(Path(__file__).parent))

from extraction.extracao import process_raw_excel_to_parquet

def main():
    print("\n" + "="*80)
    print("TESTE DE EXTRAÇÃO - PORTO REAL 2025")
    print("="*80 + "\n")
    
    planta = "Porto Real"
    ano = 2025
    mode = "all"  # Processar todos os arquivos
    
    print(f"Planta: {planta}")
    print(f"Ano: {ano}")
    print(f"Modo: {mode}")
    print("\n" + "-"*80 + "\n")
    
    try:
        # Executa a extração
        result = process_raw_excel_to_parquet(
            planta=planta,
            ano=ano,
            mode=mode
        )
        
        print("\n" + "="*80)
        print("RESULTADO DA EXTRAÇÃO")
        print("="*80)
        print(f"Status: {result['status']}")
        print(f"Mensagem: {result['mensagem']}")
        print(f"Arquivos processados: {result['arquivos_processados']}/{result['total_arquivos']}")
        print(f"Total de registros: {result['total_registros']:,}")
        print(f"Tempo total: {result['tempo_total']:.2f}s")
        
        if result['erros']:
            print("\nERROS:")
            for erro in result['erros']:
                print(f"  - {erro}")
        
        # Verifica o arquivo Parquet gerado
        parquet_file = Path(f"data_parquet/{planta}/{ano}/fiscal_{planta.replace(' ', '_')}_{ano}.parquet")
        if parquet_file.exists():
            import pandas as pd
            df = pd.read_parquet(parquet_file)
            print(f"\nArquivo Parquet gerado: {parquet_file}")
            print(f"  - Tamanho: {parquet_file.stat().st_size / (1024*1024):.2f} MB")
            print(f"  - Registros no Parquet: {len(df):,}")
            print(f"  - Colunas: {len(df.columns)}")
            print(f"  - Período: {df['Data'].min()} a {df['Data'].max()}")
        
        print("="*80 + "\n")
        
    except Exception as e:
        print(f"\nERRO CRÍTICO: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
