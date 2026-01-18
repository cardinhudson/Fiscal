"""
Página de Extração - Upload e Processamento de arquivos Excel para Parquet
"""

import streamlit as st
import sys
from pathlib import Path
import shutil

# Adicionar diretório raiz ao path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from versionamento import obter_versao_atual, verificar_mudancas_paginas
from app.utils.page_components import renderizar_cabecalho, renderizar_rodape
from extraction.extracao import (
    load_plantas,
    load_anos,
    process_raw_excel_to_parquet,
    ensure_structure,
    add_planta
)

# Configurar página
st.set_page_config(
    page_title="Extração de Dados",
    page_icon="📤",
    layout="wide"
)

# Verificar mudanças e incrementar versão se necessário
verificar_mudancas_paginas()

# Renderizar cabeçalho
renderizar_cabecalho()

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
    
    st.subheader("🎯 Seleção de Processamento")
    
    col1, col2 = st.columns(2)
    
    with col1:
        plantas = load_plantas()
        plantas_opcoes = ["Todos"] + plantas
        planta_proc = st.selectbox(
            "Selecione a Planta",
            plantas_opcoes,
            key="proc_planta",
            help="Selecione uma planta específica ou 'Todos' para processar todas"
        )
    
    with col2:
        if planta_proc == "Todos":
            # Se todas as plantas, mostrar "Todos" para anos também
            anos_opcoes = ["Todos"]
            ano_proc = st.selectbox(
                "Selecione o Ano",
                anos_opcoes,
                key="proc_ano",
                help="Com 'Todos' nas plantas, processa todos os anos de todas as plantas"
            )
        else:
            # Se planta específica, carregar anos dela + opção "Todos"
            anos = load_anos(planta_proc)
            if not anos:
                st.warning(f"Nenhum ano disponível para {planta_proc}")
                st.stop()
            anos_opcoes = ["Todos"] + anos
            ano_proc = st.selectbox(
                "Selecione o Ano",
                anos_opcoes,
                index=len(anos_opcoes)-1 if anos_opcoes else 0,
                key="proc_ano",
                help="Selecione um ano específico ou 'Todos' para processar todos os anos desta planta"
            )
    
    st.markdown("---")
    
    # Mostrar informações baseado na seleção
    base_path = Path(__file__).parent.parent.parent
    
    if planta_proc == "Todos" and ano_proc == "Todos":
        # Todas as plantas e todos os anos
        st.info("### 🌐 Modo: Processar Todas as Plantas e Anos")
        st.markdown("""
        O sistema irá processar **automaticamente** todas as plantas e anos que possuem arquivos Excel em `data_raw/`.
        
        **Ordem de processamento:**
        1. Busca todas as pastas em data_raw/
        2. Para cada planta, busca todos os anos disponíveis
        3. Valida e processa cada combinação planta/ano
        4. Gera consolidações automaticamente
        """)
        
        # Descobrir plantas e anos disponíveis
        data_raw = base_path / "data_raw"
        plantas_disponiveis = []
        if data_raw.exists():
            for planta_dir in data_raw.iterdir():
                if planta_dir.is_dir() and planta_dir.name != "Códigos Mastersaf e Sapiens.xlsx":
                    anos_planta = []
                    for ano_dir in planta_dir.iterdir():
                        if ano_dir.is_dir():
                            excel_files = [f for f in list(ano_dir.glob("*.xlsx")) + list(ano_dir.glob("*.xls")) 
                                         if not f.name.startswith("~$") and not f.name.startswith(".")]
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
    
    elif planta_proc != "Todos" and ano_proc == "Todos":
        # Uma planta específica, todos os anos
        st.info(f"### 📅 Modo: Processar Todos os Anos de {planta_proc}")
        
        # Descobrir anos disponíveis para esta planta
        data_raw = base_path / "data_raw" / planta_proc
        anos_disponiveis = []
        if data_raw.exists():
            for ano_dir in data_raw.iterdir():
                if ano_dir.is_dir():
                    excel_files = [f for f in list(ano_dir.glob("*.xlsx")) + list(ano_dir.glob("*.xls")) 
                                 if not f.name.startswith("~$") and not f.name.startswith(".")]
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
                    excel_files = [f for f in list(ano_path.glob("*.xlsx")) + list(ano_path.glob("*.xls")) 
                                 if not f.name.startswith("~$") and not f.name.startswith(".")]
                    st.markdown(f"**{ano}**: {len(excel_files)} arquivo(s) Excel")
        else:
            st.warning(f"⚠️ Nenhum ano com dados encontrado para {planta_proc}")
            st.stop()
    
    else:
        # Uma planta e um ano específico
        raw_path = base_path / "data_raw" / planta_proc / str(ano_proc)
        parquet_path = base_path / "data_parquet" / planta_proc / str(ano_proc)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.info(f"**Diretório de entrada (Excel):**\n\n`{raw_path}`")
            
            if raw_path.exists():
                excel_files = [f for f in list(raw_path.glob("*.xlsx")) + list(raw_path.glob("*.xls")) 
                             if not f.name.startswith("~$") and not f.name.startswith(".")]
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
    if planta_proc == "Todos" and ano_proc == "Todos":
        btn_label = "🌐 Processar TODAS as Plantas e Anos"
    elif planta_proc != "Todos" and ano_proc == "Todos":
        btn_label = f"📅 Processar TODOS os Anos de {planta_proc}"
    else:
        btn_label = f"🚀 Processar {planta_proc} - {ano_proc}"
    
    if st.button(btn_label, type="primary", use_container_width=True, key="btn_processar"):
        from extraction.extracao import validate_excel_files
        from datetime import datetime
        
        base_path = Path(__file__).parent.parent.parent
        
        # Preparar lista de plantas/anos para processar
        tarefas = []
        
        if planta_proc == "Todos" and ano_proc == "Todos":
            # Todas as plantas e todos os anos
            data_raw = base_path / "data_raw"
            plantas_disponiveis = []
            if data_raw.exists():
                for planta_dir in data_raw.iterdir():
                    if planta_dir.is_dir() and planta_dir.name != "Códigos Mastersaf e Sapiens.xlsx":
                        anos_planta = []
                        for ano_dir in planta_dir.iterdir():
                            if ano_dir.is_dir():
                                excel_files = [f for f in list(ano_dir.glob("*.xlsx")) + list(ano_dir.glob("*.xls")) 
                                             if not f.name.startswith("~$") and not f.name.startswith(".")]
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
            
            for item in plantas_disponiveis:
                for ano in item['anos']:
                    tarefas.append({'planta': item['planta'], 'ano': ano})
            
            if not tarefas:
                st.error("❌ Nenhuma planta/ano para processar!")
                st.stop()
            
            st.info(f"📦 Total de {len(tarefas)} combinação(ões) planta/ano para processar")
        
        elif planta_proc != "Todos" and ano_proc == "Todos":
            # Uma planta, todos os anos
            data_raw = base_path / "data_raw" / planta_proc
            anos_disponiveis = []
            if data_raw.exists():
                for ano_dir in data_raw.iterdir():
                    if ano_dir.is_dir():
                        excel_files = [f for f in list(ano_dir.glob("*.xlsx")) + list(ano_dir.glob("*.xls")) 
                                     if not f.name.startswith("~$") and not f.name.startswith(".")]
                        if excel_files:
                            try:
                                anos_disponiveis.append(int(ano_dir.name))
                            except ValueError:
                                continue
            
            for ano in sorted(anos_disponiveis):
                tarefas.append({'planta': planta_proc, 'ano': ano})
            
            if not tarefas:
                st.error("❌ Nenhum ano para processar!")
                st.stop()
            
            st.info(f"📦 Total de {len(tarefas)} ano(s) de {planta_proc} para processar")
        
        else:
            # Uma planta e um ano específico
            raw_path = base_path / "data_raw" / planta_proc / str(ano_proc)
            if not raw_path.exists():
                st.error("❌ Diretório de entrada não existe!")
                st.stop()
            
            excel_files = [f for f in list(raw_path.glob("*.xlsx")) + list(raw_path.glob("*.xls")) 
                         if not f.name.startswith("~$") and not f.name.startswith(".")]
            if not excel_files:
                st.warning("⚠️ Nenhum arquivo Excel encontrado no diretório!")
                st.stop()
            
            tarefas.append({'planta': planta_proc, 'ano': int(ano_proc)})
        
        # Determinar se é modo batch (múltiplas tarefas)
        modo_batch = len(tarefas) > 1
        
        # Processamento
        st.markdown("---")
        st.subheader("📊 Status da Extração")
        
        # STATUS AO VIVO (separado do log histórico)
        st.markdown("### 🔴 Status Atual")
        status_container = st.empty()
        progress_bar = st.progress(0)
        
        # Container para progresso global (batch)
        if modo_batch:
            st.markdown(f"### 🌐 Processando {len(tarefas)} planta(s)/ano(s)")
            global_status = st.empty()
        
        # Container para LOG EM TEMPO REAL
        st.markdown("### 📝 Log da Execução")
        logs_container = st.container()
        
        # CSS para limitar altura do log com scroll
        st.markdown("""
        <style>
        .log-container {
            max-height: 400px;
            overflow-y: auto;
            font-family: monospace;
            font-size: 12px;
            background-color: #1e1e1e;
            color: #d4d4d4;
            padding: 10px;
            border-radius: 5px;
        }
        </style>
        """, unsafe_allow_html=True)
        
        # Inicializar lista de logs
        if 'extraction_logs' not in st.session_state:
            st.session_state.extraction_logs = []
        st.session_state.extraction_logs = []
        
        # Placeholder dentro do container para logs
        with logs_container:
            logs_display = st.empty()
        
        # Função para renderizar logs
        def render_logs():
            """Renderiza os últimos 50 logs na tela"""
            ultimos = st.session_state.extraction_logs[-50:]
            with logs_display.container():
                for linha in ultimos:
                    st.code(linha, language="text")
        
        # Função para adicionar log
        def adicionar_log(mensagem, sem_timestamp=False):
            """Adiciona mensagem aos logs"""
            if sem_timestamp:
                log_entry = mensagem
            else:
                timestamp = datetime.now().strftime('%H:%M:%S')
                log_entry = f"[{timestamp}] {mensagem}"
            
            st.session_state.extraction_logs.append(log_entry)
            if len(st.session_state.extraction_logs) > 200:
                st.session_state.extraction_logs = st.session_state.extraction_logs[-200:]
        
        # Função para atualizar progresso
        def atualizar_progresso(percent, titulo, detalhe=""):
            """Atualiza barra de progresso e status"""
            status_container.info(f"**{titulo}** {detalhe}")
            progress_bar.progress(int(percent), text=f"{int(percent)}%")
        
        # Contadores
        total_tarefas = len(tarefas)
        tarefas_concluidas = 0
        tarefas_sucesso = 0
        tarefas_erro = 0
        
        # Processar cada tarefa
        for idx, tarefa in enumerate(tarefas):
            planta_atual = tarefa['planta']
            ano_atual = tarefa['ano']
            
            # Atualizar progresso global
            if modo_batch:
                progresso_batch = int((idx / total_tarefas) * 100)
                global_status.info(f"📍 Tarefa {idx+1}/{total_tarefas}: **{planta_atual} - {ano_atual}**")
            
            # Log de início
            adicionar_log(f"{'='*80}")
            adicionar_log(f"INICIANDO: Planta {planta_atual} - Ano {ano_atual}")
            adicionar_log(f"{'='*80}")
            render_logs()
            
            atualizar_progresso(0, "🏭 Iniciando processamento", f"{planta_atual} - {ano_atual}")
            
            # Validação
            adicionar_log("Validando arquivos...")
            render_logs()
            atualizar_progresso(5, "🔍 Validando arquivos...", "")
            
            atualizar_progresso(5, "🔍 Validando arquivos...", "")
            
            sucesso_validacao, mensagem_validacao, problemas = validate_excel_files(planta_atual, ano_atual)
            
            if not sucesso_validacao:
                adicionar_log(f"ERRO na validação: {mensagem_validacao}")
                
                if problemas:
                    for problema in problemas:
                        adicionar_log(f"  - Arquivo: {problema['arquivo']}")
                        adicionar_log(f"    Erro: {problema['erro']}")
                
                tarefas_erro += 1
                render_logs()
                atualizar_progresso(10, "❌ Validação falhou", mensagem_validacao)
                
                # Se for modo único, parar. Se for múltiplo, continuar
                if not modo_batch:
                    st.error(mensagem_validacao)
                    st.stop()
                else:
                    continue
            
            # Validação OK
            adicionar_log(f"VALIDACAO OK: {mensagem_validacao}")
            render_logs()
            atualizar_progresso(10, "✅ Validação OK", "Iniciando extração...")
            
            # EXECUTAR EXTRAÇÃO VIA SUBPROCESS PARA CAPTURAR TODO O OUTPUT
            import subprocess
            import sys
            import json
            from pathlib import Path
            
            base_path = Path(__file__).parent.parent.parent
            script_path = base_path / "run_extraction.py"
            python_exe = sys.executable
            
            # Preparar comando
            cmd = [python_exe, str(script_path), planta_atual, str(ano_atual), modo]
            
            # Preparar ambiente com UTF-8
            import os
            env = os.environ.copy()
            env['PYTHONIOENCODING'] = 'utf-8'
            
            try:
                # Executar processo
                adicionar_log("Executando extração...")
                render_logs()
                atualizar_progresso(15, "🚀 Iniciando extração", "")
                
                process = subprocess.Popen(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    encoding='utf-8',
                    errors='replace',
                    bufsize=1,
                    universal_newlines=True,
                    cwd=str(base_path),
                    env=env
                )
                
                # Ler output linha por linha EM TEMPO REAL
                ultima_linha_json = None
                linha_count = 0
                
                for line in process.stdout:
                    line = line.rstrip()
                    if not line or line == '-' * 80:
                        continue
                    
                    # Adicionar ao log SEM timestamp (já vem do script)
                    adicionar_log(line, sem_timestamp=True)
                    linha_count += 1
                    
                    # Atualizar display a cada 5 linhas
                    if linha_count % 5 == 0:
                        render_logs()
                    
                    # Extrair percentual para barra de progresso
                    if '[' in line and '%]' in line:
                        try:
                            percent_str = line.split('[')[1].split('%]')[0].strip()
                            percent = int(percent_str)
                            
                            # Extrair mensagem
                            if ']' in line:
                                partes = line.split(']')
                                if len(partes) >= 3:
                                    mensagem = ']'.join(partes[2:]).strip()
                                    atualizar_progresso(percent, "Processando", mensagem[:50])
                        except:
                            pass
                    
                    # Guardar última linha JSON (resultado final)
                    if line.strip().startswith('{"'):
                        ultima_linha_json = line.strip()
                
                # Aguardar conclusão
                process.wait()
                
                # Renderizar logs finais
                render_logs()
                
                # Processar resultado
                if ultima_linha_json:
                    resultado = json.loads(ultima_linha_json)
                    sucesso = resultado.get('success', False)
                    mensagem = resultado.get('message', 'Sem mensagem')
                    total_registros = resultado.get('total', 0)
                else:
                    sucesso = process.returncode == 0
                    mensagem = "Processamento concluído" if sucesso else "Erro no processamento"
                    total_registros = 0
                
                if sucesso:
                    adicionar_log(f"CONCLUIDO COM SUCESSO: {mensagem}")
                    adicionar_log(f"Total de registros: {total_registros:,}")
                    tarefas_sucesso += 1
                    atualizar_progresso(100, "✅ Concluído!", f"{total_registros:,} registros")
                else:
                    adicionar_log(f"ERRO: {mensagem}")
                    tarefas_erro += 1
                    atualizar_progresso(100, "❌ Erro", mensagem)
                
                render_logs()
                    
            except Exception as e:
                adicionar_log(f"EXCECAO: {str(e)}")
                tarefas_erro += 1
                render_logs()
                atualizar_progresso(100, "❌ Exceção", str(e)[:50])
            
            tarefas_concluidas += 1
        
        # Resumo final
        if modo_batch:
            atualizar_progresso(100, "✅ Processamento concluído", f"{tarefas_sucesso} sucesso(s), {tarefas_erro} erro(s)")
            
            adicionar_log("=" * 80)
            adicionar_log("RESUMO FINAL")
            adicionar_log(f"Total processado: {tarefas_concluidas}/{total_tarefas}")
            adicionar_log(f"Sucesso: {tarefas_sucesso}")
            adicionar_log(f"Erros: {tarefas_erro}")
            adicionar_log("=" * 80)
            render_logs()
            
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

# ==========================================
# RODAPÉ
# ==========================================
renderizar_rodape()

