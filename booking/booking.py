from flask import Flask, render_template, request, jsonify, make_response
import requests
import json
from werkzeug.exceptions import NotFound

app = Flask(__name__)

PORT = 3201
HOST = '0.0.0.0'

# Load the bookings from the json file
def load_bookings():
   with open('{}/databases/bookings.json'.format("."), 'r') as jsf:
      return json.load(jsf)["bookings"]

# Save the bookings to the json file
def save_bookings(bookings_list):
   with open('{}/databases/bookings.json'.format("."), 'w') as jsf:
      json.dump({"bookings": bookings}, jsf, indent=4)

# Load the movies
bookings = load_bookings()

@app.route("/", methods=['GET'])
def home():
   return "<h1 style='color:blue'>Welcome to the Booking service!</h1>"

@app.route("/bookings", methods=["GET"])
def get_json():
   """Return the json of all the bookings"""

   return make_response(jsonify(bookings), 200)

@app.route("/bookings/<string:userid>", methods=["GET"])
def get_booking_for_user(userid):
   """Return the booking of an user"""

   # iterate over the bookings
   for booking in bookings:

      # if the userid is the same as the one in the url
      if booking["userid"] == userid:
         make_response(booking, 200)

   return make_response("Bad input parameter", 400)

@app.route("/bookings/<string:userid>", methods=["POST"])
def add_booking_byuser(userid):
   """Add the booking for the user with the user id in url"""

   # check if the userid already exist
   userid_exist = False
   for booking in bookings:
      if booking["userid"] == userid:
         userid_exist = True

   # if the userid does not exit we create it
   if not userid_exist:
      bookings.append({"userid": userid, "dates": [{"date": request.get_json()["date"], "movies": [request.get_json()["movieid"]]}]})
      save_bookings(bookings)
      return make_response(bookings, 200)

   # if the user id is already in the json
   else:
      movie_exist_in_date = False
      date_exist = False

      # we grab the user booking
      for user_bookings in bookings:
         if user_bookings["userid"] == userid:

            # we iterate over the user booking
            for date in user_bookings["dates"]:

               # check if the date matches the one in the request body
               if date["date"] == request.get_json()["date"]:
                  date_exist = True

                  # if it's the same date, we iterate over the movies of the date
                  for movie in date["movies"]:

                     # if the movie is on the same date as in the request
                     if movie == request.get_json()["movieid"]:
                        movie_exist_in_date = True

                  # if the movie id is not in the date we add the movieid
                  if not movie_exist_in_date:
                     date["movies"].append(request.get_json()["movieid"])
                     save_bookings(bookings)
                     return make_response(bookings, 200)

            # if the date does not exist
            if not date_exist:
               user_bookings["dates"].append({"date": request.get_json()["date"], "movies": [request.get_json()["movieid"]]})
               save_bookings(bookings)
               return make_response(bookings, 200)

      # if we not already return the method we return with 409 arror
      return make_response("An existing item already exists", 409)

if __name__ == "__main__":
   print("Server running in port %s"%(PORT))
   app.run(host=HOST, port=PORT)
