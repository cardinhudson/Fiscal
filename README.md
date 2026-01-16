# Sistema de Análise Fiscal - Stellantis

Sistema completo de análise fiscal usando Python + Streamlit, totalmente escalável e preparado para novos anos e plantas automaticamente.

## 📋 Características

- ✅ **Escalável**: Adicione plantas e anos sem modificar código
- ✅ **Automático**: Detecção automática de anos disponíveis
- ✅ **Otimizado**: Formato Parquet para alta performance
- ✅ **Deduplicação**: Evita registros duplicados automaticamente
- ✅ **Visual**: Dashboards interativos com Plotly
- ✅ **Perpétuo**: Sistema funciona indefinidamente

## 🗂️ Estrutura do Projeto

```
fiscal_analytics/
├── data_raw/               # Arquivos Excel de entrada
│   ├── {planta}/
│   │   └── {ano}/
│   │       └── *.xlsx
├── data_parquet/           # Arquivos Parquet processados
│   ├── {planta}/
│   │   └── {ano}/
│   │       └── fiscal_{planta}_{ano}.parquet
├── extraction/             # Módulo de extração
│   └── extracao.py
├── app/                    # Aplicação Streamlit
│   ├── Home.py            # Página inicial (abas por planta)
│   ├── pages/
│   │   ├── analise_fiscal.py  # Análise com filtros
│   │   └── extracao.py        # Processamento de arquivos
│   └── utils/
│       ├── load_data.py       # Carregamento de dados
│       └── transform_data.py  # Transformações e visualizações
├── config/
│   └── plantas.json       # Configuração de plantas e anos
├── requirements.txt       # Dependências
└── README.md             # Este arquivo
```

## 🚀 Instalação

### 1. Clone o repositório
```bash
cd c:\user\U235107\GitSTLA\Fiscal
```

### 2. Crie um ambiente virtual (recomendado)
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

### 3. Instale as dependências
```powershell
pip install -r requirements.txt
```

## 📊 Como Usar

### 1. Preparar os dados

Coloque seus arquivos Excel na estrutura:
```
data_raw/{NomeDaPlanta}/{Ano}/arquivo.xlsx
```

Exemplo:
```
data_raw/Porto Real/2025/janeiro.xlsx
data_raw/Porto Real/2025/fevereiro.xlsx
data_raw/Goiana/2026/janeiro.xlsx
```

### 2. Iniciar a aplicação

```powershell
# IMPORTANTE (Windows): evite usar `streamlit` global do Python fora do venv.
# Use o Python do venv para garantir que Streamlit + GitPython sejam os do projeto:
C:/GIT/Fiscal/.venv/Scripts/python.exe -m streamlit run Home.py

# Alternativa: atalho do projeto
./run.ps1
```

Se o navegador não abrir sozinho, copie a URL que aparece no terminal (ex.: `http://localhost:8501`).

> Observação: o entrypoint do projeto é `Home.py` (na raiz). Se você rodar `streamlit run APP.py`, vai falhar porque esse arquivo não existe.

### 3. Processar dados

**Opção A: Upload pela Interface (Novo!)**
1. Acesse a página **Extração**
2. Na aba **Upload de Arquivos**:
   - Selecione ou crie nova planta
   - Selecione ou crie novo ano
   - Arraste arquivos Excel ou clique para selecionar
   - Escolha modo: Adicionar ou Substituir
   - Clique em "Fazer Upload"
3. Na aba **Processar Dados**:
   - Selecione a planta e ano
   - Escolha modo: Incremental (novos) ou Completo (todos)
   - Clique em "Processar"

**Opção B: Colocar arquivos manualmente**
1. Coloque arquivos em `data_raw/{Planta}/{Ano}/`
2. Acesse página Extração
3. Processe os dados

### 4. Analisar dados

1. Acesse a página **Análise Fiscal**
2. Selecione planta e ano
3. Configure filtros desejados
4. Visualize gráficos e tabelas
5. Faça download dos dados filtrados

## 🔧 Configuração de Plantas

Edite o arquivo `config/plantas.json`:

```json
{
    "plantas": [
        "Porto Real",
        "Goiana",
        "Betim",
        "Jaboatao",
        "PWT",
        "Transmissoes"
    ],
    "anos_iniciais": [2025, 2026],
    "anos_validos": "auto"
}
```

- **plantas**: Lista de plantas disponíveis
- **anos_iniciais**: Anos que sempre aparecem (mesmo sem dados)
- **anos_validos**: "auto" = detecta anos automaticamente

## 📋 Colunas Obrigatórias do Excel

Os arquivos Excel devem conter estas colunas:

- DATA_FISCAL
- ENTRADA_SAIDA
- CODIGO_PRODUTO
- DESCRICAO
- RAZAO_SOCIAL
- CFOP
- COD_NATUREZA_OP
- DESCRICAO_NATUREZA_OP
- ALIQ_ICMS
- BASE_ICMS_1
- VALOR_ICMS
- CST_ICMS
- NUM_CONTROLE_DOCTO
- UF
- MUNICIPIO

## 📋 Colunas Mantidas na Extração (Performance)

A extração lê e processa **apenas as 17 colunas essenciais** para máxima performance e menor uso de memória:

| Coluna                | Descrição                       |
|-----------------------|---------------------------------|
| DATA_FISCAL           | Data fiscal (eixo temporal)     |
| ENTRADA_SAIDA         | Tipo de operação                |
| CODIGO_PRODUTO        | Código do produto               |
| DESCRICAO             | Descrição do produto            |
| RAZAO_SOCIAL          | Nome do fornecedor              |
| CFOP                  | Código CFOP                     |
| COD_NATUREZA_OP       | Código natureza operação        |
| DESCRICAO_NATUREZA_OP | Descrição natureza operação     |
| ALIQ_ICMS             | Alíquota ICMS                   |
| BASE_ICMS_1           | Base de cálculo ICMS            |
| VALOR_ICMS            | Valor do ICMS                   |
| CST_ICMS              | Situação tributária ICMS        |
| NUM_CONTROLE_DOCTO    | Número de controle do documento |
| UF                    | Estado                          |
| MUNICIPIO             | Município                       |
| NUMERO_NF             | Número da nota fiscal           |
| QUANTIDADE            | Quantidade                      |

**Todas as demais colunas são descartadas automaticamente na extração para garantir máxima velocidade e eficiência.**

## 📈 Funcionalidades

### Home Page
- Abas por planta
- Resumo de métricas
- Total de registros e valor ICMS
- Anos disponíveis

### Análise Fiscal
- Filtros: Planta, Ano, Período, Tipo, CFOP, Fornecedor
- Gráfico mensal de ICMS
- Top 10 fornecedores
- Top 10 produtos
- Distribuição por CFOP
- Tabela de dados detalhados
- Download CSV

### Extração
- Processamento de Excel → Parquet
- Barra de progresso
- Deduplicação automática
- Append de dados novos
- Estatísticas do arquivo
- **🆕 Upload de arquivos pela interface**
- **🆕 Processamento incremental (somente novos/modificados)**
- **🆕 Criação automática de plantas e anos**
- **🆕 Modo substituir ou adicionar arquivos**

## 🔄 Expansão Automática

O sistema automaticamente:
1. Detecta novos anos nas pastas
2. Infere anos dos arquivos processados
3. Cria estrutura de diretórios sob demanda
4. Atualiza listas de plantas e anos
5. Deduplica registros

**Para adicionar nova planta:**
1. Adicione o nome em `config/plantas.json`
2. Coloque arquivos Excel em `data_raw/{NovaPlanta}/{Ano}/`
3. Processe via página Extração

**Para adicionar novo ano:**
1. Coloque arquivos Excel em `data_raw/{Planta}/{NovoAno}/`
2. Processe via página Extração
3. Ano aparece automaticamente nas seleções

## 🛠️ Manutenção

### Limpar cache
```python
import streamlit as st
st.cache_data.clear()
```

### Reprocessar dados
1. Delete arquivo Parquet antigo
2. Processe novamente via Extração

### Adicionar novas métricas
Edite `app/utils/transform_data.py`

## 📝 Notas Técnicas

- **Formato**: Parquet com PyArrow (compressão e velocidade)
- **Cache**: 5min para dados, 10min para listas
- **Deduplicação**: Por `num_controle_docto + data_fiscal + codigo_produto`
- **Conversão**: Números BR (1.234,56) → US (1234.56)
- **Snake_case**: Todas as colunas convertidas automaticamente
- **Encoding**: UTF-8 com suporte a acentos

## 🎯 Métricas Principais

Todas as análises usam:
- **VALOR_ICMS**: Valor do ICMS
- **DATA_FISCAL**: Data fiscal (eixo temporal)
- **BASE_ICMS_1**: Base de cálculo do ICMS

## 📞 Suporte

Sistema desenvolvido para Stellantis - Grupo Controlling
Ano: 2026
