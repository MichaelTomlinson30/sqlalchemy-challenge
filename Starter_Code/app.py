# Import the dependencies.
from flask import Flask, jsonify
from sqlalchemy import create_engine, func
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from datetime import datetime, timedelta


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")  


# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(engine, reflect=True)


# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

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
    """Homepage - List all available routes."""
    return (
        f"Welcome to my Climate Assignment!<br/>"
        f"Available Routes:<br/>"
        f"<a href='/api/v1.0/precipitation'>/api/v1.0/precipitation</a><br/>"
        f"<a href='/api/v1.0/stations'>/api/v1.0/stations</a><br/>"
        f"<a href='/api/v1.0/tobs'>/api/v1.0/tobs</a><br/>"
        f"/api/v1.0/&lt;start&gt;<br/>"
        f"/api/v1.0/&lt;start&gt;/&lt;end&gt;"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    """Return the last 12 months of precipitation data."""
    
    last_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()[0]
    last_date = datetime.strptime(last_date, "%Y-%m-%d")
    one_year_ago = last_date - timedelta(days=365)

    results = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= one_year_ago).all()

    precipitation_data = {date: prcp for date, prcp in results}

    return jsonify(precipitation_data)

@app.route("/api/v1.0/stations")
def stations():
    """Return a list of stations from the dataset."""
    results = session.query(Station.station).all()

    station_list = [station[0] for station in results]

    return jsonify(station_list)

@app.route("/api/v1.0/tobs")
def tobs():
    """Return temperature observations for the most-active station in the last 12 months."""
    
    most_active_station = session.query(Measurement.station, func.count(Measurement.station)).\
        group_by(Measurement.station).order_by(func.count(Measurement.station).desc()).first()[0]

    last_date = session.query(Measurement.date).filter(Measurement.station == most_active_station).\
        order_by(Measurement.date.desc()).first()[0]
    last_date = datetime.strptime(last_date, "%Y-%m-%d")
    one_year_ago = last_date - timedelta(days=365)

    results = session.query(Measurement.date, Measurement.tobs).\
        filter(Measurement.station == most_active_station, Measurement.date >= one_year_ago).all()

    tobs_data = {date: tobs for date, tobs in results}

    return jsonify(tobs_data)

@app.route("/api/v1.0/<start>")
def temperature_start(start):
    """Return TEMPMIN, TEMPAVG, and TEMPMAX for all dates greater than or equal to the start date."""
    
    results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).all()

    temperature_data = {
        'min_temperature': results[0][0],
        'avg_temperature': results[0][1],
        'max_temperature': results[0][2]
    }

    return jsonify(temperature_data)

@app.route("/api/v1.0/<start>/<end>")
def temperature_range(start, end):
    """Return TEMPMIN, TEMPAVG, and TEMPMAX for the specified start and end date range."""
    
    results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start, Measurement.date <= end).all()

    temperature_data = {
        'min_temperature': results[0][0],
        'avg_temperature': results[0][1],
        'max_temperature': results[0][2]
    }

    return jsonify(temperature_data)


if __name__ == "__main__":
    app.run(debug=True)
