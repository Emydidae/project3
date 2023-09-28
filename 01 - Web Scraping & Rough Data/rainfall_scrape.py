# Code by Peter Solis
# dependencies
from bs4 import BeautifulSoup
import pandas as pd
import requests as rq
from pprint import pprint

# base URL, list of years with data, initiate list to hold the important info
base_url = 'https://cdec.water.ca.gov/reportapp/javareports?name=PRECIPOUT.'
years = range(2007,2024)
tables = []
table_years = []

for y in years:
# get info for each year of data, cover for not having all data in 2023
    page = rq.get(f'{base_url}{y}09')
    if y == 2023:
        page = rq.get(f'{base_url}{y}08')
    soup = BeautifulSoup(page.content, 'html.parser')
# get each table
    table_list = soup.find_all('table', class_ = 'data left')
    tables.extend(table_list)
# keep track of year for each table
    table_years.extend([y for table in table_list])
# progress output
    print(f'Got tables for {y}.')

# get only the body section of each table, ignoring the header row
rows = []
row_years = []
for i in range(len(tables)):
# get list of rows
    table_row_list = tables[i].find_all('tr')
    y = table_years[i]
# iterate through rows, performing checks to make sure they are data rows
    skip_next = False
    for r in table_row_list:
    # check if one type of header row
        if r.find(class_ = 'header3') != None:
            pass
    # check if subheader for 2nd type of header row
        elif skip_next:
            skip_next = False
            pass
    # check if another type of header row
        elif r.find(class_ = 'top') != None:
            skip_next = True
            pass
    # passes all 3 checks, add
        else:
            rows.append(r)    
            row_years.append(y)
# progress output
print('Got rows.')

# for each row in these tables, we want to get:
# - 2nd cell (station ID)
# - 4th cell to 3rd from last cell (data by month)
#   > First 3 of these data cells are in the previous year
#   > Each data cell should put out a dict like this:
#       {Station ID, Precipitation (Inches), Average Precipitation, Percent of Average, Month, Year}

month_list = [10,11,12,1,2,3,4,5,6,7,8,9]
rain_data = []

for i in range(len(rows)):
# break up info station, and data points
    row = rows[i].find_all('td')
    station_id = row[1].text.split("'")[1]
    data = row[3:-2]
    year = row_years[i]
    for j in range(len(data)):
    # get the 3 stats for each month
        stats = data[j].get_text(strip = True, separator='\n').splitlines()
    # get the actual year for this data point (first 3 months are the previous year)
        year = row_years[i]
        if j < 3:
            year -= 1
    # check for null values
        if stats[2] == '---':
            stats[2] = None
        if stats[1] == '---':
            stats[1] = None
    # if we at least have the precip for that month, add the data
        if stats[0] == '---':
            pass
        else:
        # try to build the dictionary once everything is sorted
            try:
                stat_dict = {
                    'Station ID': station_id,
                    'Precipitation (Inches)': float(stats[0]),
                    'Month': month_list[j],
                    'Year': year
                }
            # handle missing values for non-essential stuff
                try:
                    stat_dict['Percent of Average'] = int(stats[2].replace('%',''))
                except TypeError:
                    stat_dict['Percent of Average'] = stats[2]
                try:
                    stat_dict['Average Precipitation'] = float(stats[1])
                except TypeError:
                    stat_dict['Average Precipitation'] = stats[1]
                rain_data.append(stat_dict)
        # print if something else goes wrong
            except:
                broke_dict = {
                    'Station ID': station_id,
                    'Precipitation (Inches)': stats[0],
                    'Average Precipitation': stats[1],
                    'Percent of Average': stats[2],
                    'Month': month_list[j],
                    'Year': year
                }
                print(f'Had issues at ID {i}:')
                pprint(broke_dict)
# progress output
    if ((i + 1) % 200) == 0:
        print(f'Did row {i + 1} of {len(rows)}.')
    if (i + 1) == len(rows):
        print(f'Done. ({len(rows)} rows)')

# create dataframe, do some sorting, export
rainfall_df = pd.DataFrame(rain_data, columns = ['Station ID', 'Precipitation (Inches)', 'Average Precipitation', 'Percent of Average', 'Month', 'Year'])
rainfall_df['Station ID'].replace('LSB', 'LBS', inplace = True) # this station seems to have a different ID now, this updates that
rainfall_df.sort_values(['Station ID','Year','Month'], inplace = True)
rainfall_df.reset_index(inplace = True, drop = True)
rainfall_df.reset_index(inplace = True, names = 'index_num')
pathStub = (__file__).replace('rainfall_scrape.py', '')
rainfall_df.to_csv(f'{pathStub}Rough Data/rainfall.csv', index = False)