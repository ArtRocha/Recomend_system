from datetime import datetime
import os
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
users = db.users

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

def ads_pdf():
    #image Dirs
    troca_venda_chart_path = f'scripts{os.sep}generate_report{os.sep}images{os.sep}ads_troca_venda_chart.png'

    best_publisher_tab_path = f'scripts{os.sep}generate_report{os.sep}images{os.sep}ads_best_publisher_table.png'
    best_publisher_chart_path = f'scripts{os.sep}generate_report{os.sep}images{os.sep}ads_best_publisher_chart.png'

    author_tro_ven_tab_path = f'scripts{os.sep}generate_report{os.sep}images{os.sep}ads_author_tro_ven_tab.png'
    author_tro_ven_chart_path = f'scripts{os.sep}generate_report{os.sep}images{os.sep}ads_author_tro_ven_chart.png'

    livros_caros_tab_path = f'scripts{os.sep}generate_report{os.sep}images{os.sep}ads_livros_caros_tab.png'
    livros_caros_chart_path = f'scripts{os.sep}generate_report{os.sep}images{os.sep}ads_livros_caros_chart.png'

    #PEGANDO O TEMPO
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
    pdf.set_font('')
    pdf.set_font('Times', size = 14, style = '')
    pdf.ln(3)
    pdf.cell(190, 5, txt = 'Top 10 autores mais anunciados', ln=1, align='C')
    pdf.image(author_tro_ven_tab_path, x=10, w=200, h=20)
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
    pdf.set_right_margin(-1)
    pdf.set_left_margin(10)
    pdf.set_font('Times', size=11, style='B')

    #Terceiro tabela gráfico - Livros mais caros
    pdf.add_page()
    pdf.set_font('')
    pdf.set_font('Times', size = 14, style = '')
    pdf.cell(190, 5, txt = 'Livros mais caros anunciados', ln=1, align='C')
    pdf.ln(3)
    
    plt.title('preço livros')
    plt.tight_layout()
    plt.savefig(livros_caros_chart_path)

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
    tipo_conta_chart_path = f'scripts{os.sep}generate_report{os.sep}images{os.sep}user_troca_venda_chart.png'

    generos_populares_tab_path = f'scripts{os.sep}generate_report{os.sep}images{os.sep}user_generos_populares_table.png'
    generos_populares_chart_path = f'scripts{os.sep}generate_report{os.sep}images{os.sep}user_generos_populares_chart.png'

    maiores_anunciadores_tab_path = f'scripts{os.sep}generate_report{os.sep}images{os.sep}user_maiores_anunciadores_tab.png'
    maiores_anunciadores_chart_path = f'scripts{os.sep}generate_report{os.sep}images{os.sep}user_maiores_anunciadores_chart.png'
    
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
    pdf.set_font('')
    pdf.set_font('Times', size = 14, style = '')
    pdf.ln(3)
    pdf.cell(190, 5, txt = 'Top 10 generos preferidos por usuário', ln=1, align='C')
    pdf.ln(1)
    pdf.image(generos_populares_tab_path, x=10, w=200, h=20)
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
    
    pdf.set_font('')
    pdf.set_font('Times', size = 14, style = '')
    pdf.cell(190, 5, txt = 'Top 10 usuários com mais anúncios', ln=1, align='C')
    pdf.ln(1)

    #Analise da distribuição das variaveis preditoras x variaveis alvo
    pdf.set_font('Times', size = 8)
    pdf.cell(190,5,ln=True, align='C')
    pdf.image(maiores_anunciadores_tab_path,x=60, w=90 ,h=75)
    
    pdf.image(maiores_anunciadores_chart_path,x=60, w=170 ,h=100)
    pdf.set_font('')
    pdf.set_font('Times', size = 8, style = 'I')
    pdf.cell(190, 5, txt = 'Usuários que mais possuem anúncios dentro do aplicativo', align='C')
    pdf.ln(10)

    #Primeira tabela e grafico gráfico - melhores editoras
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
    
    #image Dirs
    autores_mais_livros_table_path = f'scripts{os.sep}generate_report{os.sep}images{os.sep}book_autores_mais_livros_table.png'
    autores_mais_livros_chart_path = f'scripts{os.sep}generate_report{os.sep}images{os.sep}book_autores_mais_livros_chart.png'

    best_publisher_tab_path = f'scripts{os.sep}generate_report{os.sep}images{os.sep}book_best_publisher_table.png'
    best_publisher_chart_path = f'scripts{os.sep}generate_report{os.sep}images{os.sep}book_best_publisher_chart.png'

    book_per_year_tab_path = f'scripts{os.sep}generate_report{os.sep}images{os.sep}book_per_year_tab.png'
    book_per_year_chart_path = f'scripts{os.sep}generate_report{os.sep}images{os.sep}book_per_year_chart.png'

    maiores_generos_chart_path = f'scripts{os.sep}generate_report{os.sep}images{os.sep}book_maiores_generos_tab.png'
    maiores_generos_tab_path = f'scripts{os.sep}generate_report{os.sep}images{os.sep}book_maiores_generos_chart.png'
    
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

    #Primeira tabela e grafico gráfico - Autores mais presentes
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

    #Segundo tabela e gráfico - Top 10 editoras
    pdf.set_font('')
    pdf.set_font('Times', size = 14, style = '')
    pdf.ln(3)
    pdf.cell(190, 5, txt = 'Top 10 editoras', ln=1, align='C')

    pdf.image(best_publisher_tab_path, x=10, w=200, h=20)
    pdf.set_font('Times', size = 8)
    pdf.cell(w=0,h=3,ln=True, align='C')
    pdf.ln(4)

    pdf.image(best_publisher_chart_path, x=30, w=140, h=82)
    pdf.ln(0)
    pdf.set_font('')
    pdf.set_font('Times', size = 8, style = 'I')
    pdf.cell(190, 5, txt = 'Editoras que mais publicaram livros', align='C')
    pdf.ln(12)

    #Terceiro tabela gráfico - 'Livros publicados por ano
    pdf.set_right_margin(-1)
    pdf.set_left_margin(10)
    pdf.set_font('Times', size=11, style='B')

    pdf.set_font('')
    pdf.set_font('Times', size = 14, style = '')
    pdf.cell(190, 5, txt = 'Livros publicados por ano', ln=1, align='C')
    pdf.ln(1)

    pdf.set_font('Times', size = 8)
    pdf.cell(190,5,ln=True, align='C')
    pdf.image(book_per_year_tab_path,x=10, w=200 ,h=20)
    pdf.ln(1)
    
    pdf.image(book_per_year_chart_path,x=50, w=110 ,h=60)
    pdf.set_font('')
    pdf.set_font('Times', size = 8, style = 'I')
    pdf.cell(190, 5, txt = 'Livros lançados por ano', align='C')
    pdf.ln(8)

    #Quarto- Generos mais populares
    pdf.set_font('Times', size = 14)
    pdf.cell(190,5,ln=True, txt='Generos mais populares', align='C')
    pdf.image(maiores_generos_tab_path,x=10, w=200 ,h=20)
    pdf.ln(2)
    
    pdf.image(maiores_generos_chart_path,x=30, w=140 ,h=82)
    pdf.set_font('')
    pdf.set_font('Times', size = 8, style = 'I')
    pdf.cell(190, 5, txt = 'Contagem de generos por livro', align='C')
    pdf.output(f'books_report_{datetime_str}.pdf','F')

if ads_signal=='T':
    ads_pdf()
elif user_signal=='T':
    user_pdf()
elif book_signal=='T':
    books_pdf()