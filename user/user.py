from datetime import datetime

from flask import Flask, jsonify, make_response
import requests
import json

app = Flask(__name__)

PORT = 3203
HOST = '0.0.0.0'

booking_ws = "http://localhost:3201"
movie_ws = "http://localhost:3200"


# Load the users from the json file
def load_users():
    with open('{}/databases/users.json'.format("."), 'r') as jsf:
        return json.load(jsf)["users"]


# Save the users to the json file
def save_users(users_list):
    with open('{}/databases/users.json'.format("."), 'w') as jsf:
        json.dump({"movies": users_list}, jsf, indent=4)

    global users
    users = users_list

# Check if the user exist in the database
def user_exist(userid):
    exist = False
    for user in users:
        if user["id"] == userid:
            exist = True
    return exist

users = load_users()

@app.route("/", methods=['GET'])
def home():
    """Return the home page of the user service"""

    return "<h1 style='color:blue'>Welcome to the User service!</h1>"

@app.route("/users/<string:userid>/movies/watched-count", methods=["GET"])
def get_user_watchedcount(userid):
    """Return the number of movie booking booking the today date"""

    today = datetime.today().strftime('%Y%m%d')
    counter = 0

    # check to be sure the user is in the database
    if user_exist(userid):

        # request to get the user bookings
        response = requests.get(booking_ws + "/bookings/" + userid)

        # if the request has no problems and the dates list exist in json response
        if response.status_code == 200 and response.json()["dates"]:

            # iterate over all the booking dates
            for date in response.json()["dates"]:

                # if the date is before the today date
                if date["date"] < today:

                    # we iterate over the movies of the date and add 1 each times
                    for movie in date["movies"]:
                        counter += 1

        return make_response(jsonify({"watched-count": counter}), 200)
    return make_response("User not found", 404)


@app.route("/users/<string:userid>/movies/titles", methods=["GET"])
def get_booked_movie_titles(userid):
    """Return all the title of the movies in user booking"""

    titles = []

    # check to be sure the user is in the database
    if user_exist(userid):

        # request to get the user bookings
        response_booking = requests.get(booking_ws + "/bookings/" + userid)

        # if the request has no problems and the dates list exist in json response
        if response_booking.status_code == 200 and response_booking.json()["dates"]:

            # iterate over all the booking dates
            for date in response_booking.json()["dates"]:

                # we iterate over the movies of the date and add 1 each times
                for movie in date["movies"]:

                    # get the movie object
                    response_movie = requests.get(movie_ws + "/movies/" + movie)

                    # check if we get response
                    if response_movie.status_code == 200 and response_movie.json()["title"]:

                        # check if the title is not already in the movie list
                        if not response_movie.json()["title"] in titles:
                            # add title to the list
                            titles.append(response_movie.json()["title"])

            return make_response(jsonify({"titles": titles}), 200)
    return make_response("User ID not found")

if __name__ == "__main__":
    print("Server running in port %s" % (PORT))
    app.run(host=HOST, port=PORT)
