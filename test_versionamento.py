"""
Script para testar e demonstrar o sistema de versionamento
"""

from versionamento import (
    obter_versao_atual,
    incrementar_versao,
    resetar_versao,
    verificar_mudancas_paginas
)

print("=" * 60)
print("SISTEMA DE VERSIONAMENTO - TESTE")
print("=" * 60)

# 1. Versão atual
print(f"\n1. Versão atual: {obter_versao_atual()}")

# 2. Verificar mudanças nas páginas
houve_mudanca, versao = verificar_mudancas_paginas()
print(f"\n2. Verificação de mudanças:")
print(f"   - Houve mudança: {houve_mudanca}")
print(f"   - Versão: {versao}")

# 3. Demonstrar incremento
print(f"\n3. Demonstração de incremento:")
versao_atual = obter_versao_atual()
print(f"   - Antes: {versao_atual}")

# Simular alguns incrementos
print("\n   Sequência de incrementos:")
for i in range(5):
    nova_versao = incrementar_versao()
    print(f"   - Incremento {i+1}: {nova_versao}")

# Mostrar versão final
print(f"\n4. Versão final após incrementos: {obter_versao_atual()}")

print("\n" + "=" * 60)
print("✅ TESTE CONCLUÍDO")
print("=" * 60)
print("\nPara resetar a versão para 1.0, use:")
print("   from versionamento import resetar_versao")
print("   resetar_versao('1.0')")
