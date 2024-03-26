# Import the dependencies.
from flask import Flask, jsonify

# Sqlalchemy is used to query DB from Python
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

import numpy as np
import pandas as pd
import datetime as dt
#################################################
# Database Setup
#################################################
# create engine to DB
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(autoload_with=engine)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

#################################################
# Flask Setup
#################################################
app = Flask(__name__)

#################################################
# Flask Routes
#################################################
# Define home page
@app.route("/")
def home():
    print("Server received request for home page")
    return (
        "Welcome to the Hawaii API"
        f"Available Routes:</br/>"
        f"/api/v1.0/precipitation</br/>"
        f"/api/v1.0/stations</br/>"
        f"/api/v1.0/tobs</br/>"
        f"/api/v1.0/start/start_date</br/>"
        f"/api/v1.0/dates/start_date/end_date"
    )


# Define precipitation route that returns {date:precipitation} for the past 12 months
@app.route("/api/v1.0/precipitation")
def precipitation():

 # Create our session (link) from Python to the DB
    session = Session(engine)

# Calculate the date one year from the last date in data set.
    prior_year = dt.date(2017, 8, 23) - dt.timedelta(days=365)

# Query for the past year's precipitation data
    # This will provide a list of tuples
    prior_year_results = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= prior_year)

# Close the session
    session.close()

# Create a list of dictionaries containing dates paired with the precipitation measurement
    prior_year_results_list = []
    for row in prior_year_results:
        day_results = {}
        day_results[row.date] = row.prcp
        prior_year_results_list.append(day_results)

    return jsonify(prior_year_results_list)
 
 # Define stations route that returns list of stations in DB
@app.route("/api/v1.0/stations")
def stations():
    session = Session(engine)

# Query for station names within database
    stations = session.query(Station.name).all()
    session.close()
    stations_list = (list(np.ravel(stations)))

    return jsonify(stations_list)

#Define tobs route that returns most active station and last year of data
@app.route("/api/v1.0/tobs")
def tobs():
    session = Session(engine)
    prior_year = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    temperatures = session.query(Measurement.date, Measurement.tobs).filter(Measurement.station == "USC00519281").filter(Measurement.date >= prior_year).all()
    session.close()

    # Create list to collect observed temperatures from query
    temperatures_list = []
    for row in temperatures:
        temps = {}
        temps[row.date] = row.tobs
        temperatures_list.append(temps)
    
    return jsonify(temperatures_list)

####### More dynamic routes ########
# Define start route that accepts date as param which retrieves min, max, and avg for dates after param entered
@app.route("/api/v1.0/start/<start_date>")
def start(start_date):
    # Start engine to enable query
    session = Session(engine)

    # Convert start_time from string to date
    start_date = dt.date.fromisoformat(start_date)
    

    # Query for min, max, avg temperatures for all dates after date of interest
    query = session.query(func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)).filter(Measurement.date >= start_date)

    session.close()
    # Assign variables for min, max, and avg results to display in API
    for row in query:
        results = {}
        TMIN, TMAX, TAVG = row
        results["TMIN"] = TMIN
        results["TMAX"] = TMAX
        results["TAVG"] = TAVG

    return jsonify(results)
    

# Define start to end route that accepts start and end dates as params
@app.route("/api/v1.0/dates/<start_date>/<end_date>")
def range_summary(start_date, end_date):
    session = Session(engine)

    # Convert start_date and end_date from string to date
    start_date = dt.date.fromisoformat(start_date)
    end_date = dt.date.fromisoformat(end_date)

    # Query for min, max, and avg temps observed between dates entered
    query = session.query(func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)).filter(Measurement.date >= start_date).\
        filter(Measurement.date <= end_date)
    
    session.close()

    # Assign variables for min, max, and avg results to display in API
    for row in query:
        results = {}
        TMIN, TMAX, TAVG = row
        results["TMIN"] = TMIN
        results["TMAX"] = TMAX
        results["TAVG"] = TAVG

    return jsonify(results)


if __name__ == '__main__':
    app.run(debug=True)
