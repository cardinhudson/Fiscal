"""
Componentes compartilhados para todas as páginas do sistema
"""

import streamlit as st
from datetime import datetime
from pathlib import Path
import sys

# Adicionar diretório raiz ao path para importar versionamento
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from versionamento import obter_versao_atual


def obter_mes_atual():
    """Retorna o mês atual em português"""
    meses = {
        1: "Janeiro", 2: "Fevereiro", 3: "Março", 4: "Abril",
        5: "Maio", 6: "Junho", 7: "Julho", 8: "Agosto",
        9: "Setembro", 10: "Outubro", 11: "Novembro", 12: "Dezembro"
    }
    agora = datetime.now()
    return meses[agora.month]


def obter_data_atualizacao_dados():
    """Retorna a data e hora da última atualização dos arquivos de dados"""
    try:
        # Verificar parquets consolidados
        arquivos_dados = []
        pasta_plantas = Path("data_parquet/Plantas")
        
        if pasta_plantas.exists():
            for ano_dir in pasta_plantas.iterdir():
                if ano_dir.is_dir():
                    for arquivo in ano_dir.glob("*.parquet"):
                        arquivos_dados.append(arquivo)
        
        # Também verificar dados por planta
        pasta_parquet = Path("data_parquet")
        if pasta_parquet.exists():
            for planta_dir in pasta_parquet.iterdir():
                if planta_dir.is_dir() and planta_dir.name != "Plantas":
                    for ano_dir in planta_dir.iterdir():
                        if ano_dir.is_dir():
                            for arquivo in ano_dir.glob("*.parquet"):
                                arquivos_dados.append(arquivo)

        data_atualizacao = None
        for arquivo in arquivos_dados:
            if arquivo.exists():
                try:
                    data_modificacao = arquivo.stat().st_mtime
                    if data_modificacao and data_modificacao > 0:
                        if data_atualizacao is None or data_modificacao > data_atualizacao:
                            data_atualizacao = data_modificacao
                except (OSError, ValueError):
                    continue

        if data_atualizacao and data_atualizacao > 0:
            try:
                dt = datetime.fromtimestamp(data_atualizacao)
                meses = {
                    1: "Janeiro", 2: "Fevereiro", 3: "Março", 4: "Abril",
                    5: "Maio", 6: "Junho", 7: "Julho", 8: "Agosto",
                    9: "Setembro", 10: "Outubro", 11: "Novembro", 12: "Dezembro"
                }
                return f"{dt.day:02d} de {meses[dt.month]} de {dt.year} às {dt.hour:02d}:{dt.minute:02d}"
            except (ValueError, OSError):
                return None
        return None
    except Exception:
        return None


def renderizar_cabecalho():
    """Renderiza o cabeçalho padrão do sistema"""
    mes_atual = obter_mes_atual()
    ano_atual = datetime.now().year
    versao_atual = obter_versao_atual()
    data_atualizacao = obter_data_atualizacao_dados()
    
    # Montar textos do cabeçalho
    texto_esquerda = f"📚 Sistema de Análise Fiscal | Versão {versao_atual} | {mes_atual} {ano_atual} | Desenvolvido por Osvaldo Tibola e Hudson Cardin"  
    texto_direita = f"📅 Extração atualizada em: {data_atualizacao}" if data_atualizacao else ""
    
    st.markdown(f"""
    <div style='display: flex; justify-content: space-between; align-items: center; color: #fff; padding: 8px 10px; font-size: 0.85rem; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-bottom: 1px solid #5a4fcf; margin-bottom: 10px;'>
        <div style='flex: 1;'>{texto_esquerda}</div>
        <div style='flex: 0 0 auto; margin-left: 20px;'>{texto_direita}</div>
    </div>
    """, unsafe_allow_html=True)


def renderizar_rodape():
    """Renderiza o rodapé padrão do sistema"""
    mes_atual = obter_mes_atual()
    ano_atual = datetime.now().year
    versao_atual = obter_versao_atual()
    
    st.markdown(f"""
    <div style='text-align: center; color: #666; padding: 20px; margin-top: 40px;'>
        📚 Sistema de Análise Fiscal | Versão {versao_atual} | {mes_atual} {ano_atual}
        <br>
        <small>Desenvolvido por Osvaldo Tibola e Hudson Cardin ❤️ usando Python + Streamlit</small>
    </div>
    """, unsafe_allow_html=True)
