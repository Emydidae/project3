# dependencies
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify
from flask_cors import CORS
import calendar

# get path
pathStub = (__file__).replace('app.py', '')

#################################################
# Database Setup
#################################################
engine = create_engine(f'sqlite:///{pathStub}../03 - SQL Database/fire_water.sqlite')

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(autoload_with = engine)

# Save references to each table
wildfires = Base.classes.wildfires
rainfall = Base.classes.rainfall
rain_stations = Base.classes.rain_stations
"""
rain_stations - - - - - - - - - - - - - - - - - - - - - -
Station_ID - TEXT
Station_Name - TEXT
Longitude - FLOAT
Latitude - FLOAT
Elevation - BIGINT
More_Info - TEXT
rainfall - - - - - - - - - - - - - - - - - - - - - -
Index_Num - BIGINT
Station_ID - TEXT
Pcpn_In - FLOAT
Avg_Pcpn - FLOAT            # this is basically the expected precipitation amount
Avg_Pcpn_Percent - BIGINT   # this is the % of the expected precipitation that ocurred
Month - BIGINT
Year - BIGINT
wildfires - - - - - - - - - - - - - - - - - - - - - -
Unique_ID - TEXT
Acres_Burned - FLOAT
Cal_Fire_Incident - BOOLEAN
Latitude - FLOAT
Longitude - FLOAT
Month - BIGINT
Year - BIGINT
"""
# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)
CORS(app)
# this should prevent the CORS error "No 'Access-Control-Allow-Origin' header is present on the requested resource"
# if that error pops up, make sure you're running app.py from the right directory!

#################################################
# General Functions
#################################################

def monthly_rain(year):
    """
    Returns the average actual precipitation for each month of
    the given year.
    """
    # query to get rainfall.Month and average rainfall.PcpnIn for each month
    to_query = [rainfall.Month,
                func.avg(rainfall.Pcpn_In)]
    
    # search getting the wildfire data within the given year's fire season (june to nov)
    # filter by Year, group by Month, sort by Month
    monthly_rain = session.query(*to_query).filter(rainfall.Year == int(year)).group_by(rainfall.Month).order_by(rainfall.Month.asc())

    # iterate through the response, making each month into a dictionary and adding it to a list
    monthly_rain_response = []
    for item in monthly_rain:
        month_name = calendar.month_name[item[0]]
        monthly_rain_response.append({
            'month': month_name,
            'month_num': item[0],
            'avg_rainfall': round(item[1], 2)
        })
        
    # return list of dictionaries
    return monthly_rain_response

def monthly_fire(year):
    """
    Returns the average acres burned and # of fires for each
    month of the given year.
    """
    # query to get wildfires.Month, average wildfires.Acres_Burned, and # (count) of wildfires for each month
    to_query = [wildfires.Month,
                func.avg(wildfires.Acres_Burned),
                func.count(wildfires.Unique_ID)]
    
    # filter by Year, group by Month, sort by Month
    monthly_fires = session.query(*to_query).filter(wildfires.Year == int(year)).group_by(wildfires.Month).order_by(wildfires.Month.asc())

    # iterate through the response, making each month into a dictionary and adding it to a list
    monthly_fire_response = []
    for item in monthly_fires:
        month_name = calendar.month_name[item[0]]
        monthly_fire_response.append({
            'month': month_name,
            'month_num': item[0],
            'avg_acres_burned': round(item[1], 2),
            'num_of_fires': item[2]
        })

    # return list of dictionaries
    return monthly_fire_response

def data_years():
    """
    Returns list of years with data in both charts.
    """
    # build queries
    rain_years = session.query(rainfall.Year).\
                    group_by(rainfall.Year).\
                    order_by(rainfall.Year.asc())
    fire_years = session.query(wildfires.Year).\
                    group_by(wildfires.Year).\
                    order_by(wildfires.Year.asc())
    # compare & return
    years = [yr[0] for yr in rain_years if yr in fire_years]
    return years

#################################################
# Flask Routes
#################################################

@app.route('/')
def welcome():
    # list available routes on homepage
    return (
        f'Available Routes:<br/>'
        f'/years - Returns all years with both fire and rainfall data.<br/>'
        f'/map_markers/YYYY - Returns all data points for fires and data for precipitation before the fire season for year YYYY (2013-2019).<br/>'
        f'/rain_bar/YYYY - Returns average precipitation stats per month in the year YYYY (2013-2019).<br/>'
        f'/fire_bar/YYYY - Returns number of fires & average size of fires per month in the year YYYY (2013-2019).<br/>'
        f'/month_line - Returns monthly precipitation and fire stats per month over the entire dataset (2013-2019).<br/>'
    )

@ app.route('/years') # -----------------------------------------------------------------------------------------------------------------------------
def year_list():
    """
    Queries for list of all years that have data for rainfall
    and wildfires, then compares and returns list of years with
    data for both.
    """
    # get list from data_years function and return it
    return jsonify(data_years())

@app.route('/map_markers/<year>') # -----------------------------------------------------------------------------------------------------------------
def map_markers(year = 2013):
    """
    This pulls data from the given year (default 2013), and
    returns data in a json format. Will be used to populate
    the map with rain data / fire data. This is focused on
    answering the question "will a wet winter lead to a
    worse fire season?", so it pulls rainfall data starting the
    winter before (November YYYY-1) thru the start of the fire
    season (June YYYY), and fire data during the fire season
    (June YYYY thru November YYYY).
    """
    # make sure year is an integer
    try:
        int(year)
        print(f'Looking for markers in {year}...')
    except:
        year = 0
    # build query for rainfall
    # groups data to find overall rainfall for the rainy season at each station where there were measurements
    # first 3 are the total precipitation over the rainy season, total average precipitation, and number of months measured (8 would be the full season)
    to_query = [func.sum(rainfall.Pcpn_In),
                func.sum(rainfall.Avg_Pcpn),
                func.count(rainfall.Station_ID),
                rainfall.Station_ID,
                rain_stations.Station_Name,
                rain_stations.Longitude,
                rain_stations.Latitude,
                rain_stations.More_Info]
    # search getting the rainfall data & station info for each point for the given year
    # filter: 1st condition is syncing up the station info to the ID in the measurement table
    #         2nd condition is getting first part of the rainy season - November & December of the year before
    #         3rd condition is getting second part of the rainy season - January thru June of the given year
    #         final filter makes sure the station info matches up, then pulls data that is in either part of the season
    station_con = (rainfall.Station_ID == rain_stations.Station_ID)
    rain_season_con_1 = ((rainfall.Year == (int(year) - 1)) & (rainfall.Month > 10))
    rain_season_con_2 = ((rainfall.Year == int(year)) & (rainfall.Month < 7))
    rain_yr = session.query(*to_query).\
                filter(station_con & (rain_season_con_1 | rain_season_con_2)).\
                group_by(rainfall.Station_ID).\
                order_by(rainfall.Year.asc(), rainfall.Month.asc())
    # assemble response into list of dictionaries to json-ify
    rain_yr_d = []
    for item in rain_yr:
        rain_yr_d.append({
            'total_pcpn_inches': round(item[0], 2),
            'total_expected_pcpn': round(item[1], 2),
            'percent_avg_pcpn': int(100 * item[0] / item[1]),
            'months_measured': item[2],
            'Station_ID': item[3],
            'Station_Name': item[4],
            'Longitude': item[5],
            'Latitude': item[6],
            'info_link': item[7]
        })
    # build query for wildfires
    to_query = [wildfires.Acres_Burned,
                wildfires.Latitude,
                wildfires.Longitude,
                wildfires.Month,
                wildfires.Year]
    # search getting the wildfire data within the given year's fire season (june to nov)
    fire_yr = session.query(*to_query).\
                filter(wildfires.Year == int(year), wildfires.Month <= 11, wildfires.Month >= 6).\
                order_by(wildfires.Month.asc())
    # assemble response into list of dictionaries to json-ify
    fire_yr_d = []
    for item in fire_yr:
        fire_yr_d.append({
            'Acres_Burned': item[0],
            'Latitude': item[1],
            'Longitude': item[2],
            'Month': calendar.month_name[item[3]],
            'month_num': item[3],
            'Year': item[4]
        })
    # if there isn't data for one of the sets in that year, return a message saying as much
    if fire_yr_d == [] or rain_yr_d == []:
        return 'Missing data for that year...'
    # otherwise, return jsonified dictionaries
    else:
        return jsonify({'rain_data': rain_yr_d, 'fire_data': fire_yr_d})

@app.route('/rain_bar/<year>') # --------------------------------------------------------------------------------------------------------------------
def rain_bar(year = 2013):
    """
    This pulls data on rainfall from the given year (default
    2013) and returns the month and monthly average ACTUAL
    rainfall (average of Pcpn_In) for use in the rain bar graph
    (2 data points per month, JSON format).
    """
    # make sure year is an integer
    try:
        int(year)
        print(f'Looking for rain by month in {year}...')
    except:
        year = 0

    # call function to get list of dictionaries of data for the given year
    monthly_rain_table = monthly_rain(year)

    if len(monthly_rain_table) == 0:
        return 'Monthly rain data is missing rows'
    
    # return jsonified list of dicts (may want to include a check to make sure data was received)
    return jsonify(monthly_rain_table)


@app.route('/fire_bar/<year>') # --------------------------------------------------------------------------------------------------------------------
def fire_bar(year = 2013):
    """
    This pulls data on wildfires from the given year (default
    2013) and returns the month, monthly average acres burned,
    and the number (count) of wildfires per month for use in the
    fire bar graph (3 data points per month, JSON format).
    """
    # make sure year is an integer
    try:
        int(year)
        print(f'Looking for fires by month in {year}...')
    except:
        year = 0

    # call function to get list of dictionaries of data for the given year
    monthly_fire_table = monthly_fire(year)

    if len(monthly_fire_table) == 0:
        return 'Monthly fire data is missing rows'
    
    # return jsonified list of dicts (may want to include a check to make sure data was received)
    return jsonify(monthly_fire_table)

@app.route('/month_line') # --------------------------------------------------------------------------------------------------------------------
def month_line():
    """
    This pulls data on rain and wildfires across the dataset
    (Jan 2013 - Dec 2019) and returns the month, year, monthly
    average ACTUAL rainfall (average of Pcpn_In), monthly average
    acres burned, and number (count) of wildfires for use in the
    line graph (3 - 5 data points per month, as some may have no
    fire data, JSON format). Splitting these into separate lists,
    so that each can basically be put directly into plotly.
    """
    # don't worry about doing this one, it's spaghetti code before anything's even coded and I'll definitely have time to do it
    print('Looking for data by month across the dataset...')
    # create list to iterate through each of the years in the dataset (2013 THROUGH 2019)
    year_list = data_years()

    # iterate through, splitting the data points for different lines to different lists
    fire_counts = []
    avg_fire = []
    avg_rain = []
    for yr in year_list:
        # get year's-worth of data
        rain_data = monthly_rain(yr)
        fire_data = monthly_fire(yr)
        # add the rain data for each month to the list
        for item in rain_data:
            avg_rain.append({
                'avg_rainfall': item['avg_rainfall'],
                'month': f"{item['month'][0:3]} {yr}",
                'month_num': item['month_num'],
                'year': yr
            })
        # add the fire data for each month to the respective list
        for item in fire_data:
            avg_fire.append({
                'avg_acres_burned': item['avg_acres_burned'],
                'month': f"{item['month'][0:3]} {yr}",
                'month_num': item['month_num'],
                'year': yr
            })
            fire_counts.append({
                'num_of_fires': item['num_of_fires'],
                'month': f"{item['month'][0:3]} {yr}",
                'month_num': item['month_num'],
                'year': yr
            })
    # create final dictionary of data points to return
    line_data = {
        'fire_counts': fire_counts,
        'avg_fire': avg_fire,
        'avg_rain': avg_rain
    }
    # jsonified dict of lists of dicts (each item in top dict is a line, each dict in that list is a point)
    return jsonify(line_data)


# run app on startup
if __name__ == '__main__':
    app.run(debug=True)