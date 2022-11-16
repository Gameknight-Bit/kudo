from tinydb import TinyDB, Query
import kudos
from kudos import User as UserObj

UserDB = TinyDB('datastore/Users.json', sort_keys=True, indent=4)

def getTopPlayers(numUsers: int, type: str = "All-Time"):
    User = Query()

    Users = UserDB.search(User.Claimed == True)
    if len(Users) == 0:
        return []
    for i in range(len(Users)):
        Users[i] = UserObj.fromDict(Users[i])

    def keyFunc(s):
        return s.getKudosScore(type)
    Users = sorted(Users, key=keyFunc, reverse=True)
    
    if len(Users) <= numUsers:
        return Users
    return Users[:numUsers]
