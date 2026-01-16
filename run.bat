@echo off
setlocal
set REPO=%~dp0
set PY=%REPO%.venv\Scripts\python.exe

if not exist "%PY%" (
  echo Nao achei o venv em: %PY%
  echo Crie o venv e instale dependencias:
  echo   python -m venv .venv
  echo   .\.venv\Scripts\Activate.ps1
  echo   pip install -r requirements.txt
  exit /b 1
)

cd /d "%REPO%"
"%PY%" -m streamlit run Home.py
endlocal
