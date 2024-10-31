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
        json.dump({"movies": movies}, jsf, indent=4)

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
    return make_response("<h1 style='color:blue'>Welcome to the Movie service!</h1>",200)

# get all movies in json format
@app.route("/json", methods=["GET"])
def get_json():
    return make_response(movies, 200)

# get the movie by id
@app.route("/movies/<string:movieid>", methods=["GET"])
def get_movie_byid(movieid):

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

    # check if the movie already exists
    exist = movie_exist(movieid)

    # if the movie already exists, we will return a 409 error
    if exist:
        return make_response("An existing item already exists", 409)

    # if the movie does not exist, we will add the movie to the list
    else:
        movies.append(request.get_json()) # add the movie to the list
        save_movies(movies) # save the movies to the json file
        return make_response("Movie created", 200)

# delete a movie
@app.route("/movies/<string:movieid>", methods=["DELETE"])
def del_movie(movieid):
    global movies # use the global movies list

    # check if the movie already exists
    exist = movie_exist(movieid)

    # if the movie exists, we will delete the movie
    movies = [movie for movie in movies if movie["id"] != movieid]

    # save the movies to the json file and return a 200 response if the movie was deleted
    if exist:
        save_movies(movies)
        return make_response("Item deleted", 200)

    # if the movie does not exist, we will return a 400 error
    else:
        return make_response("ID not found", 400)

if __name__ == "__main__":
    #p = sys.argv[1]
    print("Server running in port %s"%(PORT))
    app.run(host=HOST, port=PORT)
