
from h2o_wave import site, ui, main, data
import pandas as pd
from plotly import io as pio
import plotly.graph_objs as go
import plotly.express as px
import data_operator as do
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
    box='1 1 5 1',
    title='HIPERMERCADO SEMPRE TEM',
    subtitle='Dashboard Vendas',
    image='https://cdn.pixabay.com/photo/2014/04/03/10/00/shopping-cart-309592_1280.png',
    color='transparent'
)

df = do.imporata_df()
df_vendas_vr = df.groupby(['Data_Venda'])['Valor_Total'].agg('sum').reset_index()
df_vendas_vr['Valor_Total'] = round(df_vendas_vr['Valor_Total'],2)
df_vendas_vr.rename(columns={'Data_Venda':'Data Venda','Valor_Total':'Faturamento'},inplace=True)
df_vendas_qtd = df.groupby(['Data_Venda'])['order_id'].nunique().reset_index()
df_vendas_qtd['order_id'] = round(df_vendas_qtd['order_id'],2)
df_vendas_qtd.rename(columns={'Data_Venda':'Data Venda','order_id':'Quantidade'},inplace=True)
df_vendas = pd.merge(df_vendas_vr, df_vendas_qtd, on = 'Data Venda', how = 'inner')
df_vendas['Ticket Médio'] = round(df_vendas['Faturamento']/df_vendas['Quantidade'],2)

# Scatter
df_scatter = df_vendas.copy()
df_scatter['Data Venda'] = df_scatter['Data Venda'].astype('string')
df_scatter.rename(columns={'Ticket Médio':'Ticket_Medio'}, inplace=True)
page['scatter'] = ui.plot_card(
    box='5 7 4 4',
    title='Faturamento em realção ao Número de Vendas',
    data=data(fields = df_scatter.columns.tolist(), rows = df_scatter.values.tolist()),
    plot=ui.plot([ui.mark(type='point', x='=Quantidade', y='=Faturamento', shape='circle',
                          size='=Faturamento', x_title='Número de Vendas', y_title='Faturamento')])
)

# Lineplot
df_line = df_vendas.copy()
df_line['Data Venda'] = df_line['Data Venda'].astype('string')
df_line.rename(columns={'Data Venda':'Data_Venda'}, inplace=True)
page.add('lineplot', ui.plot_card(
    box='1 7 4 4',
    title='Evolução do Faturamento por Dia',
    data=data(fields = df_line.columns.tolist(), rows = df_line.values.tolist()),
    plot=ui.plot([
        ui.mark(type='line', x_scale='time', x='=Data_Venda', y='=Faturamento', y_min=15000,
                           y_title='Faturamento'),
        ui.mark(type='point', x='=Data_Venda', y='=Faturamento', size=2, fill_color='black')])
))


# Heatmap
df_vendas_dia = df.groupby(['Hora','Nome_do_dia'])['Valor_Total'].agg('sum').reset_index()
df_vendas_dia['Valor_Total'] = round(df_vendas_dia['Valor_Total'],2)
df_vendas_dia.rename(columns={'Data_Venda':'Data Venda','Valor_Total':'Faturamento'},inplace=True)
df_vendas_dia = df_vendas_dia.query("Hora != '21:00:00'")
label = {'07:00:00':'07:00', '08:00:00':'08:00', '09:00:00':'09:00', '10:00:00':'10:00', '11:00:00':'11:00',
       '12:00:00':'12:00', '13:00:00':'13:00', '14:00:00':'14:00', '15:00:00':'15:00', '16:00:00':'16:00',
       '17:00:00':'17:00', '18:00:00':'18:00', '19:00:00':'19:00', '20:00:00':'20:00'}
df_vendas_dia['Hora'] = df_vendas_dia['Hora'].map(label)

data = [go.Heatmap(
x=df_vendas_dia['Nome_do_dia'],
y=df_vendas_dia['Hora'],
z=df_vendas_dia['Faturamento'],
colorscale='blues'
)]

layout = go.Layout(
    title='Faturamento por dia da semana e horário',
    font=dict(
        family="Courier New, monospace",
        size=12,
    )
)
fig = go.Figure(data=data, layout=layout)
        
config = {
        'scrollZoom': False,
        'showLink': False,
        'displayModeBar': False
}

html = pio.to_html(fig, validate=False, include_plotlyjs='cdn', config=config)
page['heat_map'] = ui.frame_card(box='9 2 4 9', title='', content=html)

# barplot
df_vendas_barplot = df.groupby(['Nome_do_dia','Periodo_Mes'])['Margem_Lucro'].agg('sum').reset_index()
df_vendas_barplot['Margem_Lucro'] = round(df_vendas_barplot['Margem_Lucro'],2)
df_vendas_barplot.rename(columns={'Data_Venda':'Data Venda'},inplace=True)
df_vendas_barplot['% Total'] = round(100*df_vendas_barplot['Margem_Lucro']/df_vendas_barplot['Margem_Lucro'].sum(),2)
df_vendas_barplot = df_vendas_barplot.sort_values(by='Margem_Lucro', ascending=False)

fig = px.bar(
    df_vendas_barplot,
    x="Nome_do_dia",
    y="Margem_Lucro",
    title="Margem de Lucro por dia da Semana e Período do mês",
    text_auto='.2s',
    color='Periodo_Mes',
    color_discrete_map = {
        "Inicio": "#a8daff",
        "Meio": "#0092ff",
        "Fim": "#021624"
    },
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
                        "text": "Período Mês",
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

html2 = pio.to_html(fig, validate=False, include_plotlyjs='cdn', config=config)
page['barplot'] = ui.frame_card(box='3 2 6 5', title='', content=html2)

# Card Resumo
faturamento = df['Valor_Total'].sum()
faturamento = "R${:,.0f}".format(faturamento).replace(",", "X").replace(".", ",").replace("X", ".")
numvendas = df['order_id'].nunique()
faturamento_medio = df['Valor_Total'].sum() / df['order_id'].nunique()
faturamento_medio = "R${:,.2f}".format(faturamento_medio).replace(",", "X").replace(".", ",").replace("X", ".")

page['card_resumo'] = ui.tall_stats_card(
    box='1 3 2 4',
    items=[
        ui.stat(label='Faturamento Total', value=f'{faturamento}'),
        ui.stat(label='Número de Vendas', value=f'{numvendas}'),
        ui.stat(label='Ticket Médio',  value=f'{faturamento_medio}'),
    ]
)

#Combobox
page['combo_box'] = ui.form_card(box='1 2 2 1', items=[
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

page.save()