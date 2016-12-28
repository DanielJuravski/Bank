import unittest
import Bank
import Client
import DB

class serverTest(unittest.TestCase):
    bank = Bank.BankLogic()
    def testClientBalanceLetters(self):
        self.failIf(self.bank.checkFromUserClientBalance("ABC"))
        pass
    def testClientBalanceNumbers(self):
        self.failUnless(self.bank.checkFromUserClientBalance("0"))
        pass
    def testAddNewClient(self):
        listOfClients = self.bank.getDB()
        newClient = Client.Client(None)
        personName = "Name"
        personId = 123456789
        personPassword = "QWERTY123456"
        ClientBalance = str(0)
        if self.bank.checkData(personName, personId, personPassword, ClientBalance) != False:
            newClient.setPersonName(personName)
            newClient.setPersonId(personId)
            newClient.setPersonPassword(personPassword)
            newClient.setClientBalance(float(ClientBalance))
            listOfClients.append(newClient)
    def testDepositAndWithdrawl(self):
        self.testAddNewClient()
        for client in self.bank.getDB():
            if client.getPersonId() == 123456789:
                originalSum = client.getClientBalance()
                client.deposit("100")
                client.deposit("asfv")
                client.withdrawal("100")
                client.withdrawal("kjhk")
                self.failUnless(client.getClientBalance() == originalSum)
    def testDB(self):
        DBToCheck = DB.DB()
        found = False
        for client in DBToCheck :
            if client.getPersonId() == 1:
                found = True
        self.failIf(found == False)
    def testProgram(self):
        #self.bank.initializeServerClientSockets()
        pass

