# Import the dependencies.
import numpy as np
import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(autoload_with=engine)

# Save references to each table
measurement = Base.classes.measurement
station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)

#################################################
# Flask Routes
#################################################

@app.route("/")
def welcome():

#List all available api routes

    return (
        f"Available Routes:<br/>"
        f"Precipitation (Last 12 months): /api/v1.0/precipitation<br/>"
        f"Stations: /api/v1.0/stations<br/>"
        f"Temperature (Last 12 months): /api/v1.0/tobs<br/>"
        f"Temperature from start date: /api/v1.0/yyyy-mm-dd<br/>"
        f"Temperature from start to end date: /api/v1.0/yyyy-mm-dd/yyyy-mm-dd"
    )

#Return the results of the precipitation analysis
@app.route("/api/v1.0/precipitation")
def precipitation():

#query the first available date and set the date for 1 year prior
    session.query(measurement.date).order_by(measurement.date.desc()).first()
    latest_date = dt.date(2017, 8, 23)
    query_date = latest_date - dt.timedelta(days=366)

#query the precipitation data
    precipitation_data = session.query(measurement.date, measurement.prcp).\
        filter(measurement.date > query_date).\
        order_by(measurement.date).all()

#create a dictionary with the precipitation data
    prec_data = []
    for date, prcp in precipitation_data:
        prec_data_item = {}
        prec_data_item["date"] = date
        prec_data_item["prcp"] = prcp
        prec_data.append(prec_data_item)

#return json data   
    return jsonify(prec_data)

#Return a JSON list of stations
@app.route("/api/v1.0/stations")
def stations():

#query the station names from sqlite
    station_name = session.query(station.name).all()
    station_name_list = list(np.ravel(station_name))

#return json data
    return jsonify(station_name_list)

#Return a list of temperature observations
@app.route("/api/v1.0/tobs")
def tobs():

#query the first available date and set the date for 1 year prior
    session.query(measurement.date).order_by(measurement.date.desc()).first()
    latest_date = dt.date(2017, 8, 23)
    query_date = latest_date - dt.timedelta(days=366)

#query the temp data from the most active station
    temp_obs = session.query(measurement.tobs).\
    filter(measurement.station == "USC00519281").\
    filter(measurement.date > query_date).\
    order_by(measurement.station).all()
    
    temp_obs_list = list(np.ravel(temp_obs))

#return json data
    return jsonify(temp_obs_list)

#For a specified start, calculate TMIN, TAVG, and TMAX for all the dates greater than or equal to the start date.
@app.route("/api/v1.0/<start>")
def start(start):

#set the start date format
    start = dt.datetime.strptime(start, "%Y-%m-%d")

#query the temp data with functions
    start_query = session.query(func.min(measurement.tobs),func.avg(measurement.tobs),func.max(measurement.tobs)).\
        filter(measurement.date >= start).all()

#create dict for the data    
    start_data = []
    for min,avg,max in start_query:
        data_item = {}
        data_item["min"] = min
        data_item["avg"] = avg
        data_item["max"] = max
        start_data.append(data_item)

#return json data
    return jsonify(start_data) 

#For a specified start date and end date, calculate TMIN, TAVG, and TMAX for the dates from the start date to the end date, inclusive.
@app.route("/api/v1.0/<start>/<end>")
def startend(start,end):

#set start and end date format
    start = dt.datetime.strptime(start, "%Y-%m-%d")
    end = dt.datetime.strptime(end, "%Y-%m-%d")

#query the temp data with functions
    startend_query = session.query(func.min(measurement.tobs),func.avg(measurement.tobs),func.max(measurement.tobs)).\
        filter(measurement.date >= start).\
        filter(measurement.date <= end).all()

#create dict for the data    
    startend_data = []
    for min,avg,max in startend_query:
        data_item = {}
        data_item["min"] = min
        data_item["avg"] = avg
        data_item["max"] = max
        startend_data.append(data_item)

#return json data
    return jsonify(startend_data)

#close session
session.close()

if __name__ == '__main__':
    app.run(debug=True)