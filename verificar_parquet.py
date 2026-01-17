import pandas as pd

df = pd.read_parquet('c:/user/U235107/GitHub/Fiscal/data_parquet/Goiana/2025/fiscal_Goiana_2025.parquet')
print(f'Registros no parquet: {len(df):,}')
print(f'Colunas: {len(df.columns)}')
print(f'Periodo: {df["data_fiscal"].min()} ate {df["data_fiscal"].max()}')
print(f'\nAmostra dos dados:')
print(df.head())
print(f'\nColunas: {list(df.columns)}')
