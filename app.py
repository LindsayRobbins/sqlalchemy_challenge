# Import dependencies
import numpy as np
import pandas as pd
import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalachemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

# connect to the database
# create engine to hawaii.sqlite
engine = create_engine("sqlite://hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()

# reflect teh tables
Base.prepare(engine, reflect=True)

# save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# create our session (link) from Python to the DB
session = Session (engine)

# Flask Setup
app = Flask(__name__)

# home route
@app.route("/")
def home():
    return(
        f"<center><h2>Hawaii Climate Analysis Local API</h2></center"
        f"<center><h3>Select from one of the available routes: </h3></center>"
        f"<center>/api/v1.0/precipitation</center>"
        f"<center>/api/v1.0/stations</center>"
        f"<center>/api/v1.0/tobs</center>"
        f"<center>/api/v1.0/start</center>"
        f"<center>/api/v1.0/end</center>"
    )

# /api/v1.0/precipitation route
@app.route("/api/v1.0/precipitation")
def precip():
    # return the previous year's precipitation as a json
    # calculate the date one year from the last date in the data set.
    previousYear = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    #previousYear

    # perform a query to retrieve the date and precipitation scores
    results = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= previousYear).all()

    session.close()
    #dictionary with the date as teh key and the precipitation (prcp) as the value
    precipitation = {date: prcp for date, prcp in results}
    # convert to a json
    return jsonify(precipitation)

# /api/v1.0/station route
@app.route("api/v1.0/stations")
def stations():
    results = session.query(Station.station).all()
    session.close()

    stationList = list(np.ravel(results))

    # convert to a json and display
    return jsonify(stationList)

# /api/v1.0/tobs route
@app.route("/api/v1.0/tobs")
def temperatures():
    # return the previous year temperatures
    # calculate the date one year from the last date in the data set.
    previousYear = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    #previousYear

    # perform a query to retrieve the temperatures from the most active station from the past year
    results = session.query(Measurement.tobs).\
        filter(Measurement.station == 'USC00519281').\
        filter(Measurement.date >= previousYear).all()
    
    session.close()

    temperatureList = list(np.ravel(results))
    
    # return the list of temperatures
    return jsonify(temperatureList)
# /api/v1.0/start/end and / api/v1.0/start routes
@app.route("/api/v1.0/<start>")
@app.route("/api/v1.0/<start>/<end>")
def dateStats(start=None, end=None):

    # select statement
    selection = [func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)]

    if not end:

        startDate = dt.datetime.strptime(start, "%m%d%Y")

        results = session.query(*selection).filter(Measurement.date >= startDate).all()

        session.close()

        temperatureList = list(np.ravel(results))
    
        # return the list of temperatures
        return jsonify(temperatureList)
    
    else: 

        startDate = dt.datetime.strptime(start, "%m%d%Y")
        endDate = dt.datetime.strptime(end, "%m%d%Y")

        results = session.query(*selection)\
            .filter(Measurement.date >= startDate)\
            .filter(Measurement.date <= endDate).all()

        session.close()

        temperatureList = list(np.ravel(results))
    
        # return the list of temperatures
        return jsonify(temperatureList)


## app launcher
if __name__ == '__main__':
    app.run(debug=True)
