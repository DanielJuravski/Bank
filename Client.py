import Person
import json
import threading

global threadLock
threadLock = threading.Lock()

class Client(Person.Person):
    def __init__(self,clientBalance):
        self.clientBalance = None
    def setClientBalance(self,i_clientBalance):
        self.clientBalance = i_clientBalance
        pass
    def getClientBalance(self):
        return self.clientBalance
    def deposit(self,i_depositSum):
        for char in range(len(i_depositSum)):
            if i_depositSum[char].isdigit() == False or i_depositSum < 0:
                return False
        #threadLock.acquire()
        self.setClientBalance(self.getClientBalance() + float(i_depositSum))
        #threadLock.release()
        return True
    def withdrawal(self,i_withdrawalSum):
        for char in range(len(i_withdrawalSum)):
            if i_withdrawalSum[char].isdigit() == False or i_withdrawalSum < 0:
                return "Illegal Char"
            elif self.clientBalance < float(i_withdrawalSum):
                return "Low Balance"
            else:
                self.setClientBalance(self.getClientBalance() - float(i_withdrawalSum))
                return "Done"
    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)