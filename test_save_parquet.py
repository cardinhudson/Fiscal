"""
Teste focado: ler um Excel e salvar direto no Parquet
"""
from pathlib import Path
from extraction.extracao import read_monthly_excel, save_to_parquet

# Arquivo de janeiro
excel_path = Path("data_raw/Goiana/2025/Movimento Fiscal - Entrada e Saída - 114 - Goiana - 2025-01.xlsx")

print("🔍 TESTE: Ler Excel e Salvar Parquet")
print("=" * 80)

# Ler
print("\n📖 Lendo Excel...")
df, ano = read_monthly_excel(excel_path)
print(f"✅ Lido: {len(df):,} registros")
print(f"   Colunas: {list(df.columns)}")

# Salvar
print(f"\n💾 Salvando em Parquet (modo='replace')...")
parquet_path = save_to_parquet(df, "Goiana", ano, mode='replace')
print(f"✅ Salvo em: {parquet_path}")

# Ler de volta
print(f"\n📖 Lendo Parquet de volta...")
import pandas as pd
df_parquet = pd.read_parquet(parquet_path)
print(f"✅ Registros no Parquet: {len(df_parquet):,}")

# Comparar
print(f"\n🔍 COMPARAÇÃO:")
print(f"   Excel:   {len(df):,}")
print(f"   Parquet: {len(df_parquet):,}")
print(f"   Diferença: {len(df) - len(df_parquet):,}")

if len(df) != len(df_parquet):
    print(f"\n⚠️ REGISTROS PERDIDOS NO SALVAMENTO!")
else:
    print(f"\n✅ Nenhum registro perdido!")
