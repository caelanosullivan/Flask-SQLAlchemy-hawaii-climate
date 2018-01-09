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
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0/<start>/<end>"
    )

# hello_dict = {"Hello": "World!"}

# @app.route("/normal")
# def normal():
#     return hello_dict


# @app.route("/jsonified")
# def jsonified():
#     return jsonify(hello_dict)


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

    prcp_twelve_months_dict = dict(prcp_twelve_months)

    # Convert list of tuples into dictionary
    #prcp_twelve_months_dict = dict(np.ravel(prcp_twelve_months))

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


# @app.route("/api/v1.0/tobs")
# def tobs():
#     """Return a json list of Temperature Observations (tobs) for the previous year"""

#     max_date = session.query(func.max(func.strftime("%Y/%m/%d", Measurement.date))).all()
#     max_date = datetime.strptime(max_date[0][0], "%Y/%m/%d").date()

#     sel = [Measurement.tobs]

#     results = session.query(*sel).\
#     filter(Measurement.date >= (max_date - relativedelta(years=1))).all()

#     #Convert list of tuples into normal list
#     tobs_12 = list(np.ravel(results))

#     return jsonify(tobs_12)  

# @app.route("/api/v1.0/names")
# def names():
#     """Return a list of all passenger names"""
#     # Query all passengers
#     results = session.query(Passenger.name).all()

#     # Convert list of tuples into normal list
#     all_names = list(np.ravel(results))

#     return jsonify(all_names)


# @app.route("/api/v1.0/passengers")
# def passengers():
#     """Return a list of passenger data including the name, age, and sex of each passenger"""
#     # Query all passengers
#     results = session.query(Passenger).all()

#     # Create a dictionary from the row data and append to a list of all_passengers
#     all_passengers = []
#     for passenger in results:
#         passenger_dict = {}
#         passenger_dict["name"] = passenger.name
#         passenger_dict["age"] = passenger.age
#         passenger_dict["sex"] = passenger.sex
#         all_passengers.append(passenger_dict)

#     return jsonify(all_passengers)


if __name__ == '__main__':
    app.run(debug=True)
