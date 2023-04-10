
from h2o_wave import site, ui, Q, main, data, app
import pandas as pd
from plotly import io as pio
import plotly.graph_objs as go
import plotly.express as px
import data_operator as do
import numpy as np

@app('/')
async def serve(q):
    from h2o_wave import data
    q.client.initialized = True
    #Combobox
    q.page['combo_box'] = ui.form_card(box='1 1 2 1', items=[
    ui.dropdown( 
        name='filtro', 
        label='',
        placeholder='Dashboard Vendas',
        choices=[
            ui.choice(name='Vendas', label='Dashboard Vendas'),
            ui.choice(name='Corredor', label='Dashboard Corredor'),
            ui.choice(name='Produto', label='Tabela de Produtos'),
        ],
        trigger=True,
        value=q.args.filtro
        ),
    ])

    if not q.args.filtro:
        q.args.filtro = 'Vendas'
        del q.page['bar_plot2']
        del q.page['bolha2']
        del q.page['donuts1']
        del q.page['donuts2']
        del q.page['table']
        q.page['meta'] = ui.meta_card(box='', themes=[
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

        q.page['header'] = ui.header_card(
            box='3 1 5 1',
            title='HIPERMERCADO SEMPRE TEM',
            subtitle=f'Dashboard {q.args.filtro}',
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
        q.page['scatter'] = ui.plot_card(
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
        q.page.add('lineplot', ui.plot_card(
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
        q.page['heat_map'] = ui.frame_card(box='9 1 4 10', title='', content=html)

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
        q.page['barplot'] = ui.frame_card(box='3 2 6 5', title='', content=html2)

        # Card Resumo
        faturamento = df['Valor_Total'].sum()
        faturamento = "R${:,.0f}".format(faturamento).replace(",", "X").replace(".", ",").replace("X", ".")
        numvendas = df['order_id'].nunique()
        faturamento_medio = df['Valor_Total'].sum() / df['order_id'].nunique()
        faturamento_medio = "R${:,.2f}".format(faturamento_medio).replace(",", "X").replace(".", ",").replace("X", ".")

        q.page['card_resumo'] = ui.tall_stats_card(
            box='1 2 2 5',
            items=[
                ui.stat(label='Faturamento Total', value=f'{faturamento}'),
                ui.stat(label='Número de Vendas', value=f'{numvendas}'),
                ui.stat(label='Ticket Médio',  value=f'{faturamento_medio}'),
            ]
        )
    elif q.args.filtro == 'Vendas':
        del q.page['bar_plot2']
        del q.page['bolha2']
        del q.page['donuts1']
        del q.page['donuts2']
        del q.page['table']
        q.page['meta'] = ui.meta_card(box='', themes=[
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

        q.page['header'] = ui.header_card(
            box='3 1 5 1',
            title='HIPERMERCADO SEMPRE TEM',
            subtitle=f'Dashboard {q.args.filtro}',
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
        q.page['scatter'] = ui.plot_card(
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
        q.page.add('lineplot', ui.plot_card(
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
        q.page['heat_map'] = ui.frame_card(box='9 1 4 10', title='', content=html)

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
        q.page['barplot'] = ui.frame_card(box='3 2 6 5', title='', content=html2)

        # Card Resumo
        faturamento = df['Valor_Total'].sum()
        faturamento = "R${:,.0f}".format(faturamento).replace(",", "X").replace(".", ",").replace("X", ".")
        numvendas = df['order_id'].nunique()
        faturamento_medio = df['Valor_Total'].sum() / df['order_id'].nunique()
        faturamento_medio = "R${:,.2f}".format(faturamento_medio).replace(",", "X").replace(".", ",").replace("X", ".")

        q.page['card_resumo'] = ui.tall_stats_card(
            box='1 2 2 5',
            items=[
                ui.stat(label='Faturamento Total', value=f'{faturamento}'),
                ui.stat(label='Número de Vendas', value=f'{numvendas}'),
                ui.stat(label='Ticket Médio',  value=f'{faturamento_medio}'),
            ]
        )

    elif q.args.filtro == 'Corredor':
        q.args.filtro = 'Corredor'
        del q.page['card_resumo']
        del q.page['barplot']
        del q.page['heat_map']
        del q.page['scatter']
        del q.page['lineplot']
        del q.page['table']

        q.page['meta'] = ui.meta_card(box='', themes=[
                ui.theme(
                    name='my-awesome-theme',
                    primary='#d6fdfd',
                    text='#d0e5f7',
                    card='#052931',
                    page='#cfe2f3',
                )
                ],
            theme='my-awesome-theme'
        )

        q.page['header'] = ui.header_card(
            box='3 1 4 1',
            title='HIPERMERCADO SEMPRE TEM',
            subtitle=f'Dashboard {q.args.filtro}',
            image='https://cdn.pixabay.com/photo/2014/04/03/10/00/shopping-cart-309592_1280.png',
            color='primary'
        )
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
        q.page['bar_plot2'] = ui.plot_card(box='1 2 6 4',
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
        df_final = df_final.query('Corredor_Ajustado != "OUTROS"')
        df_final.drop(columns=('Corredor_Ajustado'), inplace=True)
        q.page['bolha2'] = ui.plot_card(
            box='1 6 6 5',
            title='% da Margem de Lucro em Relação ao Faturamento (excluído a categoria "outros")',
            data = data(fields = df_final.columns.tolist(), rows = df_final.values.tolist()),
            plot=ui.plot([ui.mark(type='point', x='=Percentual_Margem_Faturamento',
                                y='=Faturamento',color="Corredor", shape='circle',
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
            paper_bgcolor="#052931"
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
        q.page['donuts1'] = ui.frame_card(box='7 1 5 5', title='', content=html)
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
            paper_bgcolor="#052931"
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
        q.page['donuts2'] = ui.frame_card(box='7 6 5 5', title='', content=html2)
        
    elif q.args.filtro == 'Produto':   
        del q.page['bar_plot2']
        del q.page['bolha2']
        del q.page['donuts1']
        del q.page['donuts2']
        del q.page['card_resumo']
        del q.page['barplot']
        del q.page['heat_map']
        del q.page['scatter']
        del q.page['lineplot']
        q.args.filtro = 'Produto'

        q.page['meta'] = ui.meta_card(box='', themes=[
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

        q.page['header'] = ui.header_card(
            box='3 1 5 1',
            title='HIPERMERCADO SEMPRE TEM',
            subtitle='Tabela de Produtos',
            image='https://cdn.pixabay.com/photo/2014/04/03/10/00/shopping-cart-309592_1280.png',
            color='transparent'
        )

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
        #Tabela
        q.page['table'] = ui.form_card(box='1 2 12 9', items=[
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
                        groupable=True,
                        height='780px')
        ])

    await q.page.save()

    
