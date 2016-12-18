import Client
import json
import os

class DB(list):
    def __init__(self):
        filePath = "C:\\PythonProjects\\Bank\\File.txt"
        isFileExcist = os.path.isfile(filePath)
        if isFileExcist == True:
            with open(filePath, 'r') as f:
                data = json.load(f)
                for arg in range(0, len(data)):
                    dbClient = Client.Client(None)
                    dbClient.personName = str(data[arg]["personName"])
                    dbClient.personId = int(data[arg]["personId"])
                    dbClient.personPassword = data[arg]["personPassword"]
                    dbClient.clientBalance = float(data[arg]["clientBalance"])
                    self.append(dbClient)
        else:
            return
    def saveClientsInDB(self):
        filePath = "C:\\PythonProjects\\Bank\\File.txt"
        with open(filePath,'w') as f:
            json.dump([Client.Client.__dict__ for Client.Client in self], f)