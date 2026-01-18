"""
Script para testar a geração de CFOPs não encontrados.
"""

import sys
from pathlib import Path

# Adicionar diretório ao path
sys.path.insert(0, str(Path(__file__).parent))

print("Importando módulos...")
from app.utils.load_consolidated_data import generate_cfops_nao_encontrados_from_parquets

# Testar com ano 2025
ano = 2025
print(f"\n🔍 Gerando CFOPs não encontrados para o ano {ano}...")
print()

try:
    df = generate_cfops_nao_encontrados_from_parquets(ano)
    
    if not df.empty:
        print()
        print(f"✅ Sucesso! Total de registros: {len(df)}")
        print()
        print("📋 Colunas disponíveis:")
        print(df.columns.tolist())
        print()
        print("📊 Primeiras 5 linhas:")
        print(df.head())
    else:
        print("⚠️ Nenhum CFOP não encontrado!")
except Exception as e:
    print(f"❌ Erro: {e}")
    import traceback
    traceback.print_exc()
