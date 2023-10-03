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
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"Precipitation (Last 12 months): /api/v1.0/precipitation<br/>"
        f"Stations: /api/v1.0/stations<br/>"
        f"Temperature (Last 12 months): /api/v1.0/tobs<br/>"
        f"Temperature from start date: /api/v1.0/[yyyy-mm-dd]<br/>"
        f"Temperature from start to end date: /api/v1.0/[yyyy-mm-dd/yyyy-mm-dd]"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():

    """Return the results of the precipitation analysis"""

    session.query(measurement.date).order_by(measurement.date.desc()).first()
    latest_date = dt.date(2017, 8, 23)
    query_date = latest_date - dt.timedelta(days=366)

    precipitation_data = session.query(measurement.date, measurement.prcp).\
        filter(measurement.date > query_date).\
        order_by(measurement.date).all()
    
    prec_data = []
    for date, prcp in precipitation_data:
        prec_data_item = {}
        prec_data_item["date"] = date
        prec_data_item["prcp"] = prcp
        prec_data.append(prec_data_item) 
    
    return jsonify(prec_data)

@app.route("/api/v1.0/stations")
def stations():

    """Return a JSON list of stations"""

    station_name = session.query(station.name).all()

    station_name_list = list(np.ravel(station_name))

    return jsonify(station_name_list)

@app.route("/api/v1.0/tobs")
def tobs():

    """Return a list of temperature observations"""

    session.query(measurement.date).order_by(measurement.date.desc()).first()
    latest_date = dt.date(2017, 8, 23)
    query_date = latest_date - dt.timedelta(days=366)

    temp_obs = session.query(measurement.tobs).\
    filter(measurement.station == "USC00519281").\
    filter(measurement.date > query_date).\
    order_by(measurement.station).all()
    
    temp_obs_list = list(np.ravel(temp_obs))

    return jsonify(temp_obs_list)

@app.route("/api/v1.0/<start>")
def start(start):

    start = dt.timedelta(days=0)

    start_query = session.query(func.min(measurement.tobs), func.avg(measurement.tobs), func.max(measurement.tobs)).\
        filter(measurement.date >= start).all()
    
    start_data = []
    for min,avg,max in start_query:
        data_item = {}
        data_item["min"] = min
        data_item["avg"] = avg
        data_item["max"] = max
        start_data.append(data_item)

    return jsonify(start_data) 

@app.route("/api/v1.0/<start>/<end>")
def startend(start,end):
    
    start = dt.timedelta(days=0)
    end = dt.timedelta(days=0)

    startend_query = session.query(func.min(measurement.tobs), func.avg(measurement.tobs), func.max(measurement.tobs)).\
        filter(measurement.date >= start).filter(measurement.date <= end).all()
    
    startend_data = []
    for min,avg,max in startend_query:
        data_item = {}
        data_item["min"] = min
        data_item["avg"] = avg
        data_item["max"] = max
        startend_data.append(data_item)

    return jsonify(startend_data)

session.close()

if __name__ == '__main__':
    app.run(debug=True)