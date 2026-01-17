# Sistema de Análise Fiscal - Stellantis

Sistema completo de análise fiscal usando Python + Streamlit, totalmente escalável e preparado para novos anos e plantas automaticamente.

## 📋 Características Principais

- ✅ **Escalável**: Adicione plantas e anos sem modificar código
- ✅ **Automático**: Detecção automática de anos e plantas disponíveis
- ✅ **Otimizado**: Formato Parquet para alta performance
- ✅ **Deduplicação**: Evita registros duplicados automaticamente
- ✅ **Visual**: Dashboards interativos com Plotly
- ✅ **Consolidação**: Página Home com visão consolidada de todas as plantas
- ✅ **Validação**: Verificação automática de colunas antes da extração
- ✅ **Padronização**: Merge automático com tabela de Códigos Mastersaf
- ✅ **Log em Tempo Real**: Acompanhamento detalhado do processamento
- ✅ **Edição Online**: Tabela de códigos editável direto no navegador
- ✅ **Fator de Conversão**: Visualize valores em Reais, Mil, Milhões ou Bilhões

## 🗂️ Estrutura do Projeto

```
fiscal/
├── data_raw/                      # Arquivos Excel de entrada
│   ├── {planta}/
│   │   └── {ano}/
│   │       └── *.xlsx
│   └── Códigos Mastersaf e Sapiens.xlsx  # Tabela de padronização
├── data_parquet/                  # Arquivos Parquet processados
│   ├── {planta}/
│   │   └── {ano}/
│   │       └── fiscal_{planta}_{ano}.parquet
│   └── Plantas/                   # 🆕 Consolidação multi-plantas
│       └── {ano}/
│           ├── mensal.parquet         # Dados mensais sumarizados
│           ├── fornecedores.parquet   # Fornecedores agregados
│           ├── produtos.parquet       # Produtos agregados
│           └── cfop.parquet           # CFOPs agregados
├── extraction/                    # Módulo de extração
│   ├── extracao.py               # Processamento e consolidação
│   └── logger.py                 # Sistema de log
├── app/                          # Aplicação Streamlit
│   ├── Home.py                   # 🆕 Página Home consolidada (todas plantas)
│   ├── pages/
│   │   ├── analise_fiscal.py    # Análise detalhada por planta
│   │   ├── extracao.py          # Interface de processamento
│   │   └── documentacao.py      # Documentação e equipe
│   └── utils/
│       ├── load_data.py                # Carregamento por planta
│       ├── load_consolidated_data.py   # 🆕 Carregamento consolidado
│       └── transform_data.py           # Transformações e gráficos
├── config/
│   └── plantas.json              # Configuração de plantas
├── dados_equipe_fiscal.json      # Perfis da equipe
├── requirements.txt              # Dependências
└── README.md                     # Esta documentação
```

## 🆕 Novidades e Melhorias Implementadas

### 1. **Página Home Consolidada**
- Visualização unificada de **todas as plantas** em um único dashboard
- Filtro multi-seleção de plantas
- 5 tabs: Mensal, Fornecedores, Produtos, CFOP, Códigos Mastersaf
- Métricas agregadas em tempo real
- Downloads Excel por categoria

### 2. **Sistema de Consolidação Automática**
- Após cada extração, gera arquivos parquet otimizados
- Estrutura: `data_parquet/Plantas/{ano}/`
- 4 arquivos sumarizados por categoria (mensal, fornecedores, produtos, cfop)
- Apenas colunas necessárias = **economia de memória**
- Atualização incremental por planta/ano

### 3. **Padronização com Códigos Mastersaf**
- Merge automático durante extração
- Substitui `COD_NATUREZA_OP` e `DESCRICAO_NATUREZA_OP` por valores padronizados
- Cache global para performance
- Edição online da tabela (tab dedicada em Home e Extração)

### 4. **Validação Inteligente**
- Verifica 17 colunas essenciais antes de processar
- Identifica arquivo e colunas faltantes
- Relatório detalhado de erros
- Execução automática (integrada no fluxo)

### 5. **Interface de Extração Aprimorada**
- 3 tabs: Upload, Processar, Códigos Mastersaf
- Validação automática integrada
- Log em tempo real estilo PowerShell
- Barra de progresso com percentual e tags
- Histórico completo (não apaga após conclusão)
- Dica de Ctrl+A para seleção de pasta

### 6. **Fator de Conversão Universal**
- Radio buttons horizontais (melhor UX)
- 4 opções: Reais, Mil (10³), Milhões (10⁶), Bilhões (10⁹)
- Padrão: **Milhões**
- Aplicado em todos os gráficos e tabelas
- Sincronizado entre Home e Análise Fiscal

### 7. **Sistema de Documentação**
- Página dedicada com informações do sistema
- Perfis da equipe (Funcional e Técnico)
- Upload de fotos com auto-save
- Persistência em JSON

## 🚀 Instalação

### 1. Clone o repositório
```bash
git clone https://github.com/cardinhudson/Fiscal.git
cd c:\user\U235107\GitHub\Fiscal
```

### 2. Crie um ambiente virtual (recomendado)
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 3. Instale as dependências
```powershell
pip install -r requirements.txt
```

### Dependências Principais
- **streamlit**: Interface web
- **pandas**: Manipulação de dados
- **plotly**: Gráficos interativos
- **openpyxl**: Leitura de Excel
- **python-calamine**: Leitura rápida de Excel (otimizado)
- **pyarrow**: Suporte a Parquet

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
data_raw/Goiana/2025/janeiro.xlsx
```

**Importante**: Também coloque o arquivo de códigos:
```
data_raw/Códigos Mastersaf e Sapiens.xlsx
```

### 2. Iniciar a aplicação

```powershell
# Método recomendado (usa o Python do ambiente virtual)
C:/User/U235107/GitHub/Fiscal/.venv/Scripts/python.exe -m streamlit run Home.py

# Alternativa (se venv estiver ativado)
streamlit run Home.py
```

Se o navegador não abrir sozinho, copie a URL que aparece no terminal (ex.: `http://localhost:8501`).

### 3. Processar dados

**Passo a Passo Completo:**

1. **Acesse a página Extração**
   
2. **Tab 1 - Upload de Arquivos** (opcional se já tiver dados)
   - Selecione ou crie nova planta
   - Selecione ou crie novo ano
   - Use Ctrl+A para selecionar pasta inteira
   - Escolha modo: Adicionar ou Substituir
   - Clique em "Fazer Upload"

3. **Tab 2 - Processar Dados**
   - Selecione Planta e Ano
   - Escolha modo:
     - **Incremental**: Processa apenas novos/modificados
     - **Completo**: Reprocessa tudo
   - Clique em "🚀 Processar Extração"
   - Sistema executa automaticamente:
     1. ✅ Validação de colunas
     2. ✅ Leitura dos Excel
     3. ✅ Merge com Códigos Mastersaf
     4. ✅ Conversão para Parquet
     5. ✅ Criação de consolidações
   - Acompanhe o log em tempo real

4. **Visualize os resultados**
   - **Home**: Visão consolidada de todas as plantas
   - **Análise Fiscal**: Visão detalhada por planta

### 4. Gerenciar Códigos Mastersaf

**Opção A: Na página Home (Tab Códigos Mastersaf)**
- Modo Visualizar: Filtros e download
- Modo Editar: Tabela editável com save

**Opção B: Na página Extração (Tab Códigos Mastersaf)**
- Download do arquivo Excel
- Upload de nova versão
- Estatísticas (145 CFOPs padrão)

## 🔧 Arquitetura e Fluxo de Dados

### Fluxo Completo de Processamento

```
┌─────────────────────┐
│  Arquivos Excel     │
│  (data_raw/)        │
└──────────┬──────────┘
           │
           ↓
┌─────────────────────────────────────┐
│  1. Validação de Colunas            │
│     - Verifica 17 colunas essenciais│
│     - Identifica erros por arquivo  │
└──────────┬──────────────────────────┘
           │
           ↓
┌─────────────────────────────────────┐
│  2. Leitura e Transformação         │
│     - Engine: calamine ou openpyxl  │
│     - Conversão BR → US             │
│     - Padronização snake_case       │
│     - Detecção automática do ano    │
└──────────┬──────────────────────────┘
           │
           ↓
┌─────────────────────────────────────┐
│  3. Merge com Códigos Mastersaf     │
│     - LEFT JOIN por CFOP            │
│     - Cache global                  │
│     - Substitui COD/DESC natureza   │
└──────────┬──────────────────────────┘
           │
           ↓
┌─────────────────────────────────────┐
│  4. Deduplicação                    │
│     - Remove registros duplicados   │
│     - Append incremental            │
└──────────┬──────────────────────────┘
           │
           ↓
┌─────────────────────────────────────┐
│  5. Salvamento Parquet por Planta   │
│     data_parquet/{Planta}/{Ano}/    │
└──────────┬──────────────────────────┘
           │
           ↓
┌─────────────────────────────────────┐
│  6. Consolidação Multi-Plantas      │
│     data_parquet/Plantas/{Ano}/     │
│     - mensal.parquet                │
│     - fornecedores.parquet          │
│     - produtos.parquet              │
│     - cfop.parquet                  │
└─────────────────────────────────────┘
```

### Arquivos Consolidados - Estrutura

**mensal.parquet**
```
Colunas: data_fiscal, mes, valor_icms, base_icms_1, planta, ano
Agregação: SUM por mês
Uso: Gráfico de evolução mensal no Home
```

**fornecedores.parquet**
```
Colunas: razao_social, valor_icms, base_icms_1, quantidade, 
         qtd_notas, uf, municipio, cst_icms, planta, ano
Agregação: SUM por fornecedor
Uso: Top fornecedores consolidado
```

**produtos.parquet**
```
Colunas: descricao, valor_icms, base_icms_1, quantidade,
         qtd_fornecedores, qtd_notas, cfop, cst_icms, 
         descricao_natureza_op, planta, ano
Agregação: SUM por produto
Uso: Top produtos consolidado
```

**cfop.parquet**
```
Colunas: cfop, descricao_natureza_op, valor_icms, base_icms_1,
         quantidade, qtd_fornecedores, qtd_produtos, qtd_notas,
         entrada_saida, cst_icms, planta, ano
Agregação: SUM por CFOP + descrição
Uso: Distribuição CFOP consolidada
```

## 📋 Colunas Essenciais dos Arquivos Excel

Os arquivos Excel **devem** conter estas 17 colunas:

| Coluna | Tipo | Descrição |
|--------|------|-----------|
| DATA_FISCAL | Data | Data da operação fiscal |
| ENTRADA_SAIDA | Texto | E (Entrada) ou S (Saída) |
| CODIGO_PRODUTO | Texto | Código do produto |
| DESCRICAO | Texto | Descrição do produto |
| RAZAO_SOCIAL | Texto | Razão social do fornecedor |
| CFOP | Texto | Código Fiscal de Operações |
| COD_NATUREZA_OP | Texto | Código da natureza (substituído) |
| DESCRICAO_NATUREZA_OP | Texto | Descrição da natureza (substituída) |
| ALIQ_ICMS | Número | Alíquota de ICMS (%) |
| BASE_ICMS_1 | Número | Base de cálculo do ICMS |
| VALOR_ICMS | Número | Valor do ICMS |
| CST_ICMS | Texto | Código de Situação Tributária |
| NUM_CONTROLE_DOCTO | Texto | Número de controle |
| UF | Texto | Unidade Federativa |
| MUNICIPIO | Texto | Município |
| NUMERO_NF | Texto | Número da Nota Fiscal |
| QUANTIDADE | Número | Quantidade de itens |

**Nota**: A validação automática verifica estas colunas antes de processar.

## 🎨 Funcionalidades por Página

### 📊 Home (Consolidado)
- **Visão**: Todas as plantas agregadas
- **Filtros**: Ano, seleção múltipla de plantas
- **Fator conversão**: Reais/Mil/Milhões/Bilhões (padrão: Milhões)
- **Tabs**:
  1. Mensal: Evolução temporal
  2. Fornecedores: Top com gráficos e tabelas
  3. Produtos: Top com gráficos e tabelas
  4. CFOP: Distribuição fiscal
  5. Códigos Mastersaf: Visualizar/Editar
- **Métricas**: Fornecedores únicos, ICMS total, Base ICMS, Produtos únicos
- **Downloads**: Excel por categoria

### 📈 Análise Fiscal (Detalhada)
- **Visão**: Planta individual
- **Filtros**: Planta, ano, período, tipo, CFOP, fornecedor, CST, UF, município, natureza op, produto, NF
- **Fator conversão**: Reais/Mil/Milhões/Bilhões (padrão: Milhões)
- **Tabs**: Mensal, Fornecedores, Produtos, CFOP, Dados (completo)
- **Métricas**: Total registros, ICMS, Base ICMS, Fornecedores únicos
- **Downloads**: Excel filtrado

### 📤 Extração
- **Tab 1 - Upload**:
  - Upload múltiplo de arquivos
  - Criar/selecionar planta e ano
  - Modo adicionar ou substituir
  - Dica: Ctrl+A para pasta inteira
  
- **Tab 2 - Processar**:
  - Modo incremental ou completo
  - Validação automática integrada
  - Log em tempo real estilo PowerShell
  - Barra de progresso detalhada
  - Histórico permanente
  
- **Tab 3 - Códigos Mastersaf**:
  - Download do arquivo de códigos
  - Upload de nova versão
  - Estatísticas de CFOPs

### 📚 Documentação
- **Sistema**: Informações técnicas
- **Equipe**: 
  - Perfil Funcional (Osvaldo Tibola - esquerda)
  - Perfil Técnico (Hudson Cardin - direita)
  - Upload de fotos com auto-save
  - Links LinkedIn

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

## 🚀 Performance e Otimizações

### Leitura de Excel
- **python-calamine**: Engine rápida (padrão)
- **openpyxl**: Fallback automático
- Leitura apenas de colunas necessárias (17 de ~50)

### Armazenamento Parquet
- Formato columnar comprimido
- 10-50x menor que Excel
- Leitura 100x mais rápida

### Consolidação
- Dados pré-agregados
- Apenas colunas relevantes por categoria
- Cache de códigos Mastersaf (global)

### Exemplo de Economia
- **Excel original**: 12 arquivos × 30 MB = 360 MB
- **Parquet por planta**: ~15 MB
- **Consolidações**: 4 × 2 MB = 8 MB
- **Total**: 23 MB (redução de 93%)

## 🔄 Ciclo de Atualização

1. **Upload de novos Excel** (mensal)
2. **Processamento incremental** (apenas novos)
3. **Atualização automática**:
   - Parquet da planta
   - Consolidações multi-plantas
4. **Visualização atualizada** em Home e Análise Fiscal

**Tempo médio**: 2-5 minutos para 12 arquivos (2.6M registros)

## 📝 Logs e Monitoramento

### Log em Tempo Real (Interface)
- Timestamp por operação
- Tags: VALIDANDO, PROCESSANDO, MERGE, SALVANDO, CONSOLIDANDO
- Percentual de conclusão
- Mantém histórico após término

### Log de Sessão (Sistema)
- Arquivo por execução
- Detalhes técnicos completos
- Warnings e erros
- Métricas de performance

## 🐛 Troubleshooting

### Erro: Colunas faltantes
**Problema**: Validação falha com colunas faltantes  
**Solução**: Verifique se o Excel tem as 17 colunas essenciais com nomes exatos (maiúsculas)

### Erro: CFOP não encontrado
**Problema**: Warning de CFOP não encontrado no merge  
**Solução**: Adicione o CFOP faltante na tab Códigos Mastersaf

### Performance lenta
**Problema**: Processamento demora muito  
**Soluções**:
- Instale python-calamine: `pip install python-calamine`
- Use modo Incremental ao invés de Completo
- Reduza número de arquivos simultâneos

### Consolidação não aparece
**Problema**: Home não mostra dados consolidados  
**Solução**: Execute extração completa em pelo menos uma planta/ano

### Cache desatualizado
**Problema**: Mudanças em códigos não refletem  
**Solução**: Salve as alterações na tab Códigos Mastersaf (limpa cache automaticamente)

## 🔐 Segurança e Boas Práticas

### Dados Sensíveis
- ❌ NÃO comite arquivos Excel no Git
- ❌ NÃO comite arquivos Parquet no Git
- ✅ Use .gitignore para excluir data_raw/ e data_parquet/
- ✅ Faça backup regular dos dados

### Versionamento
- ✅ Comite código-fonte (app/, extraction/, etc)
- ✅ Comite configurações (config/, requirements.txt)
- ✅ Comite documentação (README.md, etc)
- ❌ Não comite dados (.parquet, .xlsx)

## 🤝 Equipe

### Funcional
**Osvaldo Tibola**
- Product Owner
- Stellantis
- Responsável pela definição de requisitos e validação funcional

### Técnico
**Hudson Cardin**
- AWS Data Engineer
- Responsável pela arquitetura e implementação técnica
- LinkedIn: [hudson-cardin](https://www.linkedin.com/in/hudson-cardin/)

## 📅 Histórico de Versões

### v2.0.0 (Janeiro 2026) - Consolidação e Otimização
- ✅ Sistema de consolidação multi-plantas
- ✅ Arquivos parquet otimizados por categoria
- ✅ Validação automática de colunas
- ✅ Merge com Códigos Mastersaf
- ✅ Log em tempo real estilo PowerShell
- ✅ Tabela de códigos editável online
- ✅ Fator de conversão universal (padrão: Milhões)
- ✅ Página Home redesenhada (visão consolidada)
- ✅ Interface de extração com 3 tabs
- ✅ Download/upload de códigos
- ✅ Dicas de UX (Ctrl+A para pasta)

### v1.0.0 (Janeiro 2026) - Versão Inicial
- ✅ Sistema de extração Excel → Parquet
- ✅ Análise fiscal por planta
- ✅ Visualizações com Plotly
- ✅ Sistema multi-plantas e multi-anos
- ✅ Deduplicação automática
- ✅ Interface Streamlit

## 📄 Licença

Sistema desenvolvido para uso interno da Stellantis.

## 📞 Suporte

Para dúvidas ou problemas:
1. Consulte esta documentação
2. Verifique a seção Troubleshooting
3. Contate a equipe técnica

---

**Sistema de Análise Fiscal - Stellantis © 2026**  
Desenvolvido com ❤️ usando Python, Streamlit e Plotly

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
