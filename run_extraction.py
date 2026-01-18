"""
Script standalone para executar extração - usado pelo Streamlit via subprocess
"""
import sys
import os
import json

# Forçar UTF-8 no Windows
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

from extraction.extracao import process_raw_excel_to_parquet

def main():
    if len(sys.argv) != 4:
        print(json.dumps({"error": "Argumentos inválidos"}))
        sys.exit(1)
    
    planta = sys.argv[1]
    ano = int(sys.argv[2])
    mode = sys.argv[3]
    
    print(f"INICIO: Processando {planta} - {ano} (modo: {mode})")
    print("-" * 80)
    
    # Callback que imprime diretamente
    def print_progress(percent, total, message, step):
        print(f"[{percent:3d}%] [{step}] {message}", flush=True)
    
    try:
        sucesso, mensagem, total_registros = process_raw_excel_to_parquet(
            planta,
            ano,
            mode=mode,
            progress_callback=print_progress
        )
        
        print("-" * 80)
        if sucesso:
            print(f"SUCESSO: {mensagem}")
            print(f"Total: {total_registros:,} registros")
            print(json.dumps({
                "success": True,
                "message": mensagem,
                "total": total_registros
            }))
        else:
            print(f"ERRO: {mensagem}")
            print(json.dumps({
                "success": False,
                "message": mensagem,
                "total": 0
            }))
    
    except Exception as e:
        print("-" * 80)
        print(f"EXCECAO: {str(e)}")
        import traceback
        traceback.print_exc()
        print(json.dumps({
            "success": False,
            "message": str(e),
            "total": 0
        }))
        sys.exit(1)

if __name__ == "__main__":
    main()
