"""
Módulo para transformação e visualização de dados fiscais.
"""

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


def get_monthly_totals(df):
    """
    Agrupa dados por mês baseado em data_fiscal.
    
    Args:
        df: DataFrame com dados fiscais
        
    Returns:
        DataFrame com totais mensais
    """
    if df.empty or 'data_fiscal' not in df.columns:
        return pd.DataFrame()
    
    df_month = df.groupby(pd.Grouper(key='data_fiscal', freq='M')).agg({
        'valor_icms': 'sum',
        'base_icms_1': 'sum'
    }).reset_index()
    
    df_month['mes'] = df_month['data_fiscal'].dt.strftime('%Y-%m')
    
    return df_month


def plot_monthly_chart(df):
    """
    Cria gráfico de barras mensal de VALOR_ICMS.
    
    Args:
        df: DataFrame com dados fiscais
        
    Returns:
        Figura Plotly
    """
    df_month = get_monthly_totals(df)
    
    if df_month.empty:
        return go.Figure()
    
    # Formatar mês como "jan/2025", "fev/2025"
    df_month['mes_formatado'] = df_month['data_fiscal'].dt.strftime('%b/%Y').str.lower()
    
    fig = px.bar(
        df_month,
        x='mes_formatado',
        y='valor_icms',
        title='ICMS por Mês',
        labels={'mes_formatado': 'Mês', 'valor_icms': 'Valor ICMS (R$)'},
        text='valor_icms',
        color='valor_icms',
        color_continuous_scale=['#e3f2fd', '#bbdefb', '#90caf9', '#64b5f6', '#42a5f5', '#1e88e5', '#1565c0', '#0d47a1', '#01579b']
    )
    
    # Adicionar rótulos de dados externos
    fig.update_traces(
        texttemplate='%{text:,.2f}',
        textposition='outside',
        textfont=dict(size=10)
    )
    
    fig.update_layout(
        xaxis_title='Mês',
        yaxis_title='Valor ICMS (R$)',
        showlegend=False,
        hovermode='x unified',
        uniformtext_minsize=8,
        uniformtext_mode='hide',
        xaxis=dict(tickfont=dict(size=10)),
        margin=dict(t=150, b=100),
        height=600,
        coloraxis_showscale=False
    )
    
    return fig


def get_top_fornecedores(df, top_n=10):
    """
    Retorna top N fornecedores por valor_icms.
    
    Args:
        df: DataFrame com dados fiscais
        top_n: Número de fornecedores no ranking
        
    Returns:
        DataFrame com ranking
    """
    if df.empty or 'razao_social' not in df.columns:
        return pd.DataFrame()
    
    df_top = df.groupby('razao_social').agg({
        'valor_icms': 'sum',
        'base_icms_1': 'sum'
    }).reset_index()
    
    df_top = df_top.sort_values('valor_icms', ascending=False).head(top_n)
    
    return df_top


def plot_top_fornecedores(df, top_n=10):
    """
    Cria gráfico de barras horizontais com top fornecedores.
    
    Args:
        df: DataFrame com dados fiscais
        top_n: Número de fornecedores no ranking (ou 'total' para todos)
        
    Returns:
        Figura Plotly
    """
    if df.empty or 'razao_social' not in df.columns:
        return go.Figure()
    
    # Agrupar todos os fornecedores
    df_all = df.groupby('razao_social').agg({
        'valor_icms': 'sum',
        'base_icms_1': 'sum'
    }).reset_index()
    df_all = df_all.sort_values('valor_icms', ascending=False)
    
    # Selecionar top ou total
    if top_n == 'total':
        df_top = df_all
        titulo = 'Todos os Fornecedores por ICMS'
    else:
        df_top = df_all.head(top_n)
        titulo = f'Top {top_n} Fornecedores por ICMS'
    
    fig = px.bar(
        df_top,
        x='razao_social',
        y='valor_icms',
        title=titulo,
        labels={'razao_social': 'Fornecedor', 'valor_icms': 'Valor ICMS (R$)'},
        text='valor_icms',
        color='valor_icms',
        color_continuous_scale=['#e3f2fd', '#bbdefb', '#90caf9', '#64b5f6', '#42a5f5', '#1e88e5', '#1565c0', '#0d47a1', '#01579b']
    )
    
    # Adicionar rótulos de dados externos superiores
    fig.update_traces(
        texttemplate='%{text:,.2f}',
        textposition='outside',
        textfont=dict(size=9)
    )
    
    fig.update_layout(
        xaxis_title='Fornecedor',
        yaxis_title='Valor ICMS (R$)',
        showlegend=False,
        xaxis={'categoryorder': 'total descending'},
        xaxis_tickangle=-45,
        xaxis_tickfont=dict(size=10),
        margin=dict(t=150, b=150),
        height=600,
        coloraxis_showscale=False
    )
    
    return fig


def plot_top_fornecedores_pizza(df, top_n=10):
    """
    Cria gráfico de pizza com top fornecedores e "Outros".
    
    Args:
        df: DataFrame com dados fiscais
        top_n: Número de fornecedores no top
        
    Returns:
        Figura Plotly
    """
    if df.empty or 'razao_social' not in df.columns:
        return go.Figure()
    
    # Agrupar todos os fornecedores
    df_all = df.groupby('razao_social').agg({
        'valor_icms': 'sum'
    }).reset_index()
    df_all = df_all.sort_values('valor_icms', ascending=False)
    
    if top_n == 'total' or len(df_all) <= top_n:
        df_pizza = df_all.copy()
        df_pizza['label'] = df_pizza['razao_social']
    else:
        # Top N + Outros
        df_top = df_all.head(top_n).copy()
        outros_valor = df_all.iloc[top_n:]['valor_icms'].sum()
        
        df_pizza = df_top.copy()
        df_pizza['label'] = df_pizza['razao_social']
        
        if outros_valor > 0:
            df_outros = pd.DataFrame([{
                'razao_social': 'Outros',
                'valor_icms': outros_valor,
                'label': 'Outros'
            }])
            df_pizza = pd.concat([df_pizza, df_outros], ignore_index=True)
    
    fig = px.pie(
        df_pizza,
        values='valor_icms',
        names='label',
        title=f'Distribuição de ICMS - Top {top_n} Fornecedores',
        hole=0.4,
        color_discrete_sequence=['#e3f2fd', '#bbdefb', '#90caf9', '#64b5f6', '#42a5f5', '#2196f3', '#1e88e5', '#1565c0', '#0d47a1', '#01579b']
    )
    
    fig.update_traces(
        textposition='outside',
        textinfo='percent+label',
        textfont=dict(size=10)
    )
    
    fig.update_layout(
        margin=dict(t=220, b=50, l=50, r=50),
        height=550
    )
    
    return fig


def get_top_produtos(df, top_n=10):
    """
    Retorna top N produtos por valor_icms.
    
    Args:
        df: DataFrame com dados fiscais
        top_n: Número de produtos no ranking
        
    Returns:
        DataFrame com ranking
    """
    if df.empty or 'descricao' not in df.columns:
        return pd.DataFrame()
    
    df_top = df.groupby('descricao').agg({
        'valor_icms': 'sum',
        'base_icms_1': 'sum',
        'quantidade': 'sum'
    }).reset_index()
    
    df_top = df_top.sort_values('valor_icms', ascending=False).head(top_n)
    
    return df_top


def plot_top_produtos(df, top_n=10):
    """
    Cria gráfico de barras horizontais com top produtos.
    
    Args:
        df: DataFrame com dados fiscais
        top_n: Número de produtos no ranking (ou 'total' para todos)
        
    Returns:
        Figura Plotly
    """
    if df.empty or 'descricao' not in df.columns:
        return go.Figure()
    
    # Agrupar todos os produtos apenas por descricao (evita duplicatas)
    df_all = df.groupby('descricao').agg({
        'valor_icms': 'sum',
        'base_icms_1': 'sum',
        'quantidade': 'sum'
    }).reset_index()
    df_all = df_all.sort_values('valor_icms', ascending=False)
    
    # Selecionar top ou total
    if top_n == 'total':
        df_top = df_all
        titulo = 'Todos os Produtos por ICMS'
    else:
        df_top = df_all.head(top_n)
        titulo = f'Top {top_n} Produtos por ICMS'
    
    # Truncar descrição para visualização
    df_top['descricao_curta'] = df_top['descricao'].str[:40]
    
    fig = px.bar(
        df_top,
        x='descricao_curta',
        y='valor_icms',
        title=titulo,
        labels={'descricao_curta': 'Produto', 'valor_icms': 'Valor ICMS (R$)'},
        text='valor_icms',
        color='valor_icms',
        color_continuous_scale=['#e3f2fd', '#bbdefb', '#90caf9', '#64b5f6', '#42a5f5', '#1e88e5', '#1565c0', '#0d47a1', '#01579b']
    )
    
    # Adicionar rótulos de dados externos superiores
    fig.update_traces(
        texttemplate='%{text:,.2f}',
        textposition='outside',
        textfont=dict(size=9)
    )
    
    fig.update_layout(
        xaxis_title='Produto',
        yaxis_title='Valor ICMS (R$)',
        showlegend=False,
        xaxis={'categoryorder': 'total descending'},
        xaxis_tickangle=-45,
        xaxis_tickfont=dict(size=10),
        margin=dict(t=150, b=150),
        height=600,
        coloraxis_showscale=False
    )
    
    return fig


def plot_top_produtos_pizza(df, top_n=10):
    """
    Cria gráfico de pizza com top produtos e "Outros".
    
    Args:
        df: DataFrame com dados fiscais
        top_n: Número de produtos no top
        
    Returns:
        Figura Plotly
    """
    if df.empty or 'descricao' not in df.columns:
        return go.Figure()
    
    # Agrupar todos os produtos apenas por descricao
    df_all = df.groupby('descricao').agg({
        'valor_icms': 'sum'
    }).reset_index()
    df_all = df_all.sort_values('valor_icms', ascending=False)
    
    if top_n == 'total' or len(df_all) <= top_n:
        df_pizza = df_all.copy()
        df_pizza['label'] = df_pizza['descricao'].str[:30]
    else:
        # Top N + Outros
        df_top = df_all.head(top_n).copy()
        outros_valor = df_all.iloc[top_n:]['valor_icms'].sum()
        
        df_pizza = df_top.copy()
        df_pizza['label'] = df_pizza['descricao'].str[:30]
        
        if outros_valor > 0:
            df_outros = pd.DataFrame([{
                'descricao': 'Outros',
                'valor_icms': outros_valor,
                'label': 'Outros'
            }])
            df_pizza = pd.concat([df_pizza, df_outros], ignore_index=True)
    
    fig = px.pie(
        df_pizza,
        values='valor_icms',
        names='label',
        title=f'Distribuição de ICMS - Top {top_n} Produtos',
        hole=0.4,
        color_discrete_sequence=['#e3f2fd', '#bbdefb', '#90caf9', '#64b5f6', '#42a5f5', '#2196f3', '#1e88e5', '#1565c0', '#0d47a1', '#01579b']
    )
    
    fig.update_traces(
        textposition='outside',
        textinfo='percent+label',
        textfont=dict(size=10)
    )
    
    fig.update_layout(
        margin=dict(t=220, b=50, l=50, r=50),
        height=550
    )
    
    return fig


def get_cfop_distribution(df):
    """
    Retorna distribuição por CFOP.
    
    Args:
        df: DataFrame com dados fiscais
        
    Returns:
        DataFrame com distribuição
    """
    if df.empty or 'cfop' not in df.columns:
        return pd.DataFrame()
    
    # Garantir que CFOP é string
    df = df.copy()
    df['cfop'] = df['cfop'].fillna('').astype(str).str.strip()
    
    df_cfop = df.groupby(['cfop', 'descricao_natureza_op']).agg({
        'valor_icms': 'sum',
        'base_icms_1': 'sum'
    }).reset_index()
    
    df_cfop = df_cfop.sort_values('valor_icms', ascending=False)
    
    return df_cfop


def plot_cfop_distribution(df, top_n=10):
    """
    Cria gráfico de barras horizontais com CFOPs.
    
    Args:
        df: DataFrame com dados fiscais
        top_n: Número de CFOPs no ranking (ou 'total' para todos)
        
    Returns:
        Figura Plotly
    """
    if df.empty or 'cfop' not in df.columns:
        return go.Figure()
    
    # Garantir que CFOP é string desde o início
    df = df.copy()
    df['cfop'] = df['cfop'].fillna('').astype(str).str.strip()
    
    # Agrupar todos os CFOPs
    df_all = df.groupby(['cfop', 'descricao_natureza_op']).agg({
        'valor_icms': 'sum',
        'base_icms_1': 'sum'
    }).reset_index()
    df_all = df_all.sort_values('valor_icms', ascending=False)
    
    # Selecionar top ou total
    if top_n == 'total':
        df_top = df_all
        titulo = 'Todos os CFOPs por ICMS'
    else:
        df_top = df_all.head(top_n)
        titulo = f'Top {top_n} CFOPs por ICMS'
    
    # Converter CFOP para string para evitar interpretação numérica
    df_top['cfop'] = df_top['cfop'].astype(str)
    
    fig = px.bar(
        df_top,
        x='cfop',
        y='valor_icms',
        title=titulo,
        labels={'cfop': 'CFOP', 'valor_icms': 'Valor ICMS (R$)'},
        text='valor_icms',
        color='valor_icms',
        color_continuous_scale=['#e3f2fd', '#bbdefb', '#90caf9', '#64b5f6', '#42a5f5', '#1e88e5', '#1565c0', '#0d47a1', '#01579b']
    )
    
    # Adicionar rótulos de dados externos superiores
    fig.update_traces(
        texttemplate='%{text:,.2f}',
        textposition='outside',
        textfont=dict(size=9)
    )
    
    fig.update_layout(
        xaxis_title='CFOP',
        yaxis_title='Valor ICMS (R$)',
        showlegend=False,
        xaxis={'categoryorder': 'total descending', 'type': 'category'},
        xaxis_tickfont=dict(size=10),
        margin=dict(t=150, b=100),
        height=600,
        coloraxis_showscale=False
    )
    
    return fig


def plot_cfop_pizza(df, top_n=10):
    """
    Cria gráfico de pizza com CFOPs e "Outros".
    
    Args:
        df: DataFrame com dados fiscais
        top_n: Número de CFOPs no top
        
    Returns:
        Figura Plotly
    """
    if df.empty or 'cfop' not in df.columns:
        return go.Figure()
    
    # Garantir que CFOP é string
    df = df.copy()
    df['cfop'] = df['cfop'].fillna('').astype(str).str.strip()
    
    # Agrupar todos os CFOPs
    df_all = df.groupby('cfop').agg({
        'valor_icms': 'sum'
    }).reset_index()
    df_all = df_all.sort_values('valor_icms', ascending=False)
    
    if top_n == 'total' or len(df_all) <= top_n:
        df_pizza = df_all.copy()
        df_pizza['label'] = df_pizza['cfop']
    else:
        # Top N + Outros
        df_top = df_all.head(top_n).copy()
        outros_valor = df_all.iloc[top_n:]['valor_icms'].sum()
        
        df_pizza = df_top.copy()
        df_pizza['label'] = df_pizza['cfop']
        
        if outros_valor > 0:
            df_outros = pd.DataFrame([{
                'cfop': 'Outros',
                'valor_icms': outros_valor,
                'label': 'Outros'
            }])
            df_pizza = pd.concat([df_pizza, df_outros], ignore_index=True)
    
    fig = px.pie(
        df_pizza,
        values='valor_icms',
        names='label',
        title=f'Distribuição de ICMS - Top {top_n} CFOPs',
        hole=0.4,
        color_discrete_sequence=['#e3f2fd', '#bbdefb', '#90caf9', '#64b5f6', '#42a5f5', '#2196f3', '#1e88e5', '#1565c0', '#0d47a1', '#01579b']
    )
    
    fig.update_traces(
        textposition='outside',
        textinfo='percent+label',
        textfont=dict(size=10)
    )
    
    fig.update_layout(
        margin=dict(t=220, b=50, l=50, r=50),
        height=550
    )
    
    return fig


def get_tabela_sumarizada_fornecedores(df):
    """
    Retorna tabela sumarizada de fornecedores agrupada por razao_social.
    Inclui todas colunas relevantes exceto aliq_icms e numero_nf.
    """
    if df.empty or 'razao_social' not in df.columns:
        return pd.DataFrame()
    
    # Definir agregações
    agg_dict = {}
    
    # Colunas numéricas (soma)
    colunas_numericas = ['valor_icms', 'base_icms_1', 'quantidade']
    for col in colunas_numericas:
        if col in df.columns:
            agg_dict[col] = 'sum'
    
    # Colunas categóricas (primeiro valor ou mais frequente)
    colunas_info = ['uf', 'municipio', 'cst_icms']
    for col in colunas_info:
        if col in df.columns:
            agg_dict[col] = lambda x: x.mode()[0] if not x.mode().empty else x.iloc[0]
    
    # Contar número de notas fiscais
    if 'numero_nf' in df.columns:
        agg_dict['numero_nf'] = 'nunique'
    
    df_tabela = df.groupby('razao_social').agg(agg_dict).reset_index()
    
    # Converter colunas categóricas para string
    if 'cst_icms' in df_tabela.columns:
        df_tabela['cst_icms'] = df_tabela['cst_icms'].fillna('').astype(str).str.strip().str.replace('.0', '', regex=False)
    if 'cod_natureza_op' in df_tabela.columns:
        df_tabela['cod_natureza_op'] = df_tabela['cod_natureza_op'].fillna('').astype(str).str.strip().str.replace('.0', '', regex=False)
    
    # Renomear coluna de contagem
    if 'numero_nf' in df_tabela.columns:
        df_tabela.rename(columns={'numero_nf': 'qtd_notas'}, inplace=True)
    
    df_tabela = df_tabela.sort_values('valor_icms', ascending=False)
    
    return df_tabela


def get_tabela_sumarizada_produtos(df):
    """
    Retorna tabela sumarizada de produtos agrupada por codigo_produto e descricao.
    Inclui todas colunas relevantes exceto aliq_icms e numero_nf.
    """
    if df.empty or 'descricao' not in df.columns:
        return pd.DataFrame()
    
    # Definir agregações
    agg_dict = {}
    
    # Colunas numéricas (soma)
    colunas_numericas = ['valor_icms', 'base_icms_1', 'quantidade']
    for col in colunas_numericas:
        if col in df.columns:
            agg_dict[col] = 'sum'
    
    # Colunas categóricas (primeiro valor ou mais frequente)
    colunas_info = ['cfop', 'descricao_natureza_op', 'cst_icms']
    for col in colunas_info:
        if col in df.columns:
            agg_dict[col] = lambda x: x.mode()[0] if not x.mode().empty else x.iloc[0]
    
    # Contar fornecedores e notas
    if 'razao_social' in df.columns:
        agg_dict['razao_social'] = 'nunique'
    if 'numero_nf' in df.columns:
        agg_dict['numero_nf'] = 'nunique'
    
    # Agrupar apenas por descricao para evitar duplicatas
    df_tabela = df.groupby('descricao').agg(agg_dict).reset_index()
    
    # Converter colunas categóricas para string
    if 'cfop' in df_tabela.columns:
        df_tabela['cfop'] = df_tabela['cfop'].fillna('').astype(str).str.strip().str.replace('.0', '', regex=False)
    if 'cst_icms' in df_tabela.columns:
        df_tabela['cst_icms'] = df_tabela['cst_icms'].fillna('').astype(str).str.strip().str.replace('.0', '', regex=False)
    if 'cod_natureza_op' in df_tabela.columns:
        df_tabela['cod_natureza_op'] = df_tabela['cod_natureza_op'].fillna('').astype(str).str.strip().str.replace('.0', '', regex=False)
    
    # Renomear colunas de contagem
    rename_dict = {}
    if 'razao_social' in df_tabela.columns:
        rename_dict['razao_social'] = 'qtd_fornecedores'
    if 'numero_nf' in df_tabela.columns:
        rename_dict['numero_nf'] = 'qtd_notas'
    if rename_dict:
        df_tabela.rename(columns=rename_dict, inplace=True)
    
    df_tabela = df_tabela.sort_values('valor_icms', ascending=False)
    
    return df_tabela


def get_tabela_sumarizada_cfop(df):
    """
    Retorna tabela sumarizada de CFOPs agrupada por cfop e descricao_natureza_op.
    Inclui todas colunas relevantes exceto aliq_icms e numero_nf.
    """
    if df.empty or 'cfop' not in df.columns:
        return pd.DataFrame()
    
    # Garantir que CFOP é string
    df = df.copy()
    df['cfop'] = df['cfop'].fillna('').astype(str).str.strip()
    
    group_cols = ['cfop']
    if 'descricao_natureza_op' in df.columns:
        group_cols.append('descricao_natureza_op')
    
    # Definir agregações
    agg_dict = {}
    
    # Colunas numéricas (soma)
    colunas_numericas = ['valor_icms', 'base_icms_1', 'quantidade']
    for col in colunas_numericas:
        if col in df.columns:
            agg_dict[col] = 'sum'
    
    # Colunas categóricas (primeiro valor ou mais frequente)
    colunas_info = ['entrada_saida', 'cst_icms']
    for col in colunas_info:
        if col in df.columns:
            agg_dict[col] = lambda x: x.mode()[0] if not x.mode().empty else x.iloc[0]
    
    # Contar fornecedores, produtos e notas
    if 'razao_social' in df.columns:
        agg_dict['razao_social'] = 'nunique'
    if 'descricao' in df.columns:
        agg_dict['descricao'] = 'nunique'
    if 'numero_nf' in df.columns:
        agg_dict['numero_nf'] = 'nunique'
    
    df_tabela = df.groupby(group_cols).agg(agg_dict).reset_index()
    
    # Converter colunas categóricas para string
    if 'cfop' in df_tabela.columns:
        df_tabela['cfop'] = df_tabela['cfop'].fillna('').astype(str).str.strip().str.replace('.0', '', regex=False)
    if 'cst_icms' in df_tabela.columns:
        df_tabela['cst_icms'] = df_tabela['cst_icms'].fillna('').astype(str).str.strip().str.replace('.0', '', regex=False)
    if 'cod_natureza_op' in df_tabela.columns:
        df_tabela['cod_natureza_op'] = df_tabela['cod_natureza_op'].fillna('').astype(str).str.strip().str.replace('.0', '', regex=False)
    
    # Renomear colunas de contagem
    rename_dict = {}
    if 'razao_social' in df_tabela.columns:
        rename_dict['razao_social'] = 'qtd_fornecedores'
    if 'descricao' in df_tabela.columns:
        rename_dict['descricao'] = 'qtd_produtos'
    if 'numero_nf' in df_tabela.columns:
        rename_dict['numero_nf'] = 'qtd_notas'
    if rename_dict:
        df_tabela.rename(columns=rename_dict, inplace=True)
    
    df_tabela = df_tabela.sort_values('valor_icms', ascending=False)
    
    return df_tabela
