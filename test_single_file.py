"""
Teste de extração de um único arquivo
"""
import sys
from pathlib import Path
import pandas as pd

# Adicionar diretório raiz ao path
sys.path.insert(0, str(Path(__file__).parent))

from extraction.extracao import (
    load_codigos_mastersaf,
    to_snake_case,
    convert_br_column,
    remove_accents
)

# Caminho do arquivo de teste
planta = "Goiana"
ano = 2025
arquivo = "Movimento Fiscal - Entrada e Saída - 114 - Goiana - 2025-01.xlsx"

base_path = Path(__file__).parent
raw_path = base_path / "data_raw" / planta / str(ano)
file_path = raw_path / arquivo

print(f"Testando arquivo: {file_path}")
print(f"Arquivo existe: {file_path.exists()}")
print("=" * 80)

try:
    # Carregar tabela de códigos
    print("\n1. Carregando tabela de códigos Mastersaf...")
    df_codigos = load_codigos_mastersaf()
    if df_codigos is not None:
        print(f"   ✅ {len(df_codigos)} códigos carregados")
        print(f"   Colunas originais: {df_codigos.columns.tolist()}")
        
        # Converter para snake_case
        df_codigos.columns = [to_snake_case(col) for col in df_codigos.columns]
        print(f"   Colunas snake_case: {df_codigos.columns.tolist()}")
        
        # Verificar se resumo_de_operacao existe
        if 'resumo_de_operacao' in df_codigos.columns:
            print(f"   ✅ Coluna 'resumo_de_operacao' existe!")
            print(f"   Valores únicos: {df_codigos['resumo_de_operacao'].unique()[:10]}")
        else:
            print(f"   ❌ Coluna 'resumo_de_operacao' NÃO existe")
            print(f"   Colunas disponíveis: {[c for c in df_codigos.columns if 'resumo' in c or 'operacao' in c]}")
    else:
        print("   ❌ Não foi possível carregar tabela de códigos")
    
    # Carregar arquivo Excel
    print(f"\n2. Lendo arquivo Excel...")
    df = pd.read_excel(file_path)
    print(f"   ✅ {len(df)} linhas lidas")
    print(f"   Colunas: {df.columns.tolist()[:10]}")
    
    # Converter colunas para snake_case
    df.columns = [to_snake_case(col) for col in df.columns]
    print(f"   Colunas snake_case: {df.columns.tolist()[:10]}")
    
    # Verificar se CFOP existe
    if 'cfop' in df.columns:
        print(f"   ✅ Coluna CFOP existe")
        print(f"   Valores únicos CFOP: {df['cfop'].unique()[:10]}")
    
    # Fazer merge
    print(f"\n3. Testando merge...")
    if df_codigos is not None and 'cfop' in df.columns:
        # Converter CFOP para int em ambos DataFrames
        print(f"   Convertendo CFOP para int...")
        print(f"   Antes: df={df['cfop'].dtype}, codigos={df_codigos['cfop'].dtype}")
        print(f"   Amostra df: {df['cfop'].head()}")
        print(f"   Amostra codigos: {df_codigos['cfop'].head()}")
        
        df['cfop'] = pd.to_numeric(df['cfop'], errors='coerce').fillna(0).astype(int)
        df_codigos['cfop'] = pd.to_numeric(df_codigos['cfop'], errors='coerce').fillna(0).astype(int)
        
        print(f"   Depois: df={df['cfop'].dtype}, codigos={df_codigos['cfop'].dtype}")
        print(f"   Amostra df: {df['cfop'].head()}")
        print(f"   Amostra codigos: {df_codigos['cfop'].head()}")
        
        colunas_merge = ['cfop', 'cod_natureza_op', 'descricao_natureza_op']
        if 'resumo_de_operacao' in df_codigos.columns:
            colunas_merge.append('resumo_de_operacao')
            print(f"   ✅ Incluindo 'resumo_de_operacao' no merge")
        else:
            print(f"   ⚠️ 'resumo_de_operacao' não será incluído no merge")
        
        print(f"   Colunas do merge: {colunas_merge}")
        
        registros_antes = len(df)
        df_resultado = df.merge(
            df_codigos[colunas_merge],
            on='cfop',
            how='left'
        )
        print(f"   ✅ Merge concluído: {registros_antes} → {len(df_resultado)} registros")
        print(f"   Colunas após merge: {df_resultado.columns.tolist()}")
        
        # Verificar colunas criadas
        print(f"\n4. Verificando colunas criadas no merge:")
        for col in ['cod_natureza_op', 'descricao_natureza_op', 'resumo_de_operacao']:
            if col in df_resultado.columns:
                nulos = df_resultado[col].isna().sum()
                print(f"   ✅ {col}: {len(df_resultado)-nulos} valores, {nulos} nulos")
                if nulos < len(df_resultado):
                    print(f"      Valores únicos: {df_resultado[col].dropna().unique()[:5]}")
            else:
                print(f"   ❌ {col}: NÃO existe")
        
except Exception as e:
    print(f"\n❌ ERRO: {str(e)}")
    import traceback
    traceback.print_exc()
