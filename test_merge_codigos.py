"""
Teste para validar o merge com a tabela de códigos Mastersaf
"""
import pandas as pd
from pathlib import Path
from extraction.extracao import load_codigos_mastersaf, to_snake_case

def test_merge_codigos():
    """Testa o carregamento e merge da tabela de códigos"""
    
    print("=" * 60)
    print("TESTE: Merge com Tabela de Códigos Mastersaf")
    print("=" * 60)
    
    # 1. Verificar se o arquivo existe
    base_path = Path.cwd()
    codigos_path = base_path / "data_raw" / "Códigos Mastersaf e Sapiens.xlsx"
    
    print(f"\n1️⃣ Verificando arquivo de códigos...")
    print(f"   Caminho: {codigos_path}")
    
    if not codigos_path.exists():
        print(f"   ❌ ERRO: Arquivo não encontrado!")
        print(f"   Por favor, coloque o arquivo em: {codigos_path}")
        return False
    else:
        print(f"   ✅ Arquivo encontrado!")
    
    # 2. Carregar a tabela de códigos
    print(f"\n2️⃣ Carregando tabela de códigos...")
    df_codigos = load_codigos_mastersaf()
    
    if df_codigos is None:
        print(f"   ❌ ERRO: Falha ao carregar tabela de códigos")
        return False
    
    print(f"   ✅ Tabela carregada com sucesso!")
    print(f"   Registros: {len(df_codigos)}")
    print(f"   Colunas: {list(df_codigos.columns)}")
    print(f"\n   Amostra dos dados:")
    print(df_codigos.head(10).to_string(index=False))
    
    # 3. Simular um DataFrame de dados fiscais
    print(f"\n3️⃣ Simulando dados fiscais...")
    
    df_fiscal_simulado = pd.DataFrame({
        'data_fiscal': ['2025-01-01'] * 5,
        'cfop': ['5102', '1102', '5405', '6102', '9999'],  # 9999 não deve existir
        'cod_natureza_op': ['OLD_1', 'OLD_2', 'OLD_3', 'OLD_4', 'OLD_5'],
        'descricao_natureza_op': ['Descrição Antiga 1', 'Descrição Antiga 2', 'Descrição Antiga 3', 'Descrição Antiga 4', 'Descrição Antiga 5'],
        'valor_icms': [1000, 2000, 3000, 4000, 5000]
    })
    
    print(f"   DataFrame original:")
    print(df_fiscal_simulado.to_string(index=False))
    
    # 4. Fazer o merge
    print(f"\n4️⃣ Realizando merge...")
    
    # Remover colunas antigas
    df_resultado = df_fiscal_simulado.drop(columns=['cod_natureza_op', 'descricao_natureza_op'])
    
    # Preparar df_codigos para merge
    df_codigos_merge = df_codigos.copy()
    df_codigos_merge.columns = [to_snake_case(col) for col in df_codigos_merge.columns]
    
    # Merge
    registros_antes = len(df_resultado)
    df_resultado = df_resultado.merge(
        df_codigos_merge[['cfop', 'cod_natureza_op', 'descricao_natureza_op']],
        on='cfop',
        how='left'
    )
    
    print(f"   Registros antes: {registros_antes}")
    print(f"   Registros depois: {len(df_resultado)}")
    
    if len(df_resultado) != registros_antes:
        print(f"   ⚠️ AVISO: Número de registros alterou!")
    else:
        print(f"   ✅ Número de registros mantido")
    
    # 5. Verificar resultado
    print(f"\n5️⃣ Resultado do merge:")
    print(df_resultado.to_string(index=False))
    
    nao_encontrados = df_resultado['cod_natureza_op'].isna().sum()
    print(f"\n   Registros sem correspondência: {nao_encontrados}")
    
    if nao_encontrados > 0:
        print(f"   CFOPs não encontrados:")
        cfops_nao_encontrados = df_resultado[df_resultado['cod_natureza_op'].isna()]['cfop'].unique()
        for cfop in cfops_nao_encontrados:
            print(f"      - {cfop}")
    
    # 6. Validações finais
    print(f"\n6️⃣ Validações finais...")
    
    validacoes = []
    
    # Verifica se todas as colunas esperadas existem
    if 'cod_natureza_op' in df_resultado.columns:
        validacoes.append("✅ Coluna 'cod_natureza_op' presente")
    else:
        validacoes.append("❌ Coluna 'cod_natureza_op' ausente")
    
    if 'descricao_natureza_op' in df_resultado.columns:
        validacoes.append("✅ Coluna 'descricao_natureza_op' presente")
    else:
        validacoes.append("❌ Coluna 'descricao_natureza_op' ausente")
    
    # Verifica se os valores foram substituídos (não devem existir "OLD_")
    if df_resultado['cod_natureza_op'].notna().sum() > 0:
        valores_com_old = df_resultado['cod_natureza_op'].str.contains('OLD', na=False).sum()
        if valores_com_old == 0:
            validacoes.append("✅ Valores antigos substituídos corretamente")
        else:
            validacoes.append(f"❌ Ainda existem {valores_com_old} valores antigos")
    
    # Verifica se o número de registros é igual ao original
    if len(df_resultado) == len(df_fiscal_simulado):
        validacoes.append("✅ Número de registros preservado")
    else:
        validacoes.append("❌ Número de registros alterado")
    
    for validacao in validacoes:
        print(f"   {validacao}")
    
    print("\n" + "=" * 60)
    print("TESTE CONCLUÍDO")
    print("=" * 60)
    
    return all("✅" in v for v in validacoes)

if __name__ == "__main__":
    sucesso = test_merge_codigos()
    
    if sucesso:
        print("\n🎉 TODOS OS TESTES PASSARAM!")
    else:
        print("\n⚠️ ALGUNS TESTES FALHARAM - Verifique os logs acima")
