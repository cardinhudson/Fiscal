"""
Sistema de Logging para Extração de Dados Fiscais
Registra todo o processo de extração com timestamps, status e detalhes.
"""

import json
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional


class ExtractionLogger:
    """
    Logger customizado para processos de extração.
    Registra logs em arquivo e memória para visualização posterior.
    """
    
    def __init__(self, planta: str, ano: int):
        """
        Inicializa o logger.
        
        Args:
            planta: Nome da planta
            ano: Ano fiscal
        """
        self.planta = planta
        self.ano = ano
        self.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Criar diretório de logs
        self.log_dir = Path(__file__).parent.parent / "logs"
        self.log_dir.mkdir(exist_ok=True)
        
        # Arquivo de log da sessão atual
        self.log_file = self.log_dir / f"extraction_{planta}_{ano}_{self.session_id}.log"
        
        # Arquivo JSON com histórico completo
        self.history_file = self.log_dir / "extraction_history.json"
        
        # Configurar logging Python padrão
        self.logger = logging.getLogger(f"extraction_{planta}_{ano}")
        self.logger.setLevel(logging.DEBUG)
        
        # Handler para arquivo
        file_handler = logging.FileHandler(self.log_file, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        formatter = logging.Formatter(
            '%(asctime)s | %(levelname)-8s | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)
        
        # Dados da sessão atual
        self.session_data = {
            "session_id": self.session_id,
            "planta": planta,
            "ano": ano,
            "inicio": datetime.now().isoformat(),
            "fim": None,
            "status": "em_andamento",
            "arquivos_processados": [],
            "total_registros": 0,
            "total_arquivos": 0,
            "arquivos_sucesso": 0,
            "arquivos_erro": 0,
            "erros": [],
            "warnings": [],
            "tempo_total_segundos": None
        }
        
        self.inicio_timestamp = datetime.now()
        
        # Log inicial
        self.info(f"🚀 Iniciando extração - Planta: {planta}, Ano: {ano}")
    
    def debug(self, message: str):
        """Registra mensagem de debug."""
        self.logger.debug(message)
    
    def info(self, message: str):
        """Registra mensagem informativa."""
        self.logger.info(message)
        # Força flush imediato
        for handler in self.logger.handlers:
            handler.flush()
    
    def warning(self, message: str):
        """Registra aviso."""
        self.logger.warning(message)
        self.session_data["warnings"].append({
            "timestamp": datetime.now().isoformat(),
            "message": message
        })
        # Força flush imediato
        for handler in self.logger.handlers:
            handler.flush()
    
    def error(self, message: str, exception: Optional[Exception] = None):
        """
        Registra erro.
        
        Args:
            message: Mensagem de erro
            exception: Exceção Python opcional
        """
        error_data = {
            "timestamp": datetime.now().isoformat(),
            "message": message
        }
        
        if exception:
            error_data["exception_type"] = type(exception).__name__
            error_data["exception_message"] = str(exception)
            self.logger.error(f"{message} | Exceção: {type(exception).__name__}: {exception}")
        else:
            self.logger.error(message)
        
        self.session_data["erros"].append(error_data)
        self.session_data["arquivos_erro"] += 1
        
        # Força flush imediato e salva histórico parcial
        for handler in self.logger.handlers:
            handler.flush()
        # Salvar histórico parcial em caso de crash
        self._save_to_history_partial()
    
    def log_file_start(self, filename: str, file_size_mb: float):
        """
        Registra início de processamento de arquivo.
        
        Args:
            filename: Nome do arquivo
            file_size_mb: Tamanho em MB
        """
        self.info(f"📄 Processando: {filename} ({file_size_mb:.2f} MB)")
        self.session_data["total_arquivos"] += 1
    
    def log_file_success(self, filename: str, registros: int, tempo_segundos: float):
        """
        Registra sucesso no processamento de arquivo.
        
        Args:
            filename: Nome do arquivo
            registros: Quantidade de registros processados
            tempo_segundos: Tempo de processamento
        """
        self.info(f"✅ {filename} - {registros:,} registros em {tempo_segundos:.2f}s")
        
        self.session_data["arquivos_processados"].append({
            "filename": filename,
            "registros": registros,
            "tempo_segundos": round(tempo_segundos, 2),
            "status": "sucesso",
            "timestamp": datetime.now().isoformat()
        })
        
        self.session_data["total_registros"] += registros
        self.session_data["arquivos_sucesso"] += 1
        
        # Salvar histórico parcial a cada 5 arquivos processados
        if self.session_data["arquivos_sucesso"] % 5 == 0:
            self._save_to_history_partial()
    
    def log_file_error(self, filename: str, error_message: str, tempo_segundos: float):
        """
        Registra erro no processamento de arquivo.
        
        Args:
            filename: Nome do arquivo
            error_message: Mensagem de erro
            tempo_segundos: Tempo até o erro
        """
        self.error(f"❌ {filename} - Erro: {error_message}")
        
        self.session_data["arquivos_processados"].append({
            "filename": filename,
            "registros": 0,
            "tempo_segundos": round(tempo_segundos, 2),
            "status": "erro",
            "error": error_message,
            "timestamp": datetime.now().isoformat()
        })
    
    def log_progress(self, current: int, total: int, message: str):
        """
        Registra progresso.
        
        Args:
            current: Valor atual
            total: Valor total
            message: Mensagem de progresso
        """
        percent = (current / total * 100) if total > 0 else 0
        self.debug(f"📊 Progresso: {current}/{total} ({percent:.1f}%) - {message}")
    
    def finalize(self, status: str = "sucesso"):
        """
        Finaliza a sessão de logging.
        
        Args:
            status: Status final ("sucesso", "erro", "parcial")
        """
        fim_timestamp = datetime.now()
        tempo_total = (fim_timestamp - self.inicio_timestamp).total_seconds()
        
        self.session_data["fim"] = fim_timestamp.isoformat()
        self.session_data["status"] = status
        self.session_data["tempo_total_segundos"] = round(tempo_total, 2)
        
        # Log final
        if status == "sucesso":
            self.info(f"🎉 Extração concluída com sucesso!")
        elif status == "erro":
            self.info(f"❌ Extração finalizada com erros")
        else:
            self.info(f"⚠️ Extração parcial")
        
        self.info(f"📊 Resumo: {self.session_data['arquivos_sucesso']}/{self.session_data['total_arquivos']} arquivos, {self.session_data['total_registros']:,} registros")
        self.info(f"⏱️ Tempo total: {tempo_total:.2f}s ({tempo_total/60:.1f} min)")
        
        # Salvar no histórico JSON
        self._save_to_history()
        
        # Fechar handlers
        for handler in self.logger.handlers:
            handler.close()
    
    def _save_to_history(self):
        """Salva sessão atual no histórico JSON."""
        history = []
        
        # Carregar histórico existente
        if self.history_file.exists():
            try:
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    history = json.load(f)
            except:
                history = []
        
        # Adicionar sessão atual
        history.append(self.session_data)
        
        # Manter apenas últimas 100 sessões
        history = history[-100:]
        
        # Salvar com flush imediato
        with open(self.history_file, 'w', encoding='utf-8') as f:
            json.dump(history, f, indent=2, ensure_ascii=False)
            f.flush()
    
    def _save_to_history_partial(self):
        """Salva histórico parcial durante a execução (em caso de crash)."""
        try:
            history = []
            
            # Carregar histórico existente
            if self.history_file.exists():
                try:
                    with open(self.history_file, 'r', encoding='utf-8') as f:
                        history = json.load(f)
                except:
                    history = []
            
            # Atualizar ou adicionar sessão atual
            # Procurar se já existe uma entrada com este session_id
            found = False
            for i, session in enumerate(history):
                if session.get('session_id') == self.session_id:
                    history[i] = self.session_data.copy()
                    found = True
                    break
            
            if not found:
                history.append(self.session_data.copy())
            
            # Manter apenas últimas 100 sessões
            history = history[-100:]
            
            # Salvar com flush imediato
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(history, f, indent=2, ensure_ascii=False)
                f.flush()
        except Exception as e:
            # Ignorar erros ao salvar parcialmente
            self.logger.debug(f"Erro ao salvar histórico parcial: {e}")
    
    def get_session_data(self) -> Dict:
        """Retorna dados da sessão atual."""
        return self.session_data.copy()


def load_extraction_history() -> List[Dict]:
    """
    Carrega histórico de extrações.
    
    Returns:
        Lista de sessões de extração
    """
    history_file = Path(__file__).parent.parent / "logs" / "extraction_history.json"
    
    if history_file.exists():
        try:
            with open(history_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return []
    
    return []


def get_latest_logs(limit: int = 10) -> List[str]:
    """
    Retorna os últimos arquivos de log.
    
    Args:
        limit: Quantidade máxima de logs
        
    Returns:
        Lista de caminhos de arquivos de log
    """
    log_dir = Path(__file__).parent.parent / "logs"
    
    if not log_dir.exists():
        return []
    
    log_files = sorted(
        log_dir.glob("extraction_*.log"),
        key=lambda x: x.stat().st_mtime,
        reverse=True
    )
    
    return [str(f) for f in log_files[:limit]]


def read_log_file(log_path: str) -> str:
    """
    Lê conteúdo de um arquivo de log.
    
    Args:
        log_path: Caminho do arquivo
        
    Returns:
        Conteúdo do arquivo
    """
    try:
        with open(log_path, 'r', encoding='utf-8') as f:
            return f.read()
    except:
        return "Erro ao ler arquivo de log"
