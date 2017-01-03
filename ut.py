from unittest import TestCase
import Bank
import BankClient
import DB
import threading
import socket
import cPickle
import time


global clientTestName, clientTestID, clientTestPassword, clientTestBalance
clientTestName = "Name"
clientTestID = 123456789
clientTestPassword = "QWERTY123456"
clientTestBalance = str(0)

class ProjectTests(TestCase):
    bank = Bank.BankLogic()

    def testClientBalanceLetters(self):
        self.failIf(self.bank.checkFromUserClientBalance("ABC"))
        pass

    def testClientBalanceNumbers(self):
        self.failUnless(self.bank.checkFromUserClientBalance("0"))
        pass

    def testAddNewClient(self):
        listOfClients = self.bank.getDB()
        newClient = BankClient.Client(None)
        personName = clientTestName
        personId = clientTestID
        personPassword = clientTestPassword
        clientBalance = clientTestBalance
        if self.bank.checkData(personName, personId, personPassword, clientBalance) != False:
            newClient.setPersonName(personName)
            newClient.setPersonId(personId)
            newClient.setPersonPassword(personPassword)
            newClient.setClientBalance(float(clientBalance))
            listOfClients.append(newClient)

    def testDepositAndWithdrawal(self):
        self.testAddNewClient()
        for client in self.bank.getDB():
            if client.getPersonId() == 123456789:
                originalSum = client.getClientBalance()
                client.deposit("100")
                client.deposit("Text-Not-Digits")
                client.withdrawal("100")
                client.withdrawal("Text-Not-Digits")
                self.failIf(client.getClientBalance() == originalSum)

    def testDB(self):
        DBToCheck = DB.DB()
        found = False
        for client in DBToCheck :
            if client.getPersonId() == 1:
                found = True
        self.failIf(found == False)

    def testLocks(self):
        """
        Testing if the threads and the locks working as they should.
        For example, if 2 clients try to withdrawal from the same account a sum that is bigger than the balance,
        the operation will not be possible.
        :return:
        """
        DB = self.bank.getDB()
        clientTestID = 1
        for clientTest in DB:
            if clientTest.personId == clientTestID:
                clientTest.clientBalance = 0
                balanceBeforeTest = clientTest.clientBalance
                self.createDepositAndWithdrawalThreads()
                balanceAfterTest = clientTest.clientBalance
                difference = balanceAfterTest - balanceBeforeTest
                self.failIf(difference < 0)
                break
            else:
                print "Add Client with ID=1 for testing."
                break

    def createDepositAndWithdrawalThreads(self):
        global numberOfBitsToRecv
        numberOfBitsToRecv = 1024
        host = "localhost"
        port = 5000
        numberOfActions = 50
        requestThreads = []
        for i in range(numberOfActions):
            t1 = threading.Thread(target=self.depositOne, args=(host, port))
            t2 = threading.Thread(target=self.withdrawalOne, args=(host, port))
            requestThreads.append(t1)
            requestThreads.append(t2)
            t1.start()
            t2.start()
            pass
        all_done = False
        while not all_done:
            all_done = True
            for t in requestThreads:
                if t.is_alive():
                    all_done = False
                    time.sleep(1)
            pass
        threading.Thread(target=self.exit, args=(host, port)).start()
        pass

    def depositOne(self, host, port):
        clientSocket = socket.socket()
        clientSocket.connect((host, port))
        dataToSend = [1, 1, "1111", "NoToken"]
        dataToSendStr = cPickle.dumps(dataToSend)
        clientSocket.send(dataToSendStr)
        dataInStr = clientSocket.recv(numberOfBitsToRecv)
        if dataInStr:
            dataIn = cPickle.loads(dataInStr)
            dataToSend[3] = dataIn[1]
            dataToSend.append(1)
            dataToSend.append("1")
            dataToSendStr = cPickle.dumps(dataToSend)
            clientSocket.send(dataToSendStr)
            dataInStr = clientSocket.recv(numberOfBitsToRecv)
            dataIn = cPickle.loads(dataInStr)
            clientSocket.close()  # The socket has been closed, but there was no message on the server dialog box.
            print "Deposit " + str(dataIn)

    def withdrawalOne(self, host, port):
        clientSocket = socket.socket()
        clientSocket.connect((host, port))
        dataToSend = [1, 1, "1111", "NoToken"]
        dataToSendStr = cPickle.dumps(dataToSend)
        clientSocket.send(dataToSendStr)
        dataInStr = clientSocket.recv(numberOfBitsToRecv)
        if dataInStr:
            dataIn = cPickle.loads(dataInStr)
            dataToSend[3] = dataIn[1]
            dataToSend.append(2)
            dataToSend.append("1")
            dataToSendStr = cPickle.dumps(dataToSend)
            clientSocket.send(dataToSendStr)
            dataInStr = clientSocket.recv(numberOfBitsToRecv)
            dataIn = cPickle.loads(dataInStr)
            clientSocket.close()  # The socket has been closed, but there was no message on the server dialog box.
            print "Withdrawal " + str(dataIn)

    def exit(self, host, port):
        s = socket.socket()
        s.connect((host, port))
        dataToSend = [0]
        dataToSendStr = cPickle.dumps(dataToSend)
        s.send(dataToSendStr)
        s.close()