# Code by Peter Solis
# dependencies
from bs4 import BeautifulSoup
import pandas as pd
import requests as rq

pathStub = (__file__).replace('station_scrape.py', '')
rain_df = pd.read_csv(f'{pathStub}Rough Data/rainfall.csv', index_col = 0)

stations = rain_df['Station ID'].unique().tolist()
base_url = 'https://cdec.water.ca.gov/dynamicapp/staSearch?sta_chk=on&sta='
station_data = []

# search for stations by tag, find results table
for s in stations:
    page = rq.get(f'{base_url}{s}')
    soup = BeautifulSoup(page.content, 'html.parser')
    result_table = soup.find('tbody')
    results = result_table.find_all('tr')
# check for wrong # of results
    if len(results) > 1:
        print(f'Found multiple results for {s}.')
    elif len(results) == 0:
        print(f'Couldn\'t find a result for {s}.')
# if only 1 result, get the info
    else:
        s_info = results[0].find_all('td')
        try:
            station_data.append({
                'Station ID': s,
                'Station Name': s_info[1].text,
                'Longitude': float(s_info[4].text),
                'Latitude': float(s_info[5].text),
                'Elevation': int(s_info[6].text.replace(',','')),
                'Link': s_info[0].find('a')['href']
            })
            print(f'Got {s}.')
        except:
            print(f'Had an issue parsing the results table for {s}.')
            
# create dataframe, export
rain_station_df = pd.DataFrame(station_data, columns = ['Station ID', 'Station Name', 'Longitude', 'Latitude', 'Elevation', 'Link'])
rain_station_df.to_csv(f'{pathStub}Rough Data/rain_stations.csv')