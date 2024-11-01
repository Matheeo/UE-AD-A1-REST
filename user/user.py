from flask import Flask, render_template, request, jsonify, make_response
import requests
import json
from werkzeug.exceptions import NotFound

app = Flask(__name__)

PORT = 3203
HOST = '0.0.0.0'

booking_port = 3201
movie_port =
showtime_port =

# Load the users from the json file
def load_users():
   with open('{}/databases/users.json'.format("."), 'r') as jsf:
      return json.load(jsf)["users"]

# Save the users to the json file
def save_users(users_list):
   with open('{}/databases/users.json'.format("."), 'w') as jsf:
      json.dump({"movies": users_list}, jsf, indent=4)

users = load_users()

@app.route("/", methods=['GET'])
def home():
   return "<h1 style='color:blue'>Welcome to the User service!</h1>"


if __name__ == "__main__":
   print("Server running in port %s"%(PORT))
   app.run(host=HOST, port=PORT)
