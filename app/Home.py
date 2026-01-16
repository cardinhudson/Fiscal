"""
Home Page - Sistema de Análise Fiscal Stellantis
Abas por planta com resumo de métricas
"""

import streamlit as st
import sys
from pathlib import Path

# Adicionar diretório raiz ao path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.utils.load_data import get_available_plantas, load_summary

# Configuração da página
st.set_page_config(
    page_title="APP Fiscal",
    page_icon="📊",
    layout="wide"
)

# Título principal
st.title("📊 APP Fiscal – Grupo Controlling")
st.markdown("---")

# Descrição
st.markdown("""
### Bem-vindo ao Sistema de Análise Fiscal Stellantis

Sistema escalável para análise de dados fiscais das plantas do grupo.

**Funcionalidades:**
- 📈 Análise Fiscal: Visualizações e métricas por planta/ano
- 📤 Extração: Processamento de arquivos Excel para Parquet
- 🔄 Atualização automática de anos e plantas
""")

st.markdown("---")

# Carregar plantas
plantas = get_available_plantas()

# Criar abas por planta
tabs = st.tabs(plantas)

for i, planta in enumerate(plantas):
    with tabs[i]:
        st.subheader(f"Planta: {planta}")
        
        # Carregar resumo da planta
        try:
            summary = load_summary(planta)
            
            if summary['total_registros'] == 0:
                st.info(f"Nenhum dado disponível para {planta}")
                st.markdown("💡 Use a página **Extração** para processar arquivos Excel.")
            else:
                # Métricas
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("Total de Registros", f"{summary['total_registros']:,}")
                
                with col2:
                    st.metric("Valor ICMS Total", f"R$ {summary['total_valor_icms']:,.2f}")
                
                with col3:
                    st.metric("Anos Disponíveis", summary['anos_totais'])
                
                # Lista de anos com dados
                if summary['anos_disponiveis']:
                    st.markdown("**Anos com dados:**")
                    anos_str = ", ".join([str(ano) for ano in sorted(summary['anos_disponiveis'])])
                    st.write(anos_str)
                
                # Botão para ir à análise
                if st.button(f"📊 Analisar {planta}", key=f"btn_{planta}"):
                    st.switch_page("pages/analise_fiscal.py")
        
        except Exception as e:
            st.error(f"Erro ao carregar dados de {planta}: {str(e)}")

st.markdown("---")

# Rodapé
st.markdown("""
<div style="text-align: center; color: gray; padding: 20px;">
Sistema de Análise Fiscal - Stellantis © 2026
</div>
""", unsafe_allow_html=True)
