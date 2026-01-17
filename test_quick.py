"""Teste rápido de performance"""
import time
from extraction.extracao import process_raw_excel_to_parquet

print("Testando performance...")
inicio = time.time()

# Contador de callbacks
callback_count = 0

def contador_callback(percent, total, message, step):
    global callback_count
    callback_count += 1
    print(f"[{percent:3d}%] {step}: {message}")

sucesso, msg, total = process_raw_excel_to_parquet(
    'Goiana', 2025, mode='all', progress_callback=contador_callback
)

tempo = time.time() - inicio

print(f"\n{'='*70}")
print(f"Resultado: {'✅ SUCESSO' if sucesso else '❌ FALHA'}")
print(f"Mensagem: {msg}")
print(f"Registros: {total:,}")
print(f"Tempo: {tempo:.2f}s")
print(f"Callbacks: {callback_count}")
print(f"Velocidade: {total/tempo:,.0f} registros/segundo")
print(f"{'='*70}")
