import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from pymongo import MongoClient
import os
import matplotlib as mlp
mlp.rcParams.update({'figure.max_open_warning': 0})

def render_mpl_table(data, col_width=3.0, row_height=0.625, font_size=14,
                     header_color='#058fb5', row_colors=['#f2f2f1', 'w'], edge_color='w',
                     bbox=[0, 0, 1, 1], header_columns=0,
                     ax=None, **kwargs):
    if ax is None:
        size = (np.array(data.shape[::-1]) + np.array([0, 1])) * np.array([col_width, row_height])
        fig, ax = plt.subplots(figsize=size)
        ax.axis('off')
    mpl_table = ax.table(cellText=data.values, bbox=bbox, colLabels=data.columns, **kwargs)
    mpl_table.auto_set_font_size(False)
    mpl_table.set_fontsize(font_size)

    for k, cell in mpl_table._cells.items():
        cell.set_edgecolor(edge_color)
        if k[0] == 0 or k[1] < header_columns:
            cell.set_text_props(weight='bold', color='w')
            cell.set_facecolor(header_color)
        else:
            cell.set_facecolor(row_colors[k[0]%len(row_colors) ])
    return ax.get_figure(), ax

#MONGO CONECCTION
client = MongoClient()
db = client.liber
books = db.books
users = db.users
ads = db.ads

#PIPELINES 
ads_pipeline = [
    {
        '$lookup': {
            'from': 'users', 
            'localField': 'id_user', 
            'foreignField': '_id', 
            'as': 'user'
        }
    }, {
        '$lookup': {
            'from': 'books', 
            'localField': 'id_book', 
            'foreignField': '_id', 
            'as': 'book'
        }
    }, {
        '$match': {
            '$or': [
                {
                    'user.account_type': 'premium'
                }, {
                    'user.account_type': 'standard'
                }
            ]
        }
    }, {
        '$project': {
            'id_user': 1, 
            'type_ad': 1, 
            'price': 1, 
            'user_name': '$user.name', 
            'ads_type': '$user.account_type', 
            'title': '$book.title', 
            'book_year': '$book.year', 
            'book_location': '$book.location', 
            'publisher': '$book.publisher', 
            'author': '$book.authors', 
            'id_user_by': 1
        }
    }, {
        '$unwind': {
            'path': '$user_name'
        }
    }, {
        '$unwind': {
            'path': '$ads_type'
        }
    }, {
        '$unwind': {
            'path': '$title'
        }
    }, {
        '$unwind': {
            'path': '$book_year'
        }
    }, {
        '$unwind': {
            'path': '$book_location'
        }
    }, {
        '$unwind': {
            'path': '$publisher'
        }
    }, {
        '$unwind': {
            'path': '$author'
        }
    }, {
        '$unwind': {
            'path': '$author'
        }
    }
]

user_pipeline = [
    {
        '$lookup': {
            'from': 'ads', 
            'localField': '_id', 
            'foreignField': 'id_user', 
            'as': 'result'
        }
    }, {
        '$lookup': {
            'from': 'genres', 
            'localField': 'genres', 
            'foreignField': '_id', 
            'as': 'genre'
        }
    }, {
        '$project': {
            '_id': 0, 
            'name': 1, 
            'email': 1, 
            'verified': 1, 
            'activated': 1, 
            'account_type': 1, 
            'genre': '$genre.name', 
            'ads_count': {
                '$cond': {
                    'if': {
                        '$isArray': '$result'
                    }, 
                    'then': {
                        '$size': '$result'
                    }, 
                    'else': 'NA'
                }
            }
        }
    }
]

book_pipeline = [
    {
        '$lookup': {
            'from': 'genres', 
            'localField': 'genre', 
            'foreignField': '_id', 
            'as': 'result'
        }
    }, {
        '$project': {
            '_id': 0, 
            'title': 1, 
            'genres': '$result.name', 
            'subtitle': 1, 
            'authors': 1, 
            'synopsis': 1, 
            'publisher': 1, 
            'year': 1, 
            'location': 1, 
            'language': 1, 
            'page_count': 1, 
            'key_words': 1
        }
    }
]

################################################################################################################################################
#GENERATE ADS CHARTS
#ADS CHARTS IMAGES AND TABLES DIR
#image Dirs
troca_venda_chart_path = f'images{os.sep}ads_troca_venda_chart.png'

best_publisher_tab_path = f'images{os.sep}ads_best_publisher_table.png'
best_publisher_chart_path = f'images{os.sep}ads_best_publisher_chart.png'

author_tro_ven_tab_path = f'images{os.sep}ads_author_tro_ven_tab.png'
author_tro_ven_chart_path = f'images{os.sep}ads_author_tro_ven_chart.png'

livros_caros_tab_path = f'images{os.sep}ads_livros_caros_tab.png'
livros_caros_chart_path = f'images{os.sep}ads_livros_caros_chart.png'

#PEGAR DADOS ADS 
ads_bank=[]
for ads in ads.aggregate(ads_pipeline):
    ads_bank.append(ads)

df_ads = pd.json_normalize(ads_bank, max_level=0)
#CRIAR TABELA EDITORAS
best_publisher = df_ads['publisher'].value_counts().sort_values(ascending=False).head(10)
best_publisher_tab=best_publisher.to_frame().T
fig, axes = render_mpl_table(best_publisher_tab, header_columns=0, col_width=3.2)
fig.savefig(best_publisher_tab_path)
#CRIAR CHART EDITORAS
fig = plt.figure()
best_publisher.fillna(0).plot(kind='bar',figsize=(9, 7),colormap='tab20')
plt.title("Editoras mais anunciadas")
plt.tight_layout() 
plt.savefig( best_publisher_chart_path) 

#CRIAR TABELA AUTHOR POR TIPO DE ANUNCIO
author_tro_ven = df_ads.groupby('author')['type_ad'].value_counts().sort_values(ascending=False).head(13)
author_tro_ven_tab=author_tro_ven.unstack(level=1).T
fig,ax= render_mpl_table(author_tro_ven_tab, header_columns=0, col_width=3.5)
fig.savefig(author_tro_ven_tab_path)
#CRIAR CHART AUTHOR POR TIPO DE ANUNCIO
fig=plt.figure(figsize=(9, 7))
author_tro_ven.unstack(level=1).fillna(0).plot(kind='bar',layout=(1,2),colormap='tab20')
plt.tight_layout() 
plt.savefig(author_tro_ven_chart_path)


#CRIAR TABELA LIVROS CAROS
mais_caros = df_ads[['title','price']].sort_values(by='price', ascending=False).head(10)
mais_caros['price']=mais_caros['price'].astype(float) 
maiores_anunciadores_tab = mais_caros
fig, ax= render_mpl_table(maiores_anunciadores_tab, header_columns=0, col_width=3.0)
fig.savefig(livros_caros_tab_path)
#CRIAR CHART LIVROS CAROS
fig=plt.figure(figsize=(9,7))
mais_caros.plot(kind='bar', x='title', y='price',colormap='tab20', figsize=(9,7))
plt.savefig( livros_caros_chart_path)

#CRIAR CHART TROCA X VENDAS
troca_venda = df_ads['type_ad'].value_counts()
fig = plt.figure()
troca_venda.plot(kind='pie',colormap='tab20')
plt.tight_layout() 
plt.savefig( troca_venda_chart_path) 
#FIM GERAR DADOS ADS
################################################################################################################################################################################






################################################################################################################################################################################
#GERAR DADOS DE USUÁRIOS

#image Dirs
tipo_conta_chart_path = f'images{os.sep}user_troca_venda_chart.png'

generos_populares_tab_path = f'images{os.sep}user_generos_populares_table.png'
generos_populares_chart_path = f'images{os.sep}user_generos_populares_chart.png'

maiores_anunciadores_tab_path = f'images{os.sep}user_maiores_anunciadores_tab.png'
maiores_anunciadores_chart_path = f'images{os.sep}user_maiores_anunciadores_chart.png'

#PEGAR DADOS USUÁRIO
user_bank=[]
for use in users.aggregate(user_pipeline):
    user_bank.append(use)

df_users = pd.json_normalize(user_bank, max_level=0)
for ind, x in enumerate(df_users['genre']):
    df_users.at[ind, 'genre'] = x[0]

#cRIAR TABELA GENEROS PREFERIDOS
generos_populares = df_users['genre'].value_counts().sort_values(ascending=False).head(10)
generos_populares_tab=generos_populares.to_frame().T
fig,ax= render_mpl_table(generos_populares_tab, header_columns=0, col_width=3.3)
fig.savefig(generos_populares_tab_path)

#CRIAR CHART GENEROS PREFERIDOS
fig=plt.figure(figsize=(9, 7))
generos_populares.plot(kind='barh',figsize=(9, 7), colormap='tab20')
plt.tight_layout() 
plt.savefig(generos_populares_chart_path)

#GERAR TABELA MAIORES ANUNCIADORES
maiores_anunciadores = df_users[['name','ads_count']].sort_values(by='ads_count', ascending=False).head(10)
fig, ax= render_mpl_table(maiores_anunciadores, header_columns=0, col_width=3.0)
fig.savefig(maiores_anunciadores_tab_path)
#GERAR CHART MAIORES ANUNCIADORES
fig=plt.figure(figsize=(9,7))
maiores_anunciadores.plot(kind='barh',x='name', y='ads_count',colormap='tab20')
plt.title('Maiores anunciadores')
plt.tight_layout()
plt.savefig(maiores_anunciadores_chart_path)

#GERAR CHART TIPO CONTA
tipos_conta = df_users['account_type'].value_counts()
fig = plt.figure()
tipos_conta.plot(kind='pie',figsize=(9,7), colormap='tab20')
plt.title("Editoras mais anunciadas")
plt.tight_layout() 
plt.savefig( tipo_conta_chart_path) 

#FIM GERAR DADOS USUÁRIO
################################################################################################################################################################################









################################################################################################################################################################################
#GERAR DADOS LIVROS

#image Dirs
autores_mais_livros_table_path = f'images{os.sep}book_autores_mais_livros_table.png'
autores_mais_livros_chart_path = f'images{os.sep}book_autores_mais_livros_chart.png'

best_book_publisher_tab_path = f'images{os.sep}book_best_publisher_table.png'
best_book_publisher_chart_path = f'images{os.sep}book_best_publisher_chart.png'

book_per_year_tab_path = f'images{os.sep}book_per_year_tab.png'
book_per_year_chart_path = f'images{os.sep}book_per_year_chart.png'

maiores_generos_chart_path = f'images{os.sep}book_maiores_generos_tab.png'
maiores_generos_tab_path = f'images{os.sep}book_maiores_generos_chart.png'

#PEGAR DADOS LIVROS
bank=[]
for book in books.aggregate(book_pipeline):
    bank.append(book)

df_books = pd.json_normalize(bank, max_level=0)
clean_book_col = ['authors','genres']
for col in clean_book_col:
    for ind,x in enumerate(df_books[col]):
            df_books.at[ind,col] = x[0]

for ind,x in enumerate(df_books['location']):
    if isinstance(x, str):
        if 'Rio' == x[0:3]:
            df_books.at[ind,'location'] = x.replace(x, 'Rio de Janeiro')
        if 'São' == x[0:3]:
            df_books.at[ind,'location'] = x.replace(x, 'São Paulo')

#GERAR TABELA AUTORES POR LIVRO
autores_mais_livros=df_books.groupby('authors').apply(len).sort_values(ascending=False).head(10).to_frame()
autores_mais_livros_tab = autores_mais_livros.T
fig, axes = render_mpl_table(autores_mais_livros_tab, header_columns=0, col_width=3.2)
fig.savefig(autores_mais_livros_table_path)
#GERAR CHART AUTORES POR LIVRO
fig = plt.figure()
autores_mais_livros.plot(kind='barh',legend=False,figsize=(9,7), colormap='tab20')
plt.title("Top 10 autores por livro")
plt.tight_layout() 
plt.savefig( autores_mais_livros_chart_path) 

#GERAR TABELA MELHOR EDITORA
best_publisher = df_books['publisher'].value_counts().sort_values(ascending=False).head(10)
best_publisher_tab=best_publisher.to_frame().T
fig,ax= render_mpl_table(best_publisher_tab, header_columns=0, col_width=3.3)
fig.savefig(best_book_publisher_tab_path)
#GERAR CHART MELHOR EDITORA
fig=plt.figure(figsize=(9, 7))
best_publisher.fillna(0).plot(kind='barh',figsize=(9, 7),colormap='tab20')
plt.tight_layout() 
plt.savefig(best_book_publisher_chart_path)

#GERAR TABELA LIVROS POR ANO
book_per_year = df_books.groupby('year')['title'].count()
book_per_year_tab = book_per_year.to_frame().T
fig, ax= render_mpl_table(book_per_year_tab, header_columns=0, col_width=2.0)
fig.savefig(book_per_year_tab_path)
#GERAR CHART LIVROS POR ANO
fig=plt.figure(figsize=(9,7))
book_per_year = df_books['year']
book_per_year = book_per_year.to_frame()
plt.hist(book_per_year, bins=9, align='right', color='dodgerblue', edgecolor='black')
plt.title('preço livros')
plt.tight_layout()
plt.savefig(book_per_year_chart_path)

#GERAR TABELA MAIORES GENEROS
maiores_generos = df_books['genres'].value_counts().sort_values(ascending=False).head(10).to_frame()
maiores_generos_tab = maiores_generos.T
fig, ax= render_mpl_table(maiores_generos_tab, header_columns=0, col_width=3.5)
fig.savefig(maiores_generos_tab_path)  
#GERAR CHART MAIORES GENEROS
fig = plt.figure()
maiores_generos.plot(kind='barh', figsize=(9,7), colormap='tab20')
plt.tight_layout() 
plt.savefig( maiores_generos_chart_path) 