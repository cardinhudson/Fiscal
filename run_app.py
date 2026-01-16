"""
Script de inicialização rápida do sistema.
Executa: streamlit run app/Home.py
"""

import subprocess
import sys
from pathlib import Path

def main():
    """Inicia a aplicação Streamlit."""
    app_path = Path(__file__).parent / "app" / "Home.py"
    
    print("🚀 Iniciando Sistema de Análise Fiscal Stellantis...")
    print(f"📂 Arquivo principal: {app_path}")
    print("🌐 Abrirá em: http://localhost:8501")
    print("-" * 50)
    
    subprocess.run([sys.executable, "-m", "streamlit", "run", str(app_path)])

if __name__ == "__main__":
    main()
