import pandas as pd
import csv
import os
import requests
from math import radians, sin, cos, sqrt, atan2

def haversine(lat1, lon1, lat2, lon2):
    url = f'{os.environ['OSRM_SERVER']}/{lon1},{lat1};{lon2},{lat2}'
    res = requests.get(url).json()
    distance = round(res['routes'][0]['distance']/1000, 3)
    return distance


def trova_id_nel_raggio(lat_tua, lon_tua, csv_file_path, raggio_max):
    id_nel_raggio = []

    df = pd.read_csv(csv_file_path)
    for index, row in df.iterrows():
        lat_distributore = float(row['latitudine'])
        lon_distributore = float(row['longitudine'])

        distanza = haversine(lat_tua, lon_tua, lat_distributore, lon_distributore)
    
        if distanza <= raggio_max:
            id_nel_raggio.append((int(row['id']), distanza))

    return id_nel_raggio


def dati_finali(list_id, csv):
    csv_id = pd.read_csv(csv)
    list_id = sorted(list_id, key=lambda x: x[1])
    final_list = {}
    for id, distanza in list_id:
        istanza = csv_id[csv_id['id'] == id]
        id_istanza = istanza['id'].values[0]
        prezzo_benzina = istanza['prezzo_benzina'].values[0]
        prezzo_diesel = istanza['prezzo_diesel'].values[0]
        km_distanza = distanza
        indirizzo = istanza['indirizzo'].values[0]
        elem = [prezzo_benzina, prezzo_diesel, km_distanza, indirizzo]
        final_list[id_istanza] = elem
        
    return final_list

def top_score(elements): 
    top_elem = {}
    for key in elements:
        prodotto = elements[key][0] * elements[key][2]
        top_elem[key] = prodotto
        
    return top_elem

def compute_cost(data, tank, consumption_per_km): 
    final_score = {}
    for key, value in data.items(): 
        final_score[key] = total_costs(tank, consumption_per_km, 20, value[2], value[0])
    
    final_score = dict(sorted(final_score.items(), key=lambda item: item[1]))
    return final_score

        
def travel_cost(distance:float, consumo:float, price_per_lt:float) -> float:
    return distance * consumo * price_per_lt



def fill_up_cost(tank_to_fill:float, price_per_lt:float, tank:int) -> float:
    return tank_to_fill * tank * price_per_lt



def total_costs(tank:int, consumption_per_km:float, tank_to_fill:int, distance:float, price_per_lt: float) -> float:
    return round(fill_up_cost(((100 - tank_to_fill))/100, price_per_lt, tank) + travel_cost(distance, consumption_per_km, price_per_lt), 3)


if __name__ == "__main__":
    lat_mia = 44.5570356992119
    long_mia = 10.75847674675621
    raggio_max = 10
    tank = 50
    consumption_per_km = 0.15
    csv = 'lat_long_modena_today.csv'
    id_raggio = trova_id_nel_raggio(lat_mia, long_mia, csv, raggio_max)
    res = dati_finali(id_raggio, csv)
    #top_reuslts = top_score(res)
    final_score = compute_cost(res, tank, consumption_per_km)
    print(res)
    print(final_score)
    
    
    
