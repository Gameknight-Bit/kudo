# Run admin commands from this script with import admincmds #

import time
from datetime import datetime
from uuid import uuid4 as uuid
from tinydb import TinyDB, Query, where

UserDB = TinyDB('datastore/Users.json', sort_keys=True, indent=4)
UnclaimedUserDB = TinyDB('datastore/UnclaimedUsers.json', sort_keys=True, indent=4)

def reinitDB():
    global UserDB
    global UnclaimedUserDB

    UserDB = TinyDB('datastore/Users.json', sort_keys=True, indent=4)
    UnclaimedUserDB = TinyDB('datastore/UnclaimedUsers.json', sort_keys=True, indent=4)

PASSPHRASE = "I AM SURE!" #Passphrase to make sure commands are sure to go through!

# FULL RESETS!!! # 
# BE VERY CAREFUL WITH THESE COMMANDS!!!!!!!!

def FULL_RESET(Pass: str, DBType: str): #Kills Databases
    if Pass != PASSPHRASE:
        print("PASSPHRASE NOT CORRECT!!! \nMake sure to enter the correct passphrase before using this command!")
        return

    reinitDB()

    Users = Query()

    if DBType == "Both":
        UserDB.remove(where("Claimed") != None)
        UnclaimedUserDB.remove(where("Claimed") != None)
    elif DBType == "Claimed":
        UserDB.remove(where("Claimed") != None)
    elif DBType == "Unclaimed":
        UnclaimedUserDB.remove(where("Claimed") != None)
    
FULL_RESET("I AM SURE!", "Both")