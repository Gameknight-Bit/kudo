## Gameknight-Bit's .json Datastore! ##

####### Version Notes ########
VERSION = "beta_0.1"
# - Released!
# - May be bugs!
# - Make sure to stay updated on documentation with the github page!
# - .json files need to be stored in below folder
##############################

# Constants to Change!!! #
DATASTORE_PATH = "datastore" #Path to the Datastore Folder (relative path or full path)

SUCCESS_MSGS = True #Prints out at certain points for debugging
INDENT_SPACING = 4 #Number of spaces for each .json indent

## Imports ##
from os.path import exists
from os import remove
import json

# Helper Functions :) #
def cleanName(s):
    return s.replace(" ", "_")

def cleanValues(val): #Checks to make sure value is ready to be inserted into .json file
    if type(val) is dict:
        retVal = {}
        for key, value in val.items():
            retVal[key] = cleanValues(value)
        return retVal
    elif type(val) is list:
        print("WARNING: Lists should not be used for storage (Use dictionaries instead!!!)")
        #print("**The list will be converted to a dictionary with position values being strings instead of ints**")
        retVal = []
        for i in range(len(val)):
            retVal[i] = cleanValues(val[i])
        return retVal
    elif type(val) is tuple:
        print("WARNING: Tuples should not be used for storage (Use dictionaries instead!!!)")
        print("**The tuple will be converted to a dictionary with position values being strings instead of ints**")
        retVal = {}
        for i in range(len(val)):
            retVal[str(i)] = cleanValues(val[i])
        return retVal
    elif type(val) is int:
        return val
    elif type(val) is str:
        return val
    elif type(val) is bool:
        return val
    elif type(val) is float:
        return val
    elif type(val) is complex:
        return val
    elif val == None:
        return None
    else:
        print("Warning: Please make sure to convert classes into dictionaries before inserting into Datastores!")
        try:
            retVal = {key:value for key, value in val.__dict__.items() if not key.startswith('__') and not callable(key)}
            for key, value in retVal.items():
                retVal[key] = cleanValues(value)
            return retVal
        except:
            assert(False, "Exception occured when trying to convert data of type: '"+str(type(val))+"' Please contact Gameknight-Bit on the error!")
            return None


####### Classes ########
class Datastore:
    def __init__(self, datastore_name):
        self.Path = DATASTORE_PATH+"/"+datastore_name+'.json'
        with open(DATASTORE_PATH+"/"+datastore_name+'.json', "w") as f:
            if SUCCESS_MSGS:
                print(datastore_name+'.json has been accessed!')

    #Returns value associated with key (Usually dictionary)
    def GetAsync(self, key):
        with open(self.Path, "r+") as f:
            data = json.load(f)
            return data[key] or None

    #Sets value parameter to associated key
    def SetAsync(self, key, value):
        if key == "VersionDatastore111":
            assert(False, "Key cannot be named 'VersionDatastore111' as it is already in use!")
            return None

        with open(self.Path, "r+") as f:
            data = json.load(f)
            data[key] = cleanValues(value)
            if value == None:
                data.pop(key)
            f.seek(0)
            json.dump(data, f, indent=INDENT_SPACING)
            f.truncate()

    #Returns True or False based of if key is in datastore
    def CheckAsync(self, key):
        with open(self.Path, "r+") as f:
            data = json.load(f)
            return (key in data.keys())

    #Sets version number of datastore (all up to you :))
    def SetVersion(self, ver):
        if not type(ver) is str:
            assert(False, "ERROR: Version number needs to be a string!!!")
            return None
        with open(self.Path, "r+") as f:
            data = json.load(f)
            data["Version"] = cleanValues(ver)
            f.seek(0)
            json.dump(data, f, indent=INDENT_SPACING)
            f.truncate()

    #Returns Set Version (Or None if no version was set)
    def GetVersion(self):
        with open(self.Path, "r+") as f:
            data = json.load(f)
            return data["VersionDatastore111"] or None

    #Returns All Datastore Keys
    def GetKeys(self):
        with open(self.Path, "r+") as f:
            data = json.load(f)
            return data.keys()

################# Functions #################
# Parameters: name = Your datastore's name (will create .json file named: YOUR_DATASTORE_NAME.json)
# Returns Datastore obj
def NewDatastore(name):
    name = cleanName(name)
    try:
        assert(exists(DATASTORE_PATH+"/"+name), "Datastore key provided is already in use! Try a different name other than '"+name+"'")
    except Exception as e:
        print(e)
        return
    with open(DATASTORE_PATH+"/"+name, "r+") as f:
        f.seek(0)
        json.dump({}, f, ensure_ascii=False, indent=INDENT_SPACING) #inits file with {}
        f.truncate()
    return Datastore(name)
    
# Parameters: name = Your datastore's name (will create .json file named: YOUR_DATASTORE_NAME.json)
# Returns Datastore obj
def GetDatastore(name): #Safer Version of NewDatastore
    name = cleanName(name)
    if exists(DATASTORE_PATH+"/"+name):
        return Datastore(name)
    else:
        return NewDatastore(name)

# Parameters: name = Your datastore's name (will create .json file named: YOUR_DATASTORE_NAME.json)
# Returns True if Datastore was Destroyed
def DestroyDatastore(name):
    name = cleanName(name)
    if exists(DATASTORE_PATH+"/"+name):
        remove(DATASTORE_PATH+"/"+name)
        print(name+" Datastore successfully destroyed!!!")