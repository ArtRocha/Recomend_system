from datetime import datetime
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from fpdf import FPDF, HTMLMixin
from pymongo import MongoClient

#MONGO CONECCTION
client = MongoClient()
db = client.liber
books = db.books
users = db.users
ads = db.ads

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

bank=[]
for ads in ads.aggregate(ads_pipeline):
    bank.append(ads)

df = pd.json_normalize(bank, max_level=0)

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

#image Dirs
troca_venda_table_path = 'images/troca_venda_table.png'
troca_venda_chart_path = 'images/troca_venda_chart.png'

best_publisher_tab_path = 'images/best_publisher_table.png'
best_publisher_chart_path = 'images/best_publisher_chart.png'

author_tro_ven_tab_path = 'images/author_tro_ven_tab.png'
author_tro_ven_chart_path = 'images/author_tro_ven_chart.png'

livros_caros_tab_path = 'images/maiores_anunciadores_tab.png'
livros_caros_chart_path = 'images/maiores_anunciadores_chart.png'

#Primeira tabela e grafico gráfico - melhores editoras
best_publisher = df['publisher'].value_counts().sort_values(ascending=False).head(10)
best_publisher_tab=best_publisher.to_frame().T
fig, axes = render_mpl_table(best_publisher_tab, header_columns=0, col_width=3.2)
fig.savefig(best_publisher_tab_path)

fig = plt.figure()
best_publisher.fillna(0).plot(kind='bar',figsize=(9, 7),colormap='tab20')
plt.title("Editoras mais anunciadas")
plt.tight_layout() 
plt.savefig( best_publisher_chart_path) 

#Segundo tabela e gráfico - autores mais vendidos e trocados
author_tro_ven = df.groupby('author')['type_ad'].value_counts().sort_values(ascending=False).head(13)
author_tro_ven_tab=author_tro_ven.unstack(level=1).T

fig,ax= render_mpl_table(author_tro_ven_tab, header_columns=0, col_width=3.5)
fig.savefig(author_tro_ven_tab_path)
fig=plt.figure(figsize=(9, 7))
author_tro_ven.unstack(level=1).fillna(0).plot(kind='bar',layout=(1,2),colormap='tab20')
plt.tight_layout() 
# plt.title("Trocas x Vendas por autores")
plt.savefig(author_tro_ven_chart_path)


#Terceiro tabela gráfico - Livros mais caros
pdf.add_page()
mais_caros = df[['title','price']].sort_values(by='price', ascending=False).head(10)
mais_caros['price']=mais_caros['price'].astype(float) 

livros_caros =df[['title','price']].sort_values(by='price', ascending=False).head(10)
maiores_anunciadores_tab = livros_caros


fig, ax= render_mpl_table(maiores_anunciadores_tab, header_columns=0, col_width=3.0)
fig.savefig(livros_caros_tab_path)

fig=plt.figure(figsize=(9,7))
mais_caros.plot(kind='bar', x='title', y='price',colormap='tab20', figsize=(9,7))
plt.title('preço livros')
plt.tight_layout()
plt.savefig(livros_caros_chart_path)

#Quarto- Distribuição Trocas x vendas
troca_venda = df['type_ad'].value_counts()
fig = plt.figure()
troca_venda.plot(kind='pie',colormap='tab20')
plt.tight_layout() 
plt.savefig( troca_venda_chart_path) 