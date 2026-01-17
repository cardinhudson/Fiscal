# 🔧 Troubleshooting - Extração Parando

## Problema Resolvido

O sistema de logging foi aprimorado para:

1. **✅ Salvar progresso continuamente**
   - Histórico atualizado a cada 3 arquivos processados
   - Flush imediato de logs após cada operação
   - Salvamento parcial em caso de erros

2. **✅ Garantir finalização do logger**
   - Bloco `finally` garante finalização mesmo em caso de crash
   - Status "interrompido" registrado se o processo não terminar normalmente
   - Histórico salvo mesmo em interrupções inesperadas

3. **✅ Continuar após erros**
   - Processamento não para ao encontrar erro em um arquivo
   - Registra erro e continua com próximos arquivos
   - Status "parcial" quando alguns arquivos falham

## 🧪 Como Testar

Execute o script de teste:

```bash
python test_logger.py
```

Isso irá:
- Criar uma sessão de teste
- Simular processamento de arquivos (com sucesso e erro)
- Verificar se os logs foram salvos
- Exibir o conteúdo

## 🔍 Verificar Logs Após Extração

### 1. Pelo Streamlit (Recomendado)

1. Abra o app
2. Vá para a página **"Logs"**
3. Veja o histórico completo
4. Verifique se a última execução aparece

### 2. Manualmente

Verifique se os arquivos foram criados:

```bash
# Listar logs
ls logs/

# Ver último log
Get-Content (Get-ChildItem logs\extraction_*.log | Sort-Object LastWriteTime -Descending | Select-Object -First 1).FullName

# Ver histórico JSON
Get-Content logs\extraction_history.json
```

## 🚨 Se a Extração Ainda Parar

### Diagnóstico:

1. **Verifique o último arquivo processado:**
   - Abra a página de Logs
   - Veja a última sessão
   - Identifique o último arquivo com sucesso
   - O próximo arquivo é provavelmente o problemático

2. **Verifique o histórico parcial:**
   - Mesmo que a extração tenha parado, o histórico deve ter sido salvo
   - Procure por `extraction_history.json` na pasta `logs/`
   - A última entrada mostrará o progresso até o momento da parada

3. **Identifique o arquivo problemático:**
   - Liste os arquivos na pasta `data_raw/<planta>/<ano>/`
   - Compare com os arquivos processados no log
   - O arquivo seguinte ao último processado é o culpado

### Soluções:

**Opção 1: Isolar o arquivo problemático**
```bash
# Mova o arquivo problemático temporariamente
mv "data_raw/Goiana/2025/arquivo_problema.xlsx" "data_raw/arquivo_problema_backup.xlsx"

# Execute a extração novamente
# Depois analise o arquivo problemático separadamente
```

**Opção 2: Processar em lotes menores**
1. Divida os arquivos em pastas temporárias
2. Processe cada lote separadamente
3. Identifique qual lote contém o problema

**Opção 3: Analisar arquivo específico**
```python
import pandas as pd

# Tente ler o arquivo suspeito
try:
    df = pd.read_excel("caminho/arquivo_problema.xlsx")
    print(f"Linhas: {len(df)}")
    print(f"Colunas: {df.columns.tolist()}")
except Exception as e:
    print(f"Erro: {e}")
```

## 🛡️ Melhorias Implementadas

### 1. Flush Imediato
Todos os logs são escritos imediatamente no disco, não ficam em buffer.

### 2. Salvamento Parcial
O histórico é salvo:
- A cada 3 arquivos processados
- Quando ocorre um erro
- Antes de finalizar

### 3. Bloco Finally
Garante que o logger sempre finalize, mesmo em casos de:
- Exceção não capturada
- Interrupção manual (Ctrl+C)
- Timeout
- Crash do Python

### 4. Try-Catch em Múltiplos Níveis
- Leitura de arquivo Excel
- Processamento de cada arquivo
- Concatenação de DataFrames
- Salvamento em Parquet
- Finalização do logger

## 📊 Monitoramento em Tempo Real

Durante a extração, você pode:

1. **Acompanhar o arquivo de log em tempo real:**
```bash
Get-Content logs\extraction_<planta>_<ano>_<timestamp>.log -Wait
```

2. **Verificar o histórico parcial:**
```bash
Get-Content logs\extraction_history.json | ConvertFrom-Json | Select-Object -Last 1
```

## 🔑 Informações Importantes

- **Logs são salvos mesmo em caso de crash**
- **Histórico atualizado continuamente (a cada 3 arquivos)**
- **Status "interrompido" indica que o processo não terminou normalmente**
- **Arquivos `.log` contêm detalhes completos do que foi feito**
- **`extraction_history.json` contém resumo de todas as execuções**

## 📞 Próximos Passos se Continuar com Problemas

1. **Capture o log completo** e analise onde está parando
2. **Identifique o arquivo específico** que causa o problema
3. **Verifique o formato do arquivo Excel** (colunas, tipos de dados)
4. **Teste processar apenas esse arquivo** em um script separado
5. **Reporte o erro específico** com o stack trace completo do log
