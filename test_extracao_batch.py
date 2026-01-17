"""
Teste rápido de extração em modo batch para diagnosticar performance
"""
import sys
import time
from pathlib import Path
from extraction.extracao import process_raw_excel_to_parquet

# Callback com saída visual melhorada
def simple_callback(percent, total, message, step):
    timestamp = time.strftime("%H:%M:%S")
    print(f"\r[{timestamp}] [{percent:3d}%] [{step:20s}] {message}", end='', flush=True)
    if percent == 100 or "❌" in message or "✅ Dados salvos" in message:
        print()  # Nova linha para marcos importantes

print("=" * 100)
print(" " * 35 + "TESTE DE EXTRAÇÃO EM MODO BATCH")
print("=" * 100)
print()

# Testar com Goiana 2025
print("Testando: Goiana 2025")
print("-" * 100)
print()

inicio = time.time()

try:
    sucesso, mensagem, total = process_raw_excel_to_parquet(
        'Goiana',
        2025,
        mode='all',
        progress_callback=simple_callback
    )
    
    print()
    print()
    print("=" * 100)
    if sucesso:
        print(f"✅ SUCESSO: {mensagem}")
        print(f"📊 Total de registros: {total:,}")
    else:
        print(f"❌ ERRO: {mensagem}")
    
    tempo_total = time.time() - inicio
    print(f"⏱️  Tempo total: {tempo_total:.2f} segundos")
    print("=" * 100)
    
except Exception as e:
    print()
    print()
    print("=" * 100)
    print(f"❌ EXCEÇÃO: {e}")
    print("=" * 100)
    import traceback
    traceback.print_exc()
