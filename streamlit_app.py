"""Sistema de Análise Fiscal - Streamlit.

Entrypoint recomendado pelo Streamlit (nome padrão: streamlit_app.py).

Rodar:
    streamlit run streamlit_app.py
"""

import streamlit as st

from app.utils.load_data import get_available_plantas, load_summary


st.set_page_config(
    page_title="APP Fiscal",
    page_icon="📊",
    layout="wide",
)

st.title("📊 APP Fiscal – Grupo Controlling")
st.markdown("---")

st.markdown(
    """
### Bem-vindo ao Sistema de Análise Fiscal Stellantis

Sistema escalável para análise de dados fiscais das plantas do grupo.

**Funcionalidades:**
- 📈 Análise Fiscal: Visualizações e métricas por planta/ano
- 📤 Extração: Processamento de arquivos Excel para Parquet
- 🔄 Atualização automática de anos e plantas
"""
)

st.markdown("---")

plantas = get_available_plantas()

tabs = st.tabs(plantas)
for i, planta in enumerate(plantas):
    with tabs[i]:
        st.subheader(f"Planta: {planta}")

        try:
            summary = load_summary(planta)

            if summary["total_registros"] == 0:
                st.info(f"Nenhum dado disponível para {planta}")
                st.markdown("💡 Use a página **Extração** para processar arquivos Excel.")
            else:
                col1, col2, col3 = st.columns(3)

                with col1:
                    st.metric("Total de Registros", f"{summary['total_registros']:,}")

                with col2:
                    st.metric("Valor ICMS Total", f"R$ {summary['total_valor_icms']:,.2f}")

                with col3:
                    st.metric("Anos Disponíveis", summary["anos_totais"])

                if summary["anos_disponiveis"]:
                    st.markdown("**Anos com dados:**")
                    anos_str = ", ".join(
                        [str(ano) for ano in sorted(summary["anos_disponiveis"])]
                    )
                    st.write(anos_str)

                if st.button(f"📊 Analisar {planta}", key=f"btn_{planta}"):
                    st.switch_page("pages/analise_fiscal.py")

        except Exception as e:
            st.error(f"Erro ao carregar dados de {planta}: {str(e)}")

st.markdown("---")

st.markdown(
    """
<div style="text-align: center; color: gray; padding: 20px;">
Sistema de Análise Fiscal - Stellantis © 2026
</div>
""",
    unsafe_allow_html=True,
)
