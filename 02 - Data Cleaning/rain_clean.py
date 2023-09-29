import pandas as pd

# read file location and rough data
pathStub = (__file__).replace('rain_clean.py', '')
rain_stat_df = pd.read_csv(f'{pathStub}../01 - Web Scraping & Rough Data/Rough Data/rain_stations.csv')
rain_df = pd.read_csv(f'{pathStub}../01 - Web Scraping & Rough Data/Rough Data/rainfall.csv')

# rename columns to remove spaces
rain_stat_df.rename(columns = {'Station ID': 'Station_ID',
                               'Station Name': 'Station_Name',
                               'Link': 'More_Info'}, inplace = True)
# complete info link
rain_stat_df['More_Info'] = 'https://cdec.water.ca.gov' + rain_stat_df['More_Info'].astype(str)
# reset index
rain_stat_df.set_index('Station_ID', drop = True, inplace = True)
# export rain stations
rain_stat_df.to_csv(f'{pathStub}Clean Data/rain_stations.csv')

# rename columns
rain_df.rename(columns = {'index_num':'Index_Num',
                          'Station ID':'Station_ID',
                          'Precipitation (Inches)':'Pcpn_In',
                          'Average Precipitation':'Avg_Pcpn',
                          'Percent of Average':'Avg_Pcpn_Percent'}, inplace = True)
# reset index
rain_df.set_index('Index_Num', drop = True, inplace = True)
# drop if no average
rain_df.dropna(subset = ['Avg_Pcpn'], inplace = True)
# export rainfall
rain_df.to_csv(f'{pathStub}Clean Data/rainfall.csv')
print('Done.')

