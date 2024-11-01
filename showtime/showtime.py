from flask import Flask, render_template, request, jsonify, make_response
import json
from werkzeug.exceptions import NotFound

app = Flask(__name__)

PORT = 3202
HOST = '0.0.0.0'

# Load the schedule from the json file
def load_schedule():
   with open('{}/databases/times.json'.format("."), 'r') as jsf:
      return json.load(jsf)["schedule"]

# Save the schedule to the json file
def save_schedule(schedule_list):
   with open('{}/databases/times.json'.format("."), 'w') as jsf:
      json.dump({"schedule": schedule_list}, jsf, indent=4)

# Load the times
schedules = load_schedule()

@app.route("/", methods=['GET'])
def home():
   return "<h1 style='color:blue'>Welcome to the Showtime service!</h1>"

@app.route("/showtimes", methods=["GET"])
def get_schedule():
   """Return all the the schedules in json"""
   return make_response(schedules, 200)

@app.route("/showmovies/<string:date>")
def get_movies_bydate(date):
   """Return the movie by date"""

   # we will loop through the schedules list
   for schedule in schedules:

      # if the schedule date is found, we will return the schedule
      if schedule["date"] == date:
         return make_response(jsonify(schedule), 200)

   # if the schedule date is not found, we will return a 400 error
   return make_response("Bad input parameter", 400)

if __name__ == "__main__":
   print("Server running in port %s"%(PORT))
   app.run(host=HOST, port=PORT)
