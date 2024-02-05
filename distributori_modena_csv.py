import pandas as pd
import numpy as np
import requests


def ottieni_dati_impianti():
    url = "https://www.mimit.gov.it/images/exportCSV/prezzo_alle_8.csv"
    response = requests.get(url)
    data = response.content.decode('utf-8')
    data = data.split("\n")
    data.pop(0)
    data.pop(0)
    data = [row.split(';') for row in data]
    df = pd.DataFrame(data, columns=["id_impianto", "tipo_carburante", "prezzo", "is_self", "data_ora"])
    df["data"] = df["data_ora"].str.split(" ").str.get(0)
    df["ora"] = df["data_ora"].str.split(" ").str.get(1)
    df.drop('data_ora', axis=1, inplace=True)
    df = df.iloc[:-1]

    url_imp = "https://www.mimit.gov.it/images/exportCSV/anagrafica_impianti_attivi.csv"
    response_imp = requests.get(url_imp)
    data_imp = response_imp.content.decode('utf-8')
    data_imp = data_imp.split("\n")
    data_imp.pop(0)
    data_imp.pop(0)
    data_imp = [row.split(';', 9) for row in data_imp]
    df_imp = pd.DataFrame(data_imp,
                          columns=["id", "gestore", "bandiera", "tipo", "nome", "indirizzo", "comune", "provincia",
                                   "latitudine", "longitudine"])
    df_imp = df_imp.iloc[:-1]
    df_imp = df_imp[df_imp['provincia'] == 'MO']
    df_imp_list = list(df_imp['id'])
    df = df[df['id_impianto'].isin(df_imp_list)]
    df_imp = df_imp.drop(df_imp.columns.difference(['id', 'latitudine', 'longitudine', 'indirizzo']), axis=1)

    return df, df_imp


def aggiungi_prezzo_benzina(df_price, df_imp):
    df_price_copy = df_price.copy()
    df_price_copy = df_price_copy[df_price_copy['tipo_carburante'] == 'Benzina']
    df_price_copy = df_price_copy[df_price_copy['is_self'] == '1']
    df_price_copy = df_price_copy.drop(['is_self', 'data', 'ora', 'tipo_carburante'], axis=1)
    df_imp = pd.merge(df_imp, df_price_copy, left_on='id', right_on='id_impianto', how='left')
    df_imp['prezzo'] = pd.to_numeric(df_imp['prezzo'], errors='coerce')
    media_prezzo = df_imp['prezzo'].mean(skipna=True)
    df_imp['prezzo'].fillna(media_prezzo, inplace=True)
    df_imp = df_imp.drop('id_impianto', axis=1)
    df_imp.columns = ['id', 'indirizzo', 'latitudine', 'longitudine', 'prezzo_benzina']
    return df_imp


def aggiungi_prezzo_diesel(df_price, df_imp):
    df_price_copy = df_price.copy()
    df_price_copy = df_price_copy[df_price_copy['tipo_carburante'] == 'Gasolio']
    df_price_copy = df_price_copy[df_price_copy['is_self'] == '1']
    df_price_copy = df_price_copy.drop(['is_self', 'data', 'ora', 'tipo_carburante'], axis=1)
    df_imp = pd.merge(df_imp, df_price_copy, left_on='id', right_on='id_impianto', how='left')
    df_imp['prezzo'] = pd.to_numeric(df_imp['prezzo'], errors='coerce')
    media_prezzo = df_imp['prezzo'].mean(skipna=True)
    df_imp['prezzo'].fillna(media_prezzo, inplace=True)
    df_imp = df_imp.drop('id_impianto', axis=1)
    df_imp.columns = ['id', 'indirizzo', 'latitudine', 'longitudine', 'prezzo_benzina', 'prezzo_diesel']
    return df_imp


def salva_csv_per_calcolo(df):
    df.to_csv('lat_long_modena_today.csv', index=False)


if __name__ == "__main__":
    df_price, df_imp = ottieni_dati_impianti()
    df_imp = aggiungi_prezzo_benzina(df_price, df_imp)
    df_imp = aggiungi_prezzo_diesel(df_price, df_imp)
    salva_csv_per_calcolo(df_imp)
