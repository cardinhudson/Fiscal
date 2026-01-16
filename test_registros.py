"""
Script para debugar diferença de registros entre Excel e Parquet
"""
import pandas as pd
from pathlib import Path

# Caminho do arquivo de janeiro
excel_path = Path("data_raw/Goiana/2025/Movimento Fiscal - Entrada e Saída - 114 - Goiana - 2025-01.xlsx")
parquet_path = Path("data_parquet/Goiana/2025/fiscal_Goiana_2025.parquet")

print("=" * 80)
print("🔍 ANÁLISE DE REGISTROS - Janeiro 2025")
print("=" * 80)

# 1. Contar linhas no Excel (SEM filtros)
print("\n📊 LENDO EXCEL BRUTO (todas as colunas, sem filtros)...")
try:
    df_excel_full = pd.read_excel(excel_path, engine='calamine')
    print(f"✅ Total de registros no Excel (BRUTO): {len(df_excel_full):,}")
    print(f"   Colunas: {len(df_excel_full.columns)}")
except Exception as e:
    print(f"❌ Erro ao ler Excel bruto: {e}")
    df_excel_full = None

# 2. Ler com o método do sistema (apenas 17 colunas)
print("\n📊 LENDO EXCEL COM MÉTODO DO SISTEMA (17 colunas essenciais)...")
try:
    from extraction.extracao import read_monthly_excel
    df_sistema, ano = read_monthly_excel(excel_path)
    print(f"✅ Registros após read_monthly_excel(): {len(df_sistema):,}")
    print(f"   Ano detectado: {ano}")
    print(f"   Colunas: {list(df_sistema.columns)}")
    
    # Verificar se há NaN em colunas críticas
    print(f"\n🔍 Verificando valores NaN:")
    for col in df_sistema.columns:
        nan_count = df_sistema[col].isna().sum()
        if nan_count > 0:
            print(f"   - {col}: {nan_count:,} valores NaN ({nan_count/len(df_sistema)*100:.1f}%)")
    
except Exception as e:
    print(f"❌ Erro ao ler com método do sistema: {e}")
    df_sistema = None

# 3. Ler Parquet (se existir)
print("\n📊 LENDO PARQUET...")
if parquet_path.exists():
    df_parquet = pd.read_parquet(parquet_path)
    print(f"✅ Registros no Parquet: {len(df_parquet):,}")
    
    # Filtrar apenas Janeiro
    df_janeiro = df_parquet[df_parquet['data_fiscal'].dt.month == 1]
    print(f"✅ Registros de Janeiro no Parquet: {len(df_janeiro):,}")
else:
    print(f"⚠️ Parquet não existe ainda")
    df_parquet = None

# 4. ANÁLISE DE DIFERENÇAS
print("\n" + "=" * 80)
print("📊 RESUMO DA ANÁLISE")
print("=" * 80)

if df_excel_full is not None and df_sistema is not None:
    diff = len(df_excel_full) - len(df_sistema)
    percent_diff = (diff / len(df_excel_full)) * 100
    print(f"\n🔴 DIFERENÇA: {diff:,} registros perdidos ({percent_diff:.2f}%)")
    print(f"   Excel bruto:  {len(df_excel_full):,}")
    print(f"   Após sistema: {len(df_sistema):,}")
    
    if diff > 0:
        print(f"\n⚠️ POSSÍVEIS CAUSAS:")
        print(f"   1. Linhas com todas as 17 colunas essenciais vazias")
        print(f"   2. Linhas filtradas por algum critério não documentado")
        print(f"   3. Erro no usecols do pandas")
        
        # Testar: ler Excel COM usecols e comparar
        print(f"\n🧪 TESTE: Lendo Excel com usecols (17 colunas)...")
        colunas_essenciais = [
            'DATA_FISCAL', 'ENTRADA_SAIDA', 'CODIGO_PRODUTO', 'DESCRICAO',
            'RAZAO_SOCIAL', 'CFOP', 'COD_NATUREZA_OP', 'DESCRICAO_NATUREZA_OP',
            'ALIQ_ICMS', 'BASE_ICMS_1', 'VALOR_ICMS', 'CST_ICMS',
            'NUM_CONTROLE_DOCTO', 'UF', 'MUNICIPIO', 'NUMERO_NF', 'QUANTIDADE'
        ]
        try:
            df_usecols = pd.read_excel(excel_path, engine='calamine', usecols=colunas_essenciais)
            print(f"   Registros com usecols: {len(df_usecols):,}")
            
            if len(df_usecols) == len(df_excel_full):
                print(f"   ✅ usecols preserva todos os registros")
            else:
                print(f"   🔴 usecols remove {len(df_excel_full) - len(df_usecols):,} registros")
                print(f"   ⚠️ Isso indica linhas onde TODAS as 17 colunas estão vazias")
        except Exception as e:
            print(f"   ❌ Erro: {e}")

print("\n" + "=" * 80)
