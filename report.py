from datetime import datetime
import numpy as np
from matplotlib.backends.backend_pdf import PdfPages
import matplotlib.pyplot as plt
from numpy import size
import pandas as pd
import seaborn as sns
from fpdf import FPDF, HTMLMixin

df = pd.read_csv('/home/arthur/Documents/art_projects/recommend_system/data_colaborative/testando.tsv',sep='\t', index_col=0)
 
def analisys_pdf():
    title = 'Liber Reports'

    class MyFPDF(FPDF, HTMLMixin):
        pass

    pdf = MyFPDF()
    pdf.add_page()
    pdf.set_right_margin(-1)
    pdf.set_left_margin(10)
    pdf.set_font('Times', size=14, style='B')

    NetWork = 'Relatório'

    distribution_chart_path = 'images/distribution_graph.png'
    height_comparation_path = 'images/height_comparation.png'
    # max_force_comparation_path = 'images/max_force_comparation.png'
    force_comparation_path = 'images/force_comparation.png'
    correlation_variables = 'images/correlation_variables.png'
    # position_compare = 'images/position_variables.png'


    process_day = datetime.now()
    datetime_str = process_day.strftime('%d-%m-%Y')

    Header = f'{NetWork} Liber                                                                         Date: {datetime_str}' 
    pdf.multi_cell(180, 5, txt = Header, align = 'C') 

    pdf.set_font('')
    pdf.set_font('Times', size = 11, style = 'B')
    pdf.ln(2)
    pdf.cell(190, 5, txt = 'Distribution of ratings in database', ln=1, align='C')
    pdf.ln(1)

    #Primeiro gráfico - Distribuição das variaveis alvo e preditoras
    fig= plt.figure(figsize=(15,5) ) 
    a= df["rating"].value_counts(normalize=True).plot(kind='bar') 
    plt.title('Rating Distribution')
    plt.tight_layout() 
    plt.savefig( distribution_chart_path)



    #Salvar imagem com legenda
    pdf.image( distribution_chart_path, x=40, w=pdf.w-80, h=48)
    legend = 'This chart represent Distribution of ratings'
    pdf.set_font('Times', size = 8)
    pdf.cell(w=0,h=3,txt=legend,ln=True, align='C')
    pdf.ln(4)

    #Segundo gráfico - Correlação entre as variaveis 
    pdf.set_font('')
    pdf.set_font('Times', size = 11, style = 'B')
    pdf.ln(3)
    pdf.cell(190, 5, txt = 'Count evaluation per user', ln=1, align='C')
    
    fig= plt.figure(figsize=(15,5) ) 
    corr_plot = df.groupby('userId')['rating'].count().head(20).sort_values(ascending=False).plot(kind='bar')
    plt.title("Best Voter")
    plt.savefig(correlation_variables)

    #Salvar imagem com legenda
    pdf.image(correlation_variables, x=30, w=150, h=60)
    legend = 'Users who rating more books'
    pdf.set_font('Times', size = 8)
    pdf.cell(w=0,h=3,txt=legend,ln=True, align='C')
    pdf.ln(4)


    #Terceiro gráfico - Analise das comparações entre as colunas de altura
    pdf.set_font('')
    pdf.set_font('Times', size = 11, style = 'B')
    pdf.ln(6)
    pdf.cell(190, 5, txt = 'Count evaluation per books', ln=1, align='C')
    

    fig= plt.figure(figsize=(15,5) ) 
    df['rating_count'] = pd.DataFrame(df.groupby('movieId')['rating'].count())
    new = df.sort_values('rating_count', ascending=False)
    new['rating_count'].head(20).plot(kind='bar')
    plt.title("Most popular books")
    plt.savefig(height_comparation_path)

    pdf.image(height_comparation_path, x=30, w=150, h=60)
    legend = 'This image is the relationship of the height variables with the target variables with boxplot'
    pdf.set_font('Times', size = 8)
    pdf.cell(w=0,h=3,txt=legend,ln=True, align='C')
    pdf.ln(4)

    #Segunda página
    pdf.add_page()
    pdf.set_right_margin(-1)
    pdf.set_left_margin(10)
    pdf.set_font('Times', size=11, style='B')

    #Quarto gráfico - Analise das comparações entre as colunas de força
    pdf.set_font('')
    pdf.set_font('Times', size = 11, style = 'B')
    pdf.ln(4)
    pdf.cell(190, 5, txt = 'Table most popular books', ln=1, align='C')
    pdf.ln(3)

    #Analise da distribuição das variaveis preditoras x variaveis alvo
    fig, ax= plt.subplots(figsize=(15,3))
    ax.table(cellText=new.head(10).values, colLabels=new.columns, loc='center')
    ax.set_axis_off()
    # plt.tight_layout()
    plt.savefig(force_comparation_path)

    pdf.image(force_comparation_path,x=8, w=200 ,h=80)
    legend = 'This image the relationship of the force variables with the target variables in boxplot'
    pdf.set_font('Times', size = 8)
    pdf.cell(w=0,h=3,txt=legend,ln=True, align='C')
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