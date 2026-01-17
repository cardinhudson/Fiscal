"""
Página de Logs - Visualização de histórico de extrações
"""

import streamlit as st
import sys
from pathlib import Path
import pandas as pd
from datetime import datetime

# Adicionar diretório raiz ao path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from extraction.logger import (
    load_extraction_history,
    get_latest_logs,
    read_log_file
)

# Configuração da página
st.set_page_config(
    page_title="Logs de Extração",
    page_icon="📋",
    layout="wide"
)

st.title("📋 Histórico de Extrações")
st.markdown("Visualize o histórico completo de processos de extração de dados")
st.markdown("---")

# Criar abas
tab1, tab2 = st.tabs(["📊 Histórico Resumido", "📄 Logs Detalhados"])

# ==================== TAB 1: HISTÓRICO RESUMIDO ====================
with tab1:
    st.header("Histórico de Execuções")
    
    # Carregar histórico
    history = load_extraction_history()
    
    if not history:
        st.info("ℹ️ Nenhuma extração foi registrada ainda. Execute um processo de extração primeiro.")
    else:
        # Inverter para mostrar mais recentes primeiro
        history = list(reversed(history))
        
        # Filtros
        col1, col2, col3 = st.columns(3)
        
        with col1:
            plantas_disponiveis = sorted(list(set([h['planta'] for h in history])))
            planta_filtro = st.selectbox(
                "Filtrar por Planta",
                ["Todas"] + plantas_disponiveis,
                key="filtro_planta"
            )
        
        with col2:
            anos_disponiveis = sorted(list(set([h['ano'] for h in history])), reverse=True)
            ano_filtro = st.selectbox(
                "Filtrar por Ano",
                ["Todos"] + anos_disponiveis,
                key="filtro_ano"
            )
        
        with col3:
            status_disponiveis = ["Todos", "sucesso", "erro", "parcial", "em_andamento"]
            status_filtro = st.selectbox(
                "Filtrar por Status",
                status_disponiveis,
                key="filtro_status"
            )
        
        # Aplicar filtros
        history_filtered = history
        
        if planta_filtro != "Todas":
            history_filtered = [h for h in history_filtered if h['planta'] == planta_filtro]
        
        if ano_filtro != "Todos":
            history_filtered = [h for h in history_filtered if h['ano'] == ano_filtro]
        
        if status_filtro != "Todos":
            history_filtered = [h for h in history_filtered if h['status'] == status_filtro]
        
        st.markdown(f"**{len(history_filtered)} execuções encontradas**")
        st.markdown("---")
        
        # Exibir histórico
        for i, session in enumerate(history_filtered):
            # Determinar emoji de status
            status_emoji = {
                "sucesso": "✅",
                "erro": "❌",
                "parcial": "⚠️",
                "em_andamento": "🔄"
            }.get(session['status'], "❓")
            
            # Formatar datas
            inicio = datetime.fromisoformat(session['inicio'])
            fim = datetime.fromisoformat(session['fim']) if session['fim'] else None
            
            # Expandir detalhes
            with st.expander(
                f"{status_emoji} **{session['planta']}** - {session['ano']} | "
                f"{inicio.strftime('%d/%m/%Y %H:%M:%S')} | "
                f"{session['total_registros']:,} registros",
                expanded=(i == 0)  # Expandir apenas o primeiro
            ):
                # Informações principais
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric("Status", session['status'].upper())
                
                with col2:
                    st.metric("Registros", f"{session['total_registros']:,}")
                
                with col3:
                    st.metric("Arquivos Processados", f"{session['arquivos_sucesso']}/{session['total_arquivos']}")
                
                with col4:
                    if session['tempo_total_segundos']:
                        tempo_min = session['tempo_total_segundos'] / 60
                        st.metric("Tempo Total", f"{tempo_min:.1f} min")
                    else:
                        st.metric("Tempo Total", "N/A")
                
                # Detalhes da execução
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("**⏱️ Cronologia**")
                    st.write(f"**Início:** {inicio.strftime('%d/%m/%Y %H:%M:%S')}")
                    if fim:
                        st.write(f"**Fim:** {fim.strftime('%d/%m/%Y %H:%M:%S')}")
                    else:
                        st.write("**Fim:** Em andamento")
                
                with col2:
                    st.markdown("**📁 Session ID**")
                    st.code(session['session_id'], language=None)
                
                # Erros
                if session['erros']:
                    st.markdown("**❌ Erros**")
                    for erro in session['erros']:
                        erro_time = datetime.fromisoformat(erro['timestamp'])
                        st.error(f"**{erro_time.strftime('%H:%M:%S')}** - {erro['message']}")
                        if 'exception_type' in erro:
                            st.caption(f"Tipo: {erro['exception_type']}")
                
                # Warnings
                if session['warnings']:
                    st.markdown("**⚠️ Avisos**")
                    for warning in session['warnings']:
                        warning_time = datetime.fromisoformat(warning['timestamp'])
                        st.warning(f"**{warning_time.strftime('%H:%M:%S')}** - {warning['message']}")
                
                # Arquivos processados
                if session['arquivos_processados']:
                    st.markdown("**📄 Arquivos Processados**")
                    
                    # Criar DataFrame
                    arquivos_df = pd.DataFrame(session['arquivos_processados'])
                    
                    # Formatação
                    if 'timestamp' in arquivos_df.columns:
                        arquivos_df['hora'] = pd.to_datetime(arquivos_df['timestamp']).dt.strftime('%H:%M:%S')
                    
                    # Configurar colunas
                    column_config = {
                        'filename': st.column_config.TextColumn('Arquivo', width='large'),
                        'registros': st.column_config.NumberColumn('Registros', format='%d'),
                        'tempo_segundos': st.column_config.NumberColumn('Tempo (s)', format='%.2f'),
                        'status': st.column_config.TextColumn('Status', width='small'),
                        'hora': st.column_config.TextColumn('Hora', width='small')
                    }
                    
                    # Selecionar colunas para exibir
                    cols_exibir = ['filename', 'registros', 'tempo_segundos', 'status']
                    if 'hora' in arquivos_df.columns:
                        cols_exibir.append('hora')
                    
                    st.dataframe(
                        arquivos_df[cols_exibir],
                        width='stretch',
                        hide_index=True,
                        column_config=column_config
                    )

# ==================== TAB 2: LOGS DETALHADOS ====================
with tab2:
    st.header("Logs Detalhados")
    
    # Listar arquivos de log disponíveis
    log_files = get_latest_logs(limit=50)
    
    if not log_files:
        st.info("ℹ️ Nenhum arquivo de log encontrado.")
    else:
        # Selecionar arquivo de log
        log_names = [Path(f).name for f in log_files]
        selected_log = st.selectbox(
            "Selecione um arquivo de log",
            log_names,
            key="select_log_file"
        )
        
        if selected_log:
            selected_path = [f for f in log_files if Path(f).name == selected_log][0]
            
            # Botões de ação
            col1, col2, col3 = st.columns([1, 1, 3])
            
            with col1:
                # Botão para atualizar
                if st.button("🔄 Atualizar", key="btn_refresh_log"):
                    st.rerun()
            
            with col2:
                # Botão para download
                log_content = read_log_file(selected_path)
                st.download_button(
                    label="📥 Download",
                    data=log_content,
                    file_name=selected_log,
                    mime="text/plain",
                    key="btn_download_log"
                )
            
            st.markdown("---")
            
            # Exibir conteúdo do log
            log_content = read_log_file(selected_path)
            
            # Estatísticas do log
            linhas = log_content.split('\n')
            total_linhas = len(linhas)
            erros = len([l for l in linhas if 'ERROR' in l])
            warnings = len([l for l in linhas if 'WARNING' in l])
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total de Linhas", total_linhas)
            with col2:
                st.metric("Erros", erros)
            with col3:
                st.metric("Avisos", warnings)
            
            st.markdown("---")
            
            # Filtro de nível
            nivel_filtro = st.radio(
                "Filtrar por nível",
                ["Todos", "INFO", "WARNING", "ERROR", "DEBUG"],
                horizontal=True
            )
            
            # Aplicar filtro
            if nivel_filtro != "Todos":
                linhas_filtradas = [l for l in linhas if nivel_filtro in l]
            else:
                linhas_filtradas = linhas
            
            # Exibir log
            st.markdown("**📄 Conteúdo do Log:**")
            st.code('\n'.join(linhas_filtradas), language=None)

# ==================== FOOTER ====================
st.markdown("---")
st.caption("💡 **Dica:** Os logs são salvos automaticamente durante cada processo de extração e mantidos por até 100 sessões.")
