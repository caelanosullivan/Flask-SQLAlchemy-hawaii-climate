from datetime import date, time, datetime, timedelta
from dateutil.relativedelta import relativedelta
import numpy as np
import pandas as pd

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save references to the table
Measurement = Base.classes.measurements
Station = Base.classes.stations

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
        f"/api/v1.0/<'start'>    Note: append dates as YYYY-MM-DD <br/>"
        f"/api/v1.0/<'start'>/<'end'>    Note: append dates as YYYY-MM-DD"
    )


@app.route("/api/v1.0/precipitation")
def precipitation():
    """Return a json representation of a dictionary of dates and temperature observations"""
    
    # Query for dates and temperature observations from the last 12 months

    max_date = session.query(func.max(func.strftime("%Y/%m/%d", Measurement.date))).all()
    max_date = datetime.strptime(max_date[0][0], "%Y/%m/%d").date()

    sel = [Measurement.date, func.avg(Measurement.prcp)]

    prcp_twelve_months = session.query(*sel).\
        filter(Measurement.date >= (max_date - relativedelta(years=1))).\
        group_by(Measurement.date).all()    

    # Convert list of tuples into dictionary
    prcp_twelve_months_dict = dict(prcp_twelve_months)

    return jsonify(prcp_twelve_months_dict)


@app.route("/api/v1.0/stations")
def stations():
    """Return a json list of stations from the dataset"""

    sel = [Station.name]

    results  = session.query(*sel).\
        filter(Station.station == Measurement.station).\
        group_by(Measurement.station).all()
    
    #Convert list of tuples into normal list
    stations = list(np.ravel(results))

    return jsonify(stations)


@app.route("/api/v1.0/tobs")
def tobs():
    """Return a json list of Temperature Observations (tobs) for the previous year"""

    max_date = session.query(func.max(func.strftime("%Y/%m/%d", Measurement.date))).all()
    max_date = datetime.strptime(max_date[0][0], "%Y/%m/%d").date()

    sel = [Measurement.tobs]

    results = session.query(*sel).\
    filter(Measurement.date >= (max_date - relativedelta(years=1))).all()

    #Convert list of tuples into normal list
    tobs_12 = list(np.ravel(results))

    # Convert datatypes to int (int64 is not json serializable)
    tobs_12 = [int(i) for i in tobs_12]

    return jsonify(tobs_12)  

@app.route("/api/v1.0/<start>")
def one_temp(start):

    """Return a json list of the minimum temperature, the average temperature, and the\
    max temperature after a given start date."""
    
    results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).all()

    #Convert list of tuples into normal list
    temps_list = list(np.ravel(results))

    return jsonify(temps_list)

@app.route("/api/v1.0/<start>/<end>")
def two_temps(start, end):

    """Return a json list of the minimum temperature, the average temperature, and \
    the max temperature for a given start or start-end range."""
    
    results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).filter(Measurement.date <= end).all()

    #Convert list of tuples into normal list
    temps_list = list(np.ravel(results))

    return jsonify(temps_list)



if __name__ == '__main__':
    app.run(debug=True)
