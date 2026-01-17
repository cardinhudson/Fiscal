# Sistema de Logging para Extração de Dados

## 📋 Visão Geral

Foi implementado um sistema completo de logging para rastrear todas as operações de extração de dados, permitindo diagnóstico detalhado de problemas e auditoria de processos.

## ✨ Funcionalidades Implementadas

### 1. **Logger Customizado (extraction/logger.py)**

Classe `ExtractionLogger` que registra:
- ✅ Timestamp de cada operação
- ✅ Arquivos processados com sucesso/erro
- ✅ Quantidade de registros por arquivo
- ✅ Tempo de processamento
- ✅ Erros e exceções com stack trace
- ✅ Avisos (warnings)
- ✅ Progresso da extração

### 2. **Histórico Persistente**

- Logs salvos em arquivos `.log` individuais por sessão
- Histórico consolidado em JSON (`extraction_history.json`)
- Mantém últimas 100 execuções
- Cada sessão possui um `session_id` único

### 3. **Tratamento Robusto de Erros**

O processamento agora:
- ❌ **NÃO para** ao encontrar erro em um arquivo
- ✅ **Continua** processando os demais arquivos
- ✅ Registra erros detalhadamente
- ✅ Retorna status "parcial" quando alguns arquivos falham
- ✅ Captura exceções não tratadas

### 4. **Nova Página de Logs (app/pages/logs.py)**

Interface visual para:
- 📊 **Histórico Resumido:**
  - Lista todas as execuções
  - Filtros por planta, ano, status
  - Métricas: registros, tempo, arquivos processados
  - Detalhes de erros e warnings
  - Lista de arquivos processados

- 📄 **Logs Detalhados:**
  - Visualização de logs completos
  - Filtro por nível (INFO, WARNING, ERROR, DEBUG)
  - Estatísticas: total de linhas, erros, avisos
  - Download de arquivos de log

## 📁 Estrutura de Arquivos

```
logs/
├── README.md                                    # Documentação do diretório
├── extraction_Goiana_2025_20260116_143052.log  # Log individual
├── extraction_PortoReal_2025_20260116_150230.log
└── extraction_history.json                     # Histórico consolidado
```

## 🔍 Exemplo de Log

```log
2026-01-16 14:30:52 | INFO     | 🚀 Iniciando extração - Planta: Goiana, Ano: 2025
2026-01-16 14:30:52 | INFO     | 📂 Diretório: C:\user\U235107\GitHub\Fiscal\data_raw\Goiana\2025
2026-01-16 14:30:52 | INFO     | 🔧 Modo: all
2026-01-16 14:30:52 | INFO     | 📊 Arquivos encontrados: 12
2026-01-16 14:30:52 | INFO     | Iniciando leitura de 12 arquivos...
2026-01-16 14:30:52 | INFO     | 📄 Processando: janeiro_2025.xlsx (2.34 MB)
2026-01-16 14:30:55 | INFO     | ✅ janeiro_2025.xlsx - 15,234 registros em 2.87s
2026-01-16 14:30:55 | INFO     | 📄 Processando: fevereiro_2025.xlsx (1.98 MB)
2026-01-16 14:30:57 | INFO     | ✅ fevereiro_2025.xlsx - 12,890 registros em 2.11s
2026-01-16 14:31:42 | INFO     | Concatenando 12 DataFrames com 145,678 registros...
2026-01-16 14:31:45 | INFO     | Salvando 145,678 registros em Parquet...
2026-01-16 14:31:47 | INFO     | ✅ Dados salvos com sucesso!
2026-01-16 14:31:47 | INFO     | 🎉 Extração concluída com sucesso!
2026-01-16 14:31:47 | INFO     | 📊 Resumo: 12/12 arquivos, 145,678 registros
2026-01-16 14:31:47 | INFO     | ⏱️ Tempo total: 55.23s (0.9 min)
```

## 🛠️ Como Usar

### Durante a Extração

O logging é automático - não requer configuração adicional. Cada processo de extração gera:
1. Arquivo de log individual
2. Entrada no histórico JSON

### Visualizando Logs

1. Acesse a página **"Logs"** no menu do Streamlit
2. Na aba "Histórico Resumido":
   - Veja todas as execuções
   - Filtre por planta/ano/status
   - Clique para expandir detalhes
3. Na aba "Logs Detalhados":
   - Selecione um arquivo de log
   - Filtre por nível (INFO, WARNING, ERROR)
   - Faça download se necessário

### Diagnosticando Problemas

Se a extração parar ou falhar:

1. **Acesse a página Logs**
2. **Localize a execução** mais recente
3. **Verifique a aba "Histórico Resumido":**
   - Status: sucesso/erro/parcial
   - Arquivos com erro
   - Mensagens de erro detalhadas
4. **Veja os logs detalhados:**
   - Filtre por "ERROR" para ver apenas erros
   - Veja o stack trace completo
   - Identifique o arquivo problemático

## 🚨 Principais Melhorias de Confiabilidade

### Antes:
- ❌ Parava ao primeiro erro
- ❌ Sem logs persistentes
- ❌ Difícil diagnosticar problemas
- ❌ Sem histórico de execuções

### Agora:
- ✅ Continua processando outros arquivos
- ✅ Logs detalhados de cada operação
- ✅ Rastreamento completo de erros
- ✅ Histórico de todas as execuções
- ✅ Status parcial quando alguns arquivos falham
- ✅ Interface visual para análise

## 📊 Informações Rastreadas

Cada sessão de extração registra:
- Session ID único
- Planta e ano
- Data/hora de início e fim
- Tempo total de processamento
- Total de arquivos encontrados
- Arquivos processados com sucesso
- Arquivos com erro
- Total de registros extraídos
- Lista detalhada de cada arquivo:
  - Nome do arquivo
  - Quantidade de registros
  - Tempo de processamento
  - Status (sucesso/erro)
  - Mensagem de erro (se houver)
- Todos os erros e exceções
- Todos os avisos (warnings)

## 🔧 Manutenção

### Limpeza de Logs Antigos

Os logs individuais (.log) não são removidos automaticamente. Para limpar:

```bash
# Remover logs com mais de 30 dias (exemplo PowerShell)
Get-ChildItem logs\*.log | Where-Object {$_.LastWriteTime -lt (Get-Date).AddDays(-30)} | Remove-Item
```

O histórico JSON mantém automaticamente apenas as últimas 100 sessões.

## 🎯 Casos de Uso

1. **Diagnóstico de Erros:**
   - "A extração parou, não sei por quê"
   - → Verifique os logs para ver exatamente onde e por que falhou

2. **Auditoria:**
   - "Quantos registros foram extraídos ontem?"
   - → Histórico mostra todas as execuções com métricas

3. **Performance:**
   - "Qual arquivo demora mais para processar?"
   - → Logs mostram tempo individual de cada arquivo

4. **Validação:**
   - "Todos os arquivos foram processados?"
   - → Histórico mostra lista completa de arquivos

## 🔐 Segurança

- Logs contêm apenas metadados (nomes de arquivos, contagens, timestamps)
- NÃO armazenam dados sensíveis dos registros fiscais
- Arquivos de log são locais (não enviados ao Git)

## 📝 Próximos Passos Sugeridos

- [ ] Alertas automáticos por email em caso de erro
- [ ] Dashboard de métricas de extração
- [ ] Comparação entre execuções
- [ ] Export de relatórios de extração
- [ ] Integração com sistema de monitoramento
