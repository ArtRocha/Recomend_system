from datetime import datetime
import os
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from fpdf import FPDF, HTMLMixin
from pymongo import MongoClient
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("-ads", "--ads",type=str)
parser.add_argument("-use", "--user",type=str)
parser.add_argument("-boo", "--books",type=str)
args = parser.parse_args()

ads_signal = args.ads
user_signal = args.user
book_signal = args.books





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


def ads_pdf():
    bank=[]
    for ads in ads.aggregate(ads_pipeline):
        bank.append(ads)

    df = pd.json_normalize(bank, max_level=0)
    #image Dirs
    troca_venda_table_path = f'images{os.sep}ads_troca_venda_table.png'
    troca_venda_chart_path = f'images{os.sep}ads_troca_venda_chart.png'

    best_publisher_tab_path = f'images{os.sep}ads_best_publisher_table.png'
    best_publisher_chart_path = f'images{os.sep}ads_best_publisher_chart.png'

    author_tro_ven_tab_path = f'images{os.sep}ads_author_tro_ven_tab.png'
    author_tro_ven_chart_path = f'images{os.sep}ads_author_tro_ven_chart.png'

    livros_caros_tab_path = f'images{os.sep}ads_maiores_anunciadores_tab.png'
    livros_caros_chart_path = f'images{os.sep}ads_maiores_anunciadores_chart.png'
    
    process_day = datetime.now()
    datetime_str = process_day.strftime('%d-%m-%Y')
    time = process_day.strftime("%H:%M:%S")

    class MyFPDF(FPDF, HTMLMixin):
        def header(self):
            self.image(f'logo-min.png',10,6,22)
            self.set_font('Arial', 'B', 10)
            self.cell(80)
            self.cell(100,32,f'Relatório de Anúncios Liber', 0, 0, 'R')
            self.ln(20)
            self.line(10,30,200,30)
        def footer(self):
            self.set_y(-15)
            self.set_font('Arial', 'I', 8)
            self.cell(175, 10, 'Todos os direitos reservados por Liber', 0, 0, 'L')
            self.cell(15,10,f'Page {str(self.page_no())}', 0,0,'R')
            self.line(10,280,200,280)
        

    pdf = MyFPDF()
    pdf.add_page()
    pdf.set_right_margin(-1)
    pdf.set_left_margin(10)
    pdf.set_font('Times', size=14, style='B')

    
    
    pdf.set_font('Times', size = 10, style = 'I')
    pdf.multi_cell(173, 5, txt =f'{datetime_str} às {time}', align = 'R')

    

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

    pdf.set_font('')
    pdf.set_font('Times', size = 14, style = '')
    pdf.ln(3)
    pdf.cell(190, 5, txt = 'Top 10 anuncios por editora', ln=1, align='C')
    
    #Salvar imagem com legenda
    pdf.image(best_publisher_tab_path, x=10, w=200, h=20)
    pdf.ln(1)

    pdf.image(best_publisher_chart_path, x=30, w=150, h=80)
    pdf.ln(0)
    pdf.set_font('')
    pdf.set_font('Times', size = 8, style = 'I')
    pdf.cell(190, 5, txt = 'Editoras mais anunciadas pelos usuários', align='C')
    pdf.ln(8)

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

    pdf.set_font('')
    pdf.set_font('Times', size = 14, style = '')
    pdf.ln(3)
    pdf.cell(190, 5, txt = 'Top 10 autores mais anunciados', ln=1, align='C')

    pdf.image(author_tro_ven_tab_path, x=10, w=200, h=20)
    # legend = ''
    pdf.set_font('Times', size = 8)
    pdf.cell(w=0,h=3,ln=True, align='C')
    pdf.ln(4)

    pdf.image(author_tro_ven_chart_path, x=30, w=140, h=82)
    pdf.ln(0)
    pdf.set_font('')
    pdf.set_font('Times', size = 8, style = 'I')
    pdf.cell(190, 5, txt = 'Livros mais vendidos X trocados agrupados por autores', align='C')
    pdf.ln(12)

    #Segunda página
    # pdf.add_page()
    pdf.set_right_margin(-1)
    pdf.set_left_margin(10)
    pdf.set_font('Times', size=11, style='B')

    #Terceiro tabela gráfico - Livros mais caros
    pdf.add_page()
    mais_caros = df[['title','price']].sort_values(by='price', ascending=False).head(10)
    mais_caros['price']=mais_caros['price'].astype(float) 

    livros_caros =df[['title','price']].sort_values(by='price', ascending=False).head(10)
    maiores_anunciadores_tab = livros_caros
    pdf.set_font('')
    pdf.set_font('Times', size = 14, style = '')
    pdf.cell(190, 5, txt = 'Livros mais caros anunciados', ln=1, align='C')
    pdf.ln(3)

    #Analise da distribuição das variaveis preditoras x variaveis alvo
    fig, ax= render_mpl_table(maiores_anunciadores_tab, header_columns=0, col_width=3.0)
    fig.savefig(livros_caros_tab_path)
    
    fig=plt.figure(figsize=(9,7))
    mais_caros.plot(kind='bar', x='title', y='price',colormap='tab20', figsize=(9,7))
    plt.title('preço livros')
    plt.tight_layout()
    plt.savefig(livros_caros_chart_path)
    
    # legend = 'This image the relationship of the force variables with the target variables in boxplot'
    pdf.set_font('Times', size = 8)
    pdf.cell(190,5,ln=True, align='C')
    pdf.image(livros_caros_chart_path,x=40, w=140 ,h=90)
    pdf.ln(h=2)
    
    pdf.image(livros_caros_tab_path,x=60, w=80 ,h=100)
    pdf.set_font('')
    pdf.set_font('Times', size = 8, style = 'I')
    pdf.cell(190, 5, txt = 'Livros mais caros anunciados pelos usuários', align='C')
    pdf.ln(2)

    #Quarto- Distribuição Trocas x vendas
    pdf.add_page()
    troca_venda = df['type_ad'].value_counts()
    fig = plt.figure()
    troca_venda.plot(kind='pie',colormap='tab20')
    plt.tight_layout() 
    plt.savefig( troca_venda_chart_path) 
    
    pdf.set_font('')
    pdf.set_font('Times', size = 11, style = '')
    pdf.cell(190, 5, txt = 'Distribuição Vendas x Trocas', ln=1, align='C')

    pdf.image( troca_venda_chart_path, x=60, w=105, h=90)
    pdf.set_font('')
    pdf.set_font('Times', size = 8, style = 'I')
    pdf.cell(190, 5, txt = 'Distribuição do número de trocas e vendas no aplicativo', ln=1, align='C')
    # legend = 'This chart represent Distribution of ratings'
    # pdf.set_font('Times', size = 8)
    # pdf.cell(w=0,h=3,ln=True, align='L')
    pdf.ln(2)
    pdf.output(f'analysis_report_{datetime_str}.pdf','F')

def user_pdf():
    bank=[]
    for use in users.aggregate(user_pipeline):
        bank.append(use)

    df = pd.json_normalize(bank, max_level=0)
    for ind, x in enumerate(df['genre']):
        df.at[ind, 'genre'] = x[0]
    #image Dirs
    tipo_conta_chart_path = f'images{os.sep}user_troca_venda_chart.png'

    generos_populares_tab_path = f'images{os.sep}user_generos_populares_table.png'
    generos_populares_chart_path = f'images{os.sep}user_generos_populares_chart.png'

    maiores_anunciadores_tab_path = f'images{os.sep}user_maiores_anunciadores_tab.png'
    maiores_anunciadores_chart_path = f'images{os.sep}user_maiores_anunciadores_chart.png'
    
    process_day = datetime.now()
    datetime_str = process_day.strftime('%d-%m-%Y')
    time = process_day.strftime("%H:%M:%S")

    class MyFPDF(FPDF, HTMLMixin):
        def header(self):
            self.image(f'logo-min.png',10,6,22)
            self.set_font('Arial', 'B', 10)
            self.cell(80)
            self.cell(100,32,f'Relatório de Anúncios Liber', 0, 0, 'R')
            self.ln(20)
            self.line(10,30,200,30)
            self.ln(3)
        def footer(self):
            self.set_y(-15)
            self.set_font('Arial', 'I', 8)
            self.cell(175, 10, 'Todos os direitos reservados por Liber', 0, 0, 'L')
            self.cell(15,10,f'Page {str(self.page_no())}', 0,0,'R')
            self.line(10,280,200,280)
        

    pdf = MyFPDF()
    pdf.add_page()
    pdf.set_right_margin(-1)
    pdf.set_left_margin(10)
    pdf.set_font('Times', size=14, style='B')

    
    
    pdf.set_font('Times', size = 10, style = 'I')
    pdf.multi_cell(173, 5, txt =f'{datetime_str} às {time}', align = 'R')
    
    pdf.set_font('')
    pdf.set_font('Times', size = 14, style = '')
    
    pdf.cell(15)
    pdf.cell(80, 5, txt = f'Usuário cadastrados no aplicativo: {len(df)}', ln=1, align='L')
    pdf.cell(15)
    pdf.cell(80, 5, txt = f'Usuários verificados no aplicativo: {len(df.loc[df["verified"]==True])} ', ln=1, align='L')
    pdf.cell(15)
    pdf.cell(80, 5, txt = f'Usuários ativos no aplicativo: {len(df.loc[df["activated"]==True])}', ln=1, align='L')
    pdf.ln(5)
    

    

    #Segundo tabela e gráfico - autores mais vendidos e trocados
    generos_populares = df['genre'].value_counts().sort_values(ascending=False).head(10)
    generos_populares_tab=generos_populares.to_frame().T

    fig,ax= render_mpl_table(generos_populares_tab, header_columns=0, col_width=3.3)
    fig.savefig(generos_populares_tab_path)
    fig=plt.figure(figsize=(9, 7))
    generos_populares.plot(kind='barh',figsize=(9, 7), colormap='tab20')
    plt.tight_layout() 
    # plt.title("Trocas x Vendas por autores")
    plt.savefig(generos_populares_chart_path)

    pdf.set_font('')
    pdf.set_font('Times', size = 14, style = '')
    pdf.ln(3)
    pdf.cell(190, 5, txt = 'Top 10 generos preferidos por usuário', ln=1, align='C')
    pdf.ln(1)
    pdf.image(generos_populares_tab_path, x=10, w=200, h=20)
    # legend = ''
    pdf.set_font('Times', size = 8)
    pdf.cell(w=0,h=3,ln=True, align='C')
    pdf.ln(4)

    pdf.image(generos_populares_chart_path, x=10, w=180, h=82)
    pdf.ln(0)
    pdf.set_font('')
    pdf.set_font('Times', size = 8, style = 'I')
    pdf.cell(190, 5, txt = 'Generos favoritos dos usuários', align='C')
    pdf.ln(12)

    #Segunda página
    pdf.set_right_margin(-1)
    pdf.set_left_margin(10)
    pdf.set_font('Times', size=11, style='B')

    #Terceiro tabela gráfico - Livros mais caros
    # pdf.add_page()
    maiores_anunciadores = df[['name','ads_count']].sort_values(by='ads_count', ascending=False).head(10)
    pdf.set_font('')
    pdf.set_font('Times', size = 14, style = '')
    pdf.cell(190, 5, txt = 'Top 10 usuários com mais anúncios', ln=1, align='C')
    pdf.ln(1)

    #Analise da distribuição das variaveis preditoras x variaveis alvo
    fig, ax= render_mpl_table(maiores_anunciadores, header_columns=0, col_width=3.0)
    fig.savefig(maiores_anunciadores_tab_path)
    
    fig=plt.figure(figsize=(9,7))
    maiores_anunciadores.plot(kind='barh',x='name', y='ads_count',colormap='tab20')
    plt.title('Maiores anunciadores')
    plt.tight_layout()
    plt.savefig(maiores_anunciadores_chart_path)
    
    # legend = 'This image the relationship of the force variables with the target variables in boxplot'
    pdf.set_font('Times', size = 8)
    pdf.cell(190,5,ln=True, align='C')
    pdf.image(maiores_anunciadores_tab_path,x=60, w=90 ,h=75)
    
    pdf.image(maiores_anunciadores_chart_path,x=60, w=170 ,h=100)
    pdf.set_font('')
    pdf.set_font('Times', size = 8, style = 'I')
    pdf.cell(190, 5, txt = 'Usuários que mais possuem anúncios dentro do aplicativo', align='C')
    pdf.ln(10)

    #Primeira tabela e grafico gráfico - melhores editoras
    tipos_conta = df['account_type'].value_counts()
    fig = plt.figure()
    tipos_conta.plot(kind='pie',figsize=(9,7), colormap='tab20')
    plt.title("Editoras mais anunciadas")
    plt.tight_layout() 
    plt.savefig( tipo_conta_chart_path) 

    pdf.set_font('')
    pdf.set_font('Times', size = 14, style = '')
    pdf.ln(3)
    pdf.cell(190, 5, txt = 'Distribuição dos tipos de contas', ln=1, align='C')
    
    #Salvar imagem com legenda
    pdf.image(tipo_conta_chart_path, x=60, w=105, h=90)
    pdf.set_font('')
    pdf.set_font('Times', size = 8, style = 'I')
    pdf.cell(190, 5, txt = 'Distribuição de contas premium X padrão', align='C')
    pdf.ln(10)
    pdf.output(f'users_report_{datetime_str}.pdf','F')

def books_pdf():
    bank=[]
    for book in books.aggregate(book_pipeline):
        bank.append(book)

    df = pd.json_normalize(bank, max_level=0)
    clean_book_col = ['authors','genres']
    for col in clean_book_col:
        for ind,x in enumerate(df[col]):
                df.at[ind,col] = x[0]

    for ind,x in enumerate(df['location']):
        if isinstance(x, str):
            if 'Rio' == x[0:3]:
                df.at[ind,'location'] = x.replace(x, 'Rio de Janeiro')
            if 'São' == x[0:3]:
                df.at[ind,'location'] = x.replace(x, 'São Paulo')
    #image Dirs
    autores_mais_livros_table_path = f'images{os.sep}book_autores_mais_livros_table.png'
    autores_mais_livros_chart_path = f'images{os.sep}book_autores_mais_livros_chart.png'

    best_publisher_tab_path = f'images{os.sep}book_best_publisher_table.png'
    best_publisher_chart_path = f'images{os.sep}book_best_publisher_chart.png'

    book_per_year_tab_path = f'images{os.sep}book_per_year_tab.png'
    book_per_year_chart_path = f'images{os.sep}book_per_year_chart.png'

    maiores_generos_chart_path = f'images{os.sep}book_maiores_generos_tab.png'
    maiores_generos_tab_path = f'images{os.sep}book_maiores_generos_chart.png'
    
    process_day = datetime.now()
    datetime_str = process_day.strftime('%d-%m-%Y')
    time = process_day.strftime("%H:%M:%S")

    class MyFPDF(FPDF, HTMLMixin):
        def header(self):
            self.image(f'logo-min.png',10,6,22)
            self.set_font('Arial', 'B', 10)
            self.cell(80)
            self.cell(100,32,f'Relatório de Anúncios Liber', 0, 0, 'R')
            self.ln(20)
            self.line(10,30,200,30)
            self.ln(3)
        def footer(self):
            self.set_y(-15)
            self.set_font('Arial', 'I', 8)
            self.cell(175, 10, 'Todos os direitos reservados por Liber', 0, 0, 'L')
            self.cell(15,10,f'Page {str(self.page_no())}', 0,0,'R')
            self.line(10,280,200,280)
        

    pdf = MyFPDF()
    pdf.add_page()
    pdf.set_right_margin(-1)
    pdf.set_left_margin(10)
    pdf.set_font('Times', size=14, style='B')

    
    
    pdf.set_font('Times', size = 10, style = 'I')
    pdf.multi_cell(173, 5, txt =f'{datetime_str} às {time}', align = 'R')

    

    #Primeira tabela e grafico gráfico - melhores editoras
    autores_mais_livros=df.groupby('authors').apply(len).sort_values(ascending=False).head(10).to_frame()
    autores_mais_livros_tab = autores_mais_livros.T
    fig, axes = render_mpl_table(autores_mais_livros_tab, header_columns=0, col_width=3.2)
    fig.savefig(autores_mais_livros_table_path)
    fig = plt.figure()
    autores_mais_livros.plot(kind='barh',legend=False,figsize=(9,7), colormap='tab20')
    plt.title("Top 10 autores por livro")
    plt.tight_layout() 
    plt.savefig( autores_mais_livros_chart_path) 

    pdf.set_font('')
    pdf.set_font('Times', size = 14, style = '')
    pdf.ln(3)
    pdf.cell(190, 5, txt = 'Autores mais presentes nos livros', ln=1, align='C')
    
    #Salvar imagem com legenda
    pdf.image(autores_mais_livros_table_path, x=10, w=200, h=20)
    pdf.ln(1)

    pdf.image(autores_mais_livros_chart_path, x=30, w=150, h=80)
    pdf.ln(0)
    pdf.set_font('')
    pdf.set_font('Times', size = 8, style = 'I')
    pdf.cell(190, 5, txt = 'Autores que mais escreveram os livros cadastrados na base', align='C')
    pdf.ln(8)

    #Segundo tabela e gráfico - autores mais vendidos e trocados
    best_publisher = df['publisher'].value_counts().sort_values(ascending=False).head(10)
    best_publisher_tab=best_publisher.to_frame().T

    fig,ax= render_mpl_table(best_publisher_tab, header_columns=0, col_width=3.3)
    fig.savefig(best_publisher_tab_path)
    fig=plt.figure(figsize=(9, 7))
    best_publisher.fillna(0).plot(kind='barh',figsize=(9, 7),colormap='tab20')
    plt.tight_layout() 
    # plt.title("Trocas x Vendas por autores")
    plt.savefig(best_publisher_chart_path)

    pdf.set_font('')
    pdf.set_font('Times', size = 14, style = '')
    pdf.ln(3)
    pdf.cell(190, 5, txt = 'Top 10 editoras', ln=1, align='C')

    pdf.image(best_publisher_tab_path, x=10, w=200, h=20)
    # legend = ''
    pdf.set_font('Times', size = 8)
    pdf.cell(w=0,h=3,ln=True, align='C')
    pdf.ln(4)

    pdf.image(best_publisher_chart_path, x=30, w=140, h=82)
    pdf.ln(0)
    pdf.set_font('')
    pdf.set_font('Times', size = 8, style = 'I')
    pdf.cell(190, 5, txt = 'Editoras que mais publicaram livros', align='C')
    pdf.ln(12)

    #Segunda página
    # pdf.add_page()
    pdf.set_right_margin(-1)
    pdf.set_left_margin(10)
    pdf.set_font('Times', size=11, style='B')

    #Terceiro tabela gráfico - Livros mais caros
    pdf.set_font('')
    pdf.set_font('Times', size = 14, style = '')
    pdf.cell(190, 5, txt = 'Livros publicados por ano', ln=1, align='C')
    pdf.ln(1)

    #Analise da distribuição das variaveis preditoras x variaveis alvo
    book_per_year = df.groupby('year')['title'].count()
    book_per_year_tab = book_per_year.to_frame().T
    fig, ax= render_mpl_table(book_per_year_tab, header_columns=0, col_width=2.0)
    fig.savefig(book_per_year_tab_path)
    
    fig=plt.figure(figsize=(9,7))
    book_per_year = df['year']
    book_per_year = book_per_year.to_frame()
    plt.hist(book_per_year, bins=9, align='right', color='dodgerblue', edgecolor='black')
    plt.title('preço livros')
    plt.tight_layout()
    plt.savefig(book_per_year_chart_path)
    
    # legend = 'This image the relationship of the force variables with the target variables in boxplot'
    pdf.set_font('Times', size = 8)
    pdf.cell(190,5,ln=True, align='C')
    pdf.image(book_per_year_tab_path,x=10, w=200 ,h=20)
    pdf.ln(1)
    
    pdf.image(book_per_year_chart_path,x=50, w=110 ,h=60)
    pdf.set_font('')
    pdf.set_font('Times', size = 8, style = 'I')
    pdf.cell(190, 5, txt = 'Livros lançados por ano', align='C')
    pdf.ln(8)

    #Quarto- Distribuição Trocas x vendas
    maiores_generos = df['genres'].value_counts().sort_values(ascending=False).head(10).to_frame()
    maiores_generos_tab = maiores_generos.T
    fig, ax= render_mpl_table(maiores_generos_tab, header_columns=0, col_width=3.5)
    fig.savefig(maiores_generos_tab_path)  
    fig = plt.figure()
    maiores_generos.plot(kind='barh', figsize=(9,7), colormap='tab20')
    plt.tight_layout() 
    plt.savefig( maiores_generos_chart_path) 
    
    pdf.set_font('Times', size = 14)
    pdf.cell(190,5,ln=True, txt='Generos mais populares', align='C')
    pdf.image(maiores_generos_tab_path,x=10, w=200 ,h=20)
    pdf.ln(2)
    
    pdf.image(maiores_generos_chart_path,x=30, w=140 ,h=82)
    pdf.set_font('')
    pdf.set_font('Times', size = 8, style = 'I')
    pdf.cell(190, 5, txt = 'Contagem de generos por livro', align='C')
    # pdf.ln(2)
    # legend = 'This chart represent Distribution of ratings'
    # pdf.set_font('Times', size = 8)
    # pdf.cell(w=0,h=3,ln=True, align='L')
    # pdf.ln(2)
    pdf.output(f'books_report_{datetime_str}.pdf','F')

# if ads_signal=='T':
# ads_pdf()
# elif user_signal=='T':
# user_pdf()
# elif book_signal=='T':
books_pdf()