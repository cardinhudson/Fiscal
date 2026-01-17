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

# Criar abas para Upload, Processamento e Códigos
tab1, tab2, tab3 = st.tabs(["📁 Upload de Arquivos", "⚙️ Processar Dados", "📋 Códigos Mastersaf"])

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
    
    st.info("💡 **Dica:** Para selecionar vários arquivos de uma vez, use Ctrl+A (selecionar todos) ou Ctrl+Click (selecionar múltiplos) no seletor de arquivos")
    
    uploaded_files = st.file_uploader(
        "Arraste e solte arquivos Excel aqui ou clique para selecionar",
        type=["xlsx", "xls"],
        accept_multiple_files=True,
        help="Você pode selecionar múltiplos arquivos de uma vez. Use Ctrl+A para selecionar toda a pasta."
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
        if st.button("📤 Fazer Upload", type="primary", width='stretch', key="btn_fazer_upload"):
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
    
    # Opção de modo de processamento
    st.subheader("🎯 Modo de Processamento")
    modo_processamento = st.radio(
        "Escolha o modo:",
        options=["📄 Uma planta/ano específico", "📅 Todos os anos de uma planta", "🌐 Todas as plantas e anos"],
        index=0,
        horizontal=True,
        help="Selecione como deseja processar os arquivos"
    )
    
    st.markdown("---")
    
    if modo_processamento == "📄 Uma planta/ano específico":
        # Interface normal - uma planta por vez
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
    
    elif modo_processamento == "📅 Todos os anos de uma planta":
        # Interface para selecionar planta e processar todos os anos
        plantas = load_plantas()
        planta_proc = st.selectbox("Selecione a Planta", plantas, key="proc_planta_all_anos")
        
        st.markdown("---")
        
        # Descobrir anos disponíveis para esta planta
        base_path = Path(__file__).parent.parent.parent
        data_raw = base_path / "data_raw" / planta_proc
        
        anos_disponiveis = []
        if data_raw.exists():
            for ano_dir in data_raw.iterdir():
                if ano_dir.is_dir():
                    excel_files = list(ano_dir.glob("*.xlsx")) + list(ano_dir.glob("*.xls"))
                    if excel_files:
                        try:
                            anos_disponiveis.append(int(ano_dir.name))
                        except ValueError:
                            continue
        
        if anos_disponiveis:
            anos_disponiveis = sorted(anos_disponiveis)
            st.success(f"✅ {len(anos_disponiveis)} ano(s) com dados encontrado(s): {', '.join(map(str, anos_disponiveis))}")
            
            # Mostrar informações sobre cada ano
            with st.expander("📋 Ver detalhes de cada ano"):
                for ano in anos_disponiveis:
                    ano_path = base_path / "data_raw" / planta_proc / str(ano)
                    excel_files = list(ano_path.glob("*.xlsx")) + list(ano_path.glob("*.xls"))
                    st.markdown(f"**{ano}**: {len(excel_files)} arquivo(s) Excel")
        else:
            st.warning(f"⚠️ Nenhum ano com dados encontrado para {planta_proc}")
            st.stop()
    
    else:  # modo_processamento == "🌐 Todas as plantas e anos"
        # Modo processar todas - mostrar resumo
        st.markdown("---")
        st.info("### 🌐 Modo: Processar Todas as Plantas")
        st.markdown("""
        O sistema irá processar **automaticamente** todas as plantas e anos que possuem arquivos Excel em `data_raw/`.
        
        **Ordem de processamento:**
        1. Busca todas as pastas em data_raw/
        2. Para cada planta, busca todos os anos disponíveis
        3. Valida e processa cada combinação planta/ano
        4. Gera consolidações automaticamente
        """)
        
        # Descobrir plantas e anos disponíveis
        base_path = Path(__file__).parent.parent.parent
        data_raw = base_path / "data_raw"
        
        plantas_disponiveis = []
        if data_raw.exists():
            for planta_dir in data_raw.iterdir():
                if planta_dir.is_dir() and planta_dir.name != "Códigos Mastersaf e Sapiens.xlsx":
                    anos_planta = []
                    for ano_dir in planta_dir.iterdir():
                        if ano_dir.is_dir():
                            excel_files = list(ano_dir.glob("*.xlsx")) + list(ano_dir.glob("*.xls"))
                            if excel_files:
                                try:
                                    anos_planta.append(int(ano_dir.name))
                                except ValueError:
                                    continue
                    if anos_planta:
                        plantas_disponiveis.append({
                            'planta': planta_dir.name,
                            'anos': sorted(anos_planta)
                        })
        
        if plantas_disponiveis:
            st.success(f"✅ {len(plantas_disponiveis)} planta(s) encontrada(s) com dados")
            
            # Mostrar resumo em tabela
            with st.expander("📋 Ver detalhes do que será processado"):
                for item in plantas_disponiveis:
                    st.markdown(f"**{item['planta']}**: {', '.join(map(str, item['anos']))}")
        else:
            st.warning("⚠️ Nenhuma planta com dados encontrada em data_raw/")
            st.stop()
    
    st.markdown("---")
    
    # Modo de processamento
    st.subheader("Opções de Processamento")
    
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
    - ✅ Merge com tabela de Códigos Mastersaf
    """)
    
    st.markdown("---")
    
    # Botão de processar (abaixo das opções)
    if modo_processamento == "📄 Uma planta/ano específico":
        btn_label = "🚀 Processar Extração"
    elif modo_processamento == "📅 Todos os anos de uma planta":
        btn_label = f"📅 Processar TODOS os Anos de {planta_proc}"
    else:
        btn_label = "🌐 Processar TODAS as Plantas e Anos"
    
    if st.button(btn_label, type="primary", use_container_width=True, key="btn_processar"):
        from extraction.extracao import process_raw_excel_to_parquet, validate_excel_files
        from datetime import datetime
        
        base_path = Path(__file__).parent.parent.parent
        
        # Preparar lista de plantas/anos para processar
        if modo_processamento == "🌐 Todas as plantas e anos":
            # Modo todas as plantas - descobrir novamente
            data_raw = base_path / "data_raw"
            plantas_disponiveis = []
            if data_raw.exists():
                for planta_dir in data_raw.iterdir():
                    if planta_dir.is_dir() and planta_dir.name != "Códigos Mastersaf e Sapiens.xlsx":
                        anos_planta = []
                        for ano_dir in planta_dir.iterdir():
                            if ano_dir.is_dir():
                                excel_files = list(ano_dir.glob("*.xlsx")) + list(ano_dir.glob("*.xls"))
                                if excel_files:
                                    try:
                                        anos_planta.append(int(ano_dir.name))
                                    except ValueError:
                                        continue
                        if anos_planta:
                            plantas_disponiveis.append({
                                'planta': planta_dir.name,
                                'anos': sorted(anos_planta)
                            })
            
            tarefas = []
            for item in plantas_disponiveis:
                for ano in item['anos']:
                    tarefas.append({'planta': item['planta'], 'ano': ano})
            
            if not tarefas:
                st.error("❌ Nenhuma planta/ano para processar!")
                st.stop()
            
            st.info(f"📦 Total de {len(tarefas)} combinação(ões) planta/ano para processar")
        
        elif modo_processamento == "📅 Todos os anos de uma planta":
            # Modo todos os anos de uma planta
            tarefas = []
            for ano in anos_disponiveis:
                tarefas.append({'planta': planta_proc, 'ano': ano})
            
            if not tarefas:
                st.error("❌ Nenhum ano para processar!")
                st.stop()
            
            st.info(f"📦 Total de {len(tarefas)} ano(s) de {planta_proc} para processar")
        
        else:
            # Modo uma planta
            raw_path = base_path / "data_raw" / planta_proc / str(ano_proc)
            if not raw_path.exists():
                st.error("❌ Diretório de entrada não existe!")
                st.stop()
            
            excel_files = list(raw_path.glob("*.xlsx")) + list(raw_path.glob("*.xls"))
            if not excel_files:
                st.warning("⚠️ Nenhum arquivo Excel encontrado no diretório!")
                st.stop()
            
            tarefas = [{'planta': planta_proc, 'ano': ano_proc}]
        
        # Determinar se é modo batch (múltiplas tarefas)
        modo_batch = len(tarefas) > 1
        
        # Processamento
        st.markdown("---")
        st.subheader("📊 Status da Extração")
        
        # STATUS AO VIVO (separado do log histórico)
        st.markdown("### 🔴 Status Atual")
        status_atual_container = st.empty()
        arquivo_atual_container = st.empty()
        
        # Containers para progresso
        if modo_batch:
            st.markdown(f"### 🌐 Processando {len(tarefas)} planta(s)/ano(s)")
            global_progress = st.progress(0)
            global_status = st.empty()
        else:
            individual_progress = st.progress(0)
            individual_status = st.empty()
        
        # Container para log HISTÓRICO
        st.markdown("### 📝 Log Completo")
        with st.expander("📋 Ver log detalhado", expanded=False):
            log_display = st.empty()
        
        # Inicializar lista de logs
        if 'extraction_logs' not in st.session_state:
            st.session_state.extraction_logs = []
        st.session_state.extraction_logs = []
        
        # Função auxiliar para atualizar o log display
        def atualizar_log():
            """Atualiza o display do log em tempo real"""
            log_text = "\n".join(st.session_state.extraction_logs[-150:])  # Últimas 150 linhas
            log_display.code(log_text, language="log")
        
        # Contadores
        total_tarefas = len(tarefas)
        tarefas_concluidas = 0
        tarefas_sucesso = 0
        tarefas_erro = 0
        
        # Processar cada tarefa
        for idx, tarefa in enumerate(tarefas):
            planta_atual = tarefa['planta']
            ano_atual = tarefa['ano']
            
            # ATUALIZAR STATUS ATUAL IMEDIATAMENTE
            status_atual_container.info(f"🏭 **Planta:** {planta_atual} | **Ano:** {ano_atual} | **Tarefa:** {idx+1}/{total_tarefas}")
            arquivo_atual_container.warning(f"⏳ Iniciando validação...")
            
            # Log de início
            timestamp = datetime.now().strftime("%H:%M:%S")
            log_entry = f"[{timestamp}] [INICIANDO] 🏭 Planta: {planta_atual} | Ano: {ano_atual}"
            st.session_state.extraction_logs.append(log_entry)
            st.session_state.extraction_logs.append("-" * 80)
            atualizar_log()
            
            # Atualizar progresso global
            if modo_batch:
                progresso_global = int((idx / total_tarefas) * 100)
                global_progress.progress(progresso_global)
                global_status.info(f"📍 Processando {idx+1}/{total_tarefas}: **{planta_atual} - {ano_atual}**")
            
            # Validação
            timestamp = datetime.now().strftime("%H:%M:%S")
            log_entry = f"[{timestamp}] [VALIDANDO] Verificando arquivos..."
            st.session_state.extraction_logs.append(log_entry)
            atualizar_log()
            
            # ATUALIZAR STATUS ATUAL
            arquivo_atual_container.info(f"🔍 Validando arquivos Excel...")
            
            sucesso_validacao, mensagem_validacao, problemas = validate_excel_files(planta_atual, ano_atual)
            
            if not sucesso_validacao:
                timestamp = datetime.now().strftime("%H:%M:%S")
                log_entry = f"[{timestamp}] [ERRO] ❌ Validação falhou: {mensagem_validacao}"
                st.session_state.extraction_logs.append(log_entry)
                
                if problemas:
                    for problema in problemas:
                        log_entry = f"[{timestamp}] [ERRO]   - Arquivo: {problema['arquivo']}"
                        st.session_state.extraction_logs.append(log_entry)
                        log_entry = f"[{timestamp}] [ERRO]     Erro: {problema['erro']}"
                        st.session_state.extraction_logs.append(log_entry)
                
                tarefas_erro += 1
                st.session_state.extraction_logs.append("-" * 80)
                atualizar_log()
                
                # Se for modo único, parar. Se for múltiplo, continuar
                if not modo_batch:
                    st.error(mensagem_validacao)
                    st.stop()
                else:
                    continue
            
            # Validação OK
            timestamp = datetime.now().strftime("%H:%M:%S")
            log_entry = f"[{timestamp}] [VALIDAÇÃO] ✅ {mensagem_validacao}"
            st.session_state.extraction_logs.append(log_entry)
            atualizar_log()
            
            # ATUALIZAR STATUS ATUAL
            arquivo_atual_container.success(f"✅ Validação OK - Iniciando processamento...")
            
            # Função de callback para log em tempo real
            def update_progress_log(percent, total_percent, message, step):
                timestamp = datetime.now().strftime("%H:%M:%S")
                log_entry = f"[{timestamp}] [{step}] {message}"
                st.session_state.extraction_logs.append(log_entry)
                
                # Atualizar status atual de forma leve
                arquivo_atual_container.info(f"**{step}:** {message}")
                
                # Atualizar progresso
                if not modo_batch:
                    individual_progress.progress(int(percent))
                
                # Atualizar log apenas a cada 5%
                if percent % 5 == 0 or percent >= 95:
                    atualizar_log()
            
            # Processar
            try:
                sucesso, mensagem, total_registros = process_raw_excel_to_parquet(
                    planta_atual,
                    ano_atual,
                    mode=modo,
                    progress_callback=update_progress_log
                )
                
                timestamp = datetime.now().strftime("%H:%M:%S")
                
                if sucesso:
                    log_entry = f"[{timestamp}] [CONCLUÍDO] ✅ {mensagem}"
                    st.session_state.extraction_logs.append(log_entry)
                    log_entry = f"[{timestamp}] [INFO] Total de registros: {total_registros:,}"
                    st.session_state.extraction_logs.append(log_entry)
                    tarefas_sucesso += 1
                else:
                    log_entry = f"[{timestamp}] [ERRO] ❌ {mensagem}"
                    st.session_state.extraction_logs.append(log_entry)
                    tarefas_erro += 1
                
                st.session_state.extraction_logs.append("-" * 80)
                atualizar_log()
                    
            except Exception as e:
                timestamp = datetime.now().strftime("%H:%M:%S")
                log_entry = f"[{timestamp}] [EXCEÇÃO] ❌ Erro ao processar: {str(e)}"
                st.session_state.extraction_logs.append(log_entry)
                st.session_state.extraction_logs.append("-" * 80)
                tarefas_erro += 1
                atualizar_log()
            
            tarefas_concluidas += 1
        
        # Resumo final
        if modo_batch:
            global_progress.progress(100)
            
            timestamp = datetime.now().strftime("%H:%M:%S")
            st.session_state.extraction_logs.append("=" * 80)
            log_entry = f"[{timestamp}] [RESUMO FINAL]"
            st.session_state.extraction_logs.append(log_entry)
            log_entry = f"[{timestamp}] [RESUMO] Total processado: {tarefas_concluidas}/{total_tarefas}"
            st.session_state.extraction_logs.append(log_entry)
            log_entry = f"[{timestamp}] [RESUMO] ✅ Sucesso: {tarefas_sucesso}"
            st.session_state.extraction_logs.append(log_entry)
            log_entry = f"[{timestamp}] [RESUMO] ❌ Erros: {tarefas_erro}"
            st.session_state.extraction_logs.append(log_entry)
            st.session_state.extraction_logs.append("=" * 80)
            atualizar_log()
            
            if tarefas_sucesso == total_tarefas:
                st.success(f"🎉 Todas as {total_tarefas} planta(s)/ano(s) processadas com sucesso!")
                st.balloons()
            elif tarefas_sucesso > 0:
                st.warning(f"⚠️ {tarefas_sucesso} sucesso(s) e {tarefas_erro} erro(s)")
            else:
                st.error(f"❌ Todas as {tarefas_erro} tentativas falharam")
        else:
            # Modo único - mostrar resultado
            if tarefas_sucesso > 0:
                st.success("✅ Extração concluída com sucesso!")
                st.balloons()
            else:
                st.error("❌ Extração falhou")
        
        # Limpar cache
        st.cache_data.clear()

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

# ==================== TAB 3: CÓDIGOS MASTERSAF ====================
with tab3:
    st.header("📋 Gerenciar Códigos Mastersaf e Sapiens")
    
    st.markdown("""
    Este arquivo contém a tabela de códigos que relaciona **CFOP** com **COD_NATUREZA_OP** e **DESCRICAO_NATUREZA_OP**.
    
    Durante a extração, o sistema usa esta tabela para padronizar as descrições dos códigos fiscais.
    """)
    
    st.markdown("---")
    
    base_path = Path(__file__).parent.parent.parent
    codigos_path = base_path / "data_raw" / "Códigos Mastersaf e Sapiens.xlsx"
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📥 Download")
        
        if codigos_path.exists():
            st.success(f"✅ Arquivo encontrado")
            st.info(f"**Localização:**\n`{codigos_path}`")
            
            # Ler arquivo para download
            with open(codigos_path, "rb") as f:
                file_data = f.read()
            
            st.download_button(
                label="⬇️ Baixar Códigos Mastersaf.xlsx",
                data=file_data,
                file_name="Códigos Mastersaf e Sapiens.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )
            
            # Mostrar informações do arquivo
            file_size = codigos_path.stat().st_size / 1024
            st.caption(f"Tamanho: {file_size:.1f} KB")
            
            # Ler e mostrar estatísticas
            try:
                import pandas as pd
                df_codigos = pd.read_excel(codigos_path)
                st.metric("Total de CFOPs cadastrados", len(df_codigos))
            except Exception as e:
                st.warning(f"Não foi possível ler o arquivo: {e}")
        else:
            st.warning("⚠️ Arquivo não encontrado")
            st.info(f"Esperado em: `{codigos_path}`")
    
    with col2:
        st.subheader("📤 Upload (Atualizar)")
        
        st.markdown("""
        Se você editou o arquivo, faça upload da versão atualizada aqui.
        
        **Atenção:** O upload substituirá o arquivo atual.
        """)
        
        uploaded_codigos = st.file_uploader(
            "Selecione o arquivo Excel atualizado",
            type=["xlsx"],
            key="upload_codigos_mastersaf"
        )
        
        if uploaded_codigos:
            st.info(f"Arquivo selecionado: **{uploaded_codigos.name}**")
            
            if st.button("📤 Atualizar Códigos Mastersaf", type="primary", use_container_width=True):
                try:
                    # Salvar arquivo
                    with open(codigos_path, "wb") as f:
                        f.write(uploaded_codigos.getbuffer())
                    
                    st.success("✅ Arquivo de códigos atualizado com sucesso!")
                    st.balloons()
                    
                    # Limpar cache para recarregar na próxima extração
                    from extraction import extracao
                    extracao._df_codigos_cache = None
                    
                    st.rerun()
                    
                except Exception as e:
                    st.error(f"❌ Erro ao atualizar arquivo: {str(e)}")
                    st.exception(e)
    
    st.markdown("---")
    
    # Informações sobre o uso
    with st.expander("ℹ️ Como funciona?"):
        st.markdown("""
        ### Processo de Extração com Códigos
        
        1. **Upload de arquivos Excel** → Os arquivos fiscais são enviados para `data_raw`
        2. **Processamento** → Durante a extração:
           - O sistema lê os arquivos Excel
           - Faz um **merge** (relacionamento) usando a coluna **CFOP**
           - Substitui `COD_NATUREZA_OP` e `DESCRICAO_NATUREZA_OP` pelos valores desta tabela
        3. **Resultado** → Dados padronizados salvos em formato Parquet
        
        ### Estrutura do Arquivo
        
        O arquivo deve conter as seguintes colunas:
        - **CFOP** - Código Fiscal de Operações e Prestações
        - **COD_NATUREZA_OP** - Código da Natureza da Operação
        - **DESCRICAO_NATUREZA_OP** - Descrição da Natureza da Operação
        
        ### Editando o Arquivo
        
        Para editar a tabela de códigos:
        1. Faça o **download** do arquivo atual (botão acima)
        2. Abra no Excel e faça as alterações necessárias
        3. Salve o arquivo
        4. Faça o **upload** da versão atualizada
        
        **Ou** use a aba **"🏠 Home"** para editar diretamente no navegador!
        """)

