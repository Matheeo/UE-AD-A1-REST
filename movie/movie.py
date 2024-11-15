from flask import Flask, render_template, request, jsonify, make_response
import json
import sys
from werkzeug.exceptions import NotFound

app = Flask(__name__)

PORT = 3200
HOST = '0.0.0.0'

# Load the movies from the json file
def load_movies():
    with open('{}/databases/movies.json'.format("."), 'r') as jsf:
        return json.load(jsf)["movies"]

# Save the movies to the json file
def save_movies(movies_list):
    with open('{}/databases/movies.json'.format("."), 'w') as jsf:
        json.dump({"movies": movies_list}, jsf, indent=4)

    # Load the movies
    global movies
    movies = load_movies()

# Check if the movie exist
def movie_exist(movieid):
    exist = False

    # Iterate over the movies list
    for movie in movies:

        # if the movie id is found we set exist to True
        if movie["id"] == movieid:
            exist = True

    # return the exist value
    return exist

# Load the movies
movies = load_movies()

# root message
@app.route("/", methods=['GET'])
def home():
    """Return the home page of movies api"""
    return make_response("<h1 style='color:blue'>Welcome to the Movie service!</h1>",200)

# get all movies in json format
@app.route("/json", methods=["GET"])
def get_json():
    """Return all the the movies in json"""
    return make_response(movies, 200)

# get the movie by id
@app.route("/movies/<string:movieid>", methods=["GET"])
def get_movie_byid(movieid):
    """Return the movie by id"""

    # we will loop through the movies list
    for movie in movies:

        # if the movie id is found, we will return the movie
        if movie["id"] == movieid:
            return make_response(jsonify(movie), 200)

    # if the movie id is not found, we will return a 400 error
    return make_response("Bad input parameter", 400)

# add a new movie
@app.route("/movies/<string:movieid>", methods=["POST"])
def create_movie(movieid):
    """Add movies"""

    # check if the movie already exists
    exist = movie_exist(movieid)

    # if the movie already exists, we will return a 409 error
    if exist:
        return make_response("An existing item already exists", 409)

    # if the movie does not exist
    else:

        # we will add the movie to the movies list
        movies.append(request.get_json())

        # we save the new movies list
        save_movies(movies)

        # we return the movie added
        for movie in movies:
            if movie["id"] == movieid:
                return make_response(jsonify(movie), 200)

# delete a movie
@app.route("/movies/<string:movieid>", methods=["DELETE"])
def del_movie(movieid):
    """Delete a movies"""

    # use the global movies variable
    global movies

    # check if the movie already exists
    exist = movie_exist(movieid)

    # if the movies exists
    if exist:

        # we iterate over the movies list and remove the movie with the id of the movieid parameter
        movies = [movie for movie in movies if movie["id"] != movieid]

        # we save the new movies list
        save_movies(movies)
        return make_response("Item deleted", 200)

    # if the movie does not exist, we will return a 400 error
    else:
        return make_response("ID not found", 400)

@app.route("/movies/<string:movieid>/<float:rate>", methods=["PUT"])
def update_movie_rating(movieid, rate):
    """Update movie rate by its id"""

    # check if the rate is valid
    if rate < 0 or rate > 10:
        return make_response("Rate invalid", 400)

    # check if the movie already exists
    exist = movie_exist(movieid)

    # if the movie does not exist, we will return a 400 error
    if not exist:
        return make_response("ID not found", 400)

    # iterate over the movies list
    for movie in movies:

        # if the movie id is found
        if movie["id"] == movieid:

            # we update the movie rate
            movie["rating"] = rate

    # we save the new movies list
    save_movies(movies)
    return make_response("Rate updated", 200)

# get the movie by title
@app.route("/moviesbytitle", methods=["GET"])
def get_movie_bytitle():
    """Return one movie by its title"""

    # iterate over the movies list
    for movie in movies:

        # if the movie title is found
        if movie["title"] == request.args.get("title"):

            # we return the movie
            return make_response(jsonify(movie), 200)

    # if the movie id is not found, we will return a 400 error
    return make_response("Bad input parameter", 400)

# get all the movies over the minimal rate
@app.route("/movies/rating", methods=["GET"])
def get_movies_byminimalrate():
    """Return all the movie over the minimal rate"""

    movies_list = []

    # get the rate param in url
    min_rating = float(request.args.get("rate"))

    # if the rating is valid
    if min_rating >= 0 or min_rating <= 10:

        # we will loop through the movies list
        for movie in movies:

            # if the movie title is found, we will return the movie
            if movie["rating"] >= min_rating:
                movies_list.append(movie)

        return make_response(jsonify(movies_list), 200)

    # if the rate is invalid, we will return a 400 error
    return make_response("Rate invalid", 400)

# get all the movie by its director
@app.route("/movies/director", methods=["GET"])
def get_movies_bydirector():
    """Return all the movie by director"""

    movies_list = []

    # get the director param in url
    director = str(request.args.get("director"))

    # we will loop through the movies list
    for movie in movies:

        # if the movie director is the same, we add the movie in the list
        if movie["director"] == director:
            movies_list.append(movie)

    # if the movie list is empty, that means the director is not found
    if len(movies_list) == 0:
        return make_response("Director not found", 400)

    # else we return the list of movies
    else:
        return make_response(jsonify(movies_list), 200)

# get all the api endpoint
@app.route("/help", methods=["GET"])
def help():
    """Return all the endpoints of the api"""

    endpoints = []

    # iterate over each endpoint
    for rule in app.url_map.iter_rules():

        # if is not the static endpoint
        if "static" not in rule.endpoint:

            # we grab the route and the detail and add it into the list
            view_func = app.view_functions[rule.endpoint]
            doc = view_func.__doc__ or "No description available"
            endpoints.append({"route": str(rule), "detail": doc})

    return make_response(jsonify({"available_endpoints": endpoints}), 200)

if __name__ == "__main__":
    #p = sys.argv[1]
    print("Server running in port %s"%(PORT))
    app.run(host=HOST, port=PORT)
