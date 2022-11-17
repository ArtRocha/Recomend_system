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

bank=[]
for ads in ads.aggregate(ads_pipeline):
    bank.append(ads)

df = pd.json_normalize(bank, max_level=0)
#cleaning ads dataset
df['user_name']=''
df['ads_type']=''
for ind,user in enumerate(df['user']):
    df.at[ind,'user_name'] = user[0]['name']
    df.at[ind,'ads_type'] = user[0]['account_type']

df['title']=''
df['book_year']= ''
df['book_location']=''
df['publisher']=''
df['author']=''
for ind,book in enumerate(df['book']):
        if 'location' not in book[0].keys():
            df.at[ind,'title'] = book[0]['title']
            df.at[ind,'author'] = book[0]['authors'][0]
            df.at[ind,'book_year'] = book[0]['year']
            df.at[ind,'book_location'] = None
            df.at[ind,'publisher'] = book[0]['publisher']
        elif 'year' not in book[0].keys():
                df.at[ind,'title'] = book[0]['title']
                df.at[ind,'author'] = book[0]['authors'][0]
                df.at[ind,'book_year'] = None
                df.at[ind,'book_location'] = book[0]['location']
                df.at[ind,'publisher'] = book[0]['publisher']
        elif 'publisher' not in book[0].keys():
                df.at[ind,'title'] = book[0]['title']
                df.at[ind,'author'] = book[0]['authors'][0]
                df.at[ind,'book_year'] = book[0]['year']
                df.at[ind,'book_location'] = book[0]['location']
                df.at[ind,'publisher'] = None
        elif 'year' not in book[0].keys() and 'location' not in book[0].keys():
            df.at[ind,'title'] = book[0]['title']
            df.at[ind,'author'] = book[0]['authors'][0]
            df.at[ind,'book_year'] = None
            df.at[ind,'book_location'] = None
            df.at[ind,'publisher'] = book[0]['publisher']
        else:
            df.at[ind,'title'] = book[0]['title']
            df.at[ind,'author'] = book[0]['authors'][0]
            df.at[ind,'book_year'] = book[0]['year']
            df.at[ind,'book_location'] = book[0]['location']
            df.at[ind,'publisher'] = book[0]['publisher']
print('aa')
def analisys_pdf():
    process_day = datetime.now()
    datetime_str = process_day.strftime('%d-%m-%Y')
    time = process_day.strftime("%H:%M:%S")

    class MyFPDF(FPDF, HTMLMixin):
        def header(self):
            self.image('logo.png',10,6,22)
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

    troca_venda_table_path = 'images/troca_venda_table.png'
    troca_venda_chart_path = 'images/troca_venda_chart.png'

    best_publisher_tab_path = 'images/best_publisher_table.png'
    best_publisher_chart_path = 'images/best_publisher_chart.png'

    author_tro_ven_tab_path = 'images/author_tro_ven_tab.png'
    author_tro_ven_chart_path = 'images/author_tro_ven_chart.png'

    livros_caros_tab_path = 'images/maiores_anunciadores_tab.png'
    livros_caros_chart_path = 'images/maiores_anunciadores_chart.png'
    
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

analisys_pdf()