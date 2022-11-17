from datetime import datetime
import numpy as np
from matplotlib.backends.backend_pdf import PdfPages
import matplotlib.pyplot as plt
from numpy import size
import pandas as pd
import seaborn as sns
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
                     header_color='#40466e', row_colors=['#f1f1f2', 'w'], edge_color='w',
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
    if 'year' not in book[0].keys():
        df.at[ind,'title'] = book[0]['title']
        df.at[ind,'author'] = book[0]['authors'][0]
        df.at[ind,'book_year'] = None
        df.at[ind,'book_location'] = book[0]['location']
        df.at[ind,'publisher'] = book[0]['publisher']
    else:
        df.at[ind,'title'] = book[0]['title']
        df.at[ind,'author'] = book[0]['authors'][0]
        df.at[ind,'book_year'] = book[0]['year']
        df.at[ind,'book_location'] = book[0]['location']
        df.at[ind,'publisher'] = book[0]['publisher']

print('aa')
def analisys_pdf():
    title = 'Liber Reports'

    class MyFPDF(FPDF, HTMLMixin):
        def footer(self):
            # Go to 1.5 cm from bottom
            self.set_y(-15)
            # Select Arial italic 8
            self.set_font('Arial', 'I', 8)
            # Print centered page number
            self.cell(0, 10, 'Page %s' % self.page_no(), 0, 0, 'C')
        

    pdf = MyFPDF()
    pdf.add_page()
    pdf.set_right_margin(-1)
    pdf.set_left_margin(10)
    pdf.set_font('Times', size=14, style='B')

    NetWork = 'Relatório'

    troca_venda_table_path = 'images/troca_venda_table.png'
    troca_venda_chart_path = 'images/troca_venda_chart.png'

    best_publisher_tab_path = 'images/best_publisher_table.png'
    best_publisher_chart_path = 'images/best_publisher_chart.png'

    author_tro_ven_tab_path = 'images/author_tro_ven_tab.png'
    author_tro_ven_chart_path = 'images/author_tro_ven_chart.png'

    maiores_anunciadores_tab_path = 'images/maiores_anunciadores_tab.png'
    maiores_anunciadores_chart_path = 'images/maiores_anunciadores_chart.png'


    process_day = datetime.now()
    datetime_str = process_day.strftime('%d-%m-%Y')

    Header = f'{NetWork} Liber                                                                         Date: {datetime_str}' 
    pdf.multi_cell(180, 5, txt = Header, align = 'C') 

    pdf.set_font('')
    pdf.set_font('Times', size = 11, style = 'B')
    pdf.ln(2)
    pdf.cell(190, 5, txt = 'Distribuição de trocas e vendas', ln=1, align='C')
    pdf.ln(1)

    #Primeiro gráfico - Distribuição das variaveis alvo e preditoras
    troca_venda = df['type_ad'].value_counts()
    troca_venda_tab =troca_venda.to_frame().T 
    fig, axes = render_mpl_table(troca_venda_tab, header_columns=0, col_width=2.0)
    plt.tight_layout() 
    fig.savefig( troca_venda_table_path)
    # axes.table(cellText=troca_venda_tab.values, colLabels=['troca', 'vendas'], loc='left')
    fig = plt.figure()
    troca_venda.plot(kind='pie',colormap='Accent')
    plt.tight_layout() 
    plt.savefig( troca_venda_chart_path) 



    #Salvar imagem com legenda
    pdf.image( troca_venda_table_path, x=80, w=40, h=20)
    # legend = 'This chart represent Distribution of ratings'
    # pdf.set_font('Times', size = 8)
    # pdf.cell(w=0,h=3,ln=True, align='R')
    pdf.ln(4)

    pdf.image( troca_venda_chart_path, x=70, w=95, h=80)
    # legend = 'This chart represent Distribution of ratings'
    # pdf.set_font('Times', size = 8)
    # pdf.cell(w=0,h=3,ln=True, align='L')
    pdf.ln(4)

    #Segundo gráfico - Correlação entre as variaveis 
    best_publisher = df['publisher'].value_counts().sort_values(ascending=False).head(10)
    best_publisher_tab=best_publisher.to_frame().T
    fig, axes = render_mpl_table(best_publisher_tab, header_columns=0, col_width=5.0)
    fig.savefig(best_publisher_tab_path)
    fig = plt.figure()
    best_publisher.fillna(0).plot(kind='bar',figsize=(9, 7),colormap='PuOr')
    plt.title("Melhores publicadoras")
    plt.tight_layout() 
    plt.savefig( best_publisher_chart_path) 
    pdf.set_font('')
    pdf.set_font('Times', size = 11, style = 'B')
    pdf.ln(3)
    pdf.cell(190, 5, txt = 'Top 10 publicadoras', ln=1, align='C')
    
    #Salvar imagem com legenda
    pdf.image(best_publisher_tab_path, x=0, w=210, h=20)
    # legend = 'Users who rating more books'
    # pdf.set_font('Times', size = 8)
    # pdf.cell(w=0,h=3,ln=True, align='L')
    pdf.ln(4)

    pdf.image(best_publisher_chart_path, x=30, w=150, h=80)
    # legend = 'Users who rating more books'
    # pdf.set_font('Times', size = 8)
    # pdf.cell(w=0,h=3,ln=True, align='L')
    pdf.ln(4)


    #Terceiro gráfico - Analise das comparações entre as colunas de altura
    author_tro_ven = df.groupby('author')['type_ad'].value_counts().sort_values(ascending=False).head(13)
    author_tro_ven_tab=author_tro_ven.to_frame()

    pdf.set_font('')
    pdf.set_font('Times', size = 11, style = 'B')
    pdf.ln(6)
    pdf.cell(190, 5, txt = 'Count evaluation per books', ln=1, align='C')
    

    fig,ax= render_mpl_table(author_tro_ven_tab, header_columns=0, col_width=2.0)
    fig.savefig(author_tro_ven_tab_path)
    fig=plt.figure(figsize=(9, 7))
    author_tro_ven.unstack(level=1).fillna(0).plot(kind='bar', subplots=True,layout=(1,2),colormap='Accent')
    plt.title("Trocas x Vendas por autores")
    plt.savefig(author_tro_ven_chart_path)

    pdf.image(author_tro_ven_tab_path, x=30, w=150, h=60)
    # legend = ''
    pdf.set_font('Times', size = 8)
    pdf.cell(w=0,h=3,ln=True, align='C')
    pdf.ln(4)

    #Segunda página
    pdf.add_page()
    pdf.set_right_margin(-1)
    pdf.set_left_margin(10)
    pdf.set_font('Times', size=11, style='B')

    #Quarto gráfico - Analise das comparações entre as colunas de força
    maiores_anunciadores = df.groupby('user_name')['type_ad'].value_counts().sort_values(ascending=False).head(10)
    maiores_anunciadores_tab = maiores_anunciadores.to_frame()
    pdf.set_font('')
    pdf.set_font('Times', size = 11, style = 'B')
    pdf.ln(4)
    pdf.cell(190, 5, txt = 'Table most popular books', ln=1, align='C')
    pdf.ln(3)

    #Analise da distribuição das variaveis preditoras x variaveis alvo
    fig, ax= render_mpl_table(maiores_anunciadores_tab, header_columns=1, col_width=2.0)
    fig.savefig(maiores_anunciadores_tab_path)
    fig=plt.figure()
    maiores_anunciadores.unstack(level=1).plot(kind='bar',figsize=(9, 7),colormap='Accent')
    fig.savefig(maiores_anunciadores_chart_path)
    pdf.image(maiores_anunciadores_tab_path,x=8, w=200 ,h=80)
    # legend = 'This image the relationship of the force variables with the target variables in boxplot'
    pdf.set_font('Times', size = 8)
    pdf.cell(w=0,h=3,ln=True, align='C')
    pdf.ln(h=2)

    # #Quinto gráfico - Analise das comparações entre as colunas max_force
    # pdf.set_font('')
    # pdf.set_font('Times', size = 11, style = 'B')
    # pdf.ln(6)
    # pdf.cell(190, 5, txt = 'Distribution of target and predictor variables in boxplot by Max_Force', ln=1, align='L')
    # pdf.ln(5)


    # fig= plt.figure(figsize=(10,3) ) 
    # fig.add_subplot(1,3,1) 
    # ar_6=sns.boxplot(x=usefull_info["Generic Segmentation"],y=usefull_info["MaxForce_F0500pN"]) 
    # fig.add_subplot(1,3,2) 
    # ar_6=sns.boxplot(x=usefull_info["Generic Segmentation"],y=usefull_info["MaxForce_F1500pN"]) 
    # fig.add_subplot(1,3,3) 
    # ar_6=sns.boxplot(x=usefull_info["Generic Segmentation"],y=usefull_info["MaxForce_F3000pN"]) 
    # plt.tight_layout() 
    # plt.savefig(max_force_comparation_path)

    # pdf.image(max_force_comparation_path,x=40, w=pdf.w-80,h=50)
    # legend = 'This image the relationship of the MaxForce variables with the target variables in boxplot'
    # pdf.set_font('Times', size = 8)
    # pdf.cell(w=0,h=3,txt=legend,ln=True, align='C')
    # pdf.ln(h=3)



    # #Quarta parte - Analise das comparações entre as colunas de posição
    # pdf.set_font('')
    # pdf.set_font('Times', size = 11, style = 'B')
    # pdf.ln(8)
    # pdf.cell(190, 5, txt = 'Distribution of target and predictor variables in boxplot by Position', ln=1, align='L')
    # pdf.ln(7)

    # fig= plt.figure(figsize=(10,3) ) 
    # fig.add_subplot(1,3,1) 
    # ar_6=sns.boxplot(x=usefull_info["Generic Segmentation"],y=usefull_info["Position Index"]) 
    # fig.add_subplot(1,3,2) 
    # ar_6=sns.boxplot(x=usefull_info["Generic Segmentation"],y=usefull_info["MaxPosition_F0500pN"]) 
    # fig.add_subplot(1,3,3) 
    # ar_6=sns.boxplot(x=usefull_info["Generic Segmentation"],y=usefull_info["MaxPosition_F1500pN"]) 
    # plt.tight_layout() 
    # plt.savefig(position_compare)

    # pdf.image(position_compare,x=40, w=pdf.w-80,h=50)
    # legend = 'This image the relationship of the Position variables with the target variables in boxplot'
    # pdf.set_font('Times', size = 8)
    # pdf.cell(w=0,h=3,txt=legend,ln=True, align='C')
    # pdf.ln(h=3)



    pdf.output(f'analysis_report_{datetime_str}.pdf','F')

analisys_pdf()