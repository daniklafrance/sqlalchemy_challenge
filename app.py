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
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0/<start>/<end>"
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

    precipitation_data = session.query(measurement.date, measurement.prcp).\
        filter(measurement.date > query_date).\
        order_by(measurement.date).all()
    
    prec_data = []
    for date, prcp in precipitation_data:
        prec_data_item = {}
        prec_data_item["date"] = date
        prec_data_item["prcp"] = prcp
        prec_data.append(prec_data_item) 
    
    return jsonify(prec_data

if __name__ == '__main__':
    app.run(debug=True)

    session.close()
