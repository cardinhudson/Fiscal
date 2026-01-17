"""Sistema de Análise Fiscal - Streamlit.

Página Home com consolidação de todas as plantas.

Rodar:
    streamlit run Home.py
"""

import streamlit as st
import pandas as pd
import sys
from pathlib import Path
from io import BytesIO


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
    load_consolidated_cfop
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

st.markdown("---")

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

# Filtros opcionais
st.sidebar.header("Filtros Opcionais")

# Filtro de Plantas (multi-seleção)
if 'planta' in df_mensal.columns:
    plantas_disponiveis = sorted(df_mensal['planta'].unique().tolist())
    plantas_sel = st.sidebar.multiselect(
        "Plantas",
        plantas_disponiveis,
        default=plantas_disponiveis,
        help="Selecione uma ou mais plantas para filtrar"
    )
    
    # Aplicar filtro de plantas
    if plantas_sel:
        if not df_mensal.empty:
            df_mensal = df_mensal[df_mensal['planta'].isin(plantas_sel)]
        if not df_fornecedores.empty:
            df_fornecedores = df_fornecedores[df_fornecedores['planta'].isin(plantas_sel)]
        if not df_produtos.empty:
            df_produtos = df_produtos[df_produtos['planta'].isin(plantas_sel)]
        if not df_cfop.empty:
            df_cfop = df_cfop[df_cfop['planta'].isin(plantas_sel)]

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
    st.subheader("Evolução Mensal de ICMS - Todas as Plantas")
    
    if not df_mensal.empty:
        # Gráfico mensal
        fig_month = plot_monthly_chart(df_mensal, divisor=divisor, sufixo=sufixo)
        st.plotly_chart(fig_month, use_container_width=True, key="chart_mensal_home")
        
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
                        "CFOP": st.column_config.TextColumn(
                            "CFOP",
                            help="Código Fiscal de Operações e Prestações",
                            max_chars=4,
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
            
        except Exception as e:
            st.error(f"❌ Erro ao carregar arquivo: {str(e)}")
            st.exception(e)
    else:
        st.warning("⚠️ Arquivo de códigos não encontrado")
        st.info(f"Esperado em: `{codigos_path}`")
        st.markdown("💡 Faça upload do arquivo na página **Extração → Códigos Mastersaf**")
