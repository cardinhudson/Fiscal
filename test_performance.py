"""
Script de teste de performance da extração.
Mede o tempo de leitura e processamento.
"""

import sys
import time
from pathlib import Path

# Adicionar ao path
sys.path.insert(0, str(Path(__file__).parent))

from extraction.extracao import read_monthly_excel

# Arquivo de teste
test_file = Path("data_raw/Goiana/2025/Movimento Fiscal - Entrada e Saída - 114 - Goiana - 2025-01.xlsx")

if test_file.exists():
    print("=" * 60)
    print("🧪 TESTE DE PERFORMANCE - EXTRAÇÃO")
    print("=" * 60)
    print(f"\n📁 Arquivo: {test_file.name}")
    print(f"📏 Tamanho: {test_file.stat().st_size / 1024 / 1024:.2f} MB")
    
    # Teste de leitura
    print("\n⏱️ Iniciando leitura...")
    start = time.time()
    
    df, ano = read_monthly_excel(test_file)
    
    end = time.time()
    tempo_leitura = end - start
    
    print(f"✅ Leitura concluída em {tempo_leitura:.2f} segundos")
    print(f"📊 Linhas lidas: {len(df):,}")
    print(f"📋 Colunas lidas: {len(df.columns)}")
    print(f"📅 Ano detectado: {ano}")
    print(f"\n🏷️ Colunas presentes:")
    for col in df.columns:
        print(f"   - {col}")
    
    # Cálculo de performance
    linhas_por_segundo = len(df) / tempo_leitura
    mb_por_segundo = (test_file.stat().st_size / 1024 / 1024) / tempo_leitura
    
    print(f"\n📈 Performance:")
    print(f"   - {linhas_por_segundo:,.0f} linhas/segundo")
    print(f"   - {mb_por_segundo:.2f} MB/segundo")
    
    # Análise de memória
    memoria_df = df.memory_usage(deep=True).sum() / 1024 / 1024
    print(f"\n💾 Uso de memória: {memoria_df:.2f} MB")
    
    print("\n" + "=" * 60)
    
    if len(df.columns) == 17:
        print("✅ CORRETO: 17 colunas essenciais carregadas")
    else:
        print(f"⚠️ ATENÇÃO: {len(df.columns)} colunas (esperado 17)")
    
    if tempo_leitura < 5:
        print("✅ RÁPIDO: Tempo de leitura < 5 segundos")
    elif tempo_leitura < 10:
        print("⚠️ MÉDIO: Tempo de leitura entre 5-10 segundos")
    else:
        print("❌ LENTO: Tempo de leitura > 10 segundos")
    
    print("=" * 60)
    
else:
    print(f"❌ Arquivo não encontrado: {test_file}")
