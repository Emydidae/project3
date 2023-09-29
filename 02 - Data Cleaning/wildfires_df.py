import pandas as pd
from pathlib import Path
import datetime

wildfires = Path("../01 - Web Scraping & Rough Data/Rough Data/California_Fire_Incidents.csv")
wildfires_df = pd.read_csv(wildfires)

## acres burned, calfire incident, started, lon, lat
wildfires_clean_df = wildfires_df[['AcresBurned', 'CalFireIncident', 'Started', 'Latitude', 'Longitude', 'UniqueId']]

wildfires_clean_df.rename(columns={'AcresBurned': 'Acres Burned', 'CalFireIncident': 'CalFire Incident', 'Started': 'Start Date'}, inplace=True)

# convert datetime column to string
wildfires_clean_df['Start Date'] = wildfires_clean_df['Start Date'].str[:10]
wildfires_clean_df['Start Date'] = pd.to_datetime(wildfires_clean_df['Start Date'], format='%Y-%m-%d')

wildfires_clean_df['Month'] = wildfires_clean_df['Start Date'].dt.month
wildfires_clean_df['Year'] = wildfires_clean_df['Start Date'].dt.year

wildfires_clean_df = wildfires_clean_df.drop(columns=['Start Date'])

wildfires_clean_df.to_csv("wildfires.csv", index=False, header=True)