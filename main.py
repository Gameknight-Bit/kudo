# Imports #
# if imports do not work try cmd 'pip install -r requirements.txt' #
from flask import Flask, render_template, redirect, url_for, request, session
import re
import time

#File Imports#
import DatastoreService
from kudos import User

########### Constants ############
MAX_USERNAME_LEN = 70 #Usernames cannot be over 70 characters long
MAX_USERID_LEN = 20 #Usernames cannot be over 20 characters long

SESSION_TIMEOUT = 1*3600 #Number of hours *3600

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
#   "Claimed": False
#   "Verified": False
#   "VerificationReq": False
#   "Password": encryptedPass #Encrypted with SHA-256 and salted vals
#   "Misc": {}
# }

emailRegex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'

app = Flask(__name__, static_url_path="/static") #Default behavior :)
app.secret_key = 'reallysecretkeysmile'

@app.route("/") #Homepage
def home():
    return render_template("home.html")

@app.route("/api/register/", methods=["GET", "POST"]) #Register Account
def register():
    message = '' #output message

    if request.method == 'POST' and 'userid' in request.form and 'username' in request.form and 'password' in request.form and 'email' in request.form and 'passwordCheck' in request.form:
        userid = request.form['userid'].encode('utf8').decode('utf8')
        username = request.form['username'].encode('utf8').decode('utf8')
        password = request.form['password'].encode('utf8').decode('utf8')
        passwordCheck = request.form['passwordCheck'].encode('utf8').decode('utf8')
        email = request.form['email'].encode('utf8').decode('utf8')

        if not re.fullmatch(emailRegex, email):
            message = "Invalid email address!"
        elif passwordCheck != password:
            message = "The 2 passwords do not match!"
        elif not userid.isascii() or not password.isascii():
            message = "Characters for userid and password must be valid ascii!"
        elif not userid or not password or not email:
            message = 'Please fill out the form!'
        elif len(userid) > MAX_USERID_LEN:
            message = 'UserId characters need to be less than '+str(MAX_USERID_LEN)+'!'
        elif len(username) > MAX_USERNAME_LEN:
            message = 'Username chracters need to be less than '+str(MAX_USERNAME_LEN)+'!'
        else:
            if users.CheckAsync(userid):
                acc = User.fromDict(users.GetAsync(userid))
                if acc.Claimed == True:
                    message = "Account already exists!"
                elif acc.Email != email:
                    message = "Email does not match with linking account!"
                else:
                    message = "Sending confirmation email to '"+email+"'. <br>Please check your <b>email</b> and type the numbers sent below..."
                    #is claiming account to be theirs
                    #need confirmation from e-mail
                    # VERIFIES ACCOUNT AUTOMATICALLY (Can start sending kudos automatically) #
                    
            else:
                #New UNVERIFIED ACCOUNT# (Limits: cannot post pfp, cannot send kudos, cannot be placed on leaderboards)
                #Needs to send verification request#
                acc = User(userid, username, email, password)
                acc.setAttributes({"Misc": {"CreationDate": int(time.time())}})
                users.SetAsync(userid, acc.toDict())
    elif request.method == "POST":
        message = "Please fill out the form!"

    return render_template('register.html', msg=message)

@app.route("/api/confirmation/", methods=["GET", "POST"])
def confirm(): #Confirmation code enter
    message = ""
    if request.method == 'POST' and 'numbers1' in request.form:
        numbers = [request.form['numbers1'], request.form['numbers2'], request.form['numbers3'], request.form['numbers4'], request.form['numbers5'], request.form['numbers6']]

@app.route("/api/login/", methods=["GET", "POST"]) #Login
def login():
    message = ''
    print(request.form)
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        username = request.form['username']
        password = request.form['password']

        if username == "" or password == "":
            message = "Please fill out the form!"
            return render_template('login.html', msg=message)

        acc = None

        if users.CheckAsync(username):
            acc = User.fromDict(users.GetAsync(username))
        else:
            for x in users.GetAsDict().values():
                if x['UserId'] == username or x["Username"] == username or x["Email"] == username:
                    acc = User.fromDict(x)
                    break
            
        if acc == None:
            message = "Incorrect username"
        else:
            if acc.checkPass(password):
                session['loggedin'] = True
                session['id'] = acc.UserId
                session['username'] = acc.Username
                session['lastupdate'] = int(time.time())
                return redirect(url_for('home'))
            else:
                message = "Incorrect password or username"
    elif request.method == "POST":
        message = "Please fill out the form!"

    print(message)
    return render_template('login.html', msg=message)

@app.route("/api/logout/")
def logout():
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('username', None)
    session.pop('lastupdate', None)

    return redirect(url_for('login'))

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True) #change when deploying :)!