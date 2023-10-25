from flask import Flask, render_template, redirect, request, jsonify
from datetime import datetime
import re
from cs50 import SQL

app = Flask(__name__)

db = SQL("sqlite:///locations.db")

@app.route('/', methods=["GET"])
def main():
    return render_template("main.html")

@app.route('/about', methods=["GET"])
def about():
   return render_template("about.html")

@app.route('/report', methods=["GET"])
def report():
  #get form data
  damageType = request.args.get("damageType")
  picture = request.args.get("picture")
  location = request.args.get("location")

  # if all fields are filled in
  if damageType and location:

    # if damageType is valid
    if damageType not in ["Pothole", "Sidewalk Damage", "Faulty Traffic Light", "Damaged/Vandalised Signs", "Streetlight Failure", "Street Drainage Problem", "Fallen Trees/Branches"]:
      return redirect("/")

    # checks if the location string is a valid lat, long coordinate
    valid_address = True
    valid = location.split()

    coordFormatMatch = re.search("[-]?[0-9]+[.][0-9]{6}[0-9]* [-]?[0-9]+[.][0-9]{6}[0-9]*", location)
    if not coordFormatMatch:
      # no matches
      valid_address = False
    elif coordFormatMatch.span()[1] != len(location):
      # extra characters
      valid_address = False
    elif abs(float(valid[0])) >  90 or abs(float(valid[1])) > 180:
      #invalid coordinates
      valid_address = False

    # if not valid coordinates, don't add record
    if valid_address:
        # get time
        time = datetime.now()
        time = time.strftime("%Y-%m-%d %H:%M:%S")
        # add new damage record to sql database
        db.execute("INSERT INTO locations (damagetype, latitude, longitude, timereported, validity_points, sent_yet) VALUES (?, ?, ?, ?, ?, ?);", damageType, valid[0], valid[1], time, 1, False)

  return redirect("/")

@app.route("/getMarkers", methods=["GET"])
def getMarkers():
    # get bounds form data
    neLat = request.args.get("neLat")
    neLng = request.args.get("neLng")

    swLat = request.args.get("swLat")
    swLng = request.args.get("swLng")

    # make sure all data arrived
    if neLat and neLng and swLat and swLng:
        # get all potholes in bounds
        locations = db.execute("SELECT damagetype, validity_points, sent_yet, latitude, longitude FROM locations WHERE (latitude BETWEEN ? AND ?) AND (longitude BETWEEN ? AND ?)", swLat, neLat, swLng, neLng)

        # save the stuff in format below
        data = {
            "locations" : locations
        }

        return jsonify(data)
    else:
        return jsonify({"message": "missing bounds"})

@app.route("/confirm", methods=["GET"])
def confirm():
  # get user info
  damagetype = request.args.get("damagetype")
  latitude = request.args.get("latitude")
  longitude = request.args.get("longitude")
  status = request.args.get("status")

  if status == "True":
    status = 1
  elif status == "False":
    status = -1
  else:
    return "invalid status"

  # update that record
  db.execute("UPDATE locations SET validity_points = validity_points + ? WHERE damagetype = ? AND latitude = ? AND longitude = ? AND validity_points < 15", status, damagetype, latitude, longitude)

  return "completed"