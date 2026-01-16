"""
Módulo para carregamento de dados fiscais.
"""

import pandas as pd
import streamlit as st
from pathlib import Path
from extraction.extracao import load_plantas, load_anos


def get_base_path():
    """Retorna o caminho base do projeto."""
    return Path(__file__).parent.parent.parent


@st.cache_data(ttl=300)
def load_data(planta: str, ano: int):
    """
    Carrega dados fiscais de uma planta e ano específicos.
    
    Args:
        planta: Nome da planta
        ano: Ano fiscal
        
    Returns:
        DataFrame com os dados fiscais
    """
    base_path = get_base_path()
    parquet_path = base_path / "data_parquet" / planta / str(ano) / f"fiscal_{planta}_{ano}.parquet"
    
    if not parquet_path.exists():
        return pd.DataFrame()
    
    df = pd.read_parquet(parquet_path)
    
    # Garantir que data_fiscal é datetime
    if 'data_fiscal' in df.columns:
        df['data_fiscal'] = pd.to_datetime(df['data_fiscal'])
    
    # Garantir que colunas específicas sejam tratadas como string
    string_columns = ['numero_nf', 'cfop', 'num_controle_docto', 'cst_icms', 'codigo_produto', 'cod_natureza_op']
    for col in string_columns:
        if col in df.columns:
            df[col] = df[col].fillna('').astype(str).str.strip()
            # Limpar valores inválidos
            df[col] = df[col].replace(['nan', 'None', '<NA>'], '')
    
    return df


@st.cache_data(ttl=600)
def load_summary(planta: str):
    """
    Carrega resumo de dados de uma planta (todos os anos).
    
    Args:
        planta: Nome da planta
        
    Returns:
        dict com métricas da planta
    """
    anos = load_anos(planta)
    
    total_registros = 0
    total_valor_icms = 0
    anos_com_dados = []
    
    for ano in anos:
        df = load_data(planta, ano)
        if not df.empty:
            total_registros += len(df)
            anos_com_dados.append(ano)
            
            if 'valor_icms' in df.columns:
                total_valor_icms += df['valor_icms'].sum()
    
    return {
        'planta': planta,
        'total_registros': total_registros,
        'total_valor_icms': total_valor_icms,
        'anos_disponiveis': anos_com_dados,
        'anos_totais': len(anos_com_dados)
    }


@st.cache_data(ttl=600)
def get_available_plantas():
    """Retorna lista de plantas configuradas."""
    return load_plantas()


@st.cache_data(ttl=600)
def get_available_anos(planta):
    """Retorna lista de anos disponíveis para uma planta."""
    return load_anos(planta)
