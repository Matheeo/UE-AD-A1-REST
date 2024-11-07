from flask import Flask, render_template, request, jsonify, make_response
import requests
import json
from werkzeug.exceptions import NotFound

app = Flask(__name__)

PORT = 3201
HOST = '0.0.0.0'

showtime_ws = "http://localhost:3202"


# Load the bookings from the json file
def load_bookings():
    with open('{}/databases/bookings.json'.format("."), 'r') as jsf:
        return json.load(jsf)["bookings"]


# Save the bookings to the json file
def save_bookings(bookings_list):
    with open('{}/databases/bookings.json'.format("."), 'w') as jsf:
        json.dump({"bookings": bookings_list}, jsf, indent=4)

    # load the bookings
    global bookings
    bookings = load_bookings()



def movie_available(date, movieid):
    """Check if the movie is available at the date"""

    # request the showtime service for the movies of the date
    response = requests.get(showtime_ws + "/showmovies/" + date)

    # if the response is 200 and the movies are not empty
    if response.status_code == 200 and response.json()["movies"]:

        # iterate over all the movies
        for movie in response.json()["movies"]:

            # if the movie is the same as the one in the request
            if movie == movieid:

                # return True if the movie is available
                return True

    # return False if the movie is not available
    return False

# Load the movies
bookings = load_bookings()


@app.route("/", methods=['GET'])
def home():
    """Return the home page"""
    return "<h1 style='color:blue'>Welcome to the Booking service!</h1>"


@app.route("/bookings", methods=["GET"])
def get_json():
    """Return the bookings in json format"""

    return make_response(jsonify(bookings), 200)


@app.route("/bookings/<string:userid>", methods=["GET"])
def get_booking_for_user(userid):
    """Return the booking for the user with the user id in url"""

    # iterate over the bookings
    for booking in bookings:

        # if the user id is the same as the one in the request
        if booking["userid"] == userid:

            # return the booking
            return make_response(booking, 200)

    # if the user id is not found return 404
    return make_response("Bad input parameter", 400)


@app.route("/bookings/<string:userid>", methods=["POST"])
def add_booking_byuser(userid):
    """Add the booking for the user with the user id in url"""

    data = request.get_json()
    date = data["date"]
    movieid = data["movieid"]

    # Check if the user already has a booking
    existing_user_bookings = next((booking for booking in bookings if booking["userid"] == userid), None)

    # if the user has no booking yet
    if not existing_user_bookings:

        # check if the movie is available
        if movie_available(date, movieid):

            # create a new booking for the user
            new_booking = {"userid": userid, "dates": [{"date": date, "movies": [movieid]}]}

            # add the booking to the bookings list
            bookings.append(new_booking)

            # save the bookings
            save_bookings(bookings)

            # return the new booking
            return make_response(new_booking, 200)

        # if the movie is not available return 409
        else:
            return make_response("Booking not possible", 409)

    # if the user already has a booking
    else:

        # iterate over the dates of the user
        for date_entry in existing_user_bookings["dates"]:

            # if the date is the same as the one in the request
            if date_entry["date"] == date:

                # if the movie is already in the booking return 409
                if movieid in date_entry["movies"]:
                    return make_response("An existing item already exists", 409)

                # if the movie is available add it to the booking
                if movie_available(date, movieid):

                    # add the movie to the booking
                    date_entry["movies"].append(movieid)

                    # save the bookings
                    save_bookings(bookings)

                    # return the booking
                    return make_response(existing_user_bookings, 200)

                # if the movie is not available return 409
                else:
                    return make_response("Booking not possible", 409)

        # if the date is not in the booking and the movie is available
        if movie_available(date, movieid):

            # add the date and the movie to the booking
            existing_user_bookings["dates"].append({"date": date, "movies": [movieid]})

            # save the bookings
            save_bookings(bookings)

            # return the booking
            return make_response(existing_user_bookings, 200)

        # if the movie is not available return 409
        else:
            return make_response("Booking not possible", 409)


if __name__ == "__main__":
    print("Server running in port %s" % (PORT))
    app.run(host=HOST, port=PORT)
