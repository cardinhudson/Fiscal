"""
Página de Extração - Upload e Processamento de arquivos Excel para Parquet
"""

import streamlit as st
import sys
from pathlib import Path
import shutil

# Adicionar diretório raiz ao path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from extraction.extracao import (
    load_plantas,
    load_anos,
    process_raw_excel_to_parquet,
    ensure_structure,
    add_planta
)

# Configuração da página
st.set_page_config(
    page_title="Extração de Dados",
    page_icon="📤",
    layout="wide"
)

st.title("📤 Extração de Dados")
st.markdown("Faça upload e processe arquivos Excel para formato Parquet otimizado")
st.markdown("---")

# Criar abas para Upload e Processamento
tab1, tab2 = st.tabs(["📁 Upload de Arquivos", "⚙️ Processar Dados"])

# ==================== TAB 1: UPLOAD ====================
with tab1:
    st.header("Upload de Arquivos Excel")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Input para planta (com opção de criar nova)
        plantas_existentes = load_plantas()
        planta_opcao = st.radio(
            "Planta",
            ["Selecionar existente", "Criar nova"],
            horizontal=True
        )
        
        if planta_opcao == "Selecionar existente":
            planta_upload = st.selectbox("Selecione a Planta", plantas_existentes, key="upload_planta_sel")
        else:
            planta_upload = st.text_input(
                "Nome da nova planta",
                placeholder="Ex: Porto Real, Goiana...",
                key="upload_planta_nova"
            )
            if planta_upload and planta_upload not in plantas_existentes:
                st.info(f"✨ Nova planta '{planta_upload}' será criada automaticamente")
    
    with col2:
        # Input para ano (com opção de criar novo)
        if planta_opcao == "Selecionar existente":
            anos_existentes = load_anos(planta_upload)
        else:
            anos_existentes = []
        
        ano_opcao = st.radio(
            "Ano",
            ["Selecionar existente", "Criar novo"] if anos_existentes else ["Criar novo"],
            horizontal=True
        )
        
        if ano_opcao == "Selecionar existente" and anos_existentes:
            ano_upload = st.selectbox("Selecione o Ano", anos_existentes, key="upload_ano_sel")
        else:
            ano_upload = st.number_input(
                "Ano",
                min_value=2000,
                max_value=2050,
                value=2026,
                step=1,
                key="upload_ano_novo"
            )
            if anos_existentes and ano_upload not in anos_existentes:
                st.info(f"✨ Novo ano '{ano_upload}' será criado automaticamente")
    
    st.markdown("---")
    
    # Upload de arquivos
    st.subheader("Selecione os arquivos Excel")
    
    uploaded_files = st.file_uploader(
        "Arraste e solte arquivos Excel aqui ou clique para selecionar",
        type=["xlsx", "xls"],
        accept_multiple_files=True,
        help="Você pode selecionar múltiplos arquivos de uma vez"
    )
    
    if uploaded_files:
        st.success(f"✅ {len(uploaded_files)} arquivo(s) selecionado(s)")
        
        # Mostrar lista de arquivos
        with st.expander("Ver arquivos selecionados"):
            for i, file in enumerate(uploaded_files, 1):
                st.write(f"{i}. {file.name} ({file.size / 1024:.1f} KB)")
        
        # Opção de substituir ou adicionar
        modo_upload = st.radio(
            "O que fazer com arquivos existentes?",
            ["Adicionar novos arquivos", "Substituir todos os arquivos"],
            help="'Adicionar' mantém arquivos existentes. 'Substituir' remove todos e adiciona os novos."
        )
        
        # Botão de upload
        if st.button("📤 Fazer Upload", type="primary", use_container_width=True, key="btn_fazer_upload"):
            if not planta_upload or not ano_upload:
                st.error("❌ Selecione/digite a planta e o ano")
            else:
                try:
                    # Se for nova planta, adicionar ao JSON
                    if planta_opcao == "Criar nova" and planta_upload not in plantas_existentes:
                        if add_planta(planta_upload):
                            st.success(f"✨ Nova planta '{planta_upload}' adicionada ao sistema")
                            st.cache_data.clear()  # Limpar cache para atualizar listas
                    
                    # Criar estrutura de diretórios
                    ensure_structure(planta_upload, ano_upload)
                    
                    base_path = Path(__file__).parent.parent.parent
                    target_path = base_path / "data_raw" / planta_upload / str(ano_upload)
                    
                    # Se modo substituir, limpar pasta primeiro
                    if modo_upload == "Substituir todos os arquivos":
                        if target_path.exists():
                            for file in target_path.glob("*.xlsx"):
                                file.unlink()
                            for file in target_path.glob("*.xls"):
                                file.unlink()
                            st.info("🗑️ Arquivos antigos removidos")
                    
                    # Salvar arquivos
                    progress_bar = st.progress(0)
                    status_text = st.empty()
                    
                    for i, uploaded_file in enumerate(uploaded_files):
                        # Atualizar progresso
                        progress = int((i / len(uploaded_files)) * 100)
                        progress_bar.progress(progress)
                        status_text.text(f"Salvando {uploaded_file.name}...")
                        
                        # Salvar arquivo
                        file_path = target_path / uploaded_file.name
                        with open(file_path, "wb") as f:
                            f.write(uploaded_file.getbuffer())
                    
                    # Finalizar
                    progress_bar.progress(100)
                    status_text.text("Concluído!")
                    st.success(f"✅ {len(uploaded_files)} arquivo(s) enviado(s) com sucesso para {target_path}")
                    st.balloons()
                    
                    # Limpar cache
                    st.cache_data.clear()
                    
                except Exception as e:
                    st.error(f"❌ Erro ao fazer upload: {str(e)}")
                    st.exception(e)
    else:
        st.info("👆 Selecione um ou mais arquivos Excel para fazer upload")

# ==================== TAB 2: PROCESSAR ====================
with tab2:
    st.header("Processar Arquivos Excel")
    
    col1, col2 = st.columns(2)
    
    with col1:
        plantas = load_plantas()
        planta_proc = st.selectbox("Selecione a Planta", plantas, key="proc_planta")
    
    with col2:
        anos = load_anos(planta_proc)
        if not anos:
            st.warning(f"Nenhum ano disponível para {planta_proc}")
            st.stop()
        ano_proc = st.selectbox("Selecione o Ano", anos, index=len(anos)-1 if anos else 0, key="proc_ano")
    
    st.markdown("---")
    
    # Informações sobre diretórios
    base_path = Path(__file__).parent.parent.parent
    raw_path = base_path / "data_raw" / planta_proc / str(ano_proc)
    parquet_path = base_path / "data_parquet" / planta_proc / str(ano_proc)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.info(f"**Diretório de entrada (Excel):**\n\n`{raw_path}`")
        
        if raw_path.exists():
            excel_files = list(raw_path.glob("*.xlsx")) + list(raw_path.glob("*.xls"))
            st.success(f"✅ {len(excel_files)} arquivo(s) Excel encontrado(s)")
            
            # Mostrar últimas modificações
            if excel_files:
                from datetime import datetime
                latest_file = max(excel_files, key=lambda f: f.stat().st_mtime)
                latest_time = datetime.fromtimestamp(latest_file.stat().st_mtime)
                st.caption(f"Última modificação: {latest_time.strftime('%d/%m/%Y %H:%M')}")
        else:
            st.warning("⚠️ Diretório não existe")
    
    with col2:
        st.info(f"**Diretório de saída (Parquet):**\n\n`{parquet_path}`")
        
        if parquet_path.exists():
            parquet_files = list(parquet_path.glob("*.parquet"))
            if parquet_files:
                st.success(f"✅ Arquivo Parquet existente")
                
                # Mostrar última modificação do Parquet
                from datetime import datetime
                from extraction.extracao import get_parquet_last_modified
                last_mod = get_parquet_last_modified(planta_proc, ano_proc)
                if last_mod:
                    st.caption(f"Última atualização: {last_mod.strftime('%d/%m/%Y %H:%M')}")
            else:
                st.info("ℹ️ Nenhum arquivo Parquet ainda")
        else:
            st.info("ℹ️ Diretório será criado ao processar")
    
    st.markdown("---")
    
    # Modo de processamento
    st.subheader("Opções de Processamento")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        modo_proc = st.radio(
            "Modo de processamento",
            ["🔄 Incremental (somente novos/modificados)", "♻️ Completo (todos os arquivos)"],
            help="Incremental processa apenas arquivos novos ou modificados após o último processamento. Completo processa todos os arquivos."
        )
        
        modo = 'new' if '🔄' in modo_proc else 'all'
        
        st.markdown("""
        **Recursos do processamento:**
        - ✅ Conversão automática de números BR → US
        - ✅ Padronização de colunas (snake_case)
        - ✅ Deduplicação automática
        - ✅ Append de novos dados aos existentes
        - ✅ Detecção automática do ano
        - ✅ Validação de integridade
        """)
    
    with col2:
        if st.button("🚀 Processar", type="primary", use_container_width=True, key="btn_processar"):
            if not raw_path.exists():
                st.error("❌ Diretório de entrada não existe!")
            else:
                excel_files = list(raw_path.glob("*.xlsx")) + list(raw_path.glob("*.xls"))
                
                if not excel_files:
                    st.warning("⚠️ Nenhum arquivo Excel encontrado no diretório!")
                else:
                    # Criar barra de progresso e status
                    progress_bar = st.progress(0)
                    col_status1, col_status2 = st.columns(2)
                    status_text = col_status1.empty()
                    step_text = col_status2.empty()
                    
                    def update_progress(percent, total_percent, message, step):
                        """
                        Callback para atualizar progresso com percentual e tags.
                        Args:
                            percent: Percentual atual (0-100)
                            total_percent: Total de percentual (sempre 100)
                            message: Mensagem principal
                            step: Tag do passo atual
                        """
                        progress_bar.progress(percent)
                        status_text.markdown(f"**{message}**")
                        step_text.markdown(f"🏷️ `{step}` • **{percent}%**")
                    
                    # Processar
                    try:
                        sucesso, mensagem, total_registros = process_raw_excel_to_parquet(
                            planta_proc,
                            ano_proc,
                            mode=modo,
                            progress_callback=update_progress
                        )
                        
                        if sucesso:
                            st.success(f"✅ {mensagem}")
                            st.balloons()
                            
                            # Limpar cache
                            st.cache_data.clear()
                            
                            # Forçar rerun para atualizar estatísticas
                            st.rerun()
                            
                        else:
                            st.error(f"❌ {mensagem}")
                            
                    except Exception as e:
                        st.error(f"❌ Erro ao processar: {str(e)}")
                        st.exception(e)

# ==================== ESTATÍSTICAS ====================
st.markdown("---")
st.header("📊 Estatísticas dos Dados Processados")

# Selecionar planta e ano para estatísticas
col1, col2 = st.columns(2)

with col1:
    planta_stats = st.selectbox("Planta", load_plantas(), key="stats_planta")

with col2:
    anos_stats = load_anos(planta_stats)
    if anos_stats:
        ano_stats = st.selectbox("Ano", anos_stats, index=len(anos_stats)-1, key="stats_ano")
    else:
        st.warning("Nenhum ano disponível")
        st.stop()

base_path = Path(__file__).parent.parent.parent
parquet_path = base_path / "data_parquet" / planta_stats / str(ano_stats)

if parquet_path.exists():
    parquet_files = list(parquet_path.glob("*.parquet"))
    
    if parquet_files:
        import pandas as pd
        
        for pq_file in parquet_files:
            df = pd.read_parquet(pq_file)
            
            st.subheader(f"Arquivo: {pq_file.name}")
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Registros", f"{len(df):,}")
            
            with col2:
                if 'valor_icms' in df.columns:
                    total_icms = df['valor_icms'].sum()
                    st.metric("Total ICMS", f"R$ {total_icms:,.2f}")
                else:
                    st.metric("Total ICMS", "N/A")
            
            with col3:
                if 'data_fiscal' in df.columns:
                    min_date = df['data_fiscal'].min()
                    st.metric("Data Inicial", min_date.strftime('%d/%m/%Y'))
                else:
                    st.metric("Data Inicial", "N/A")
            
            with col4:
                if 'data_fiscal' in df.columns:
                    max_date = df['data_fiscal'].max()
                    st.metric("Data Final", max_date.strftime('%d/%m/%Y'))
                else:
                    st.metric("Data Final", "N/A")
            
            # Informações adicionais
            col1, col2 = st.columns(2)
            
            with col1:
                # Mostrar colunas disponíveis
                with st.expander("Ver Colunas Disponíveis"):
                    st.write(df.columns.tolist())
            
            with col2:
                # Mostrar tipos de dados
                with st.expander("Ver Tipos de Dados"):
                    st.write(df.dtypes.to_dict())
    else:
        st.info("ℹ️ Nenhum arquivo Parquet encontrado. Faça upload e processe os dados primeiro.")
else:
    st.info("ℹ️ Diretório não existe. Faça upload e processe os dados primeiro.")

