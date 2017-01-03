import json

class Person:
    def __init__(self,personId,personName,personPassword):
        self.personId = None       #TODO: Private Veraible
        self.personName = None     #TODO: Private Veraible
        self.personPassword = None #TODO: Private Veraible

    def setPersonId(self,i_personID):
        self.personId = i_personID
        pass

    def getPersonId(self):
        return self.personId

    def setPersonName(self,i_personName):
        self.personName = i_personName
        pass

    def getPersonName(self):
        return self.personName

    def setPersonPassword(self,i_personPassword):
        self.personPassword = i_personPassword
        pass

    def getPersonPassword(self):
        return self.personPassword

    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)