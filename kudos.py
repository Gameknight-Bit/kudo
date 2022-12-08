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

def reinitDB():
    global UserDB
    global UnclaimedUserDB

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
        self.Metadata = {
            "Event": "none",
            "Note": "",
            "Value": 1,
        }

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
            "Kudos": {} #Only goes up to KUDO_LIMIT
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

            for key, v in self.Kudos.items():
                v = Kudos.fromDict(v)
                if v.TimeGiven >= latest_unix:
                    arr.append(v)

            return KudoScoreCalc(arr)

    def giveStatus(self):
        print(self.KudoSettings)
        if self.KudoSettings["IsAdmin"] == True or self.KudoSettings["Role"] == "Teacher" or self.KudoSettings["KudoLimit"] < 0:
            return True

        lastTime = self.LastKudos["LastTime"]
        givenKudos = self.LastKudos["Kudos"]

        maxUserKudos = self.KudoSettings["KudoLimit"]
        timeframeUser = self.KudoSettings["Cooldowns"]*86400

        for key, item in givenKudos.copy().items(): #Cleans all kudos that have cooled down
            kudo = Kudos.fromDict(item)
            if int(time.time())-kudo.TimeGiven > timeframeUser:
                givenKudos.pop(key)

        if len(givenKudos) < maxUserKudos: #If updated list has spots avaliable
            return int(maxUserKudos-len(givenKudos))
        else:
            return False


    def giveKudos(self, recipient, quantity: int = 1, message: str = "") -> bool:
        status = self.giveStatus() #false or number of kudos avaliable to give
        if status == False and status >= quantity:
            return False

        print(quantity)
        
        for _ in range(quantity):
            # Give Recipient their kudos
            kudo = Kudos(self.UserId)
            kudo.Metadata["Message"] = message
            recipient.Kudos[str(kudo.ID)] = kudo.toDict()

            # Update own user with kudos
            self.LastKudos["Kudos"][str(kudo.ID)] = kudo.toDict()
            self.LastKudos["LastTime"] = int(time.time())
            self.LastKudos["TotalGiven"] -=- 1 #-=- Incrementor >:)

        if recipient.Claimed == True:
            updateUser("Claimed", recipient)
        else:
            updateUser("Unclaimed", recipient)

        updateUser("Claimed", self)
        return True


def initUser(id, username, email, password, isAdmin=False, isVerified=False, userRole="Student"):
    user = User(id, username, email, password)
    user.KudoSettings["IsAdmin"] = isAdmin
    user.Verified = isVerified
    user.KudoSettings["Role"] = userRole
    user.Misc["ProfilePicture"] = "Default.png"

    return user

def getUsers(dbType, id="", username="", email=""): #dbType = "Claimed" or "Unclaimed"
    reinitDB()
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
    reinitDB()
    Users = Query()

    curDB = UnclaimedUserDB
    if dbType == "Claimed":
        curDB = UserDB

    if curDB.search(Users.UserId == user.UserId):
        return "Error: User already in DB, User updateUser or deleteUser first!!!"
    curDB.insert(user.toDict())

def updateUser(dbType, user: User): #dbType = "Claimed" or "Unclaimed"
    reinitDB()

    Users = Query()

    curDB = UnclaimedUserDB
    if dbType == "Claimed":
        curDB = UserDB

    if curDB.search(Users.UserId == user.UserId):
        curDB.update(user.toDict(), Users.UserId==user.UserId)
    else:
        return "ERROR: Userid Not found in database..."

def getDB(dbType): #dbType = "Claimed" or "Unclaimed"
    reinitDB()

    curDB = UnclaimedUserDB
    if dbType == "Claimed":
        curDB = UserDB

    return curDB