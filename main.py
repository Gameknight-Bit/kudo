# Imports #
# if imports do not work try cmd 'pip install -r requirements.txt' #

from flask import Flask, render_template, redirect, url_for, request, session
import re
import time

#File Imports#
from kudos import User
import kudos

import datetime

import leaderboard

########### Constants ############
MAX_USERNAME_LEN = 70 #Usernames cannot be over 70 characters long
MAX_USERID_LEN = 20 #Usernames cannot be over 20 characters long

SESSION_TIMEOUT = 1*3600 #Number of hours *3600

##################################

# Init #
#users = DatastoreService.GetDatastore("Users")
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
    if 'loggedin' in session and session['loggedin'] == True:
        return redirect(url_for('home'))

    message = '' #output message

    if request.method == 'POST' and 'userid' in request.form and 'username' in request.form and 'password' in request.form and 'email' in request.form and 'passwordCheck' in request.form:
        userid = request.form['userid'].encode('utf8').decode('utf8')

        username = request.form['username'].encode('utf8').decode('utf8')
        if userid == "":
            userid = username.lower().replace(' ', '_')
        else:
            userid = userid.lower().replace(' ', '_')
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
            if len(kudos.getUsers("Both", id = userid)) != 0 :
                acc = kudos.getUsers("Both", id = userid)[0]
                if acc.Claimed == True:
                    message = "Account userid already exists!"
                elif acc.Email != email:
                    message = "Email does not match with linking account!"
                else:
                    message = "Sending confirmation email to '"+email+"'. Please check your email and type the numbers sent below..."
                    #is claiming account to be theirs
                    #need confirmation from e-mail
                    # VERIFIES ACCOUNT AUTOMATICALLY (Can start sending kudos automatically) #
                    
                    return redirect(url_for('confirm'))
            else:
                #New UNVERIFIED ACCOUNT# (Limits: cannot post pfp, cannot send kudos, cannot be placed on leaderboards)
                #Needs to send verification request#
                acc = kudos.initUser(userid, username, email, password, False, False)
                acc.setAttributes({"Claimed": True, "Misc": {"CreationDate": int(time.time())}})
                kudos.setUser("Claimed", acc)

                return redirect(url_for('login', msg="Account Sucessfully Created! Please Login...", err="False"))
    elif request.method == "POST":
        message = "Please fill out the form!"

    return render_template('register.html', msg=message)

@app.route("/api/confirmation/", methods=["GET", "POST"])
def confirm(): #Confirmation code enter
    if 'loggedin' in session and session['loggedin'] == True:
        return redirect(url_for('home'))
    message = ""
    if request.method == 'POST' and 'numbers1' in request.form:
        numbers = [request.form['numbers1'], request.form['numbers2'], request.form['numbers3'], request.form['numbers4'], request.form['numbers5'], request.form['numbers6']]

    return render_template('confirmation.html')

@app.route("/api/login/", methods=["GET", "POST"]) #Login
def login():
    if 'loggedin' in session and session['loggedin'] == True:
        return redirect(url_for('home'))

    message = request.args.get('msg') or ''
    err = request.args.get('err') or 'True'
    print(request.form)
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        username = request.form['username']
        password = request.form['password']

        if username == "" or password == "":
            message = "Please fill out the form!"
            return render_template('login.html', msg=message)

        acc = None

        if len(kudos.getUsers("Claimed", username=username)) != 0:
            acc = kudos.getUsers("Claimed", username=username)[0]
        else:
            acc = kudos.getUsers("Claimed", id=username, username=username, email=username)
            if len(acc) != 0:
                acc = acc[0]
            else:
                acc = None
            
        if acc == None:
            message = "Username does not exist..."
        else:
            if acc.checkPass(password):
                session['loggedin'] = True
                session['id'] = acc.UserId
                session['username'] = acc.Username
                session['lastupdate'] = int(time.time())
                session['pfpurl'] = url_for('static', filename='/img/profilePics/Default.png')
                if ("ProfilePicture" in acc.Misc) and (acc.Misc["ProfilePicture"] != "Default.png"):
                    session['pfpurl'] = acc.Misc["ProfilePicture"]

                if 'previousurl' in session:
                    if session['previousurl'] != "":
                        urlname = session['previousurl']
                        session.pop('previousurl')
                        return redirect(urlname)

                return redirect(url_for('home'))
            else:
                message = "Incorrect password or username"
    elif request.method == "POST":
        message = "Please fill out the form!"

    print(message)
    return render_template('login.html', msg=message, err=err)

@app.route("/api/logout/")
def logout():
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('username', None)
    session.pop('lastupdate', None)
    session.pop('pfpurl', None)

    return redirect(url_for('login'))

@app.route("/leaderboard")
def leaders():
    leaderboards = {}
    leaderboards["monthly"] = leaderboard.getTopPlayers(10, "Monthly")
    leaderboards["all-time"] = leaderboard.getTopPlayers(10, "All-Time")

    return render_template("leaderboard.html", boards=leaderboards)

@app.route("/user/<userId>")
def userPage(userId):
    users = kudos.getUsers("Both", id=userId)
    if len(users) > 0:
        users = users[0]
    else:
        users = ""
        return redirect(url_for("error", messages="User does not exist!", errorcode=404))

    pic = url_for('static', filename='/img/profilePics/Default.png')
    if ("ProfilePicture" in users.Misc) and (users.Misc["ProfilePicture"] != "Default.png"):
        pic = users.Misc["ProfilePicture"]

    if 'loggedin' in session and session['loggedin'] == True:
        loggedinuser = kudos.getUsers("Claimed", id=session['id'])[0]

        if 'success' in request.args:
            print(request.args["success"])
            return render_template("user.html", User=users, AbleToDonate=loggedinuser.giveStatus(), ProfilePic=pic, Success = str(request.args["success"]))
        else:
            return render_template("user.html", User=users, AbleToDonate=loggedinuser.giveStatus(), ProfilePic=pic)
    
    return render_template("user.html", User=users, AbleToDonate=False, ProfilePic=pic)

@app.route("/user/<userId>/edit", methods=["GET", "POST"])
def editPage(userId):
    users = kudos.getUsers("Claimed", id=userId)
    if len(users) > 0:
        users = users[0]
    else:
        users = ""
        return redirect(url_for("error", messages="User does not exist!", errorcode=404))

    #IMPLEMENT PICTURES SETTING AND ALSO SETTING OTHER SETTINGS!!!!

    pic = url_for('static', filename='/img/profilePics/Default.png')
    if ("ProfilePicture" in users.Misc) and (users.Misc["ProfilePicture"] != "Default.png"):
        pic = users.Misc["ProfilePicture"]

    if 'loggedin' in session and session['loggedin'] == True:
        if userId == session['id']:
            return render_template("edit.html", User=users, ProfilePic=pic)
        else:
            return redirect(url_for("userPage", userId=userId))
    else:
        return redirect(url_for("login"))

@app.route("/user/<userId>/give", methods=["POST"])
def givePage(userId):
    print(request.form)

    user = kudos.getUsers("Claimed", id=userId)
    if len(user) > 0:
        user = user[0]
    else:
        redirect(url_for('.error', messages="User with ID: "+str(userId)+" does NOT exist!", errorcode=404))

    if "loggedin" in session and session["loggedin"] == True:
        loggedinuser = kudos.getUsers("Claimed", id=session['id'])[0]
    else:
        session['previousurl'] = '/user/'+userId+'/give'
        return redirect(url_for('login'))
    num = request.form.get("NumberToSend")
    if num == '':
        num = 1

    success = loggedinuser.giveKudos(user, int(num), str(request.form.get('KudosMessage')))

    return redirect(url_for(".userPage", userId=userId, success=success))
    #return render_template("user.html", User=user, AbleToDonate=loggedinuser.giveStatus(), Success = success)

###### Error Handling Pages ########
@app.route("/error")
def error():
    message = request.args['messages'] #Using redirect(url_for('.error', message, errorcode))
    errorcode = request.args['errorcode']
    return render_template("error.html", Message=message, ErrorCode=errorcode)

############## JINJA2 FILTER STUFF :) #############################

#Used for converting unix time into dates
@app.template_filter('todate')
def _jinja2_filter_datetime(date, fmt=None):
    print(date)
    dt = datetime.datetime.fromtimestamp(date)
    return dt.strftime("%B %d, %Y")

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True) #change when deploying :)!