"""
Módulo de extração e processamento de arquivos Excel para Parquet.
Converte dados fiscais de Excel mensal para formato Parquet otimizado.
"""

import os
import json
import pandas as pd
import streamlit as st
from pathlib import Path
from datetime import datetime
import unicodedata
import re
import time
from typing import Optional
from extraction.logger import ExtractionLogger


def get_base_path():
    """Retorna o caminho base do projeto."""
    # Usar diretório de trabalho atual ao invés de __file__
    # para funcionar independente de onde o módulo é importado
    return Path.cwd()


# Cache para evitar recarregar a tabela de códigos múltiplas vezes
_df_codigos_cache = None

def load_codigos_mastersaf():
    """
    Carrega a tabela de códigos Mastersaf e Sapiens.
    A tabela é carregada apenas uma vez e mantida em cache.
    
    Returns:
        DataFrame com as colunas CFOP, COD_NATUREZA_OP e DESCRICAO_NATUREZA_OP
    """
    global _df_codigos_cache
    
    if _df_codigos_cache is not None:
        return _df_codigos_cache
    
    try:
        base_path = get_base_path()
        codigos_path = base_path / "data_raw" / "Códigos Mastersaf e Sapiens.xlsx"
        
        if not codigos_path.exists():
            print(f"⚠️ Arquivo de códigos não encontrado: {codigos_path}")
            return None
        
        # Ler as colunas necessárias (incluindo RESUMO DE OPERAÇÃO se existir)
        try:
            df_codigos = pd.read_excel(
                codigos_path,
                usecols=['CFOP', 'COD_NATUREZA_OP', 'DESCRICAO_NATUREZA_OP', 'RESUMO DE OPERAÇÃO']
            )
        except ValueError:
            # Se RESUMO DE OPERAÇÃO não existir, carregar sem ela
            df_codigos = pd.read_excel(
                codigos_path,
                usecols=['CFOP', 'COD_NATUREZA_OP', 'DESCRICAO_NATUREZA_OP']
            )
        
        # Converter CFOP para string e padronizar
        df_codigos['CFOP'] = df_codigos['CFOP'].astype(str).str.strip()
        df_codigos['COD_NATUREZA_OP'] = df_codigos['COD_NATUREZA_OP'].astype(str).str.strip()
        df_codigos['DESCRICAO_NATUREZA_OP'] = df_codigos['DESCRICAO_NATUREZA_OP'].astype(str).str.strip()
        if 'RESUMO DE OPERAÇÃO' in df_codigos.columns:
            df_codigos['RESUMO DE OPERAÇÃO'] = df_codigos['RESUMO DE OPERAÇÃO'].astype(str).str.strip()
        
        # Remover duplicatas (manter primeira ocorrência)
        df_codigos = df_codigos.drop_duplicates(subset=['CFOP'], keep='first')
        
        # Armazenar em cache
        _df_codigos_cache = df_codigos
        
        print(f"✅ Tabela de códigos carregada: {len(df_codigos)} CFOPs")
        return df_codigos
        
    except Exception as e:
        print(f"❌ Erro ao carregar tabela de códigos: {e}")
        return None


def validate_excel_files(planta: str, ano: int):
    """
    Valida se os arquivos Excel possuem as colunas essenciais antes do processamento.
    
    Args:
        planta: Nome da planta
        ano: Ano fiscal
        
    Returns:
        Tuple[bool, str, list]: (sucesso, mensagem, lista de problemas detalhados)
    """
    base_path = get_base_path()
    raw_path = base_path / "data_raw" / planta / str(ano)
    
    if not raw_path.exists():
        return False, f"❌ Diretório não existe: {raw_path}", []
    
    # Listar arquivos Excel, ignorando temporários/ocultos
    excel_files = [
        f for f in list(raw_path.glob("*.xlsx")) + list(raw_path.glob("*.xls"))
        if not f.name.startswith("~$") and not f.name.startswith(".")
    ]
    
    if not excel_files:
        return False, "❌ Nenhum arquivo Excel encontrado", []
    
    # Colunas essenciais obrigatórias
    colunas_essenciais = [
        'DATA_FISCAL',
        'ENTRADA_SAIDA', 
        'CODIGO_PRODUTO',
        'DESCRICAO',
        'RAZAO_SOCIAL',
        'CFOP',
        'COD_NATUREZA_OP',
        'DESCRICAO_NATUREZA_OP',
        'ALIQ_ICMS',
        'BASE_ICMS_1',
        'VALOR_ICMS',
        'CST_ICMS',
        'NUM_CONTROLE_DOCTO',
        'UF',
        'MUNICIPIO',
        'NUMERO_NF',
        'QUANTIDADE'
    ]
    
    problemas = []
    arquivos_ok = 0
    
    for file_path in excel_files:
        try:
            # Ler apenas o cabeçalho (primeira linha) para validar colunas
            try:
                df_header = pd.read_excel(file_path, nrows=0, engine='calamine')
            except:
                df_header = pd.read_excel(file_path, nrows=0, engine='openpyxl')
            
            colunas_arquivo = list(df_header.columns)
            colunas_faltantes = [col for col in colunas_essenciais if col not in colunas_arquivo]
            
            if colunas_faltantes:
                problemas.append({
                    'arquivo': file_path.name,
                    'erro': 'Colunas faltantes',
                    'detalhes': colunas_faltantes
                })
            else:
                arquivos_ok += 1
                
        except Exception as e:
            problemas.append({
                'arquivo': file_path.name,
                'erro': 'Erro ao ler arquivo',
                'detalhes': str(e)
            })
    
    if problemas:
        msg = f"⚠️ {len(problemas)} arquivo(s) com problemas de {len(excel_files)} total"
        return False, msg, problemas
    else:
        msg = f"✅ Todos os {arquivos_ok} arquivos estão compatíveis"
        return True, msg, []


def ensure_structure(planta: str, ano: int):
    """
    Garante que toda a estrutura de diretórios existe para uma planta e ano.
    Se não existir, cria automaticamente.
    
    Args:
        planta: Nome da planta
        ano: Ano fiscal
    """
    base_path = get_base_path()
    
    paths = [
        base_path / "data_raw" / planta / str(ano),
        base_path / "data_parquet" / planta / str(ano),
    ]
    
    for path in paths:
        path.mkdir(parents=True, exist_ok=True)


def remove_accents(text):
    """Remove acentuação de texto."""
    if pd.isna(text):
        return text
    text = str(text)
    nfkd = unicodedata.normalize('NFKD', text)
    return "".join([c for c in nfkd if not unicodedata.combining(c)])


def to_snake_case(text):
    """Converte texto para snake_case."""
    text = remove_accents(text)
    text = text.lower()
    text = re.sub(r'[^\w\s]', '', text)
    text = re.sub(r'\s+', '_', text)
    return text


def convert_br_number(value):
    """Converte número no formato BR (1.234,56) para US (1234.56)."""
    if pd.isna(value):
        return None
    
    if isinstance(value, (int, float)):
        return float(value)
    
    value = str(value).strip()
    if value == '':
        return None
    
    # Remove pontos de milhar e substitui vírgula por ponto
    value = value.replace('.', '').replace(',', '.')
    
    try:
        return float(value)
    except:
        return None


def convert_br_column(series):
    """Converte coluna inteira de números BR para US (vetorizado - mais rápido)."""
    # Substitui . por nada e , por . em toda a série de uma vez
    series = series.astype(str).str.replace('.', '', regex=False).str.replace(',', '.', regex=False)
    # Converte para numérico, colocando NaN onde falhar
    return pd.to_numeric(series, errors='coerce')


def read_monthly_excel(file_path, logger: Optional[ExtractionLogger] = None):
    """
    Lê um arquivo Excel mensal e padroniza os dados.
    Lê APENAS as colunas essenciais para melhor performance.
    
    Args:
        file_path: Caminho do arquivo Excel
        logger: Logger opcional para rastreamento
        
    Returns:
        DataFrame padronizado com ano detectado
    """
    start_time = time.time()
    
    try:
        if logger:
            file_size_mb = file_path.stat().st_size / (1024 * 1024)
            logger.log_file_start(file_path.name, file_size_mb)
        
        # Colunas essenciais que serão utilizadas no sistema (em MAIÚSCULAS como no Excel)
        colunas_essenciais = [
            'DATA_FISCAL',
            'ENTRADA_SAIDA', 
            'CODIGO_PRODUTO',
            'DESCRICAO',
            'RAZAO_SOCIAL',
            'CFOP',
            'ALIQ_ICMS',
            'BASE_ICMS_1',
            'VALOR_ICMS',
            'CST_ICMS',
            'NUM_CONTROLE_DOCTO',
            'UF',
            'MUNICIPIO',
            'NUMERO_NF',
            'QUANTIDADE'
        ]
        
        # Ler Excel com APENAS as colunas essenciais (muito mais rápido)
        # IMPORTANTE: Calamine lê números como float direto (não como texto formatado BR)
        # Por isso, NÃO usamos dtype=str para colunas numéricas com calamine
        try:
            # Tentar ler com python-calamine (muito mais rápido para arquivos grandes)
            import python_calamine
            df = pd.read_excel(
                file_path, 
                engine='calamine',
                usecols=colunas_essenciais
            )
            # Calamine lê números como float direto, não precisa converter BR→US
            calamine_used = True
        except (ImportError, Exception):
            try:
                # Fallback para openpyxl com otimizações
                # Openpyxl lê como texto, precisa converter BR→US
                df = pd.read_excel(
                    file_path, 
                    dtype=str, 
                    engine='openpyxl', 
                    usecols=colunas_essenciais,
                    engine_kwargs={'data_only': True, 'read_only': True}
                )
                calamine_used = False
            except ValueError as e:
                # Se alguma coluna não existir, ler tudo e filtrar depois
                print(f"⚠️ Erro ao ler colunas específicas: {e}")
                df = pd.read_excel(file_path, dtype=str, engine='openpyxl')
                print(f"📊 Total de colunas no arquivo: {len(df.columns)}")
                # Filtrar apenas colunas que existem
                colunas_disponiveis = [col for col in colunas_essenciais if col in df.columns]
                df = df[colunas_disponiveis]
                print(f"✅ Filtradas para {len(df.columns)} colunas essenciais")
                calamine_used = False
        
        # Converter colunas para snake_case
        df.columns = [to_snake_case(col) for col in df.columns]
        
        # Remover colunas totalmente vazias (se houver)
        df = df.dropna(axis=1, how='all')
        
        # Converter data_fiscal (cache formato para acelerar)
        if 'data_fiscal' in df.columns:
            df['data_fiscal'] = pd.to_datetime(df['data_fiscal'], errors='coerce', format='mixed', cache=True)
        
        # Colunas numéricas: converter APENAS se openpyxl (calamine já lê como número)
        numeric_columns = ['aliq_icms', 'base_icms_1', 'valor_icms', 'quantidade']
        
        if not calamine_used:
            # Openpyxl: precisa converter BR → US
            for col in numeric_columns:
                if col in df.columns:
                    df[col] = convert_br_column(df[col])
        else:
            # Calamine: já são números, apenas garantir tipo float
            for col in numeric_columns:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors='coerce')
        
        # Todas as colunas de texto (não numéricas): garantir que sejam string
        # Incluindo colunas numéricas que funcionam como identificadores
        string_columns = [
            'tipo_registro', 'cnpj_estabelecimento', 'numero_documento', 
            'descricao', 'codigo_produto', 'fornecedor', 'cnpj_fornecedor', 
            'cfop', 'cst_icms', 'num_controle_docto', 'numero_nf', 'entrada_saida',
            'razao_social', 'uf', 'municipio', 'cod_natureza_op', 'descricao_natureza_op'
        ]
        for col in string_columns:
            if col in df.columns:
                # Converter para string, preservando valores vazios como string vazia
                df[col] = df[col].fillna('').astype(str).str.strip()
                # Limpar valores inválidos
                df[col] = df[col].replace(['nan', 'None', '<NA>'], '')
        
        # Detectar ano automaticamente
        if 'data_fiscal' in df.columns:
            anos = df['data_fiscal'].dt.year.dropna().unique()
            if len(anos) > 0:
                ano_detectado = int(anos[0])
            else:
                ano_detectado = datetime.now().year
        else:
            ano_detectado = datetime.now().year
        
        # ===== MERGE COM TABELA DE CÓDIGOS MASTERSAF =====
        # Substituir COD_NATUREZA_OP e DESCRICAO_NATUREZA_OP pelos valores da tabela de códigos
        df_codigos = load_codigos_mastersaf()
        
        if df_codigos is not None and 'cfop' in df.columns:
            # Remover as colunas antigas antes do merge
            colunas_para_remover = ['cod_natureza_op', 'descricao_natureza_op', 'resumo_de_operacao']
            df = df.drop(columns=[col for col in colunas_para_remover if col in df.columns])
            
            # Preparar df_codigos com nomes em snake_case para o merge
            df_codigos_merge = df_codigos.copy()
            df_codigos_merge.columns = [to_snake_case(col) for col in df_codigos_merge.columns]
            
            # Converter CFOP para int em ambos DataFrames para o merge funcionar
            if 'cfop' in df.columns:
                df['cfop'] = pd.to_numeric(df['cfop'], errors='coerce').fillna(0).astype(int)
            if 'cfop' in df_codigos_merge.columns:
                df_codigos_merge['cfop'] = pd.to_numeric(df_codigos_merge['cfop'], errors='coerce').fillna(0).astype(int)
            
            # Selecionar colunas disponíveis para o merge
            colunas_merge = ['cfop', 'cod_natureza_op', 'descricao_natureza_op']
            if 'resumo_de_operacao' in df_codigos_merge.columns:
                colunas_merge.append('resumo_de_operacao')
            
            # Fazer o merge usando CFOP como chave
            registros_antes = len(df)
            df = df.merge(
                df_codigos_merge[colunas_merge],
                on='cfop',
                how='left'
            )
            
            # Verificar se o merge funcionou
            if len(df) == registros_antes:
                nao_encontrados = df['cod_natureza_op'].isna().sum()
                if nao_encontrados > 0:
                    print(f"⚠️ {nao_encontrados} registros sem correspondência na tabela de códigos")
                else:
                    print(f"✅ Merge realizado com sucesso: {registros_antes} registros mantidos")
            else:
                print(f"⚠️ Atenção: merge alterou número de registros ({registros_antes} → {len(df)})")
            
            # Preencher registros não encontrados com "Não encontrado"
            df['cod_natureza_op'] = df['cod_natureza_op'].fillna('Não encontrado')
            df['descricao_natureza_op'] = df['descricao_natureza_op'].fillna('Não encontrado')
            if 'resumo_de_operacao' in df.columns:
                df['resumo_de_operacao'] = df['resumo_de_operacao'].fillna('Não encontrado')
            
            # Garantir que as novas colunas sejam string
            for col in ['cod_natureza_op', 'descricao_natureza_op', 'resumo_de_operacao']:
                if col in df.columns:
                    df[col] = df[col].astype(str).str.strip()
        
        # Log de sucesso
        if logger:
            tempo_processamento = time.time() - start_time
            logger.log_file_success(file_path.name, len(df), tempo_processamento)
        
        return df, ano_detectado
    
    except Exception as e:
        # Log de erro se o logger existir
        if logger:
            tempo_erro = time.time() - start_time
            logger.log_file_error(file_path.name, str(e), tempo_erro)
        # Re-lançar a exceção para ser tratada no nível superior
        raise


def save_to_parquet(df, planta, ano, mode='replace'):
    """
    Salva DataFrame em Parquet com append e deduplicação.
    
    Args:
        df: DataFrame com os dados
        planta: Nome da planta
        ano: Ano fiscal
        mode: 'replace' = substitui arquivo, 'append' = adiciona aos dados existentes
    """
    # Garantir estrutura de diretórios
    ensure_structure(planta, ano)
    
    base_path = get_base_path()
    parquet_path = base_path / "data_parquet" / planta / str(ano) / f"fiscal_{planta}_{ano}.parquet"
    
    # Se modo append E arquivo existe, carregar e concatenar
    if mode == 'append' and parquet_path.exists():
        df_existing = pd.read_parquet(parquet_path)
        df = pd.concat([df_existing, df], ignore_index=True)
    
    # NÃO deduplicar - cada linha é um registro fiscal legítimo
    # Mesmo que pareçam duplicados, podem ser múltiplos itens da mesma NF
    
    # Salvar com compressão para melhor performance
    df.to_parquet(
        parquet_path, 
        index=False, 
        engine='pyarrow',
        compression='snappy'  # Compressão rápida
    )
    
    return parquet_path


def get_parquet_last_modified(planta: str, ano: int):
    """
    Retorna a data de última modificação do arquivo Parquet.
    
    Args:
        planta: Nome da planta
        ano: Ano fiscal
        
    Returns:
        datetime ou None
    """
    base_path = get_base_path()
    parquet_path = base_path / "data_parquet" / planta / str(ano) / f"fiscal_{planta}_{ano}.parquet"
    
    if parquet_path.exists():
        return datetime.fromtimestamp(parquet_path.stat().st_mtime)
    return None


def process_raw_excel_to_parquet(planta: str, ano: int, mode='all', progress_callback=None):
    """
    Processa arquivos Excel de uma planta/ano para Parquet.
    
    Args:
        planta: Nome da planta
        ano: Ano fiscal
        mode: 'all' = processar todos, 'new' = somente novos/modificados
        progress_callback: Função callback para atualizar progresso (current, total, message, step)
        
    Returns:
        tuple: (sucesso, mensagem, registros_processados)
    """
    # Inicializar logger
    logger = ExtractionLogger(planta, ano)
    
    try:
        base_path = get_base_path()
        raw_path = base_path / "data_raw" / planta / str(ano)
        
        if not raw_path.exists():
            logger.error(f"Diretório não existe: {raw_path}")
            logger.finalize(status="erro")
            return False, f"Diretório não existe: {raw_path}", 0
        
        if progress_callback:
            progress_callback(0, 100, "🔍 Verificando arquivos Excel...", "Iniciando")
        
        logger.info(f"📂 Diretório: {raw_path}")
        logger.info(f"🔧 Modo: {mode}")
        
        # Listar arquivos Excel, ignorando temporários/ocultos
        excel_files = [
            f for f in list(raw_path.glob("*.xlsx")) + list(raw_path.glob("*.xls"))
            if not f.name.startswith("~$") and not f.name.startswith(".")
        ]
        
        if not excel_files:
            logger.warning(f"Nenhum arquivo Excel válido encontrado em {raw_path}")
            logger.finalize(status="erro")
            return False, f"Nenhum arquivo Excel válido encontrado em {raw_path}", 0
        
        logger.info(f"📊 Arquivos encontrados: {len(excel_files)}")
    
        # Filtrar por modo
        if mode == 'new':
            if progress_callback:
                progress_callback(5, 100, "🔎 Verificando arquivos modificados...", "Modo Incremental")
            
            logger.info("Verificando arquivos modificados...")
            
            last_parquet_time = get_parquet_last_modified(planta, ano)
            if last_parquet_time:
                original_count = len(excel_files)
                # Filtrar apenas arquivos modificados após o último processamento
                excel_files = [
                    f for f in excel_files 
                    if datetime.fromtimestamp(f.stat().st_mtime) > last_parquet_time
                ]
                if not excel_files:
                    logger.info("Nenhum arquivo novo ou modificado encontrado")
                    logger.finalize(status="sucesso")
                    return True, "Nenhum arquivo novo ou modificado encontrado", 0
                
                logger.info(f"Filtrados: {len(excel_files)} de {original_count} arquivos para processar")
                
                if progress_callback:
                    progress_callback(10, 100, f"✅ {len(excel_files)} de {original_count} arquivos precisam ser processados", "Filtrado")
        
        total_registros = 0
        total_files = len(excel_files)
        all_dataframes = []  # Acumular todos os DataFrames
        
        # FASE 1: Ler todos os arquivos Excel (mais rápido em batch)
        logger.info(f"Iniciando leitura de {total_files} arquivos...")
        
        # Contador para salvamento periódico
        arquivos_processados_desde_ultimo_save = 0
        
        for i, file_path in enumerate(excel_files):
            # Calcular percentual (10-80% para leitura)
            percent = int(10 + (i / total_files * 70))
            
            # Callback simples apenas a cada 2 arquivos ou no primeiro/último
            if progress_callback and (i % 2 == 0 or i == 0 or i == total_files - 1):
                progress_callback(
                    percent, 
                    100, 
                    f"{file_path.name}",
                    f"Arquivo {i+1}/{total_files}"
                )
            
            try:
                # Ler arquivo
                df, ano_detectado = read_monthly_excel(file_path, logger=logger)
                
                # Validar ano detectado com ano esperado
                if ano_detectado != ano:
                    warning_msg = f"Ano detectado ({ano_detectado}) difere do esperado ({ano}) em {file_path.name}"
                    logger.warning(warning_msg)
                    if st:
                        st.warning(warning_msg)
                
                all_dataframes.append(df)
                total_registros += len(df)
                arquivos_processados_desde_ultimo_save += 1
                
                # Salvar progresso a cada 3 arquivos para evitar perda total em caso de crash
                if arquivos_processados_desde_ultimo_save >= 3:
                    logger._save_to_history_partial()
                    arquivos_processados_desde_ultimo_save = 0
                
            except Exception as e:
                error_msg = str(e)
                if "Conversion failed" in error_msg:
                    error_msg = "Erro de tipo de dados - arquivo contém valores mistos"
                
                # Log do erro com detalhes
                tempo_erro = time.time()
                logger.log_file_error(file_path.name, error_msg, 0)
                logger.error(f"Falha ao processar {file_path.name}", exception=e)
                
                # Continuar com próximo arquivo
                if progress_callback:
                    progress_callback(
                        percent, 
                        100, 
                        f"ERRO: {file_path.name}",
                        f"Erro {i+1}/{total_files}"
                    )
                continue
        
        # Verificar se conseguiu processar pelo menos um arquivo
        if not all_dataframes:
            logger.error("Nenhum arquivo foi processado com sucesso")
            logger.finalize(status="erro")
            return False, "Nenhum arquivo foi processado com sucesso", 0
    
        # FASE 2: Concatenar e salvar TUDO de uma vez (muito mais rápido)
        if progress_callback:
            progress_callback(85, 100, f"🔗 Unindo {len(all_dataframes)} arquivos ({total_registros:,} registros)...", "Concatenando")
        
        logger.info(f"Concatenando {len(all_dataframes)} DataFrames com {total_registros:,} registros...")
        
        if all_dataframes:
            df_final = pd.concat(all_dataframes, ignore_index=True)
            
            logger.debug(f"Soma dos DataFrames individuais: {total_registros:,}")
            logger.debug(f"Após concat: {len(df_final):,}")
            logger.debug(f"Diferença: {total_registros - len(df_final):,}")
            
            if progress_callback:
                progress_callback(90, 100, f"💾 Salvando {len(df_final):,} registros em Parquet...", "Escrevendo")
            
            logger.info(f"Salvando {len(df_final):,} registros em Parquet...")
            
            # Salvar tudo de uma vez - mode='replace' para evitar duplicação em batch
            save_to_parquet(df_final, planta, ano, mode='replace')
            
            logger.info("✅ Dados salvos com sucesso!")
            
            if progress_callback:
                progress_callback(95, 100, "✅ Dados salvos com sucesso!", "Finalizado")
            
            # Criar consolidação para a página Home
            if progress_callback:
                progress_callback(97, 100, "📊 Criando consolidação de plantas...", "Consolidando")
            
            logger.info("Criando arquivos consolidados...")
            sucesso_cons, msg_cons = create_consolidated_parquets(planta, ano)
            if sucesso_cons:
                logger.info(f"Consolidação criada: {msg_cons}")
            else:
                logger.warning(f"Erro na consolidação: {msg_cons}")
        
        if progress_callback:
            progress_callback(98, 100, "🎯 Finalizando processamento...", "Quase pronto")
        
        if progress_callback:
            progress_callback(100, 100, f"🎉 Concluído! {total_registros:,} registros", "Finalizado")
        
        # Determinar status final
        if logger.session_data["arquivos_erro"] == 0:
            status_final = "sucesso"
        elif logger.session_data["arquivos_sucesso"] > 0:
            status_final = "parcial"
        else:
            status_final = "erro"
        
        logger.finalize(status=status_final)
        
        return True, f"Processados {len(excel_files)} arquivos com {total_registros:,} registros", total_registros
    
    except Exception as e:
        # Capturar qualquer erro não tratado
        logger.error(f"Erro crítico durante processamento", exception=e)
        
        # IMPORTANTE: Sempre finalizar o logger, mesmo em caso de erro
        try:
            logger.finalize(status="erro")
        except:
            pass  # Garantir que não lance exceção ao finalizar
        
        return False, f"Erro crítico: {str(e)}", 0
    
    finally:
        # Garantir que o logger seja finalizado em qualquer situação
        # Usar finally para executar mesmo se houver return/exception
        try:
            # Verificar se o logger já foi finalizado
            if logger and logger.session_data.get("fim") is None:
                logger.finalize(status="interrompido")
        except:
            pass  # Ignorar erros ao finalizar


def create_consolidated_parquets(planta: str, ano: int):
    """
    Cria arquivos parquet consolidados otimizados para a página Home.
    Gera tabelas sumarizadas por categoria para economizar memória.
    
    Args:
        planta: Nome da planta que foi processada
        ano: Ano que foi processado
        
    Returns:
        Tuple[bool, str]: (sucesso, mensagem)
    """
    try:
        base_path = get_base_path()
        
        # Caminho dos dados da planta
        parquet_path = base_path / "data_parquet" / planta / str(ano)
        
        if not parquet_path.exists():
            return False, f"Diretório de parquet não existe: {parquet_path}"
        
        # Verificar se existe arquivo parquet para esta planta/ano
        parquet_files = list(parquet_path.glob("*.parquet"))
        if not parquet_files:
            return False, f"Nenhum arquivo parquet encontrado em {parquet_path}"
        
        print(f"📊 Criando consolidações para {planta} - {ano}...")
        
        # Carregar dados completos da planta
        df = pd.read_parquet(parquet_path)
        
        if df.empty:
            return False, f"DataFrame vazio para {planta} - {ano}"
        
        # Criar diretório consolidado
        consolidated_path = base_path / "data_parquet" / "Plantas" / str(ano)
        consolidated_path.mkdir(parents=True, exist_ok=True)
        
        # 1. MENSAL - Agregado por mês
        print("  📈 Criando mensal.parquet...")
        if 'data_fiscal' in df.columns:
            df_mensal = df.groupby([
                pd.Grouper(key='data_fiscal', freq='ME')
            ]).agg({
                'valor_icms': 'sum',
                'base_icms_1': 'sum'
            }).reset_index()
            
            df_mensal['mes'] = df_mensal['data_fiscal'].dt.strftime('%Y-%m')
            df_mensal['planta'] = planta
            df_mensal['ano'] = ano
            
            # Salvar ou atualizar mensal.parquet
            mensal_file = consolidated_path / "mensal.parquet"
            if mensal_file.exists():
                # Carregar existente e remover dados antigos desta planta/ano
                df_mensal_existente = pd.read_parquet(mensal_file)
                df_mensal_existente = df_mensal_existente[
                    ~((df_mensal_existente['planta'] == planta) & (df_mensal_existente['ano'] == ano))
                ]
                df_mensal = pd.concat([df_mensal_existente, df_mensal], ignore_index=True)
            
            df_mensal.to_parquet(mensal_file, index=False)
            print(f"    ✅ mensal.parquet: {len(df_mensal)} registros")
        
        # 2. FORNECEDORES - Top agregado por razao_social
        print("  🏢 Criando fornecedores.parquet...")
        if 'razao_social' in df.columns:
            agg_dict = {
                'valor_icms': 'sum',
                'base_icms_1': 'sum',
                'quantidade': 'sum'
            }
            
            if 'numero_nf' in df.columns:
                agg_dict['numero_nf'] = 'nunique'
            if 'uf' in df.columns:
                agg_dict['uf'] = lambda x: x.mode()[0] if not x.mode().empty else x.iloc[0]
            if 'municipio' in df.columns:
                agg_dict['municipio'] = lambda x: x.mode()[0] if not x.mode().empty else x.iloc[0]
            if 'cst_icms' in df.columns:
                agg_dict['cst_icms'] = lambda x: x.mode()[0] if not x.mode().empty else x.iloc[0]
            
            df_fornecedores = df.groupby('razao_social').agg(agg_dict).reset_index()
            
            if 'numero_nf' in df_fornecedores.columns:
                df_fornecedores.rename(columns={'numero_nf': 'qtd_notas'}, inplace=True)
            
            df_fornecedores['planta'] = planta
            df_fornecedores['ano'] = ano
            df_fornecedores = df_fornecedores.sort_values('valor_icms', ascending=False)
            
            # Salvar ou atualizar fornecedores.parquet
            fornecedores_file = consolidated_path / "fornecedores.parquet"
            if fornecedores_file.exists():
                df_forn_existente = pd.read_parquet(fornecedores_file)
                df_forn_existente = df_forn_existente[
                    ~((df_forn_existente['planta'] == planta) & (df_forn_existente['ano'] == ano))
                ]
                df_fornecedores = pd.concat([df_forn_existente, df_fornecedores], ignore_index=True)
            
            df_fornecedores.to_parquet(fornecedores_file, index=False)
            print(f"    ✅ fornecedores.parquet: {len(df_fornecedores)} registros")
        
        # 3. PRODUTOS - Agregado por descricao
        print("  📦 Criando produtos.parquet...")
        if 'descricao' in df.columns:
            agg_dict = {
                'valor_icms': 'sum',
                'base_icms_1': 'sum',
                'quantidade': 'sum'
            }
            
            if 'razao_social' in df.columns:
                agg_dict['razao_social'] = 'nunique'
            if 'numero_nf' in df.columns:
                agg_dict['numero_nf'] = 'nunique'
            if 'cfop' in df.columns:
                agg_dict['cfop'] = lambda x: x.mode()[0] if not x.mode().empty else x.iloc[0]
            if 'cst_icms' in df.columns:
                agg_dict['cst_icms'] = lambda x: x.mode()[0] if not x.mode().empty else x.iloc[0]
            if 'descricao_natureza_op' in df.columns:
                agg_dict['descricao_natureza_op'] = lambda x: x.mode()[0] if not x.mode().empty else x.iloc[0]
            
            df_produtos = df.groupby('descricao').agg(agg_dict).reset_index()
            
            # Converter CFOP para int se existir
            if 'cfop' in df_produtos.columns:
                df_produtos['cfop'] = pd.to_numeric(df_produtos['cfop'], errors='coerce').fillna(0).astype(int)
            
            rename_dict = {}
            if 'razao_social' in df_produtos.columns:
                rename_dict['razao_social'] = 'qtd_fornecedores'
            if 'numero_nf' in df_produtos.columns:
                rename_dict['numero_nf'] = 'qtd_notas'
            if rename_dict:
                df_produtos.rename(columns=rename_dict, inplace=True)
            
            df_produtos['planta'] = planta
            df_produtos['ano'] = ano
            df_produtos = df_produtos.sort_values('valor_icms', ascending=False)
            
            # Salvar ou atualizar produtos.parquet
            produtos_file = consolidated_path / "produtos.parquet"
            if produtos_file.exists():
                df_prod_existente = pd.read_parquet(produtos_file)
                df_prod_existente = df_prod_existente[
                    ~((df_prod_existente['planta'] == planta) & (df_prod_existente['ano'] == ano))
                ]
                df_produtos = pd.concat([df_prod_existente, df_produtos], ignore_index=True)
            
            df_produtos.to_parquet(produtos_file, index=False)
            print(f"    ✅ produtos.parquet: {len(df_produtos)} registros")
        
        # 4. CFOP - Agregado por cfop e descricao_natureza_op
        print("  🔢 Criando cfop.parquet...")
        if 'cfop' in df.columns:
            df_copy = df.copy()
            # Manter CFOP como int para evitar erros no parquet
            df_copy['cfop'] = pd.to_numeric(df_copy['cfop'], errors='coerce').fillna(0).astype(int)
            
            group_cols = ['cfop']
            if 'descricao_natureza_op' in df_copy.columns:
                group_cols.append('descricao_natureza_op')
            
            agg_dict = {
                'valor_icms': 'sum',
                'base_icms_1': 'sum',
                'quantidade': 'sum'
            }
            
            if 'razao_social' in df_copy.columns:
                agg_dict['razao_social'] = 'nunique'
            if 'descricao' in df_copy.columns:
                agg_dict['descricao'] = 'nunique'
            if 'numero_nf' in df_copy.columns:
                agg_dict['numero_nf'] = 'nunique'
            if 'entrada_saida' in df_copy.columns:
                agg_dict['entrada_saida'] = lambda x: x.mode()[0] if not x.mode().empty else x.iloc[0]
            if 'cst_icms' in df_copy.columns:
                agg_dict['cst_icms'] = lambda x: x.mode()[0] if not x.mode().empty else x.iloc[0]
            
            df_cfop = df_copy.groupby(group_cols).agg(agg_dict).reset_index()
            
            rename_dict = {}
            if 'razao_social' in df_cfop.columns:
                rename_dict['razao_social'] = 'qtd_fornecedores'
            if 'descricao' in df_cfop.columns:
                rename_dict['descricao'] = 'qtd_produtos'
            if 'numero_nf' in df_cfop.columns:
                rename_dict['numero_nf'] = 'qtd_notas'
            if rename_dict:
                df_cfop.rename(columns=rename_dict, inplace=True)
            
            df_cfop['planta'] = planta
            df_cfop['ano'] = ano
            df_cfop = df_cfop.sort_values('valor_icms', ascending=False)
            
            # Salvar ou atualizar cfop.parquet
            cfop_file = consolidated_path / "cfop.parquet"
            if cfop_file.exists():
                df_cfop_existente = pd.read_parquet(cfop_file)
                df_cfop_existente = df_cfop_existente[
                    ~((df_cfop_existente['planta'] == planta) & (df_cfop_existente['ano'] == ano))
                ]
                df_cfop = pd.concat([df_cfop_existente, df_cfop], ignore_index=True)
            
            df_cfop.to_parquet(cfop_file, index=False)
            print(f"    ✅ cfop.parquet: {len(df_cfop)} registros")
        
        # 5. CFOPs NÃO ENCONTRADOS - Registros sem correspondência na tabela de códigos
        print("  ⚠️ Criando cfops_nao_encontrados.parquet...")
        if 'cod_natureza_op' in df.columns:
            df_nao_encontrados = df[df['cod_natureza_op'] == 'Não encontrado'].copy()
            
            if not df_nao_encontrados.empty:
                # Agrupar por CFOP e agregar informações
                agg_dict = {
                    'valor_icms': 'sum',
                    'base_icms_1': 'sum',
                    'quantidade': 'sum'
                }
                
                if 'numero_nf' in df_nao_encontrados.columns:
                    agg_dict['numero_nf'] = 'nunique'
                if 'razao_social' in df_nao_encontrados.columns:
                    agg_dict['razao_social'] = 'nunique'
                if 'descricao' in df_nao_encontrados.columns:
                    agg_dict['descricao'] = 'nunique'
                if 'entrada_saida' in df_nao_encontrados.columns:
                    agg_dict['entrada_saida'] = lambda x: x.mode()[0] if not x.mode().empty else x.iloc[0]
                if 'data_fiscal' in df_nao_encontrados.columns:
                    agg_dict['data_fiscal'] = ['min', 'max']
                
                df_cfops_nao_enc = df_nao_encontrados.groupby('cfop').agg(agg_dict).reset_index()
                
                # Renomear colunas multi-level se existir
                if isinstance(df_cfops_nao_enc.columns, pd.MultiIndex):
                    df_cfops_nao_enc.columns = ['_'.join(col).strip('_') if col[1] else col[0] 
                                                 for col in df_cfops_nao_enc.columns.values]
                
                # Renomear colunas para ficar mais claro
                rename_dict = {}
                if 'numero_nf' in df_cfops_nao_enc.columns:
                    rename_dict['numero_nf'] = 'qtd_notas'
                if 'razao_social' in df_cfops_nao_enc.columns:
                    rename_dict['razao_social'] = 'qtd_fornecedores'
                if 'descricao' in df_cfops_nao_enc.columns:
                    rename_dict['descricao'] = 'qtd_produtos'
                if 'data_fiscal_min' in df_cfops_nao_enc.columns:
                    rename_dict['data_fiscal_min'] = 'primeira_ocorrencia'
                if 'data_fiscal_max' in df_cfops_nao_enc.columns:
                    rename_dict['data_fiscal_max'] = 'ultima_ocorrencia'
                
                if rename_dict:
                    df_cfops_nao_enc.rename(columns=rename_dict, inplace=True)
                
                df_cfops_nao_enc['planta'] = planta
                df_cfops_nao_enc['ano'] = ano
                df_cfops_nao_enc = df_cfops_nao_enc.sort_values('valor_icms', ascending=False)
                
                # Salvar ou atualizar cfops_nao_encontrados.parquet
                cfops_nao_enc_file = consolidated_path / "cfops_nao_encontrados.parquet"
                if cfops_nao_enc_file.exists():
                    df_nao_enc_existente = pd.read_parquet(cfops_nao_enc_file)
                    df_nao_enc_existente = df_nao_enc_existente[
                        ~((df_nao_enc_existente['planta'] == planta) & (df_nao_enc_existente['ano'] == ano))
                    ]
                    df_cfops_nao_enc = pd.concat([df_nao_enc_existente, df_cfops_nao_enc], ignore_index=True)
                
                df_cfops_nao_enc.to_parquet(cfops_nao_enc_file, index=False)
                print(f"    ⚠️ cfops_nao_encontrados.parquet: {len(df_cfops_nao_enc)} CFOPs únicos não encontrados")
            else:
                print(f"    ✅ Nenhum CFOP não encontrado!")
        
        print(f"✅ Consolidação concluída para {planta} - {ano}")
        return True, f"Consolidação criada em {consolidated_path}"
        
    except Exception as e:
        print(f"❌ Erro ao criar consolidação: {e}")
        return False, f"Erro: {str(e)}"


def load_plantas():
    """Carrega lista de plantas do JSON."""
    base_path = get_base_path()
    config_path = base_path / "config" / "plantas.json"
    
    with open(config_path, 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    return config['plantas']


def add_planta(nome_planta: str):
    """
    Adiciona uma nova planta ao arquivo de configuração.
    
    Args:
        nome_planta: Nome da planta a adicionar
        
    Returns:
        bool: True se adicionada, False se já existia
    """
    base_path = get_base_path()
    config_path = base_path / "config" / "plantas.json"
    
    with open(config_path, 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    if nome_planta not in config['plantas']:
        config['plantas'].append(nome_planta)
        config['plantas'].sort()  # Manter ordenado
        
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=4, ensure_ascii=False)
        
        return True
    
    return False


def load_anos(planta):
    """
    Carrega lista de anos disponíveis para uma planta.
    Combina anos_iniciais + anos detectados nas pastas + faixa dinâmica.
    
    Args:
        planta: Nome da planta
        
    Returns:
        Lista de anos disponíveis (ordenada)
    """
    base_path = get_base_path()
    config_path = base_path / "config" / "plantas.json"
    
    with open(config_path, 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    anos = set(config['anos_iniciais'])
    
    # Detectar anos nas pastas data_raw
    raw_path = base_path / "data_raw" / planta
    if raw_path.exists():
        for ano_dir in raw_path.iterdir():
            if ano_dir.is_dir() and ano_dir.name.isdigit():
                anos.add(int(ano_dir.name))
    
    # Detectar anos nas pastas data_parquet
    parquet_path = base_path / "data_parquet" / planta
    if parquet_path.exists():
        for ano_dir in parquet_path.iterdir():
            if ano_dir.is_dir() and ano_dir.name.isdigit():
                anos.add(int(ano_dir.name))
    
    # Se nenhum ano foi detectado, criar faixa de 2010 até ano_atual + 5
    if len(anos) == 0:
        ano_atual = datetime.now().year
        anos = set(range(2010, ano_atual + 6))
    
    return sorted(list(anos))
