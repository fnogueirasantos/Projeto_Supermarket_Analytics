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
            primary='#d6fdfd',
            text='#d0e5f7',
            card='#001426',
            page='#193a50',
        )
        ],
    theme='my-awesome-theme'
)

page['header'] = ui.header_card(
    box='3 1 5 1',
    title='HIPERMERCADO SEMPRE TEM',
    subtitle='Dashboard Vendas',
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

df = do.imporata_df()
df_selec = df.groupby(['Corredor',]).agg({'Valor_Total': ['sum'],'Margem_Lucro' : ['sum']},
                                          axis=1).reset_index()
df_selec.columns = [
    '_'.join(col).rstrip('_') for col in df_selec.columns.values
    ]

df_selec.rename(columns={'Valor_Total_sum':'Faturamento',
                         'Margem_Lucro_sum':'Margem de Lucro'}, inplace=True)
df_selec['%Faturamento'] = round(100*df_selec['Faturamento'] / df_selec['Faturamento'].sum(),2)
df_selec['%Margem de Lucro'] = round(100*df_selec['Margem de Lucro'] / df_selec['Margem de Lucro'].sum(),2)
df_selec = df_selec[['Corredor', 'Faturamento','%Faturamento', 
                    'Margem de Lucro', '%Margem de Lucro']]
df_selec.sort_values(by='Faturamento', ascending=False, inplace=True)
df_selec = df_selec.round(2)
df_selec['Corredor_Ajustado'] = np.where((df_selec['%Faturamento'] > 2), df_selec['Corredor'], "OUTROS")

# Barplot
page['bar_plot'] = ui.plot_card(box='1 2 6 4',
								title = 'Fuutamento por Corredor',
								data = data(fields = df_selec.columns.tolist(), rows = df_selec.values.tolist()),
								plot = ui.plot(
                                marks = [ui.mark(type = 'interval',
										x='=Corredor_Ajustado',
										y='=Faturamento',                                                     
										#color='=Corredor_Ajustado'
                                            )],    
             ),
    )

#Scatter Plot
dfprep = df.groupby(['Corredor',]).agg({'Valor_Total': ['sum'],'Margem_Lucro' : ['sum']},
                                          axis=1).reset_index()
dfprep.columns = [
    '_'.join(col).rstrip('_') for col in dfprep.columns.values
    ]

dfprep.rename(columns={'Valor_Total_sum':'Faturamento',
                         'Margem_Lucro_sum':'Margem de Lucro'}, inplace=True)
dfprep['%Faturamento'] = round(100*df_selec['Faturamento'] / dfprep['Faturamento'].sum(),2)
dfprep['%Margem de Lucro'] = round(100*df_selec['Margem de Lucro'] / dfprep['Margem de Lucro'].sum(),2)
dfprep = dfprep[['Corredor', 'Faturamento','%Faturamento', 
                    'Margem de Lucro', '%Margem de Lucro']]
dfprep.sort_values(by='Faturamento', ascending=False, inplace=True)
dfprep = dfprep.round(2)
dfprep['Corredor_Ajustado'] = np.where((dfprep['%Faturamento'] > 2), dfprep['Corredor'], "OUTROS")
dfprep = dfprep[['Corredor','Corredor_Ajustado']]
df_buble = df.groupby(['Corredor','Data_Venda']).agg({'Valor_Total': ['sum'],'Margem_Lucro': ['sum']},
                                          axis=1).reset_index()
df_buble.columns = [
    '_'.join(col).rstrip('_') for col in df_buble.columns.values
    ]

df_buble.rename(columns={'Valor_Total_sum':'Faturamento',
                         'Margem_Lucro_sum':'Margem de Lucro'}, inplace=True)
df_buble.sort_values(by='Faturamento', ascending=False, inplace=True)
df_buble = df_buble.round(2)
df_final = pd.merge(df_buble, dfprep, on = 'Corredor')
df_final['Data_Venda'] = df_final['Data_Venda'].astype('string')
df_final['Percentual_Margem_Faturamento'] = round(100* df_final['Margem de Lucro'] / df_final['Faturamento'],2)
df_final = df_final.query('Percentual_Margem_Faturamento > 0')
page['bolha2'] = ui.plot_card(
    box='1 6 6 5',
    title='% de Lucro em Relação ao Faturamento',
    data = data(fields = df_final.columns.tolist(), rows = df_final.values.tolist()),
    plot=ui.plot([ui.mark(type='point', x='=Percentual_Margem_Faturamento',
                           y='=Faturamento',color="Corredor_Ajustado",
                           y_max=30000,x_title='% Margem de Lucro', y_title='Faturamento')])
)



# Donuts01
df_fat = df_selec[['Corredor', 'Faturamento','%Faturamento']]
df_fat['Corredor'] = np.where((df_fat['%Faturamento'] > 2), df_fat['Corredor'], "OUTROS")
fig = px.pie(
    df_fat, 
    values="Faturamento",
    names="Corredor",
    color_discrete_sequence=["#32a852", "#3b848a", "#9c3370"],
    hole=.6,
    title="% de Fatuamento por Corredor"
).update_layout(
    title = {"x": .5, "y": .99, "font": {"color":"white", "size": 12}},
    plot_bgcolor="#FFFFFF",
    paper_bgcolor="#001426"
).update_yaxes(
    {"title": ""}, color='white',
    gridcolor="white"
).update_xaxes(
    {"title": ""},color='white',
).update_layout(font_color="#d0e5f7",
                legend_title={
                        "text": "Corredor",
                        "font":{
                        "color":"#d0e5f7",
                        "family": "Comic Sans"
            }
        }
)
       
config = {
        'scrollZoom': False,
        'showLink': False,
        'displayModeBar': False
}

html = pio.to_html(fig, validate=False, include_plotlyjs='cdn', config=config)
page['donuts1'] = ui.frame_card(box='7 1 4 5', title='', content=html)
# Donuts02
df_fat2 = df_selec[['Corredor', 'Margem de Lucro','%Margem de Lucro']]
df_fat2['Corredor'] = np.where((df_fat2['%Margem de Lucro'] > 2), df_fat2['Corredor'], "OUTROS")
fig2 = px.pie(
    df_fat2, 
    values="Margem de Lucro",
    names="Corredor",
    color_discrete_sequence=["#32a852", "#3b848a", "#9c3370"],
    hole=.6,
    title="% da Margem de Lucro por Corredor"
).update_layout(
    title = {"x": .5, "y": .99, "font": {"color":"white", "size": 12}},
    plot_bgcolor="#FFFFFF",
    paper_bgcolor="#001426"
).update_yaxes(
    {"title": ""}, color='white',
    gridcolor="white"
).update_xaxes(
    {"title": ""},color='white',
).update_layout(font_color="#d0e5f7",
                legend_title={
                        "text": "Corredor",
                        "font":{
                        "color":"#d0e5f7",
                        "family": "Comic Sans",
            }
        }
)
       
config = {
        'scrollZoom': False,
        'showLink': False,
        'displayModeBar': False
}

html2 = pio.to_html(fig2, validate=False, include_plotlyjs='cdn', config=config)
page['donuts2'] = ui.frame_card(box='7 6 4 5', title='', content=html2)


page.save()