import pandas as pd
from pandas_profiling import ProfileReport

df = pd.read_csv('/home/arthur/Documents/art_projects/recommend_system/metadata.tsv', sep='\t', index_col=0)

new = df[['budget', 'genres', 'id','original_language', 'original_title', 'overview',
       'popularity', 'release_date', 'revenue', 'runtime','title', 'vote_average', 'vote_count', 'cast', 'crew', 'keywords', 'director',
       'soup']]
new.to_csv('newBase.tsv', sep='\t', index=False)
profile = ProfileReport(new, title="Exemplo de relatório liber")
profile.to_file("your_report.html")
# updates=[]
# for _, row in df.iterrows():
#     updates.append(({'_id':_}, {'cell_type': row.get('Kind of Sample')}))
    
# print(updates)