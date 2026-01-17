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
