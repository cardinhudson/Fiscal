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


def get_base_path():
    """Retorna o caminho base do projeto."""
    return Path(__file__).parent.parent


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


def read_monthly_excel(file_path):
    """
    Lê um arquivo Excel mensal e padroniza os dados.
    Lê APENAS as colunas essenciais para melhor performance.
    
    Args:
        file_path: Caminho do arquivo Excel
        
    Returns:
        DataFrame padronizado com ano detectado
    """
    # Colunas essenciais que serão utilizadas no sistema (em MAIÚSCULAS como no Excel)
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
    
    return df, ano_detectado


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
    base_path = get_base_path()
    raw_path = base_path / "data_raw" / planta / str(ano)
    
    if not raw_path.exists():
        return False, f"Diretório não existe: {raw_path}", 0
    
    if progress_callback:
        progress_callback(0, 100, "🔍 Verificando arquivos Excel...", "Iniciando")
    
    # Listar arquivos Excel, ignorando temporários/ocultos
    excel_files = [
        f for f in list(raw_path.glob("*.xlsx")) + list(raw_path.glob("*.xls"))
        if not f.name.startswith("~$") and not f.name.startswith(".")
    ]
    
    if not excel_files:
        return False, f"Nenhum arquivo Excel válido encontrado em {raw_path}", 0
    
    # Filtrar por modo
    if mode == 'new':
        if progress_callback:
            progress_callback(5, 100, "🔎 Verificando arquivos modificados...", "Modo Incremental")
        
        last_parquet_time = get_parquet_last_modified(planta, ano)
        if last_parquet_time:
            original_count = len(excel_files)
            # Filtrar apenas arquivos modificados após o último processamento
            excel_files = [
                f for f in excel_files 
                if datetime.fromtimestamp(f.stat().st_mtime) > last_parquet_time
            ]
            if not excel_files:
                return True, "Nenhum arquivo novo ou modificado encontrado", 0
            
            if progress_callback:
                progress_callback(10, 100, f"✅ {len(excel_files)} de {original_count} arquivos precisam ser processados", "Filtrado")
    
    total_registros = 0
    total_files = len(excel_files)
    all_dataframes = []  # Acumular todos os DataFrames
    
    # FASE 1: Ler todos os arquivos Excel (mais rápido em batch)
    for i, file_path in enumerate(excel_files):
        # Calcular percentual (10-80% para leitura)
        percent = int(10 + (i / total_files * 70))
        
        if progress_callback:
            progress_callback(
                percent, 
                100, 
                f"📄 {i+1}/{total_files}: {file_path.name}",
                "Lendo Excel"
            )
        
        try:
            df, ano_detectado = read_monthly_excel(file_path)
            
            if progress_callback:
                progress_callback(
                    percent + 1, 
                    100, 
                    f"✓ Lido {len(df):,} registros",
                    f"Processado {i+1}/{total_files}"
                )
            
            # Validar ano detectado com ano esperado
            if ano_detectado != ano:
                st.warning(f"Ano detectado ({ano_detectado}) difere do esperado ({ano}) em {file_path.name}")
            
            all_dataframes.append(df)
            total_registros += len(df)
            
        except Exception as e:
            error_msg = str(e)
            if "Conversion failed" in error_msg:
                error_msg = "Erro de tipo de dados - arquivo contém valores mistos"
            return False, f"Erro ao processar {file_path.name}: {error_msg}", total_registros
    
    # FASE 2: Concatenar e salvar TUDO de uma vez (muito mais rápido)
    if progress_callback:
        progress_callback(85, 100, f"🔗 Unindo {len(all_dataframes)} arquivos ({total_registros:,} registros)...", "Concatenando")
    
    if all_dataframes:
        df_final = pd.concat(all_dataframes, ignore_index=True)
        
        print(f"\n🔍 DEBUG:")
        print(f"   Soma dos DataFrames individuais: {total_registros:,}")
        print(f"   Após concat: {len(df_final):,}")
        print(f"   Diferença: {total_registros - len(df_final):,}")
        
        if progress_callback:
            progress_callback(90, 100, f"💾 Salvando {len(df_final):,} registros em Parquet...", "Escrevendo")
        
        # Salvar tudo de uma vez - mode='replace' para evitar duplicação em batch
        save_to_parquet(df_final, planta, ano, mode='replace')
        
        if progress_callback:
            progress_callback(95, 100, "✅ Dados salvos com sucesso!", "Finalizado")
    
    if progress_callback:
        progress_callback(95, 100, "🎯 Finalizando processamento...", "Quase pronto")
    
    if progress_callback:
        progress_callback(100, 100, f"🎉 Concluído! {total_registros:,} registros", "Finalizado")
    
    return True, f"Processados {len(excel_files)} arquivos com {total_registros:,} registros", total_registros


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
