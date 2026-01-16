"""
Teste de debug - verificar conversão de valores.
"""

import sys
import pandas as pd
from pathlib import Path

# Adicionar ao path
sys.path.insert(0, str(Path(__file__).parent))

from extraction.extracao import read_monthly_excel, convert_br_column

print("=" * 70)
print("🔍 TESTE DE CONVERSÃO DE VALORES")
print("=" * 70)

# Arquivo de teste
test_file = Path("data_raw/Goiana/2025/Movimento Fiscal - Entrada e Saída - 114 - Goiana - 2025-01.xlsx")

if test_file.exists():
    print(f"\n📁 Processando: {test_file.name}")
    
    # Ler arquivo
    df, ano = read_monthly_excel(test_file)
    
    print(f"\n📊 Total de linhas: {len(df):,}")
    print(f"📋 Colunas: {len(df.columns)}")
    
    # Verificar coluna VALOR_ICMS
    if 'valor_icms' in df.columns:
        print("\n💰 Análise da coluna VALOR_ICMS:")
        print(f"   Tipo de dados: {df['valor_icms'].dtype}")
        print(f"   Valores nulos: {df['valor_icms'].isna().sum():,}")
        print(f"   Valores únicos: {df['valor_icms'].nunique():,}")
        
        # Total
        total = df['valor_icms'].sum()
        print(f"\n   📈 TOTAL VALOR_ICMS: {total:,.2f}")
        print(f"   📈 Em milhões: {total / 1_000_000:,.2f}M")
        print(f"   📈 Em bilhões: {total / 1_000_000_000:,.2f}B")
        
        # Primeiros valores
        print(f"\n   🔍 Primeiros 10 valores:")
        for i, val in enumerate(df['valor_icms'].head(10), 1):
            print(f"      {i}. {val:,.2f}")
        
        # Estatísticas
        print(f"\n   📊 Estatísticas:")
        print(f"      Média: {df['valor_icms'].mean():,.2f}")
        print(f"      Mediana: {df['valor_icms'].median():,.2f}")
        print(f"      Mínimo: {df['valor_icms'].min():,.2f}")
        print(f"      Máximo: {df['valor_icms'].max():,.2f}")
        
        # Verificar se há valores muito altos (possível erro de conversão)
        valores_altos = df[df['valor_icms'] > 1_000_000]['valor_icms']
        if len(valores_altos) > 0:
            print(f"\n   ⚠️ {len(valores_altos):,} valores acima de 1 milhão encontrados!")
            print(f"      Exemplos:")
            for i, val in enumerate(valores_altos.head(5), 1):
                print(f"         {i}. {val:,.2f}")
    
    # Verificar data_fiscal
    if 'data_fiscal' in df.columns:
        print(f"\n📅 Análise de DATA_FISCAL:")
        print(f"   Data mínima: {df['data_fiscal'].min()}")
        print(f"   Data máxima: {df['data_fiscal'].max()}")
        
        # Agrupar por mês
        df_mensal = df.groupby(df['data_fiscal'].dt.to_period('M'))['valor_icms'].sum()
        print(f"\n   📊 Total por mês:")
        for mes, valor in df_mensal.items():
            print(f"      {mes}: R$ {valor:,.2f} ({valor / 1_000_000:,.2f}M)")
    
    print("\n" + "=" * 70)
    
    # Testar conversão direta
    print("\n🧪 TESTE DE CONVERSÃO BR → US:")
    
    teste_valores = pd.Series([
        "478.991.324,28",
        "1.234,56",
        "100,00",
        "1.000.000,00"
    ])
    
    print("   Valores de teste (formato BR):")
    for i, val in enumerate(teste_valores, 1):
        print(f"      {i}. {val}")
    
    convertidos = convert_br_column(teste_valores)
    
    print("\n   Valores convertidos (float):")
    for i, val in enumerate(convertidos, 1):
        print(f"      {i}. {val:,.2f}")
    
    print("\n" + "=" * 70)
    
else:
    print(f"❌ Arquivo não encontrado: {test_file}")
