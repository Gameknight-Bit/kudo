# Kudos Backend System #
# 9/28/2022 #

import bcrypt
import time
from datetime import datetime
from uuid import uuid4 as uuid
from tinydb import TinyDB, Query

KUDO_TIMEFRAME = 7 #Time in days where kudo is allowed
KUDO_LIMIT = 5

UserDB = TinyDB('datastore/Users.json', sort_keys=True, indent=4)
UnclaimedUserDB = TinyDB('datastore/UnclaimedUsers.json', sort_keys=True, indent=4)

###############

def get_hashed_password(plain_text):
    return bcrypt.hashpw(plain_text.encode('utf8'), bcrypt.gensalt())

def check_password(plain_text, hashed_password):
    return bcrypt.checkpw(plain_text.encode('utf8'), hashed_password.encode('utf8'))

def KudoScoreCalc(kudosObjs):
    totalScore = 0
    for v in kudosObjs:
        if v.Quantiled == False:
            totalScore += 1
        else:
            #LOOKUP GIVENBY USER AND CHECK WHAT QUANTILE THEY ARE IN THAT THEY GAVE POINTS!!!!
            Quantile = 1
            totalScore += 1/Quantile
        
        if "ExtraPoints" in v.Metadata.keys():
            totalScore += float(v.Metadata["ExtraPoints"])

    return totalScore

class Kudos():
    def __init__(self, useridgiven: str) -> None:
        self.ID = str(uuid())
        self.TimeGiven = int(time.time())
        self.GivenBy = useridgiven
        self.Quantiled = False
        self.Metadata = {}

    def setAttributes(self, dict):
        for k, v in dict.items():
            setattr(self, k, v)

    def fromDict(dir):
        tempUser = Kudos(dir["GivenBy"])
        for k, v in dir.items():
            if k == "GivenBy":
                continue
            else:
                setattr(tempUser, k, v)
        return tempUser

    def toDict(self):
        return {key:value for key, value in self.__dict__.items() if not key.startswith('__') and not callable(key)}

class User():
    def __init__(self, userid, username, email, password="placeholder"):
        self.UserId = userid
        self.Username = username
        self.Email = email
        self.Grade = "?"
        self.Password = get_hashed_password(password).decode('utf8') #Hashed Password is stored!
        self.Claimed = False
        self.Verified = False
        self.SocialLinks = {}
        self.Kudos = {} #Kudos Recieved
        self.LastKudos = { #Kudos Given out
            "LastTime": 0,
            "TotalGiven": 0,
            "Kudos": {}
        }
        self.KudoSettings = {
            "IsAdmin": False,
            "KudoLimit": KUDO_LIMIT,
            "Cooldowns": KUDO_TIMEFRAME,
            "Role": "Student",
            "Quantiled": False
        }
        self.Classes = {}
        self.VerificationReq = {
            "sent": False, 
            "msg": "placeholder request msg",
            "time-sent": 0,
            "key": ""
        }
        self.LastLogin = 0
        self.Status = "New Here :)"
        self.Misc = {}

    def setAttributes(self, dict):
        for k, v in dict.items():
            setattr(self, k, v)
        
    def checkPass(self, plain_text):
        return check_password(plain_text, self.Password)

    def fromDict(dir):
        tempUser = User(dir["UserId"], dir["Username"], dir["Email"])
        for k, v in dir.items():
            if k == "UserId" or k=="Username" or k=="Email":
                continue
            elif k == "Password":
                setattr(tempUser, k, v) #No hashing multiple times!!!
            else:
                setattr(tempUser, k, v)
        return tempUser

    def toDict(self):
        return {key:value for key, value in self.__dict__.items() if not key.startswith('__') and not callable(key)}

    def getKudosScore(self, type: str = "All-Time"):
        if type == "All-Time":
            return KudoScoreCalc(self.Kudos)
        elif type == "Monthly":
            arr = []

            given_date = datetime.today().date()
            first_day_of_month = given_date.replace(day = 1)
            latest_unix = time.mktime(first_day_of_month.timetuple())

            for v in self.Kudos:
                if v.TimeGiven >= latest_unix:
                    arr.append(v)

            return KudoScoreCalc(arr)


def initUser(id, username, email, password, isAdmin=False, isVerified=False, userRole="Student"):
    user = User(id, username, email, password)
    user.KudoSettings["IsAdmin"] = isAdmin
    user.Verified = isVerified
    user.KudoSettings["Role"] = userRole

    return user

def getUsers(dbType, id="", username="", email=""): #dbType = "Claimed" or "Unclaimed"
    Users = Query()

    ar = []

    curDB = UnclaimedUserDB
    if dbType == "Claimed":
        curDB = UserDB
    if dbType == "Both":
        ar = getUsers("Claimed", id, username, email)
    
    if id != "":
        for item in curDB.search(Users.UserId == id):
            ar.append(User.fromDict(item))
    if username != "":
        for item in curDB.search(Users.Username == username):
            ar.append(User.fromDict(item))
    if email != "":
        for item in curDB.search(Users.Email == email):
            ar.append(User.fromDict(item))
    if id=="" and username=="" and email=="":
        for item in curDB:
            ar.append(User.fromDict(item))
    return ar

def setUser(dbType, user: User): #dbType = "Claimed" or "Unclaimed"
    Users = Query()

    curDB = UnclaimedUserDB
    if dbType == "Claimed":
        curDB = UserDB

    if curDB.search(Users.UserId == user.UserId):
        return "Error: User already in DB, User updateUser or deleteUser first!!!"
    curDB.insert(user.toDict())

def updateUser(dbType, user: User): #dbType = "Claimed" or "Unclaimed"
    Users = Query()

    curDB = UnclaimedUserDB
    if dbType == "Claimed":
        curDB = UserDB

    if curDB.search(Users.UserId == user.UserId):
        curDB.update(user.toDict(), Users.UserId==user.UserId)
    else:
        return "ERROR: Userid Not found in database..."

def getDB(dbType): #dbType = "Claimed" or "Unclaimed"
    curDB = UnclaimedUserDB
    if dbType == "Claimed":
        curDB = UserDB

    return curDB