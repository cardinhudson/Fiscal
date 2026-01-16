"""Script de inicialização rápida do sistema.

Executa a aplicação Streamlit (streamlit_app.py).

Observação:
- Se existir um ambiente virtual em .venv, este script dá preferência a ele,
  para evitar erros de dependências quando você roda com um Python global.
"""

import os
import socket
import shutil
import subprocess
import sys
import time
import webbrowser
from pathlib import Path


def _pick_free_port(start_port: int = 8501, max_tries: int = 20) -> int:
    for port in range(start_port, start_port + max_tries):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            try:
                sock.bind(("127.0.0.1", port))
                return port
            except OSError:
                continue
    raise RuntimeError(
        f"Não encontrei uma porta livre entre {start_port} e {start_port + max_tries - 1}."
    )


def _wait_for_port(host: str, port: int, timeout_s: float = 10.0) -> bool:
    """Retorna True quando conseguir conectar em host:port antes do timeout."""
    deadline = time.time() + timeout_s
    while time.time() < deadline:
        try:
            with socket.create_connection((host, port), timeout=0.5):
                return True
        except OSError:
            time.sleep(0.1)
    return False

def main():
    """Inicia a aplicação Streamlit."""
    repo_root = Path(__file__).parent
    app_path = repo_root / "streamlit_app.py"

    venv_python_windows = repo_root / ".venv" / "Scripts" / "python.exe"
    venv_python_posix = repo_root / ".venv" / "bin" / "python"
    preferred_python = None
    if venv_python_windows.exists():
        preferred_python = venv_python_windows
    elif venv_python_posix.exists():
        preferred_python = venv_python_posix

    python_executable = str(preferred_python) if preferred_python else sys.executable
    
    print("🚀 Iniciando Sistema de Análise Fiscal Stellantis...")
    print(f"📂 Arquivo principal: {app_path}")
    port = _pick_free_port(8501)
    url = f"http://localhost:{port}"
    print(f"🌐 Abrirá em: {url}")
    if preferred_python:
        print(f"🐍 Usando Python do venv: {python_executable}")
    print("-" * 50)

    cmd = [
        python_executable,
        "-m",
        "streamlit",
        "run",
        str(app_path),
        "--server.port",
        str(port),
        "--server.address",
        "localhost",
    ]

    env = os.environ.copy()
    git_exe = shutil.which("git")
    if git_exe:
        env.setdefault("GIT_PYTHON_GIT_EXECUTABLE", git_exe)
        git_dir = str(Path(git_exe).parent)
        if git_dir and git_dir not in env.get("PATH", ""):
            env["PATH"] = f"{git_dir}{os.pathsep}{env.get('PATH', '')}"

    try:
        process = subprocess.Popen(cmd, cwd=str(repo_root), env=env)
    except FileNotFoundError:
        print("❌ Não consegui executar o Python configurado.")
        print(f"Tentado: {python_executable}")
        raise

    _wait_for_port("127.0.0.1", port, timeout_s=10.0)

    opened = False
    try:
        if sys.platform.startswith("win"):
            os.startfile(url)  # type: ignore[attr-defined]
            opened = True
        else:
            opened = bool(webbrowser.open(url))
    except Exception as exc:
        print(f"⚠️ Não consegui abrir automaticamente o navegador: {exc}")

    if not opened:
        print(f"➡️ Abra manualmente no navegador: {url}")

    process.wait()

if __name__ == "__main__":
    main()
