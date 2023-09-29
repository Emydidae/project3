import pandas as pd
from pathlib import Path
import datetime

wildfires = Path("../01 - Web Scraping & Rough Data/Rough Data/California_Fire_Incidents.csv")
wildfires_df = pd.read_csv(wildfires)

## acres burned, calfire incident, started, lon, lat
wildfires_clean_df = wildfires_df[['AcresBurned', 'CalFireIncident', 'Started', 'Latitude', 'Longitude', 'UniqueId']]

wildfires_clean_df.rename(columns={'AcresBurned': 'Acres_Burned', 'CalFireIncident': 'Cal_Fire_Incident', 'Started': 'Start_Date', 'UniqueId': 'Unique_ID'}, inplace=True)

# convert datetime column to string
wildfires_clean_df['Start_Date'] = wildfires_clean_df['Start_Date'].str[:10]
wildfires_clean_df['Start_Date'] = pd.to_datetime(wildfires_clean_df['Start_Date'], format='%Y-%m-%d')

wildfires_clean_df['Month'] = wildfires_clean_df['Start_Date'].dt.month
wildfires_clean_df['Year'] = wildfires_clean_df['Start_Date'].dt.year

wildfires_clean_df = wildfires_clean_df.drop(columns=['Start_Date'])

# remove duplicates
wildfires_clean_df.drop_duplicates(inplace = True)

# remove where lon, lat = 0
no_lon_lat = wildfires_clean_df[wildfires_clean_df['Longitude'] == 0].index.to_list()
wildfires_clean_df.drop(no_lon_lat, inplace = True)

print(wildfires_clean_df.shape)

wildfires_clean_df.to_csv("Clean Data/wildfires.csv", index=False, header=True)