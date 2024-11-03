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

def movie_exist(movieid):
    exist = False
    for movie in movies:
        if movie["id"] == movieid:
            exist = True
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

    # if the movie does not exist, we will add the movie to the list
    else:
        movies.append(request.get_json()) # add the movie to the list
        save_movies(movies) # save the movies to the json file
        return make_response(request.get_json(), 200)

# delete a movie
@app.route("/movies/<string:movieid>", methods=["DELETE"])
def del_movie(movieid):
    """Delete a movies"""

    global movies # use the global movies list

    # check if the movie already exists
    exist = movie_exist(movieid)

    # save the movies to the json file and return a 200 response if the movie was deleted
    if exist:

        # if the movie exists, we will delete the movie
        movies = [movie for movie in movies if movie["id"] != movieid]

        # we save the new movies list
        save_movies(movies)
        return make_response("Item deleted", 200)

    # if the movie does not exist, we will return a 400 error
    else:
        return make_response("ID not found", 400)

@app.route("/movies/<string:movieid>/<int:rate>", methods=["PUT"])
def update_movie_rating(movieid, rate):
    """Update movie rate by its id"""

    # Demander a la prof si on peux renvoyer une autre erreur pour note invalide
    if (rate < 0 or rate > 10) or not isinstance(rate, int):
        return make_response("Rate invalid", 400)

    # check if the movie already exists
    exist = movie_exist(movieid)

    # if the movie does not exist, we will return a 400 error
    if not exist:
        return make_response("ID not found", 400)

    # if the movie exists, we will update the movie rate
    for movie in movies:
        if movie["id"] == movieid:
            movie["rate"] = rate

    # we save the new movies list
    save_movies(movies)
    return make_response("Rate updated", 200)

# get the movie by title
@app.route("/moviesbytitle", methods=["GET"])
def get_movie_bytitle():
    """Return one movie by its title"""

    # we will loop through the movies list
    for movie in movies:

        # if the movie title is found, we will return the movie
        if movie["title"] == request.args.get("title"):
            return make_response(jsonify(movie), 200)

    # if the movie id is not found, we will return a 400 error
    return make_response("Bad input parameter", 400)

# get all the movies over the minimal rate
@app.route("/movies/rating", methods=["GET"])
def get_movies_byminimalrate():
    """Return all the movie over the minimal rate"""

    movies_list = []

    # convert the rate to int, if that raise an Exception
    try:
        min_rating = int(request.args.get("min_rating"))
    except (TypeError, ValueError):
        return make_response("Rate invalid", 400)

    # if the rating is valid
    if min_rating >= 0 or min_rating <= 10:

        # we will loop through the movies list
        for movie in movies:

            # if the movie title is found, we will return the movie
            if movie["rating"] >= min_rating:
                movies_list.append(movie)

        return make_response(jsonify(movies_list), 200)
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
