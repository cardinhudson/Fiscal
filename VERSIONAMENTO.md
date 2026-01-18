# Sistema de Versionamento - Projeto Fiscal

## 📋 O que foi implementado

Sistema de versionamento automático idêntico ao projeto TC, adaptado para o projeto Fiscal Stellantis.

## 📁 Arquivos Criados/Modificados

### 1. `versionamento.py` (NOVO)
- Sistema completo de versionamento automático
- Incremento seguindo padrão: 1.0 → 1.01 → 1.02 → ... → 1.09 → 1.1 → 1.11 → etc.
- Monitoramento de mudanças nas páginas (`app/pages/`)
- Auto-incremento quando detecta alterações

**Funções principais:**
- `obter_versao_atual()` - Retorna versão atual sem incrementar
- `incrementar_versao()` - Incrementa versão manualmente
- `resetar_versao(nova_versao)` - Reseta para versão específica
- `verificar_mudancas_paginas()` - Verifica mudanças e auto-incrementa

### 2. `Home.py` (MODIFICADO)
Adicionado:
- **Import:** `from versionamento import obter_versao_atual, verificar_mudancas_paginas`
- **Verificação automática:** Chama `verificar_mudancas_paginas()` ao iniciar
- **Funções auxiliares:**
  - `obter_mes_atual()` - Retorna mês em português
  - `obter_data_atualizacao_dados()` - Retorna data/hora da última atualização dos parquets
- **Cabeçalho:** Banner com versão, data e desenvolvedores
- **Rodapé:** Footer com versão e créditos

### 3. Arquivos JSON (AUTO-GERADOS)
- `versao.json` - Armazena versão atual e data de atualização
- `controle_paginas.json` - Timestamps das páginas para detectar mudanças

## 🎨 Visual do Cabeçalho e Rodapé

### Cabeçalho (Topo de todas as páginas)
```
┌────────────────────────────────────────────────────────────────────┐
│ 📚 Sistema de Análise Fiscal | Versão 1.0 | Janeiro 2026 |        │
│ Desenvolvido por Osvaldo Tibola e Hudson Cardin                    │
│                            📅 Dados atualizados em: 18/01/2026 11:27│
└────────────────────────────────────────────────────────────────────┘
```

### Rodapé (Final da página)
```
┌────────────────────────────────────────────────────────────────────┐
│          📚 Sistema de Análise Fiscal | Versão 1.0 | Janeiro 2026  │
│              Desenvolvido por Osvaldo Tibola e Hudson Cardin        │
└────────────────────────────────────────────────────────────────────┘
```

## 🚀 Como Funciona

### 1. Incremento Automático
Cada vez que uma página em `app/pages/` é modificada, o sistema:
1. Detecta a mudança comparando timestamps
2. Incrementa a versão automaticamente
3. Atualiza o arquivo `versao.json`

### 2. Exibição da Versão
- **Home.py** exibe a versão no cabeçalho e rodapé
- Atualiza automaticamente a cada execução
- Mostra data/hora da última atualização dos dados

### 3. Controle Manual
Você pode controlar a versão manualmente:

```python
from versionamento import resetar_versao, incrementar_versao

# Resetar para versão específica
resetar_versao("2.0")

# Incrementar manualmente
incrementar_versao()
```

## 📝 Equipe

Os nomes foram configurados de acordo com `dados_equipe_fiscal.json`:
- **Osvaldo Tibola** - Primeiro desenvolvedor
- **Hudson Cardin** - Especialista Controle e Gestão

## 🔧 Próximos Passos

Para aplicar o mesmo cabeçalho/rodapé nas outras páginas:

1. **app/pages/analise_fiscal.py**
2. **app/pages/extracao.py**
3. **app/pages/documentacao.py**

Basta adicionar no início de cada página:
```python
from versionamento import obter_versao_atual

mes_atual = obter_mes_atual()
ano_atual = datetime.now().year
versao_atual = obter_versao_atual()
# ... código do cabeçalho
```

E no final:
```python
# ... código do rodapé
```

## ✅ Validação

Todos os arquivos foram validados:
- ✅ `versionamento.py` - Sintaxe OK
- ✅ `Home.py` - Sintaxe OK
- ✅ Sistema funcionando: Versão 1.0 criada
- ✅ Arquivos JSON gerados automaticamente

## 🎯 Benefícios

1. **Rastreabilidade:** Versão incrementa a cada mudança
2. **Profissionalismo:** Cabeçalho/rodapé padronizados
3. **Informativo:** Mostra data de atualização dos dados
4. **Automático:** Não precisa lembrar de incrementar manualmente
5. **Créditos:** Reconhece desenvolvedores em todas as páginas
