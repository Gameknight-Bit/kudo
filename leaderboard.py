from tinydb import TinyDB, Query
import kudos

UserDB = TinyDB('Users.json', sort_keys=True, indent=4)

def getTopPlayers(numUsers: int, type: str = "All-Time"):
    User = Query()

    Users = UserDB.search(User.Claimed == True)
    if len(Users) == 0:
        return []
    Users = sorted(Users.items(), key=lambda item: item.getKudoScore(type), reverse=True)
    
    if len(Users) <= numUsers:
        return Users
    return Users[:numUsers]
