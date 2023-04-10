from h2o_wave import site, ui, main, data
import pandas as pd
from plotly import io as pio
import plotly.graph_objs as go
import plotly.express as px
import data_operator as do
import numpy as np
import locale
locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')

page = site['/']

page['meta'] = ui.meta_card(box='', themes=[
        ui.theme(
            name='my-awesome-theme',
            primary='#000000',
            text='#000000',
            card='#d0e0e3',
            page='#5fa0af',
        )
        ],
    theme='my-awesome-theme'
)

page['header'] = ui.header_card(
    box='3 1 5 1',
    title='HIPERMERCADO SEMPRE TEM',
    subtitle='Tabela de Produtos',
    image='https://cdn.pixabay.com/photo/2014/04/03/10/00/shopping-cart-309592_1280.png',
    color='transparent'
)

#Combobox
page['combo_box'] = ui.form_card(box='1 1 2 1', items=[
    ui.dropdown( 
        name='combo', 
        label='',
        choices=[
            ui.choice(name='Vendas', label='Dashboard Vendas'),
            ui.choice(name='Corredor', label='Dashboard Corredor'),
            ui.choice(name='Produto', label='Dashboard Produto'),
            ui.choice(name='Insights', label='Insights'),

        ],
        trigger=True,
        value='Vendas'
        ),
    ])

#### ------

# Prepara os dados
df = do.imporata_df()
df_produto = df.groupby(['Produto','Un Medida','Corredor']).agg({'Valor_Total': ['sum'],'CMV':['sum'],
                                                      'Margem_Lucro': ['sum'], 'Qtd': ['sum']},
                                          axis=1).reset_index()
df_produto.columns = [
    '_'.join(col).rstrip('_') for col in df_produto.columns.values
    ]

df_produto.rename(columns={'Valor_Total_sum':'Faturamento',
                           'Margem_Lucro_sum':'Margem_Lucro',
                           'Qtd_sum':'Quantidade', 'CMV_sum':'CMV',
                           'Valor_Unit_sum':'Pr_Medio_Venda'}, inplace=True)
df_prod_normaliza = pd.read_excel('normaliza_produtos.xlsx')
df_produto_final = pd.merge(df_prod_normaliza, df_produto, on = 'Produto', how = 'inner')
df_produto_ajus = df_produto_final.groupby(['Produto','Produto_normalizado','Un Medida','Corredor']).agg({'Faturamento': ['sum'],
                                                                          'CMV': ['sum'],
                                                                        'Margem_Lucro': ['sum'],'Quantidade': ['sum']}
                                                                                              ,axis=1).reset_index()
df_produto_ajus.columns = [
    '_'.join(col).rstrip('_') for col in df_produto_ajus.columns.values
    ]
df_produto_ajus = df_produto_ajus.sort_values(by='Faturamento_sum', ascending=False)
df_produto_ajus['Percent_Fatu_Tot'] = round(100*df_produto_ajus.Faturamento_sum / df_produto_ajus.Faturamento_sum.sum(),2)
df_produto_ajus['Percent_Margem_Fatu'] = round(100*df_produto_ajus.Margem_Lucro_sum / df_produto_ajus.Faturamento_sum,2)
df_produto_ajus['Percent_Margem_Tot'] = round(100*df_produto_ajus.Margem_Lucro_sum / df_produto_ajus.Margem_Lucro_sum.sum(),2)
df_produto_ajus['Indicador_Lucratividade'] = ['Muito Alta' if v > 60 else 'Alta' if v > 40 else 'Média' if v > 30 else 'Baixa' if v > 15 else 'Muito Baixa' if v > 0 else 'Prejuizo' for v in df_produto_ajus['Percent_Margem_Fatu']]
df_produto_ajus.rename(columns={'Produto_normalizado':'Produto Agrupado',
                 'Faturamento_sum':'Faturamento', 'CMV_sum':'Custo', 'Margem_Lucro_sum':'Margem', 'Quantidade_sum':'Qtd',
                 'Percent_Fatu_Tot':'%Faturamento Total', 'Percent_Margem_Fatu':'%Margem/Faturamento',
                 'Percent_Margem_Tot':'%Margem Total'},inplace=True)


df_tabela = df_produto_ajus[['Produto Agrupado','Produto','Corredor','Indicador_Lucratividade','Qtd','Un Medida','Faturamento','Custo','Margem','%Margem/Faturamento']]
df_tabela = df_tabela.round(2)
df_tabela['Faturamento'] = 'R$ ' + df_tabela['Faturamento'].astype("string")
df_tabela['Custo'] = 'R$ ' + df_tabela['Custo'].astype("string")
df_tabela['Margem'] = 'R$ ' + df_tabela['Margem'].astype("string")
df_tabela['%Margem/Faturamento'] = '% ' + df_tabela['%Margem/Faturamento'].astype("string")
page['example'] = ui.form_card(box='1 2 12 9', items=[
    ui.table(name='table', columns=[
        ui.table_column(name='Produto Agrupado', label='Produto Agrupado',filterable=True),
        ui.table_column(name='Produto', label='Produto',searchable=True),
        ui.table_column(name='Corredor', label='Corredor',filterable=True),
        ui.table_column(name='Indicador_Lucratividade', label='Lucratividade', filterable=True),
        ui.table_column(name='Qtd', label='Qtd Vendido'),
        ui.table_column(name='Un Medida', label='Un'),
        ui.table_column(name='Faturamento', label='Faturamento'),
        ui.table_column(name='Custo', label='Custo'),
        ui.table_column(name='Margem', label='Margem'),
        ui.table_column(name='%Margem/Faturamento', label='%Margem/Faturamento')
    ], rows=[
                    ui.table_row(
                        name=str(i),
                        cells=[str(df_tabela[col].values[i]) for col in df_tabela.columns.values]
                    ) for i in range(len(df_tabela))
                ],
                downloadable=True,
                groupable=False,
                height='780px')
])

page.save()