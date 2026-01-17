# Diretório de Logs

Este diretório armazena os logs de extração de dados do sistema.

## Estrutura de Arquivos

- `extraction_<planta>_<ano>_<timestamp>.log` - Logs detalhados de cada sessão de extração
- `extraction_history.json` - Histórico consolidado das últimas 100 execuções

## Formato dos Logs

Cada arquivo de log contém:
- Timestamp de cada operação
- Nível de log (DEBUG, INFO, WARNING, ERROR)
- Mensagens detalhadas do processo
- Informações sobre arquivos processados
- Erros e exceções capturadas

## Retenção

- Arquivos de log individuais: Mantidos indefinidamente (gerenciar manualmente se necessário)
- Histórico JSON: Últimas 100 sessões

## Visualização

Use a página **Logs** no Streamlit para visualizar:
- Resumo de todas as execuções
- Detalhes de cada sessão
- Logs completos em tempo real
- Filtros por planta, ano, status
