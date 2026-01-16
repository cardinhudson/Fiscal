"""Script de inicialização rápida do sistema.

Executa a aplicação Streamlit (app/Home.py).

Observação:
- Se existir um ambiente virtual em .venv, este script dá preferência a ele,
  para evitar erros de dependências quando você roda com um Python global.
"""

import os
import shutil
import subprocess
import sys
import time
import webbrowser
from pathlib import Path

def main():
    """Inicia a aplicação Streamlit."""
    repo_root = Path(__file__).parent
    app_path = repo_root / "app" / "Home.py"

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
    url = "http://localhost:8501"
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
        "8501",
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

    time.sleep(1.0)
    try:
        webbrowser.open(url)
    except Exception:
        pass

    process.wait()

if __name__ == "__main__":
    main()
