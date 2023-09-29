# dependencies
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, inspect
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

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)
CORS(app)

#################################################
# Flask Routes
#################################################

@app.route('/')
def welcome():
    # list available routes on homepage
    return (
        f'Available Routes:<br/>'
        f'/yearMarkers/YYYY - All data points for fires and rainfall in year YYYY (2013-2019)<br/>'
    )

@app.route('/yearMarkers/<year>')
def year_data(year = 2017):
    """
    This pulls data from the given year (default 2017),
    and returns it in a json format. Will be used to populate
    the map with rain data / fire data.
    """
    # make sure year is an integer
    try:
        int(year)
    except:
        year = 0
    # build query for rainfall
    to_query = [rainfall.Pcpn_In,
                rainfall.Avg_Pcpn_Percent,
                rainfall.Month,
                rainfall.Year,
                rainfall.Station_ID,
                rain_stations.Station_Name,
                rain_stations.Longitude,
                rain_stations.Latitude]
    rain_yr = session.query(*to_query).\
                filter(rainfall.Station_ID == rain_stations.Station_ID, rainfall.Year == int(year)).\
                order_by(rainfall.Month.asc())
    # assemble response into dictionary
    rain_yr_d = []
    for item in rain_yr:
        rain_yr_d.append({
            'Pcpn_In': item[0],
            'Avg_Pcpn_Percent': item[1],
            'Month': item[2],
            'Year': item[3],
            'Station_ID': item[4],
            'Station_Name': item[5],
            'Longitude': item[6],
            'Latitude': item[7]
        })
    # build query for wildfires
    to_query = [wildfires.Acres_Burned,
                wildfires.Latitude,
                wildfires.Longitude,
                wildfires.Month,
                wildfires.Year]
    fire_yr = session.query(*to_query).\
                filter(wildfires.Year == int(year)).\
                order_by(wildfires.Month.asc())
    # assemble response into dictionary
    fire_yr_d = []
    for item in fire_yr:
        fire_yr_d.append({
            'Acres_Burned': item[0],
            'Latitude': item[1],
            'Longitude': item[2],
            'Month': item[3],
            'Year': item[4]
        })
    if fire_yr_d == [] or rain_yr_d == []:
        return 'Missing data for that year.'
    else:
        return jsonify({'rain_data': rain_yr_d, 'fire_data': fire_yr_d})

# run app on startup
if __name__ == '__main__':
    app.run(debug=True)