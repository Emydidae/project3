import pandas as pd
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import Session

# get path
pathStub = (__file__).replace('convert_sqlite.py', '')

# connection to db
engine = create_engine(f'sqlite:///{pathStub}fire_water.sqlite')
session = Session(bind=engine)

# drop tables if they exist, create schema
with engine.connect() as conn:
    conn.execute(text('DROP TABLE IF EXISTS rainfall;'))
    conn.execute(text('DROP TABLE IF EXISTS rain_stations;'))
    conn.execute(text('DROP TABLE IF EXISTS wildfires;'))
    conn.execute(text('CREATE TABLE rain_stations (\
                      Station_ID TEXT PRIMARY KEY,\
                      Station_Name TEXT,\
                      Longitude FLOAT,\
                      Latitude FLOAT,\
                      Elevation BIGINT,\
                      More_Info TEXT);'))
    conn.execute(text('CREATE TABLE rainfall (\
                      Index_Num BIGINT PRIMARY KEY,\
                      Station_ID TEXT,\
                      Pcpn_In FLOAT,\
                      Avg_Pcpn FLOAT,\
                      Avg_Pcpn_Percent BIGINT,\
                      Month BIGINT,\
                      Year BIGINT,\
                      FOREIGN KEY(Station_ID) REFERENCES rain_stations(Station_ID));'))
    conn.execute(text('CREATE TABLE wildfires (\
                      Unique_ID TEXT PRIMARY KEY,\
                      Acres_Burned FLOAT,\
                      Cal_Fire_Incident BOOLEAN,\
                      Latitude FLOAT,\
                      Longitude FLOAT,\
                      Month BIGINT,\
                      Year BIGINT);'))
# I need to do this instead of just making them with to_sql because the primary key is needed to read the class
# and I prefer SQL code for making tables to doing the whole class thing


# make rain station table
rain_stat_df = pd.read_csv(f'{pathStub}../02 - Data Cleaning/Clean Data/rain_stations.csv')
rain_stat_df.set_index('Station_ID', drop = True, inplace = True)
rain_stat_df.to_sql(name = 'rain_stations', con = engine, if_exists = 'append')

# make rainfall table
rain_df = pd.read_csv(f'{pathStub}../02 - Data Cleaning/Clean Data/rainfall.csv')
rain_df.set_index('Index_Num', drop = True, inplace = True)
rain_df.to_sql(name = 'rainfall', con = engine, if_exists = 'append')

# make fire table
fire_df = pd.read_csv(f'{pathStub}../02 - Data Cleaning/Clean Data/wildfires.csv')
fire_df.set_index('Unique_ID', drop = True, inplace = True)
fire_df.to_sql(name = 'wildfires', con = engine, if_exists = 'append')

print('Done, printing tables & columns...')

# get table names
insp = inspect(engine)
response = insp.get_table_names()
for table in response:
    print(f'{table} - - - - - - - - - - - - - - - - - - - - - -')
    cols = insp.get_columns(table)
    for col in cols:
        print(f'{col["name"]} - {col["type"]}')