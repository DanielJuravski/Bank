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
        feedback = None
        for char in range(len(i_depositSum)):
            if i_depositSum[char].isdigit() == False or i_depositSum < 0:
                feedback = False
            else:
                threadLock.acquire()
                self.setClientBalance(self.getClientBalance() + float(i_depositSum))
                threadLock.release()
                feedback = True
        return feedback

    def withdrawal(self,i_withdrawalSum):
        feedback = None
        threadLock.acquire()
        for char in range(len(i_withdrawalSum)):
            if i_withdrawalSum[char].isdigit() == False or i_withdrawalSum < 0:
                feedback = "Illegal Char"
                break
            elif self.clientBalance < float(i_withdrawalSum):
                feedback = "Low Balance"
                break
            else:
                self.setClientBalance(self.getClientBalance() - float(i_withdrawalSum))
                feedback = "Done"
                break
        threadLock.release()
        return feedback

    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)