"""
Módulo para carregar dados consolidados de todas as plantas.
"""

import pandas as pd
from pathlib import Path


def get_base_path():
    """Retorna o caminho base do projeto."""
    return Path.cwd()


def get_available_anos_consolidated():
    """
    Retorna lista de anos disponíveis na consolidação.
    
    Returns:
        list: Lista de anos com dados consolidados
    """
    base_path = get_base_path()
    consolidated_path = base_path / "data_parquet" / "Plantas"
    
    if not consolidated_path.exists():
        return []
    
    anos = []
    for ano_dir in consolidated_path.iterdir():
        if ano_dir.is_dir():
            try:
                anos.append(int(ano_dir.name))
            except ValueError:
                continue
    
    return sorted(anos)


def load_consolidated_mensal(ano: int):
    """
    Carrega dados mensais consolidados de todas as plantas.
    
    Args:
        ano: Ano fiscal
        
    Returns:
        DataFrame com colunas: data_fiscal, mes, valor_icms, base_icms_1, planta, ano
    """
    base_path = get_base_path()
    mensal_file = base_path / "data_parquet" / "Plantas" / str(ano) / "mensal.parquet"
    
    if not mensal_file.exists():
        return pd.DataFrame()
    
    df = pd.read_parquet(mensal_file)
    
    # Filtrar apenas pelo ano solicitado
    if 'ano' in df.columns:
        df = df[df['ano'] == ano]
    
    return df


def load_consolidated_fornecedores(ano: int):
    """
    Carrega dados de fornecedores consolidados de todas as plantas.
    
    Args:
        ano: Ano fiscal
        
    Returns:
        DataFrame com agregações por fornecedor
    """
    base_path = get_base_path()
    fornecedores_file = base_path / "data_parquet" / "Plantas" / str(ano) / "fornecedores.parquet"
    
    if not fornecedores_file.exists():
        return pd.DataFrame()
    
    df = pd.read_parquet(fornecedores_file)
    
    # Filtrar apenas pelo ano solicitado
    if 'ano' in df.columns:
        df = df[df['ano'] == ano]
    
    return df


def load_consolidated_produtos(ano: int):
    """
    Carrega dados de produtos consolidados de todas as plantas.
    
    Args:
        ano: Ano fiscal
        
    Returns:
        DataFrame com agregações por produto
    """
    base_path = get_base_path()
    produtos_file = base_path / "data_parquet" / "Plantas" / str(ano) / "produtos.parquet"
    
    if not produtos_file.exists():
        return pd.DataFrame()
    
    df = pd.read_parquet(produtos_file)
    
    # Filtrar apenas pelo ano solicitado
    if 'ano' in df.columns:
        df = df[df['ano'] == ano]
    
    return df


def load_consolidated_cfop(ano: int):
    """
    Carrega dados de CFOP consolidados de todas as plantas.
    
    Args:
        ano: Ano fiscal
        
    Returns:
        DataFrame com agregações por CFOP
    """
    base_path = get_base_path()
    cfop_file = base_path / "data_parquet" / "Plantas" / str(ano) / "cfop.parquet"
    
    if not cfop_file.exists():
        return pd.DataFrame()
    
    df = pd.read_parquet(cfop_file)
    
    # Filtrar apenas pelo ano solicitado
    if 'ano' in df.columns:
        df = df[df['ano'] == ano]
    
    return df


def generate_cfops_nao_encontrados_from_parquets(ano: int):
    """
    Gera arquivo de CFOPs não encontrados lendo os parquets já existentes.
    Não precisa rodar extração novamente.
    
    Args:
        ano: Ano fiscal
        
    Returns:
        DataFrame consolidado com CFOPs não encontrados
    """
    base_path = get_base_path()
    data_parquet_path = base_path / "data_parquet"
    
    # Lista para armazenar todos os CFOPs não encontrados
    all_cfops_nao_encontrados = []
    
    # Procurar em todas as plantas
    if data_parquet_path.exists():
        for planta_dir in data_parquet_path.iterdir():
            if not planta_dir.is_dir() or planta_dir.name == "Plantas":
                continue
            
            # Verificar se existe o ano
            ano_dir = planta_dir / str(ano)
            if not ano_dir.exists():
                continue
            
            # Procurar arquivo parquet principal
            parquet_file = None
            for file in ano_dir.glob("*.parquet"):
                if file.name.startswith("fiscal_"):
                    parquet_file = file
                    break
            
            if parquet_file and parquet_file.exists():
                try:
                    df = pd.read_parquet(parquet_file)
                    
                    # Filtrar apenas registros não encontrados
                    if 'cod_natureza_op' in df.columns:
                        df_nao_enc = df[df['cod_natureza_op'] == 'Não encontrado'].copy()
                        
                        if not df_nao_enc.empty:
                            # Agrupar por CFOP - usar apenas funções simples
                            df_grouped = df_nao_enc.groupby('cfop').agg({
                                'valor_icms': 'sum',
                                'base_icms_1': 'sum',
                                'quantidade': 'sum'
                            }).reset_index()
                            
                            # Adicionar contagens separadamente para evitar MultiIndex
                            if 'numero_nf' in df_nao_enc.columns:
                                df_grouped['qtd_notas'] = df_nao_enc.groupby('cfop')['numero_nf'].nunique().values
                            if 'razao_social' in df_nao_enc.columns:
                                df_grouped['qtd_fornecedores'] = df_nao_enc.groupby('cfop')['razao_social'].nunique().values
                            if 'descricao' in df_nao_enc.columns:
                                df_grouped['qtd_produtos'] = df_nao_enc.groupby('cfop')['descricao'].nunique().values
                            if 'entrada_saida' in df_nao_enc.columns:
                                df_grouped['entrada_saida'] = df_nao_enc.groupby('cfop')['entrada_saida'].agg(
                                    lambda x: x.mode()[0] if not x.mode().empty else x.iloc[0]
                                ).values
                            if 'data_fiscal' in df_nao_enc.columns:
                                df_grouped['primeira_ocorrencia'] = df_nao_enc.groupby('cfop')['data_fiscal'].min().values
                                df_grouped['ultima_ocorrencia'] = df_nao_enc.groupby('cfop')['data_fiscal'].max().values
                            
                            df_grouped['planta'] = planta_dir.name
                            df_grouped['ano'] = ano
                            
                            all_cfops_nao_encontrados.append(df_grouped)
                
                except Exception as e:
                    print(f"Erro ao processar {planta_dir.name}: {e}")
                    continue
    
    # Consolidar todos os resultados
    if all_cfops_nao_encontrados:
        df_final = pd.concat(all_cfops_nao_encontrados, ignore_index=True)
        
        # Verificar qual coluna usar para ordenação
        if 'valor_icms' in df_final.columns:
            df_final = df_final.sort_values('valor_icms', ascending=False)
        elif 'valor_icms_sum' in df_final.columns:
            df_final = df_final.sort_values('valor_icms_sum', ascending=False)
        
        # Salvar no diretório Plantas
        consolidated_path = base_path / "data_parquet" / "Plantas" / str(ano)
        consolidated_path.mkdir(parents=True, exist_ok=True)
        
        output_file = consolidated_path / "cfops_nao_encontrados.parquet"
        df_final.to_parquet(output_file, index=False)
        
        print(f"✅ Arquivo gerado: {output_file}")
        print(f"📊 Total de CFOPs não encontrados: {len(df_final)}")
        print(f"📋 Colunas disponíveis: {df_final.columns.tolist()}")
        
        return df_final
    else:
        return pd.DataFrame()


def load_consolidated_cfops_nao_encontrados(ano: int, auto_generate: bool = True):
    """
    Carrega dados de CFOPs não encontrados consolidados de todas as plantas.
    Se o arquivo não existir e auto_generate=True, gera automaticamente dos parquets.
    
    Args:
        ano: Ano fiscal
        auto_generate: Se True, gera arquivo automaticamente se não existir
        
    Returns:
        DataFrame com CFOPs que não foram encontrados na tabela de códigos
    """
    base_path = get_base_path()
    cfops_nao_enc_file = base_path / "data_parquet" / "Plantas" / str(ano) / "cfops_nao_encontrados.parquet"
    
    # Se arquivo não existe e auto_generate está ativado, gerar
    if not cfops_nao_enc_file.exists() and auto_generate:
        print(f"📋 Gerando arquivo de CFOPs não encontrados para {ano}...")
        df = generate_cfops_nao_encontrados_from_parquets(ano)
        return df
    
    # Carregar arquivo existente
    if cfops_nao_enc_file.exists():
        df = pd.read_parquet(cfops_nao_enc_file)
        
        # Filtrar apenas pelo ano solicitado
        if 'ano' in df.columns:
            df = df[df['ano'] == ano]
        
        return df
    
    return pd.DataFrame()
