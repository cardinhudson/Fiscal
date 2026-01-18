"""
Página de Análise Fiscal - Sistema de Análise Fiscal Stellantis
"""

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import sys
from pathlib import Path

# Adicionar diretório raiz ao path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from app.utils.load_data import load_data, get_available_plantas, get_available_anos
from app.utils.transform_data import (
    plot_monthly_chart,
    plot_top_fornecedores,
    plot_top_fornecedores_pizza,
    plot_top_produtos,
    plot_top_produtos_pizza,
    plot_cfop_distribution,
    plot_cfop_pizza,
    get_monthly_totals,
    get_top_fornecedores,
    get_top_produtos,
    get_cfop_distribution,
    get_tabela_sumarizada_fornecedores,
    get_tabela_sumarizada_produtos,
    get_tabela_sumarizada_cfop
)

# Configuração da página
st.set_page_config(
    page_title="Análise Fiscal",
    page_icon="📊",
    layout="wide"
)

st.title("📊 Análise Fiscal")

# Seletor de Unidade Monetária com radio buttons
st.markdown("---")
unidade_monetaria = st.radio(
    "💰 **Fator conversão:**",
    ["💵 Reais", "📊 Mil (10³)", "📈 Milhões (10⁶)", "🚀 Bilhões (10⁹)"],
    horizontal=True,
    index=2,
    key="unidade_monetaria"
)

# Definir divisor baseado na unidade selecionada
if "Mil" in unidade_monetaria:
    divisor = 1e3
    sufixo = "mil"
elif "Milhões" in unidade_monetaria:
    divisor = 1e6
    sufixo = "mi"
elif "Bilhões" in unidade_monetaria:
    divisor = 1e9
    sufixo = "bi"
else:
    divisor = 1
    sufixo = ""

st.markdown("---")

# Sidebar - Filtros principais
st.sidebar.header("Filtros Principais")

# Seleção de Planta
plantas = get_available_plantas()
planta_sel = st.sidebar.selectbox("Planta", plantas)

# Seleção de Ano
anos = get_available_anos(planta_sel)
if not anos:
    st.error(f"Nenhum ano disponível para a planta {planta_sel}")
    st.stop()

ano_sel = st.sidebar.selectbox("Ano", anos, index=len(anos)-1 if anos else 0)

# Carregar dados
df = load_data(planta_sel, ano_sel)

if df.empty:
    st.warning(f"Sem dados disponíveis para {planta_sel} - {ano_sel}")
    st.info("💡 Use a página **Extração** para processar arquivos Excel.")
    st.stop()

# Filtro de período
st.sidebar.header("Filtros de Período")

min_date = df['data_fiscal'].min().date() if 'data_fiscal' in df.columns else datetime.now().date()
max_date = df['data_fiscal'].max().date() if 'data_fiscal' in df.columns else datetime.now().date()

start_date = st.sidebar.date_input(
    "Data Inicial",
    value=min_date,
    min_value=min_date,
    max_value=max_date
)

end_date = st.sidebar.date_input(
    "Data Final",
    value=max_date,
    min_value=min_date,
    max_value=max_date
)

# Aplicar filtro de data
df_filtered = df[
    (df['data_fiscal'].dt.date >= start_date) &
    (df['data_fiscal'].dt.date <= end_date)
]

# Filtros opcionais
st.sidebar.header("Filtros Opcionais")

# Filtro Entrada/Saída
if 'entrada_saida' in df.columns:
    tipos = ['Todos'] + sorted(df['entrada_saida'].dropna().unique().tolist())
    tipo_sel = st.sidebar.selectbox("Tipo", tipos)
    if tipo_sel != 'Todos':
        df_filtered = df_filtered[df_filtered['entrada_saida'] == tipo_sel]

# Filtro CFOP
if 'cfop' in df.columns:
    cfops_disponiveis = sorted(df['cfop'].dropna().unique().tolist())
    cfop_sel = st.sidebar.multiselect("CFOP", cfops_disponiveis)
    if cfop_sel:
        df_filtered = df_filtered[df_filtered['cfop'].isin(cfop_sel)]

# Filtro Fornecedor
if 'razao_social' in df.columns:
    fornecedores = ['Todos'] + sorted(df['razao_social'].dropna().unique().tolist())
    fornecedor_sel = st.sidebar.selectbox("Fornecedor", fornecedores)
    if fornecedor_sel != 'Todos':
        df_filtered = df_filtered[df_filtered['razao_social'] == fornecedor_sel]

# Filtro CST ICMS
if 'cst_icms' in df.columns:
    csts_disponiveis = sorted(df['cst_icms'].dropna().unique().tolist())
    cst_sel = st.sidebar.multiselect("CST ICMS", csts_disponiveis)
    if cst_sel:
        df_filtered = df_filtered[df_filtered['cst_icms'].isin(cst_sel)]

# Filtro UF
if 'uf' in df.columns:
    ufs_disponiveis = ['Todos'] + sorted(df['uf'].dropna().unique().tolist())
    uf_sel = st.sidebar.selectbox("UF", ufs_disponiveis)
    if uf_sel != 'Todos':
        df_filtered = df_filtered[df_filtered['uf'] == uf_sel]

# Filtro Município
if 'municipio' in df.columns:
    municipios_disponiveis = ['Todos'] + sorted(df['municipio'].dropna().unique().tolist())
    municipio_sel = st.sidebar.selectbox("Município", municipios_disponiveis)
    if municipio_sel != 'Todos':
        df_filtered = df_filtered[df_filtered['municipio'] == municipio_sel]

# Filtro Código de Natureza de Operação
if 'cod_natureza_op' in df.columns:
    nat_ops_disponiveis = sorted(df['cod_natureza_op'].dropna().unique().tolist())
    nat_op_sel = st.sidebar.multiselect("Código Natureza Op", nat_ops_disponiveis)
    if nat_op_sel:
        df_filtered = df_filtered[df_filtered['cod_natureza_op'].isin(nat_op_sel)]

# Filtro Descrição de Natureza de Operação
if 'descricao_natureza_op' in df.columns:
    desc_nat_ops = ['Todos'] + sorted(df['descricao_natureza_op'].dropna().unique().tolist())
    desc_nat_op_sel = st.sidebar.selectbox("Descrição Natureza Op", desc_nat_ops)
    if desc_nat_op_sel != 'Todos':
        df_filtered = df_filtered[df_filtered['descricao_natureza_op'] == desc_nat_op_sel]

# Filtro Resumo de Operação
if 'resumo_de_operacao' in df.columns:
    resumo_ops_disponiveis = ['Todos'] + sorted(df['resumo_de_operacao'].dropna().unique().tolist())
    resumo_op_sel = st.sidebar.selectbox("Resumo de Operação", resumo_ops_disponiveis)
    if resumo_op_sel != 'Todos':
        df_filtered = df_filtered[df_filtered['resumo_de_operacao'] == resumo_op_sel]

# Filtro Código do Produto
if 'codigo_produto' in df.columns:
    codigo_produto_input = st.sidebar.text_input("Código Produto (busca)", "")
    if codigo_produto_input:
        df_filtered = df_filtered[df_filtered['codigo_produto'].str.contains(codigo_produto_input, case=False, na=False)]

# Filtro Descrição do Produto
if 'descricao' in df.columns:
    descricao_input = st.sidebar.text_input("Descrição Produto (busca)", "")
    if descricao_input:
        df_filtered = df_filtered[df_filtered['descricao'].str.contains(descricao_input, case=False, na=False)]

# Filtro Número NF
if 'numero_nf' in df.columns:
    numero_nf_input = st.sidebar.text_input("Número NF (busca)", "")
    if numero_nf_input:
        df_filtered = df_filtered[df_filtered['numero_nf'].str.contains(numero_nf_input, case=False, na=False)]

# Métricas principais
st.header("Resumo do Período")

col1, col2, col3, col4 = st.columns(4)

with col1:
    total_registros = len(df_filtered)
    st.metric("Total de Registros", f"{total_registros:,}")

with col2:
    if 'valor_icms' in df_filtered.columns:
        total_icms = df_filtered['valor_icms'].sum() / divisor
        label_icms = f"Total ICMS ({sufixo})" if sufixo else "Total ICMS"
        st.metric(label_icms, f"R$ {total_icms:,.2f}")
    else:
        st.metric("Total ICMS", "N/A")

with col3:
    if 'base_icms_1' in df_filtered.columns:
        total_base = df_filtered['base_icms_1'].sum() / divisor
        label_base = f"Base ICMS ({sufixo})" if sufixo else "Base ICMS"
        st.metric(label_base, f"R$ {total_base:,.2f}")
    else:
        st.metric("Base ICMS", "N/A")

with col4:
    if 'razao_social' in df_filtered.columns:
        total_fornecedores = df_filtered['razao_social'].nunique()
        st.metric("Fornecedores Únicos", f"{total_fornecedores:,}")
    else:
        st.metric("Fornecedores Únicos", "N/A")

# Visualizações
st.header("Análises")

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📈 Mensal",
    "🏢 Fornecedores",
    "📦 Produtos",
    "🔢 CFOP",
    "📋 Dados"
])

with tab1:
    st.subheader("Evolução Mensal de ICMS")
    fig_month = plot_monthly_chart(df_filtered, divisor=divisor, sufixo=sufixo)
    st.plotly_chart(fig_month, width='stretch', key="chart_mensal")
    
    # Tabela mensal
    df_month = get_monthly_totals(df_filtered)
    if not df_month.empty:
        # Aplicar divisor na tabela
        df_month_display = df_month.copy()
        df_month_display['valor_icms'] = df_month_display['valor_icms'] / divisor
        df_month_display['base_icms_1'] = df_month_display['base_icms_1'] / divisor
        st.dataframe(
            df_month_display[['mes', 'valor_icms', 'base_icms_1']],
            width='stretch',
            hide_index=True
        )

with tab2:
    st.subheader("Fornecedores por ICMS")
    
    # Seletor de Top
    top_n_forn = st.selectbox(
        "Selecione o Top:",
        [10, 15, 20, 30, 50, 100, 200, 500, 'total'],
        key='top_fornecedores'
    )
    
    # Tabela em expander (ANTES dos gráficos)
    with st.expander("📊 Tabela Detalhada de Fornecedores"):
        df_tabela_forn = get_tabela_sumarizada_fornecedores(df_filtered)
        if not df_tabela_forn.empty:
            # Configurar formatação de colunas numéricas
            column_config = {}
            if 'valor_icms' in df_tabela_forn.columns:
                column_config['valor_icms'] = st.column_config.NumberColumn(
                    "Valor ICMS (R$)",
                    format="%.2f"
                )
            if 'base_icms_1' in df_tabela_forn.columns:
                column_config['base_icms_1'] = st.column_config.NumberColumn(
                    "Base ICMS (R$)",
                    format="%.2f"
                )
            if 'quantidade' in df_tabela_forn.columns:
                column_config['quantidade'] = st.column_config.NumberColumn(
                    "Quantidade",
                    format="%.2f"
                )
            if 'cst_icms' in df_tabela_forn.columns:
                column_config['cst_icms'] = st.column_config.TextColumn(
                    "CST ICMS"
                )
            if 'qtd_notas' in df_tabela_forn.columns:
                column_config['qtd_notas'] = st.column_config.NumberColumn(
                    "Qtd Notas",
                    format="%d"
                )
            if 'numero_nf' in df_tabela_forn.columns:
                column_config['numero_nf'] = st.column_config.TextColumn(
                    "Número NF"
                )
            if 'cod_natureza_op' in df_tabela_forn.columns:
                column_config['cod_natureza_op'] = st.column_config.TextColumn(
                    "Cód Natureza Op"
                )
            
            st.dataframe(
                df_tabela_forn, 
                width='stretch', 
                hide_index=True,
                column_config=column_config
            )
            
            # Botão Excel export
            from io import BytesIO
            buffer_forn = BytesIO()
            with pd.ExcelWriter(buffer_forn, engine='openpyxl') as writer:
                df_tabela_forn.to_excel(writer, index=False, sheet_name='Fornecedores')
            st.download_button(
                label="📥 Download Excel",
                data=buffer_forn.getvalue(),
                file_name=f"fornecedores_{planta_sel}_{ano_sel}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                key="download_excel_fornecedores"
            )
        else:
            st.info("Sem dados para exibir.")
    
    # Gráfico de barras horizontal
    fig_forn = plot_top_fornecedores(df_filtered, top_n=top_n_forn, divisor=divisor, sufixo=sufixo)
    st.plotly_chart(fig_forn, width='stretch', key="chart_fornecedores_bar")
    
    # Gráfico de pizza
    fig_forn_pizza = plot_top_fornecedores_pizza(df_filtered, top_n=top_n_forn)
    st.plotly_chart(fig_forn_pizza, width='stretch', key="chart_fornecedores_pizza")

with tab3:
    st.subheader("Produtos por ICMS")
    
    # Seletor de Top
    top_n_prod = st.selectbox(
        "Selecione o Top:",
        [10, 15, 20, 30, 50, 100, 200, 500, 'total'],
        key='top_produtos'
    )
    
    # Tabela em expander (ANTES dos gráficos)
    with st.expander("📊 Tabela Detalhada de Produtos"):
        df_tabela_prod = get_tabela_sumarizada_produtos(df_filtered)
        if not df_tabela_prod.empty:
            # Configurar formatação de colunas numéricas
            column_config = {}
            if 'valor_icms' in df_tabela_prod.columns:
                column_config['valor_icms'] = st.column_config.NumberColumn(
                    "Valor ICMS (R$)",
                    format="%.2f"
                )
            if 'base_icms_1' in df_tabela_prod.columns:
                column_config['base_icms_1'] = st.column_config.NumberColumn(
                    "Base ICMS (R$)",
                    format="%.2f"
                )
            if 'quantidade' in df_tabela_prod.columns:
                column_config['quantidade'] = st.column_config.NumberColumn(
                    "Quantidade",
                    format="%.2f"
                )
            if 'cfop' in df_tabela_prod.columns:
                column_config['cfop'] = st.column_config.NumberColumn(
                    "CFOP",
                    format="%d"
                )
            if 'cst_icms' in df_tabela_prod.columns:
                column_config['cst_icms'] = st.column_config.TextColumn(
                    "CST ICMS"
                )
            if 'qtd_fornecedores' in df_tabela_prod.columns:
                column_config['qtd_fornecedores'] = st.column_config.NumberColumn(
                    "Qtd Fornecedores",
                    format="%d"
                )
            if 'qtd_notas' in df_tabela_prod.columns:
                column_config['qtd_notas'] = st.column_config.NumberColumn(
                    "Qtd Notas",
                    format="%d"
                )
            if 'numero_nf' in df_tabela_prod.columns:
                column_config['numero_nf'] = st.column_config.TextColumn(
                    "Número NF"
                )
            if 'cod_natureza_op' in df_tabela_prod.columns:
                column_config['cod_natureza_op'] = st.column_config.TextColumn(
                    "Cód Natureza Op"
                )
            
            st.dataframe(
                df_tabela_prod, 
                width='stretch', 
                hide_index=True,
                column_config=column_config
            )
            
            # Botão Excel export
            from io import BytesIO
            buffer_prod = BytesIO()
            with pd.ExcelWriter(buffer_prod, engine='openpyxl') as writer:
                df_tabela_prod.to_excel(writer, index=False, sheet_name='Produtos')
            st.download_button(
                label="📥 Download Excel",
                data=buffer_prod.getvalue(),
                file_name=f"produtos_{planta_sel}_{ano_sel}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                key="download_excel_produtos"
            )
        else:
            st.info("Sem dados para exibir.")
    
    # Gráfico de barras horizontal
    fig_prod = plot_top_produtos(df_filtered, top_n=top_n_prod, divisor=divisor, sufixo=sufixo)
    st.plotly_chart(fig_prod, width='stretch', key="chart_produtos_bar")
    
    # Gráfico de pizza
    fig_prod_pizza = plot_top_produtos_pizza(df_filtered, top_n=top_n_prod)
    st.plotly_chart(fig_prod_pizza, width='stretch', key="chart_produtos_pizza")

with tab4:
    st.subheader("Distribuição por CFOP")
    
    # Seletor de Top
    top_n_cfop = st.selectbox(
        "Selecione o Top:",
        [10, 15, 20, 30, 50, 100, 200, 500, 'total'],
        key='top_cfop'
    )
    
    # Tabela em expander (ANTES dos gráficos)
    with st.expander("📊 Tabela Detalhada de CFOP"):
        df_tabela_cfop = get_tabela_sumarizada_cfop(df_filtered)
        if not df_tabela_cfop.empty:
            # Configurar formatação de colunas numéricas
            column_config = {}
            if 'valor_icms' in df_tabela_cfop.columns:
                column_config['valor_icms'] = st.column_config.NumberColumn(
                    "Valor ICMS (R$)",
                    format="%.2f"
                )
            if 'base_icms_1' in df_tabela_cfop.columns:
                column_config['base_icms_1'] = st.column_config.NumberColumn(
                    "Base ICMS (R$)",
                    format="%.2f"
                )
            if 'quantidade' in df_tabela_cfop.columns:
                column_config['quantidade'] = st.column_config.NumberColumn(
                    "Quantidade",
                    format="%.2f"
                )
            if 'cfop' in df_tabela_cfop.columns:
                column_config['cfop'] = st.column_config.NumberColumn(
                    "CFOP",
                    format="%d"
                )
            if 'cst_icms' in df_tabela_cfop.columns:
                column_config['cst_icms'] = st.column_config.TextColumn(
                    "CST ICMS"
                )
            if 'qtd_fornecedores' in df_tabela_cfop.columns:
                column_config['qtd_fornecedores'] = st.column_config.NumberColumn(
                    "Qtd Fornecedores",
                    format="%d"
                )
            if 'qtd_produtos' in df_tabela_cfop.columns:
                column_config['qtd_produtos'] = st.column_config.NumberColumn(
                    "Qtd Produtos",
                    format="%d"
                )
            if 'qtd_notas' in df_tabela_cfop.columns:
                column_config['qtd_notas'] = st.column_config.NumberColumn(
                    "Qtd Notas",
                    format="%d"
                )
            if 'numero_nf' in df_tabela_cfop.columns:
                column_config['numero_nf'] = st.column_config.TextColumn(
                    "Número NF"
                )
            if 'cod_natureza_op' in df_tabela_cfop.columns:
                column_config['cod_natureza_op'] = st.column_config.TextColumn(
                    "Cód Natureza Op"
                )
            
            st.dataframe(
                df_tabela_cfop, 
                width='stretch', 
                hide_index=True,
                column_config=column_config
            )
            
            # Botão Excel export
            from io import BytesIO
            buffer_cfop = BytesIO()
            with pd.ExcelWriter(buffer_cfop, engine='openpyxl') as writer:
                df_tabela_cfop.to_excel(writer, index=False, sheet_name='CFOP')
            st.download_button(
                label="📥 Download Excel",
                data=buffer_cfop.getvalue(),
                file_name=f"cfop_{planta_sel}_{ano_sel}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                key="download_excel_cfop"
            )
        else:
            st.info("Sem dados para exibir.")
    
    # Gráfico de barras horizontal
    fig_cfop = plot_cfop_distribution(df_filtered, top_n=top_n_cfop, divisor=divisor, sufixo=sufixo)
    st.plotly_chart(fig_cfop, width='stretch', key="chart_cfop_bar")
    
    # Gráfico de pizza
    fig_cfop_pizza = plot_cfop_pizza(df_filtered, top_n=top_n_cfop)
    st.plotly_chart(fig_cfop_pizza, width='stretch', key="chart_cfop_pizza")

with tab5:
    st.subheader("Dados Detalhados")
    
    # Informações sobre o dataset
    col1, col2 = st.columns(2)
    with col1:
        st.info(f"**Total de registros filtrados:** {len(df_filtered):,}")
    with col2:
        if st.button("⬇️ Download Excel", key="btn_download_excel_dados"):
            from io import BytesIO
            buffer_dados = BytesIO()
            with pd.ExcelWriter(buffer_dados, engine='openpyxl') as writer:
                df_filtered.to_excel(writer, index=False, sheet_name='Dados')
            st.download_button(
                label="Baixar dados filtrados",
                data=buffer_dados.getvalue(),
                file_name=f"fiscal_{planta_sel}_{ano_sel}_{start_date}_{end_date}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                key="download_dados_completo"
            )
    
    # Tabela completa
    st.dataframe(
        df_filtered,
        width='stretch',
        hide_index=True,
        height=600
    )
