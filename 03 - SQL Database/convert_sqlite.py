import pandas as pd
from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import Session

# connection to db
engine = create_engine('sqlite:///fire_water.sqlite')
session = Session(bind=engine)

# get table names
insp = inspect(engine)
response = insp.get_table_names()

# make rainfall table
if 'rainfall' not in response:
    rain_df = pd.read_csv('../01 - Web Scraping & Rough Data/Rough Data/rainfall.csv')
    rain_df.set_index('index_num', drop = True, inplace = True)
    rain_df.to_sql(name = 'rainfall', con = engine, if_exists = 'replace')
else:
    rain_df = pd.read_csv('../01 - Web Scraping & Rough Data/Rough Data/rainfall.csv')
    rain_df.set_index('index_num', drop = True, inplace = True)
    rain_df.to_sql(name = 'rainfall', con = engine, if_exists = 'replace')
    print('Rainfall already made.')

# make rain station table
if 'rain_stations' not in response:
    rain_stat_df = pd.read_csv('../01 - Web Scraping & Rough Data/Rough Data/rain_stations.csv')
    rain_stat_df.set_index('Station ID', drop = True, inplace = True)
    rain_stat_df.to_sql(name = 'rain_stations', con = engine, if_exists = 'replace')
else:
    rain_stat_df = pd.read_csv('../01 - Web Scraping & Rough Data/Rough Data/rain_stations.csv')
    rain_stat_df.set_index('Station ID', drop = True, inplace = True)
    rain_stat_df.to_sql(name = 'rain_stations', con = engine, if_exists = 'replace')
    print('Rain Stations already made.')

# make fire table
if 'wildfires' not in response:
    fire_df = pd.read_csv('../02 - Data Cleaning/wildfires.csv')
    fire_df.set_index('UniqueId', drop = True, inplace = True)
    fire_df.to_sql(name = 'wildfires', con = engine, if_exists = 'replace')
else:
    fire_df = pd.read_csv('../02 - Data Cleaning/wildfires.csv')
    fire_df.set_index('UniqueId', drop = True, inplace = True)
    fire_df.to_sql(name = 'wildfires', con = engine, if_exists = 'replace')
    print('Wildfires already made.')

rain_col = insp.get_columns('wildfires')
print(rain_col)