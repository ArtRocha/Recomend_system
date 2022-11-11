import pandas as pd

df = pd.read_csv('base_clean.tsv', sep='\t', encoding='utf-8')

# new = df.rename(columns={'id':'ISBN', 'overview': 'sinopse', 'genres': 'genero', 'popularity':'popularidade', 'budget':'orcamento', 'original_language':'idioma', 'release_date': 'lancamento', 'revenue':'receita', 'runtime':'paginas', 'cast':'elenco'})

# new.to_csv('base_clean.tsv', sep='\t', index=False)

print(df)