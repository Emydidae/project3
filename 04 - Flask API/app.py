# dependencies
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify
from flask_cors import CORS

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
    # filter by Year, group by Month, sort by Month

    # iterate through the response, making each month into a dictionary and adding it to a list

    return # list of dictionaries

def monthly_fire(year):
    """
    Returns the average acres burned and # of fires for each
    month of the given year.
    """
    # query to get wildfires.Month, average wildfires.Acres_Burned, and # (count) of wildfires for each month
    # filter by Year, group by Month, sort by Month

    # iterate through the response, making each month into a dictionary and adding it to a list

    return # list of dictionaries

#################################################
# Flask Routes
#################################################

@app.route('/')
def welcome():
    # list available routes on homepage
    return (
        f'Available Routes:<br/>'
        f'/map_markers/YYYY - Returns all data points for fires and data for precipitation befor the fire season for year YYYY (2013-2019).<br/>'
        f'/rain_bar/YYYY - Returns average precipitation stats per month in the year YYYY (2013-2019).<br/>'
        f'/fire_bar/YYYY - Returns number of fires & average size of fires per month in the year YYYY (2013-2019).<br/>'
        f'/month_line - Returns monthly precipitation and fire stats per month over the entire dataset (2013-2019).<br/>'
    )

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
            'Month': item[3],
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
    # <response variable> = monthly_rain(year)

    return # jsonified list of dicts (may want to include a check to make sure data was received)


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
    # <response variable> = monthly_fire(year)

    return # jsonified list of dicts (may want to include a check to make sure data was received)

@app.route('/month_line') # --------------------------------------------------------------------------------------------------------------------
def month_line():
    """
    This pulls data on rain and wildfires across the dataset
    (Jan 2013 - Dec 2019) and returns the month, year, monthly
    average ACTUAL rainfall (average of Pcpn_In), monthly average
    acres burned, and number (count) of wildfires for use in the
    line graph (3 - 5 data points per month, as some may have no
    fire data, JSON format).
    """
    # don't worry about doing this one, it's spaghetti code before anything's even coded and I'll definitely have time to do it
    print('Looking for data by month across the dataset...')
    # iterate through each of the years in the dataset (2013 THROUGH 2019)

        # for each year, call functions to get query for fire and rain data for that year
        # <response variable> = monthly_rain(year)
        # <response variable> = monthly_fire(year)

        # combining these two into one dictionary will be hard since either dataset might be missing
        # some months of data in any given year, and we want to return them in a list so that the order
        # goes through to the javascript so we don't have to resort using the year and months before 
        # making the line graph.
        # the best way I can think of looks like this:
        # first, before calling for any data, make a huge dictionary with each month/year combo as a key leading
        # to a smaller dict, which might look like this:
        #   full_dict = {}
        #   for y in range(2013,2020):                      
        #       for m in range(1,13):
        #           key = y * 100 + m                       # results in key looking like YYYYMM
        #           full_dict[f'{key}'] = {'Year': y}
        # now that you've got the structure, you can loop through years, make the function calls, then
        # iterate through each result and add the info for each one
        #   for item in <fire_response_variable>:
        #       key = year * 100 + item['Month']
        #       joint_dict[f'{key}'].update(item)           # this adds the key-value pairs to the already-existing dictionary we made 5 lines above this
        # then you'd repeat that for the rain response so you now have a dictionary where the keys are YYYYMM and
        # the values are a dictionary of all data for that YYYYMM combo, so we can iterate through like 10
        # lines above (maybe just use [(y * 100) + m for y in range(2013, 2020)for m in range(1,13)] to make
        # a list of keys to iterate through rather than 2 for loops both times), appending each key in order
        # to a list.
        # probably a very inefficient way to do it but it's the best solution I can come up with lol

    return # jsonified list of dicts


# run app on startup
if __name__ == '__main__':
    app.run(debug=True)