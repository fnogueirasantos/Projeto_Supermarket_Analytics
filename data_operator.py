import pandas as pd


def imporata_df():
    df = pd.read_csv("dados_market.csv", sep=',', encoding='utf-8')
    df['Data_Venda'] = pd.to_datetime(df['Data_Venda'])
    df = df.query('Corredor != "RESTAURANTE"')
    return(df)
