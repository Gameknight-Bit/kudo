# Kudos Backend System #
# 9/28/2022 #

import bcrypt
from tinydb import TinyDB, Query

KUDO_TIMEFRAME = 7 #Time in days where kudo is allowed
KUDO_LIMIT = 5

UserDB = TinyDB('Users.json')
UnclaimedUserDB = TinyDB('UnclaimedUsers.json')

###############

def get_hashed_password(plain_text):
    return bcrypt.hashpw(plain_text.encode('utf8'), bcrypt.gensalt())

def check_password(plain_text, hashed_password):
    return bcrypt.checkpw(plain_text.encode('utf8'), hashed_password.encode('utf8'))

class User():
    def __init__(self, userid, username, email, password="placeholder"):
        self.UserId = userid
        self.Username = username
        self.Email = email
        self.Password = get_hashed_password(password).decode('utf8') #Hashed Password is stored!
        self.Claimed = False
        self.Verified = False
        self.SocialLinks = {}
        self.Kudos = {}
        self.LastKudos = {
            "LastTime": 0,
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

def initUser(id, username, email, password, isAdmin=False, isVerified=False, userRole="Student"):
    user = User(id, username, email, password)
    user.KudoSettings["IsAdmin"] = isAdmin
    user.Verified = isVerified
    user.KudoSettings["Role"] = userRole

    return user

def getUsers(dbType, id="", username="", email=""): #dbType = "Claimed" or "Unclaimed"
    Users = Query()

    curDB = UnclaimedUserDB
    if dbType == "Claimed":
        curDB = UserDB
    
    if id != "":
        return curDB.search(Users.UserId == id)
    elif username != "":
        return curDB.search(Users.Username == username)
    elif email != "":
        return curDB.search(Users.Email == email)
    else:
        return curDB

def setUser(dbType, user: User): #dbType = "Claimed" or "Unclaimed"
    Users = Query()

    curDB = UnclaimedUserDB
    if dbType == "Claimed":
        curDB = UserDB

    if curDB.search(Users.UserId == user.UserId):
        return "Error: User already in DB, User updateUser or deleteUser first!!!"


def getDB(dbType): #dbType = "Claimed" or "Unclaimed"
    curDB = UnclaimedUserDB
    if dbType == "Claimed":
        curDB = UserDB

    return curDB