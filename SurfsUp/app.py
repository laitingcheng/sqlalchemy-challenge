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

# Save reference to the table

Measurement = Base.classes.measurement
Station = Base.classes.station

#################################################
# Flask Setup
#################################################
app = Flask(__name__)

#################################################
# Flask Routes
#################################################

@app.route("/")
def home():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"- Query precipitation data for the last year<br/>"
        f"<br/>"
        f"/api/v1.0/stations<br/>"
        f"- List of weather stations from the dataset<br/>"
        f"<br/>"
        f"/api/v1.0/tobs<br/>"
        f"- Query the dates and temperature observations of the most active station for the last year of data<br/>"
        f"<br/>"
        f"/api/v1.0/start_date<br/>"
        f"- Returns the minimum, average, and maximum temperature for all dates greater than and equal to the start date<br/>"
        f"<br/>"
        f"/api/v1.0/start_date/end_date<br/>"
        f"- Returns the minimum, average, and maximum temperature for dates between the start and end date inclusive<br/>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    """Query precipitation data for the last year"""
    session = Session(engine)
    # Calculate the date 1 year ago from the last data point in the database
    last_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()[0]
    year_ago_date = str(eval(last_date[:4]) - 1) + last_date[4:]

    # Perform a query to retrieve the data and precipitation scores
    results = session.query(Measurement.date, Measurement.prcp).\
        filter(Measurement.date >= year_ago_date).\
        order_by(Measurement.date).all()

    session.close()

    # Create a dictionary from the row data and append to a list of all_dates
    all_dates = []
    for date, prcp in results:
        date_dict = {}
        date_dict[date] = prcp
        all_dates.append(date_dict)

    return jsonify(all_dates)

@app.route("/api/v1.0/stations")
def stations():
    """Return a JSON list of stations from the dataset"""
    session = Session(engine)
    results = session.query(Station.station, Station.name).all()
    session.close()

    # Create a dictionary from the row data and append to a list of all_stations
    all_stations = []
    for station, name in results:
        station_dict = {}
        station_dict["Station"] = station
        station_dict["Name"] = name
        all_stations.append(station_dict)

    return jsonify(all_stations)

@app.route("/api/v1.0/tobs")
def tobs():
    """Query the dates and temperature observations of the most active station for the last year of data"""
    session = Session(engine)
    
    # Query the most active station
    most_active_station = session.query(Measurement.station)\
        .group_by(Measurement.station)\
        .order_by(func.count().desc())\
        .first()[0]
    
    # Calculate the date one year from the last date in data set.
    last_date = session.query(Measurement.date)\
        .order_by(Measurement.date.desc())\
        .first()[0]
    
    one_year_ago = dt.datetime.strptime(last_date, '%Y-%m-%d') - dt.timedelta(days=365)
    
    # Query the last 12 months of temperature observation data for this station
    results = session.query(Measurement.date, Measurement.tobs)\
        .filter(Measurement.date >= one_year_ago)\
        .filter(Measurement.station == most_active_station)\
        .all()
    
    session.close()
    
    # Convert the query results to a dictionary using date as the key and temperature as the value
    tobs_data = {}
    for date, tobs in results:
        tobs_data[date] = tobs
    
    return jsonify(tobs_data)

@app.route("/api/v1.0/<start>")
def calc_temps_start(start):
    """Return a JSON list of the minimum, average, and maximum temperatures 
    for all dates greater than or equal to the start date.
    """
    session = Session(engine)

    # Query the minimum, average, and maximum temperatures for all dates greater
    # than or equal to the start date
    sel = [func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]
    results = session.query(*sel).filter(Measurement.date >= start).all()

    session.close()

    # Convert the results to a dictionary
    temps = list(np.ravel(results))
    temp_dict = {"TMIN": temps[0], "TAVG": temps[1], "TMAX": temps[2]}

    # Return the JSON representation of the dictionary
    return jsonify(temp_dict)


@app.route("/api/v1.0/<start>/<end>")
def calc_temps_start_end(start, end):
    """Return a JSON list of the minimum, average, and maximum temperatures
    for the dates from the start date to the end date, inclusive.
    """
    session = Session(engine)

    # Query the minimum, average, and maximum temperatures for dates between
    # the start and end dates, inclusive
    sel = [func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]
    results = session.query(*sel).filter(Measurement.date >= start).filter(Measurement.date <= end).all()

    session.close()

    # Convert the results to a dictionary
    temps = list(np.ravel(results))
    temp_dict = {"TMIN": temps[0], "TAVG": temps[1], "TMAX": temps[2]}

    # Return the JSON representation of the dictionary
    return jsonify(temp_dict)



if __name__ == '__main__':
    app.run(debug=True)




