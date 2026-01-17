# Modificações Implementadas - Merge com Tabela de Códigos Mastersaf

## 📋 Resumo das Alterações

### Arquivo: `extraction/extracao.py`

#### 1. Nova Função: `load_codigos_mastersaf()`
- **Localização:** Após a função `get_base_path()`
- **Funcionalidade:**
  - Carrega o arquivo `data_raw/Códigos Mastersaf e Sapiens.xlsx`
  - Lê apenas as colunas necessárias: `CFOP`, `COD_NATUREZA_OP`, `DESCRICAO_NATUREZA_OP`
  - Implementa **cache** para evitar recarregar o arquivo múltiplas vezes
  - Remove duplicatas baseando-se no CFOP
  - Padroniza os dados (trim, conversão para string)

#### 2. Modificação: `process_excel_to_dataframe()`
- **Localização:** Antes do `return df, ano_detectado`
- **Funcionalidade:**
  - Carrega a tabela de códigos usando `load_codigos_mastersaf()`
  - **Remove** as colunas antigas: `cod_natureza_op` e `descricao_natureza_op`
  - Faz **merge** (LEFT JOIN) usando a coluna `cfop` como chave
  - Substitui as colunas antigas pelas novas da tabela de códigos
  - Mantém o **mesmo número de registros** (LEFT JOIN)
  - Registros sem correspondência ficam com valores vazios/NaN
  - Adiciona logs informativos sobre o processo

## ✅ Validações Realizadas

### Teste Executado: `test_merge_codigos.py`

**Resultados:**
- ✅ Arquivo de códigos encontrado e carregado (145 CFOPs)
- ✅ Merge realizado sem alterar número de registros
- ✅ Valores antigos substituídos corretamente pelos novos
- ✅ Colunas `cod_natureza_op` e `descricao_natureza_op` presentes no resultado
- ✅ Registros sem correspondência identificados (CFOPs não cadastrados)

## 🔄 Fluxo de Processamento

### Antes:
```
Excel → process_excel_to_dataframe() → DataFrame com COD/DESC originais → Parquet
```

### Depois:
```
Excel → process_excel_to_dataframe() → 
  ├─ Carrega Códigos Mastersaf
  ├─ Remove colunas antigas
  ├─ Merge por CFOP
  └─ DataFrame com COD/DESC da tabela de códigos → Parquet
```

## 📊 Impacto no Sistema

### ✅ Sem Necessidade de Alterações em:
- `app/pages/analise_fiscal.py` - Usa as mesmas colunas
- `app/utils/transform_data.py` - Usa as mesmas colunas
- `app/utils/load_data.py` - Carrega os mesmos Parquets
- Todos os gráficos e métricas - Trabalham com os mesmos nomes de colunas

### 🎯 Benefícios:
1. **Padronização:** Todos os dados usam a mesma tabela de códigos
2. **Manutenção:** Basta atualizar `Códigos Mastersaf e Sapiens.xlsx`
3. **Performance:** Cache evita recarregar a tabela para cada arquivo
4. **Transparência:** Logs informam sobre registros sem correspondência
5. **Integridade:** LEFT JOIN mantém todos os registros originais

## 📁 Arquivo Necessário

**Caminho:** `data_raw/Códigos Mastersaf e Sapiens.xlsx`

**Estrutura Mínima:**
| CFOP | COD_NATUREZA_OP | DESCRICAO_NATUREZA_OP |
|------|-----------------|----------------------|
| 5102 | 356             | REVENDA MERC.ADQ.TERC |
| 1102 | 3               | COMPRA PARA COMERCIALIZACAO |
| ...  | ...             | ... |

## 🚀 Como Usar

### Extração Normal:
```python
# A extração funcionará automaticamente com o merge
python test_extracao_goiana.py
```

### Validar Merge:
```python
# Executar teste específico do merge
python test_merge_codigos.py
```

## ⚠️ Observações

1. **CFOPs não cadastrados:** Ficarão com `COD_NATUREZA_OP` e `DESCRICAO_NATUREZA_OP` vazios
2. **Cache:** A tabela de códigos é carregada apenas uma vez por execução
3. **Performance:** O merge adiciona tempo mínimo ao processamento (< 1 segundo)
4. **Logs:** Mensagens informativas sobre o processo são exibidas no console

## 🔍 Monitoramento

Durante a extração, observe as mensagens:
- `✅ Tabela de códigos carregada: X CFOPs`
- `✅ Merge realizado com sucesso: X registros mantidos`
- `⚠️ X registros sem correspondência na tabela de códigos`

Se houver CFOPs não encontrados, adicione-os à tabela `Códigos Mastersaf e Sapiens.xlsx`.
