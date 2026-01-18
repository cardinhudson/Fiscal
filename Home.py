"""Sistema de Análise Fiscal - Streamlit.

Página Home com consolidação de todas as plantas.

Rodar:
    streamlit run Home.py
"""

import streamlit as st
import pandas as pd
import sys
import shutil
from pathlib import Path
from io import BytesIO
from datetime import datetime


def _ensure_running_via_streamlit() -> None:
    try:
        from streamlit.runtime.scriptrunner import get_script_run_ctx

        if get_script_run_ctx() is None:
            print("Este app deve ser iniciado via Streamlit:")
            print("  C:/GIT/Fiscal/.venv/Scripts/python.exe -m streamlit run Home.py")
            raise SystemExit(0)
    except Exception:
        # Se a API interna mudar, não bloqueia a execução.
        return


_ensure_running_via_streamlit()

# Adicionar diretório raiz ao path
sys.path.insert(0, str(Path(__file__).parent))

from app.utils.load_consolidated_data import (
    get_available_anos_consolidated,
    load_consolidated_mensal,
    load_consolidated_fornecedores,
    load_consolidated_produtos,
    load_consolidated_cfop,
    load_consolidated_cfops_nao_encontrados
)
from app.utils.transform_data import (
    plot_monthly_chart,
    plot_top_fornecedores,
    plot_top_fornecedores_pizza,
    plot_top_produtos,
    plot_top_produtos_pizza,
    plot_cfop_distribution,
    plot_cfop_pizza
)

# Configuração da página
st.set_page_config(
    page_title="Sistema Fiscal Stellantis",
    page_icon="🏭",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Título e descrição
st.title("🏭 Sistema de Análise Fiscal Stellantis")
st.markdown("### Consolidação de Todas as Plantas")

st.markdown("""
Bem-vindo ao Sistema de Análise Fiscal Stellantis! 
Este dashboard apresenta uma visão consolidada de **todas as plantas** para análise estratégica.
""")

# Seletor de Unidade Monetária com radio buttons
st.markdown("---")
unidade_monetaria = st.radio(
    "💰 **Fator conversão:**",
    ["💵 Reais", "📊 Mil (10³)", "📈 Milhões (10⁶)", "🚀 Bilhões (10⁹)"],
    horizontal=True,
    index=2,
    key="unidade_monetaria_home"
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

# Sidebar - Filtros principais
st.sidebar.header("Filtros Principais")

# Seleção de Ano
anos = get_available_anos_consolidated()
if not anos:
    st.warning("⚠️ Nenhum dado consolidado disponível.")
    st.info("💡 Use a página **Extração** para processar arquivos Excel.")
    st.info("📌 Os dados consolidados são criados automaticamente após cada extração.")
    st.stop()

ano_sel = st.sidebar.selectbox("Ano", anos, index=len(anos)-1 if anos else 0)

# Carregar dados consolidados
st.sidebar.info(f"📊 Carregando dados de **{ano_sel}**...")

df_mensal = load_consolidated_mensal(ano_sel)
df_fornecedores = load_consolidated_fornecedores(ano_sel)
df_produtos = load_consolidated_produtos(ano_sel)
df_cfop = load_consolidated_cfop(ano_sel)

# Verificar se há dados
if df_mensal.empty and df_fornecedores.empty and df_produtos.empty and df_cfop.empty:
    st.warning(f"⚠️ Sem dados consolidados para o ano {ano_sel}")
    st.info("💡 Processe dados na página **Extração** para gerar consolidações.")
    st.stop()

# Filtro de Plantas (na página principal)
st.markdown("---")
st.markdown("### 🏭 Filtro de Plantas")

planta_option = "Todas"

if not df_mensal.empty and 'planta' in df_mensal.columns:
    plantas_disponiveis = sorted(df_mensal['planta'].unique().tolist())
    plantas_options = ["Todas"] + plantas_disponiveis
    
    planta_option = st.selectbox(
        "Selecione a planta para análise:",
        plantas_options,
        index=0,
        help="Escolha 'Todas' para visualizar dados de todas as plantas",
        key="filtro_planta_home"
    )
    
    # Aplicar filtro de plantas se não for "Todas"
    if planta_option != "Todas":
        if not df_mensal.empty and 'planta' in df_mensal.columns:
            df_mensal = df_mensal[df_mensal['planta'] == planta_option]
        if not df_fornecedores.empty and 'planta' in df_fornecedores.columns:
            df_fornecedores = df_fornecedores[df_fornecedores['planta'] == planta_option]
        if not df_produtos.empty and 'planta' in df_produtos.columns:
            df_produtos = df_produtos[df_produtos['planta'] == planta_option]
        if not df_cfop.empty and 'planta' in df_cfop.columns:
            df_cfop = df_cfop[df_cfop['planta'] == planta_option]

st.markdown("---")

# Filtros opcionais
st.sidebar.header("Filtros Avançados")

# Filtro de Mês
if 'mes' in df_mensal.columns and not df_mensal.empty:
    meses_raw = sorted(df_mensal['mes'].dropna().unique().tolist())
    if meses_raw:
        # Criar dicionário de mapeamento mês -> nome bonito
        import calendar
        import locale
        try:
            locale.setlocale(locale.LC_TIME, 'pt_BR.UTF-8')
        except:
            try:
                locale.setlocale(locale.LC_TIME, 'Portuguese_Brazil.1252')
            except:
                pass
        
        meses_dict = {}
        for mes in meses_raw:
            try:
                # mes está no formato 'YYYY-MM'
                ano, mes_num = mes.split('-')
                mes_nome = calendar.month_name[int(mes_num)].capitalize()
                meses_dict[mes] = f"{mes_nome}/{ano}"
            except:
                meses_dict[mes] = mes
        
        opcoes_mes = ["Todos"] + [meses_dict[m] for m in meses_raw]
        mes_sel_display = st.sidebar.selectbox(
            "Mês",
            opcoes_mes,
            help="Filtrar por mês",
            key="filtro_mes_home"
        )
        
        if mes_sel_display != "Todos":
            # Encontrar o mês original correspondente
            mes_original = [k for k, v in meses_dict.items() if v == mes_sel_display][0]
            if not df_mensal.empty:
                df_mensal = df_mensal[df_mensal['mes'] == mes_original]
            if not df_fornecedores.empty and 'mes' in df_fornecedores.columns:
                df_fornecedores = df_fornecedores[df_fornecedores['mes'] == mes_original]
            if not df_produtos.empty and 'mes' in df_produtos.columns:
                df_produtos = df_produtos[df_produtos['mes'] == mes_original]
            if not df_cfop.empty and 'mes' in df_cfop.columns:
                df_cfop = df_cfop[df_cfop['mes'] == mes_original]

# Filtro de Entrada/Saída
if 'entrada_saida' in df_mensal.columns and not df_mensal.empty:
    entrada_saida_disponiveis = sorted(df_mensal['entrada_saida'].dropna().unique().tolist())
    if entrada_saida_disponiveis:
        entrada_saida_options = ["Todos"] + entrada_saida_disponiveis
        entrada_saida_sel = st.sidebar.selectbox(
            "Entrada/Saída",
            entrada_saida_options,
            help="Filtrar por tipo de operação",
            key="filtro_entrada_saida_home"
        )
        if entrada_saida_sel != "Todos":
            if not df_mensal.empty:
                df_mensal = df_mensal[df_mensal['entrada_saida'] == entrada_saida_sel]
            if not df_fornecedores.empty and 'entrada_saida' in df_fornecedores.columns:
                df_fornecedores = df_fornecedores[df_fornecedores['entrada_saida'] == entrada_saida_sel]
            if not df_produtos.empty and 'entrada_saida' in df_produtos.columns:
                df_produtos = df_produtos[df_produtos['entrada_saida'] == entrada_saida_sel]
            if not df_cfop.empty and 'entrada_saida' in df_cfop.columns:
                df_cfop = df_cfop[df_cfop['entrada_saida'] == entrada_saida_sel]

# Filtro de CFOP
if 'cfop' in df_mensal.columns and not df_mensal.empty:
    cfop_disponiveis = sorted(df_mensal['cfop'].dropna().unique().tolist())
    if cfop_disponiveis:
        # Converter CFOPs para string para exibição
        cfop_str_list = [str(int(c)) if isinstance(c, float) else str(c) for c in cfop_disponiveis]
        cfop_options = ["Todos"] + cfop_str_list
        cfop_sel = st.sidebar.selectbox(
            "CFOP",
            cfop_options,
            help="Filtrar por Código Fiscal",
            key="filtro_cfop_home"
        )
        if cfop_sel != "Todos":
            # Converter de volta para o tipo original para filtro
            cfop_num = int(cfop_sel)
            if not df_mensal.empty:
                df_mensal = df_mensal[df_mensal['cfop'] == cfop_num]
            if not df_fornecedores.empty and 'cfop' in df_fornecedores.columns:
                df_fornecedores = df_fornecedores[df_fornecedores['cfop'] == cfop_num]
            if not df_produtos.empty and 'cfop' in df_produtos.columns:
                df_produtos = df_produtos[df_produtos['cfop'] == cfop_num]
            if not df_cfop.empty and 'cfop' in df_cfop.columns:
                df_cfop = df_cfop[df_cfop['cfop'] == cfop_num]

# Filtro de Resumo de Operação
if 'resumo_de_operacao' in df_mensal.columns and not df_mensal.empty:
    resumo_disponiveis = sorted(df_mensal['resumo_de_operacao'].dropna().unique().tolist())
    if resumo_disponiveis:
        resumo_options = ["Todos"] + resumo_disponiveis
        resumo_sel = st.sidebar.selectbox(
            "Resumo de Operação",
            resumo_options,
            help="Filtrar por resumo da operação fiscal",
            key="filtro_resumo_home"
        )
        if resumo_sel != "Todos":
            if not df_mensal.empty:
                df_mensal = df_mensal[df_mensal['resumo_de_operacao'] == resumo_sel]
            if not df_fornecedores.empty and 'resumo_de_operacao' in df_fornecedores.columns:
                df_fornecedores = df_fornecedores[df_fornecedores['resumo_de_operacao'] == resumo_sel]
            if not df_produtos.empty and 'resumo_de_operacao' in df_produtos.columns:
                df_produtos = df_produtos[df_produtos['resumo_de_operacao'] == resumo_sel]
            if not df_cfop.empty and 'resumo_de_operacao' in df_cfop.columns:
                df_cfop = df_cfop[df_cfop['resumo_de_operacao'] == resumo_sel]

# Filtro de Código Natureza Operação
if 'cod_natureza_op' in df_mensal.columns and not df_mensal.empty:
    cod_nat_disponiveis = sorted(df_mensal['cod_natureza_op'].dropna().unique().tolist())
    if cod_nat_disponiveis:
        cod_nat_options = ["Todos"] + cod_nat_disponiveis
        cod_nat_sel = st.sidebar.selectbox(
            "Código Natureza Op",
            cod_nat_options,
            help="Filtrar por código da natureza da operação",
            key="filtro_cod_nat_home"
        )
        if cod_nat_sel != "Todos":
            if not df_mensal.empty:
                df_mensal = df_mensal[df_mensal['cod_natureza_op'] == cod_nat_sel]
            if not df_fornecedores.empty and 'cod_natureza_op' in df_fornecedores.columns:
                df_fornecedores = df_fornecedores[df_fornecedores['cod_natureza_op'] == cod_nat_sel]
            if not df_produtos.empty and 'cod_natureza_op' in df_produtos.columns:
                df_produtos = df_produtos[df_produtos['cod_natureza_op'] == cod_nat_sel]
            if not df_cfop.empty and 'cod_natureza_op' in df_cfop.columns:
                df_cfop = df_cfop[df_cfop['cod_natureza_op'] == cod_nat_sel]

# Filtro de Descrição Natureza Operação
if 'descricao_natureza_op' in df_mensal.columns and not df_mensal.empty:
    desc_nat_disponiveis = sorted(df_mensal['descricao_natureza_op'].dropna().unique().tolist())
    if desc_nat_disponiveis:
        desc_nat_options = ["Todos"] + desc_nat_disponiveis
        desc_nat_sel = st.sidebar.selectbox(
            "Descrição Natureza Op",
            desc_nat_options,
            help="Filtrar por descrição da natureza da operação",
            key="filtro_desc_nat_home"
        )
        if desc_nat_sel != "Todos":
            if not df_mensal.empty:
                df_mensal = df_mensal[df_mensal['descricao_natureza_op'] == desc_nat_sel]
            if not df_fornecedores.empty and 'descricao_natureza_op' in df_fornecedores.columns:
                df_fornecedores = df_fornecedores[df_fornecedores['descricao_natureza_op'] == desc_nat_sel]
            if not df_produtos.empty and 'descricao_natureza_op' in df_produtos.columns:
                df_produtos = df_produtos[df_produtos['descricao_natureza_op'] == desc_nat_sel]
            if not df_cfop.empty and 'descricao_natureza_op' in df_cfop.columns:
                df_cfop = df_cfop[df_cfop['descricao_natureza_op'] == desc_nat_sel]

# Filtro de Razão Social (Fornecedor)
if 'razao_social' in df_fornecedores.columns and not df_fornecedores.empty:
    fornecedor_disponiveis = sorted(df_fornecedores['razao_social'].dropna().unique().tolist())
    if fornecedor_disponiveis:
        fornecedor_options = ["Todos"] + fornecedor_disponiveis
        fornecedor_sel = st.sidebar.selectbox(
            "Fornecedor",
            fornecedor_options,
            help="Filtrar por fornecedor",
            key="filtro_fornecedor_home"
        )
        if fornecedor_sel != "Todos":
            df_fornecedores = df_fornecedores[df_fornecedores['razao_social'] == fornecedor_sel]

# Filtro de Descrição Produto
if 'descricao_produto' in df_produtos.columns and not df_produtos.empty:
    produto_disponiveis = sorted(df_produtos['descricao_produto'].dropna().unique().tolist())
    if produto_disponiveis:
        produto_options = ["Todos"] + produto_disponiveis
        produto_sel = st.sidebar.selectbox(
            "Descrição Produto",
            produto_options,
            help="Filtrar por descrição do produto",
            key="filtro_produto_home"
        )
        if produto_sel != "Todos":
            df_produtos = df_produtos[df_produtos['descricao_produto'] == produto_sel]

# Filtro de UF (Estado)
if 'uf' in df_fornecedores.columns and not df_fornecedores.empty:
    uf_disponiveis = sorted(df_fornecedores['uf'].dropna().unique().tolist())
    if uf_disponiveis:
        uf_options = ["Todos"] + uf_disponiveis
        uf_sel = st.sidebar.selectbox(
            "UF (Estado)",
            uf_options,
            help="Filtrar por estado (UF)",
            key="filtro_uf_home"
        )
        if uf_sel != "Todos":
            df_fornecedores = df_fornecedores[df_fornecedores['uf'] == uf_sel]

# Filtro de Município
if 'municipio' in df_fornecedores.columns and not df_fornecedores.empty:
    municipio_disponiveis = sorted(df_fornecedores['municipio'].dropna().unique().tolist())
    if municipio_disponiveis:
        municipio_options = ["Todos"] + municipio_disponiveis
        municipio_sel = st.sidebar.selectbox(
            "Município",
            municipio_options,
            help="Filtrar por município",
            key="filtro_municipio_home"
        )
        if municipio_sel != "Todos":
            df_fornecedores = df_fornecedores[df_fornecedores['municipio'] == municipio_sel]

# Filtro de CST ICMS
if 'cst_icms' in df_fornecedores.columns and not df_fornecedores.empty:
    cst_disponiveis = sorted(df_fornecedores['cst_icms'].dropna().unique().tolist())
    if cst_disponiveis:
        cst_options = ["Todos"] + cst_disponiveis
        cst_sel = st.sidebar.selectbox(
            "CST ICMS",
            cst_options,
            help="Filtrar por CST ICMS",
            key="filtro_cst_home"
        )
        if cst_sel != "Todos":
            df_fornecedores = df_fornecedores[df_fornecedores['cst_icms'] == cst_sel]
            # Aplicar também em produtos e cfop se existir
            if 'cst_icms' in df_produtos.columns and not df_produtos.empty:
                df_produtos = df_produtos[df_produtos['cst_icms'] == cst_sel]
            if 'cst_icms' in df_cfop.columns and not df_cfop.empty:
                df_cfop = df_cfop[df_cfop['cst_icms'] == cst_sel]

# Métricas principais
st.header("📊 Resumo Consolidado")

col1, col2, col3, col4 = st.columns(4)

with col1:
    if not df_fornecedores.empty:
        total_registros = len(df_fornecedores)
        st.metric("Fornecedores Únicos", f"{total_registros:,}")
    else:
        st.metric("Fornecedores Únicos", "N/A")

with col2:
    if not df_mensal.empty and 'valor_icms' in df_mensal.columns:
        total_icms = df_mensal['valor_icms'].sum() / divisor
        label_icms = f"Total ICMS ({sufixo})" if sufixo else "Total ICMS"
        st.metric(label_icms, f"R$ {total_icms:,.2f}")
    else:
        st.metric("Total ICMS", "N/A")

with col3:
    if not df_mensal.empty and 'base_icms_1' in df_mensal.columns:
        total_base = df_mensal['base_icms_1'].sum() / divisor
        label_base = f"Base ICMS ({sufixo})" if sufixo else "Base ICMS"
        st.metric(label_base, f"R$ {total_base:,.2f}")
    else:
        st.metric("Base ICMS", "N/A")

with col4:
    if not df_produtos.empty:
        total_produtos = len(df_produtos)
        st.metric("Produtos Únicos", f"{total_produtos:,}")
    else:
        st.metric("Produtos Únicos", "N/A")

# Visualizações
st.header("📈 Análises Consolidadas")

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📈 Mensal",
    "🏢 Fornecedores",
    "📦 Produtos",
    "🔢 CFOP",
    "📋 Códigos Mastersaf"
])

# TAB 1: MENSAL
with tab1:
    titulo_plantas = f"Evolução Mensal de ICMS - {planta_option if planta_option != 'Todas' else 'Todas as Plantas'}"
    st.subheader(titulo_plantas)
    
    if not df_mensal.empty:
        # Gráfico de Top Plantas por ICMS (apenas se "Todas" estiver selecionado)
        if planta_option == "Todas":
            st.markdown("### 📊 Top Plantas por ICMS")
            
            # Agregar por planta
            df_plantas_agg = df_mensal.groupby('planta').agg({
                'valor_icms': 'sum',
                'base_icms_1': 'sum'
            }).reset_index()
            
            # Aplicar divisor
            df_plantas_agg['valor_icms'] = df_plantas_agg['valor_icms'] / divisor
            df_plantas_agg['base_icms_1'] = df_plantas_agg['base_icms_1'] / divisor
            
            # Ordenar por valor ICMS
            df_plantas_agg = df_plantas_agg.sort_values('valor_icms', ascending=False)
            
            # Criar gráfico de barras
            import plotly.graph_objects as go
            
            fig_plantas = go.Figure(data=[
                go.Bar(
                    x=df_plantas_agg['planta'],
                    y=df_plantas_agg['valor_icms'],
                    text=df_plantas_agg['valor_icms'].apply(lambda x: f'R$ {x:,.2f}'),
                    textposition='auto',
                    marker_color='#1f77b4',
                    hovertemplate='<b>%{x}</b><br>ICMS: R$ %{y:,.2f}<extra></extra>'
                )
            ])
            
            label_icms = f"ICMS ({sufixo})" if sufixo else "ICMS"
            fig_plantas.update_layout(
                xaxis_title="Planta",
                yaxis_title=f"Valor {label_icms}",
                showlegend=False,
                height=400,
                margin=dict(l=50, r=50, t=10, b=50)
            )
            
            st.plotly_chart(fig_plantas, use_container_width=True, key="chart_plantas_icms")
        
        # Gráfico mensal (sempre exibido)
        st.markdown("### 📈 Evolução Mensal")
        fig_month = plot_monthly_chart(df_mensal, divisor=divisor, sufixo=sufixo)
        st.plotly_chart(fig_month, use_container_width=True, key="chart_mensal_home")
        
        st.markdown("---")
        
        # Tabela mensal
        df_month_display = df_mensal.copy()
        df_month_display['valor_icms'] = df_month_display['valor_icms'] / divisor
        df_month_display['base_icms_1'] = df_month_display['base_icms_1'] / divisor
        
        st.dataframe(
            df_month_display[['mes', 'planta', 'valor_icms', 'base_icms_1']],
            use_container_width=True,
            hide_index=True
        )
        
        # Download Excel
        buffer_mensal = BytesIO()
        with pd.ExcelWriter(buffer_mensal, engine='openpyxl') as writer:
            df_month_display.to_excel(writer, index=False, sheet_name='Mensal')
        st.download_button(
            label="📥 Download Excel",
            data=buffer_mensal.getvalue(),
            file_name=f"mensal_consolidado_{ano_sel}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            key="download_excel_mensal_home"
        )
    else:
        st.info("Sem dados mensais disponíveis")

# TAB 2: FORNECEDORES
with tab2:
    st.subheader("Fornecedores por ICMS - Todas as Plantas")
    
    if not df_fornecedores.empty:
        # Seletor de Top
        top_n_forn = st.selectbox(
            "Selecione o Top:",
            [10, 15, 20, 30, 50, 100, 200, 500, 'total'],
            key='top_fornecedores_home'
        )
        
        # Re-agregar por fornecedor (somar todas as plantas)
        df_forn_agg = df_fornecedores.groupby('razao_social').agg({
            'valor_icms': 'sum',
            'base_icms_1': 'sum',
            'quantidade': 'sum'
        }).reset_index().sort_values('valor_icms', ascending=False)
        
        # Gráfico de barras
        fig_forn = plot_top_fornecedores(df_forn_agg, top_n=top_n_forn, divisor=divisor, sufixo=sufixo)
        st.plotly_chart(fig_forn, use_container_width=True, key="chart_fornecedores_home")
        
        # Gráfico de pizza
        fig_forn_pizza = plot_top_fornecedores_pizza(df_forn_agg, top_n=top_n_forn)
        st.plotly_chart(fig_forn_pizza, use_container_width=True, key="chart_fornecedores_pizza_home")
        
        # Tabela detalhada
        with st.expander("📊 Tabela Detalhada"):
            df_forn_display = df_fornecedores.copy()
            df_forn_display['valor_icms'] = df_forn_display['valor_icms'] / divisor
            df_forn_display['base_icms_1'] = df_forn_display['base_icms_1'] / divisor
            
            st.dataframe(
                df_forn_display,
                use_container_width=True,
                hide_index=True
            )
            
            # Download Excel
            buffer_forn = BytesIO()
            with pd.ExcelWriter(buffer_forn, engine='openpyxl') as writer:
                df_forn_display.to_excel(writer, index=False, sheet_name='Fornecedores')
            st.download_button(
                label="📥 Download Excel",
                data=buffer_forn.getvalue(),
                file_name=f"fornecedores_consolidado_{ano_sel}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                key="download_excel_fornecedores_home"
            )
    else:
        st.info("Sem dados de fornecedores disponíveis")

# TAB 3: PRODUTOS
with tab3:
    st.subheader("Produtos por ICMS - Todas as Plantas")
    
    if not df_produtos.empty:
        # Seletor de Top
        top_n_prod = st.selectbox(
            "Selecione o Top:",
            [10, 15, 20, 30, 50, 100, 200, 500, 'total'],
            key='top_produtos_home'
        )
        
        # Re-agregar por produto (somar todas as plantas)
        df_prod_agg = df_produtos.groupby('descricao').agg({
            'valor_icms': 'sum',
            'base_icms_1': 'sum',
            'quantidade': 'sum'
        }).reset_index().sort_values('valor_icms', ascending=False)
        
        # Gráfico de barras
        fig_prod = plot_top_produtos(df_prod_agg, top_n=top_n_prod, divisor=divisor, sufixo=sufixo)
        st.plotly_chart(fig_prod, use_container_width=True, key="chart_produtos_home")
        
        # Gráfico de pizza
        fig_prod_pizza = plot_top_produtos_pizza(df_prod_agg, top_n=top_n_prod)
        st.plotly_chart(fig_prod_pizza, use_container_width=True, key="chart_produtos_pizza_home")
        
        # Tabela detalhada
        with st.expander("📊 Tabela Detalhada"):
            df_prod_display = df_produtos.copy()
            df_prod_display['valor_icms'] = df_prod_display['valor_icms'] / divisor
            df_prod_display['base_icms_1'] = df_prod_display['base_icms_1'] / divisor
            
            st.dataframe(
                df_prod_display,
                use_container_width=True,
                hide_index=True
            )
            
            # Download Excel
            buffer_prod = BytesIO()
            with pd.ExcelWriter(buffer_prod, engine='openpyxl') as writer:
                df_prod_display.to_excel(writer, index=False, sheet_name='Produtos')
            st.download_button(
                label="📥 Download Excel",
                data=buffer_prod.getvalue(),
                file_name=f"produtos_consolidado_{ano_sel}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                key="download_excel_produtos_home"
            )
    else:
        st.info("Sem dados de produtos disponíveis")

# TAB 4: CFOP
with tab4:
    st.subheader("Distribuição por CFOP - Todas as Plantas")
    
    if not df_cfop.empty:
        # Seletor de Top
        top_n_cfop = st.selectbox(
            "Selecione o Top:",
            [10, 15, 20, 30, 50, 100, 200, 500, 'total'],
            key='top_cfop_home'
        )
        
        # Re-agregar por CFOP (somar todas as plantas)
        group_cols = ['cfop']
        if 'descricao_natureza_op' in df_cfop.columns:
            group_cols.append('descricao_natureza_op')
        
        df_cfop_agg = df_cfop.groupby(group_cols).agg({
            'valor_icms': 'sum',
            'base_icms_1': 'sum',
            'quantidade': 'sum'
        }).reset_index().sort_values('valor_icms', ascending=False)
        
        # Gráfico de barras
        fig_cfop = plot_cfop_distribution(df_cfop_agg, top_n=top_n_cfop, divisor=divisor, sufixo=sufixo)
        st.plotly_chart(fig_cfop, use_container_width=True, key="chart_cfop_home")
        
        # Gráfico de pizza
        fig_cfop_pizza = plot_cfop_pizza(df_cfop_agg, top_n=top_n_cfop)
        st.plotly_chart(fig_cfop_pizza, use_container_width=True, key="chart_cfop_pizza_home")
        
        # Tabela detalhada
        with st.expander("📊 Tabela Detalhada"):
            df_cfop_display = df_cfop.copy()
            df_cfop_display['valor_icms'] = df_cfop_display['valor_icms'] / divisor
            df_cfop_display['base_icms_1'] = df_cfop_display['base_icms_1'] / divisor
            
            st.dataframe(
                df_cfop_display,
                use_container_width=True,
                hide_index=True
            )
            
            # Download Excel
            buffer_cfop = BytesIO()
            with pd.ExcelWriter(buffer_cfop, engine='openpyxl') as writer:
                df_cfop_display.to_excel(writer, index=False, sheet_name='CFOP')
            st.download_button(
                label="📥 Download Excel",
                data=buffer_cfop.getvalue(),
                file_name=f"cfop_consolidado_{ano_sel}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                key="download_excel_cfop_home"
            )
    else:
        st.info("Sem dados de CFOP disponíveis")

# TAB 5: CÓDIGOS MASTERSAF
with tab5:
    st.subheader("📋 Tabela de Códigos Mastersaf e Sapiens")
    
    st.markdown("""
    Esta tabela é usada durante a extração para padronizar os códigos fiscais.
    Você pode visualizar e editar os dados diretamente aqui.
    """)
    
    base_path = Path.cwd()
    codigos_path = base_path / "data_raw" / "Códigos Mastersaf e Sapiens.xlsx"
    
    if codigos_path.exists():
        try:
            # Carregar dados
            df_codigos = pd.read_excel(codigos_path)
            
            st.success(f"✅ {len(df_codigos)} CFOPs cadastrados")
            
            st.markdown("---")
            
            # Opções de visualização/edição
            modo = st.radio(
                "Modo:",
                ["👁️ Visualizar", "✏️ Editar"],
                horizontal=True,
                key="modo_codigos_home"
            )
            
            if modo == "👁️ Visualizar":
                # Modo visualização com filtros
                st.markdown("### Visualizar Dados")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    # Filtro por CFOP
                    cfop_filtro = st.text_input(
                        "🔍 Filtrar por CFOP",
                        placeholder="Ex: 5102",
                        help="Digite parte do CFOP para filtrar",
                        key="cfop_filtro_home"
                    )
                
                with col2:
                    # Filtro por descrição
                    desc_filtro = st.text_input(
                        "🔍 Filtrar por Descrição",
                        placeholder="Ex: VENDA",
                        help="Digite parte da descrição para filtrar",
                        key="desc_filtro_home"
                    )
                
                # Aplicar filtros
                df_filtrado = df_codigos.copy()
                
                if cfop_filtro:
                    df_filtrado = df_filtrado[
                        df_filtrado['CFOP'].astype(str).str.contains(cfop_filtro, case=False, na=False)
                    ]
                
                if desc_filtro:
                    df_filtrado = df_filtrado[
                        df_filtrado['DESCRICAO_NATUREZA_OP'].astype(str).str.contains(desc_filtro, case=False, na=False)
                    ]
                
                st.info(f"Mostrando {len(df_filtrado)} de {len(df_codigos)} registros")
                
                # Exibir tabela
                st.dataframe(
                    df_filtrado,
                    use_container_width=True,
                    height=400
                )
                
                # Download
                col1, col2, col3 = st.columns([1, 1, 2])
                with col1:
                    # Download do filtrado como CSV
                    csv = df_filtrado.to_csv(index=False).encode('utf-8')
                    st.download_button(
                        "📥 Baixar CSV (filtrado)",
                        csv,
                        "codigos_filtrados.csv",
                        "text/csv",
                        use_container_width=True,
                        key="download_csv_codigos_home"
                    )
                
                with col2:
                    # Download completo Excel
                    with open(codigos_path, "rb") as f:
                        st.download_button(
                            "📥 Baixar Excel (completo)",
                            f.read(),
                            "Códigos Mastersaf e Sapiens.xlsx",
                            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                            use_container_width=True,
                            key="download_excel_codigos_home"
                        )
            
            else:  # Modo Editar
                st.markdown("### ✏️ Editar Dados")
                
                st.warning("⚠️ **Atenção:** Alterações feitas aqui afetarão a extração de dados futura.")
                
                # Usar st.data_editor para edição
                df_editado = st.data_editor(
                    df_codigos,
                    num_rows="dynamic",  # Permite adicionar/remover linhas
                    use_container_width=True,
                    height=400,
                    key="editor_codigos_home",
                    column_config={
                        "CFOP": st.column_config.NumberColumn(
                            "CFOP",
                            help="Código Fiscal de Operações e Prestações",
                            format="%d",
                            required=True
                        ),
                        "COD_NATUREZA_OP": st.column_config.TextColumn(
                            "COD_NATUREZA_OP",
                            help="Código da Natureza da Operação",
                            required=True
                        ),
                        "DESCRICAO_NATUREZA_OP": st.column_config.TextColumn(
                            "DESCRICAO_NATUREZA_OP",
                            help="Descrição da Natureza da Operação",
                            required=True
                        ),
                        "RESUMO DE OPERAÇÃO": st.column_config.TextColumn(
                            "RESUMO DE OPERAÇÃO",
                            help="Resumo da Operação Fiscal",
                            required=False
                        )
                    }
                )
                
                # Verificar se houve alterações
                if not df_editado.equals(df_codigos):
                    st.info("📝 Há alterações não salvas")
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        if st.button("💾 Salvar Alterações", type="primary", use_container_width=True, key="salvar_codigos_home"):
                            try:
                                # Salvar no Excel
                                df_editado.to_excel(codigos_path, index=False)
                                
                                st.success("✅ Alterações salvas com sucesso!")
                                st.balloons()
                                
                                # Limpar cache
                                from extraction import extracao
                                extracao._df_codigos_cache = None
                                
                                st.rerun()
                                
                            except Exception as e:
                                st.error(f"❌ Erro ao salvar: {str(e)}")
                                st.exception(e)
                    
                    with col2:
                        if st.button("🔄 Cancelar / Recarregar", use_container_width=True, key="cancelar_codigos_home"):
                            st.rerun()
                else:
                    st.success("✅ Nenhuma alteração pendente")
            
            # Tabela de CFOPs não encontrados nos dados processados
            st.markdown("---")
            st.subheader("🔍 CFOPs Não Encontrados na Tabela de Códigos")
            
            with st.expander("📋 Ver CFOPs sem correspondência", expanded=False):
                st.markdown("""
                Esta tabela mostra os **CFOPs** que aparecem nos dados processados mas **não estão cadastrados** 
                na tabela de Códigos Mastersaf. Estes registros ficam marcados como "Não encontrado".
                """)
                
                # Carregar dados consolidados de CFOPs não encontrados
                df_cfops_nao_encontrados = load_consolidated_cfops_nao_encontrados(ano_sel)
                
                if not df_cfops_nao_encontrados.empty:
                    # Aplicar filtro de planta se necessário
                    if planta_option != "Todas":
                        df_cfops_nao_encontrados = df_cfops_nao_encontrados[
                            df_cfops_nao_encontrados['planta'] == planta_option
                        ]
                    
                    if not df_cfops_nao_encontrados.empty:
                        # Preparar dados para exibição
                        df_display = df_cfops_nao_encontrados.copy()
                        
                        # Aplicar divisor nos valores monetários
                        if 'valor_icms' in df_display.columns:
                            df_display['valor_icms'] = df_display['valor_icms'] / divisor
                        if 'base_icms_1' in df_display.columns:
                            df_display['base_icms_1'] = df_display['base_icms_1'] / divisor
                        
                        # Selecionar colunas relevantes para exibição
                        colunas_exibir = ['cfop', 'planta', 'valor_icms', 'base_icms_1', 'quantidade']
                        if 'qtd_notas' in df_display.columns:
                            colunas_exibir.append('qtd_notas')
                        if 'qtd_fornecedores' in df_display.columns:
                            colunas_exibir.append('qtd_fornecedores')
                        if 'qtd_produtos' in df_display.columns:
                            colunas_exibir.append('qtd_produtos')
                        if 'entrada_saida' in df_display.columns:
                            colunas_exibir.append('entrada_saida')
                        if 'primeira_ocorrencia' in df_display.columns:
                            colunas_exibir.append('primeira_ocorrencia')
                        if 'ultima_ocorrencia' in df_display.columns:
                            colunas_exibir.append('ultima_ocorrencia')
                        
                        # Filtrar apenas colunas que existem
                        colunas_exibir = [col for col in colunas_exibir if col in df_display.columns]
                        df_display = df_display[colunas_exibir]
                        
                        # Renomear colunas para melhor visualização
                        label_icms = f"Valor ICMS ({sufixo})" if sufixo else "Valor ICMS"
                        label_base = f"Base ICMS ({sufixo})" if sufixo else "Base ICMS"
                        
                        rename_map = {
                            'cfop': 'CFOP',
                            'planta': 'Planta',
                            'valor_icms': label_icms,
                            'base_icms_1': label_base,
                            'quantidade': 'Quantidade',
                            'qtd_notas': 'Qtd Notas',
                            'qtd_fornecedores': 'Qtd Fornecedores',
                            'qtd_produtos': 'Qtd Produtos',
                            'entrada_saida': 'Tipo',
                            'primeira_ocorrencia': 'Primeira Ocorrência',
                            'ultima_ocorrencia': 'Última Ocorrência'
                        }
                        df_display = df_display.rename(columns=rename_map)
                        
                        st.warning(f"⚠️ Encontrados **{len(df_display)} CFOPs únicos** sem cadastro na tabela de códigos")
                        
                        # Exibir tabela
                        st.dataframe(
                            df_display,
                            use_container_width=True,
                            height=400,
                            hide_index=True
                        )
                        
                        # Botões de ação
                        col1, col2, col3 = st.columns([1, 1, 1])
                        
                        with col1:
                            csv_data = df_display.to_csv(index=False).encode('utf-8-sig')
                            st.download_button(
                                label="📥 Exportar CSV",
                                data=csv_data,
                                file_name=f"cfops_nao_encontrados_{ano_sel}_{planta_option}.csv",
                                mime="text/csv",
                                use_container_width=True,
                                key="download_cfops_nao_encontrados"
                            )
                        
                        with col2:
                            if st.button("➕ Adicionar à Tabela de Códigos", 
                                        use_container_width=True, 
                                        type="primary",
                                        key="btn_add_cfops"):
                                st.session_state['mostrar_editor_cfops'] = True
                                st.rerun()
                        
                        # Editor para adicionar CFOPs não encontrados
                        if st.session_state.get('mostrar_editor_cfops', False):
                            st.markdown("---")
                            st.markdown("### ✏️ Editor de Novos Códigos")
                            st.info("💡 Preencha as informações para os CFOPs não encontrados abaixo:")
                            
                            # Preparar DataFrame para edição
                            cfops_unicos = df_cfops_nao_encontrados['cfop'].unique()
                            
                            # Criar DataFrame no formato da tabela de códigos
                            df_novos_codigos = pd.DataFrame({
                                'CFOP': cfops_unicos,
                                'COD_NATUREZA_OP': [''] * len(cfops_unicos),
                                'DESCRICAO_NATUREZA_OP': [''] * len(cfops_unicos),
                                'RESUMO DE OPERAÇÃO': [''] * len(cfops_unicos)
                            })
                            
                            # Ordenar por CFOP
                            df_novos_codigos = df_novos_codigos.sort_values('CFOP').reset_index(drop=True)
                            
                            # Editor de dados
                            df_editado = st.data_editor(
                                df_novos_codigos,
                                use_container_width=True,
                                height=400,
                                num_rows="fixed",
                                key="editor_novos_cfops",
                                column_config={
                                    "CFOP": st.column_config.NumberColumn(
                                        "CFOP",
                                        help="Código Fiscal - Não editável",
                                        disabled=True,
                                        format="%d"
                                    ),
                                    "COD_NATUREZA_OP": st.column_config.TextColumn(
                                        "Código Natureza Op",
                                        help="Digite o código da natureza da operação",
                                        required=True,
                                        max_chars=10
                                    ),
                                    "DESCRICAO_NATUREZA_OP": st.column_config.TextColumn(
                                        "Descrição Natureza Op",
                                        help="Digite a descrição da natureza da operação",
                                        required=True,
                                        max_chars=200
                                    ),
                                    "RESUMO DE OPERAÇÃO": st.column_config.TextColumn(
                                        "Resumo de Operação",
                                        help="Digite o resumo da operação (opcional)",
                                        required=False,
                                        max_chars=200
                                    )
                                }
                            )
                            
                            # Verificar se há dados preenchidos
                            linhas_preenchidas = df_editado[
                                (df_editado['COD_NATUREZA_OP'].str.strip() != '') & 
                                (df_editado['DESCRICAO_NATUREZA_OP'].str.strip() != '')
                            ]
                            
                            st.info(f"📝 {len(linhas_preenchidas)} de {len(df_editado)} CFOPs preenchidos")
                            
                            # Botões de ação
                            col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 1])
                            
                            with col_btn1:
                                if st.button("❌ Cancelar", use_container_width=True):
                                    st.session_state['mostrar_editor_cfops'] = False
                                    st.rerun()
                            
                            with col_btn2:
                                if st.button("💾 Salvar na Tabela de Códigos", 
                                           use_container_width=True, 
                                           type="primary",
                                           disabled=len(linhas_preenchidas) == 0):
                                    try:
                                        # Carregar tabela existente
                                        codigos_path = Path("data_raw") / "Códigos Mastersaf e Sapiens.xlsx"
                                        
                                        if codigos_path.exists():
                                            df_codigos_existente = pd.read_excel(codigos_path)
                                            
                                            # Filtrar apenas linhas preenchidas
                                            df_para_adicionar = linhas_preenchidas.copy()
                                            
                                            # Converter CFOP para int
                                            df_para_adicionar['CFOP'] = df_para_adicionar['CFOP'].astype(int)
                                            
                                            # Verificar se algum CFOP já existe
                                            cfops_existentes = df_codigos_existente['CFOP'].values
                                            cfops_duplicados = df_para_adicionar[
                                                df_para_adicionar['CFOP'].isin(cfops_existentes)
                                            ]['CFOP'].tolist()
                                            
                                            if cfops_duplicados:
                                                st.warning(f"⚠️ Os seguintes CFOPs já existem na tabela: {cfops_duplicados}")
                                                st.info("Apenas os CFOPs novos serão adicionados.")
                                                df_para_adicionar = df_para_adicionar[
                                                    ~df_para_adicionar['CFOP'].isin(cfops_existentes)
                                                ]
                                            
                                            if not df_para_adicionar.empty:
                                                # Concatenar com tabela existente
                                                df_final = pd.concat([df_codigos_existente, df_para_adicionar], 
                                                                    ignore_index=True)
                                                
                                                # Ordenar por CFOP
                                                df_final = df_final.sort_values('CFOP').reset_index(drop=True)
                                                
                                                # Fazer backup do arquivo original
                                                backup_path = codigos_path.parent / f"Códigos Mastersaf e Sapiens_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
                                                import shutil
                                                shutil.copy2(codigos_path, backup_path)
                                                
                                                # Salvar arquivo atualizado
                                                df_final.to_excel(codigos_path, index=False, engine='openpyxl')
                                                
                                                st.success(f"✅ {len(df_para_adicionar)} CFOPs adicionados com sucesso!")
                                                st.info(f"📁 Backup criado em: {backup_path.name}")
                                                st.balloons()
                                                
                                                # Limpar estado e recarregar
                                                st.session_state['mostrar_editor_cfops'] = False
                                                
                                                # Sugerir reprocessamento
                                                st.warning("🔄 **Importante:** Execute a extração novamente para atualizar os dados com os novos códigos!")
                                                
                                                # Esperar 2 segundos e recarregar
                                                import time
                                                time.sleep(2)
                                                st.rerun()
                                            else:
                                                st.info("ℹ️ Nenhum CFOP novo para adicionar.")
                                        else:
                                            st.error("❌ Arquivo de códigos não encontrado!")
                                    
                                    except Exception as e:
                                        st.error(f"❌ Erro ao salvar: {str(e)}")
                                        st.exception(e)
                    else:
                        st.success("✅ Todos os CFOPs da planta selecionada foram encontrados na tabela de códigos!")
                else:
                    st.success("✅ Todos os CFOPs foram encontrados na tabela de códigos!")
        
        except Exception as e:
            st.error(f"❌ Erro ao carregar dados de CFOPs não encontrados: {str(e)}")
            st.exception(e)
    else:
        st.warning("⚠️ Arquivo de códigos não encontrado")
        st.info(f"Esperado em: `{codigos_path}`")
        st.markdown("💡 Faça upload do arquivo na página **Extração → Códigos Mastersaf**")

# Botão de exportação consolidada no final da página
st.markdown("---")
st.markdown("### 📥 Exportação de Dados")

col_export1, col_export2, col_export3 = st.columns([1, 2, 1])

with col_export2:
    if st.button("📥 Exportar Tudo para Excel", use_container_width=True, type="primary", key="btn_export_final"):
        try:
            import os
            from io import BytesIO
            
            # Caminho Downloads do usuário
            downloads_path = os.path.join(os.path.expanduser("~"), "Downloads")
            filename = f"Fiscal_Consolidado_{ano_sel}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
            filepath = os.path.join(downloads_path, filename)
            
            # Criar Excel com múltiplas abas
            with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
                if not df_mensal.empty:
                    df_mensal.to_excel(writer, sheet_name='Mensal', index=False)
                if not df_fornecedores.empty:
                    df_fornecedores.to_excel(writer, sheet_name='Fornecedores', index=False)
                if not df_produtos.empty:
                    df_produtos.to_excel(writer, sheet_name='Produtos', index=False)
                if not df_cfop.empty:
                    df_cfop.to_excel(writer, sheet_name='CFOP', index=False)
            
            st.success(f"✅ Arquivo salvo em: `{filepath}`")
            st.info(f"📊 Exportadas {len([d for d in [df_mensal, df_fornecedores, df_produtos, df_cfop] if not d.empty])} abas")
            st.balloons()
            
        except Exception as e:
            st.error(f"❌ Erro ao exportar: {str(e)}")

st.markdown("")
st.caption("Sistema de Análise Fiscal Stellantis - Desenvolvido pela Equipe Fiscal")
