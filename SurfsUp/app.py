# Import the dependencies.

from flask import Flask,jsonify
import numpy as np
import pandas as pd
import datetime as dt
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

#################################################
# Database Setup
#################################################

engine = create_engine("sqlite:///Resources/hawaii.sqlite")
# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(autoload_with=engine)

# Save references to each table
Station = Base.classes.station
measurements=Base.classes.measurement

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
def home():

    return """
 <ul>
        <li>/api/v1.0/precipitation</li>
        <li>/api/v1.0/stations</li>
        <li>/api/v1.0/tobs</li>
        <li>/api/v1.0/{start}</li>
        <li>/api/v1.0/{start}/{end}</li>
    </ul>
"""
@app.route("/api/v1.0/precipitation")
def prcp():
 # create session link from python to DB
    session=Session(engine)
    """Return a list of precipitation and date for one year"""
    # Calculate the date one year from the last date in data set.
    latest_year_start = dt.date(2017, 8, 23) - dt.timedelta(days=365)
  
    # Perform a query to retrieve the data and precipitation scores
    results=session.query(measurements.date, measurements.prcp).\
                          order_by(measurements.date.asc()).\
                          filter(measurements.date>=latest_year_start).all()
    precipitation= {date: prcp for date, prcp in results}
    session.close()
    return jsonify(precipitation)

@app.route("/api/v1.0/stations")
def stations():
    # create session
    session=Session(engine)

    """Return a list of all stations"""
    # query all stations
    station_result=session.query(Station.station).all()
    stations =list(np.ravel(station_result))
    session.close()
    return jsonify(stations)

@app.route("/api/v1.0/tobs")
def tobs():
    session = Session(engine)

    # Determine the most active station ID
    most_active_station_id = session.query(measurements.station).\
                             group_by(measurements.station).\
                             order_by(func.count(measurements.station).desc()).\
                             first()[0]

    # Find the most recent date and calculate one year ago
    most_recent_date = session.query(func.max(measurements.date)).scalar()
    most_recent_date = dt.datetime.strptime(most_recent_date, '%Y-%m-%d')
    latest_year_start = most_recent_date - dt.timedelta(days=365)

    # Query the last 12 months of TOBS data for the most active station
    results = session.query(measurements.date, measurements.tobs).\
        filter(measurements.station == most_active_station_id).\
        filter(measurements.date >= latest_year_start).all()
    session.close()

    # Convert to list of dictionaries
    tobs_list = [{"date": date, "tobs": tobs} for date, tobs in results]
    return jsonify(tobs_list)

@app.route("/api/v1.0/<start>")
@app.route("/api/v1.0/<start>/<end>")
def temps(start=None, end=None):

    if not end:
        results = session.query(func.min(measurements.tobs), func.avg(measurements.tobs), func.max(measurements.tobs)).\
            filter(measurements.date >= start).all()
        temps = list(np.ravel(results))
        session.close()
        return jsonify(temps)
  
    results = session.query(func.min(measurements.tobs), func.avg(measurements.tobs), func.max(measurements.tobs)).\
        filter(measurements.date >= start).filter(measurements.date <= end).all()  
    temps = list(np.ravel(results))
    session.close()
    return jsonify(temps)

if __name__ == "__main__":
    app.run(debug=True)