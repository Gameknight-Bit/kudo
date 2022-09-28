# Imports #
# if imports do not work try cmd 'pip install -r requirements.txt' #
from flask import Flask, render_template, redirect, url_for, request, session

#File Imports#
import DatastoreService

##################################

# Init #
users = DatastoreService.GetDatastore("Users")
# Datastore Key:
# UserId: {
#   "UserId": UserId,
#   "Username": Username,
#   "Email": Email,
#   "SocialLinks": {"Twitter": Twitter, "Reddit": Reddit, "ex": exampleLink},
#   "Kudos": {KudoObj, KudoObj}, #(Must convert dict into obj using kudos.py)
#   "Score": ScoreNum,
#   "LastKudos": {NumKudos, }##############################################################
#   "Classes": {"1": ClassObj}, #(Must convert dict into obj using kudos.py)
#   "Password": encryptedPass #Encrypted with SHA-256 and salted vals
# }

app = Flask(__name__, static_url_path="/static") #Default behavior :)

@app.route("/") #Homepage
def home():
    return render_template("home.html")