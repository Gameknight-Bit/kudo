# Kudos Backend System #
# 9/28/2022 #

import bcrypt

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
#   "VerificationReq": {False, msg, time}
#   "Password": encryptedPass #Encrypted with SHA-256 and salted vals
#   "Misc": {}
# }

def get_hashed_password(plain_text):
    return bcrypt.hashpw(plain_text, bcrypt.gensalt())

def check_password(plain_text, hashed_password):
    return bcrypt.checkpw(plain_text, hashed_password)

class User():
    def __init__(self, userid, username, email, password="placeholder"):
        self.UserId = userid
        self.Username = username
        self.Email = email
        self.Password = get_hashed_password(password) #Hashed Password is stored!
        self.Claimed = False
        self.SocialLinks = {}
        self.Kudos = {}
        self.LastKudos = {}
        self.Classes = {}
        self.Verified = False
        self.VerificationReq = {False, "placeholder request msg", 0}
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

    def toDict(self):
        return {key:value for key, value in self.__dict__.items() if not key.startswith('__') and not callable(key)}