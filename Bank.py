import Client
import DB
import re
import socket
import cPickle
import os,binascii

class BankLogic:
    def __init__(self):
        self.db = DB.DB()
        self.tokenDB = {}
        global numberOfBitsToRecv
        numberOfBitsToRecv = 1024
    def getDB(self):
        return self.db
    def getTokenDB(self):
        return self.tokenDB
    def initializeServerClientSockets(self):
        host = '127.0.0.1'
        port = 5000

        serverSocket = socket.socket()
        serverSocket.bind((host, port))

        serverSocket.listen(1)
        clientSocket, addr = serverSocket.accept()

        print "Connection from: " + str(addr) + " started."
        return clientSocket, serverSocket ,addr

    #Main loop
    def main(self):
        clientSocket, serverSocket, clientAddr = self.initializeServerClientSockets()
        while True:
            dataStr = clientSocket.recv(numberOfBitsToRecv)
            data = cPickle.loads(dataStr)
            if data[0] == 1:
                self.login(clientSocket, data)
            elif data[0] == 2:
                self.joinNewClient(clientSocket, data)
            elif data[0] ==0:
                self.exit(clientSocket, serverSocket, clientAddr)
                break
        serverSocket.close()

    # Sign-in of a new client
    def joinNewClient(self, i_clientSocket, i_data):
        """
        The server gets from the client, new data of a new user for signing in.
        It checks it, if all the data is legal - creates new 'client' object and add it to the DB of clients.
        If the data is illegal, sends to the client, "False" massage.
        :param i_clientSocket: Client's socket.
        :param i_data: List with the new user data.
        :return:
        """
        personName = i_data[1]
        personId = i_data[2]
        personPassword = i_data[3]
        ClientBalance = i_data[4]
        if self.checkData(personName,personId,personPassword,ClientBalance) != False :
            client = Client.Client(None)
            client.setPersonName(personName)
            client.setPersonId(personId)
            client.setPersonPassword(personPassword)
            client.setClientBalance(float(ClientBalance))
            self.getDB().append(client)
            msgToClient = "True"
        else:
            msgToClient = "False"
        msgToClientDump = cPickle.dumps(msgToClient)
        i_clientSocket.send(msgToClientDump)
    def checkFromUserPersonName(self, i_personName):
        if i_personName.isalpha():
            return True
        else:
            return False
    def checkFromUserPersonID(self, i_personID):
        return self.parseIntRE(i_personID)
    def checkFromUserPersonPassword(self,i_personPassword):
        return True
    def checkFromUserClientBalance(self,i_clientBalance):
        for char in range(len(i_clientBalance)):
            if i_clientBalance[char].isdigit() == False or i_clientBalance < 0:
                return False
        return True
    def checkData(self, i_personName, i_personID, i_personPassword, i_clientBalance):
        """
        Checks if all the that recieved from the client is legal.
        :param i_personName: The person name.
        :param i_personID: The person ID.
        :param i_personPassword: The person password.
        :param i_clientBalance: The client balance.
        :return: bool: True - the data is legal.
                       False - the is illegal.
        """
        check1 = self.checkFromUserPersonName(i_personName)
        check2 = self.checkFromUserPersonID(i_personID)
        check3 = self.checkFromUserPersonPassword(i_personPassword)
        check4 = self.checkFromUserClientBalance(i_clientBalance)
        return check1 and check2 and check3 and check4
    def parseIntRE(self,i_ToCheck):
        i_strToCheck = str(i_ToCheck)
        match = re.search('(\d+)',i_strToCheck)
        if match != None and match.group() == i_strToCheck:
            return True
        return False

    #Login of excisting client
    def login(self, i_clientSocket, i_data):
        """
        The login menu.
        First checks if the client was logged already, if so compares the tokens.
            If not logged, checks if the client's ID and password are right.
                If True; sends to the client his unique token.
        If logged; scanning the data the recv from client.
        :param i_clientSocket: Client's socket
        :param i_data: The client's input.|'Main menu chice'|'ID'|'Password'|'Token'|'Operation menu choice'|'relevant operation data'|
        :return:
        """
        listOfClients = self.getDB()
        IDToCheck = i_data[1]
        passwordToCheck = i_data[2]
        tokenToCheck = i_data[3]
        if self.getTokenDB().has_key(IDToCheck):
            if self.getTokenDB()[IDToCheck] == tokenToCheck:
                for client in listOfClients:
                    if client.getPersonId() == IDToCheck:
                        self.operationsMenu(i_clientSocket, i_data, client)
        else:
            dataToSend = list()
            searchInListOfClients = False
            for client in listOfClients:
                if client.getPersonId() == IDToCheck and client.getPersonPassword() == passwordToCheck:
                    searchInListOfClients = True
                    numberOfRand = 10
                    token = binascii.b2a_hex(os.urandom(numberOfRand))
                    self.tokenDB[IDToCheck] = token
                    dataToSend.append(client)
                    dataToSend.append(token)
                    dataToSendStr = cPickle.dumps(dataToSend) #dataToSend = [client,token]
                    i_clientSocket.send(dataToSendStr)
            if searchInListOfClients == False:
                dataToSendStr = cPickle.dumps("False")
                i_clientSocket.send(dataToSendStr)
    def operationsMenu(self, i_clientSocket, i_data, i_client):
        clientID = i_data[1]
        operationChoice = i_data[4]
        success = None
        if operationChoice == 1:
            sumToDeposit = i_data[5]
            success = self.depositOnAccount(i_client, sumToDeposit)
        elif operationChoice == 2:
            sumToWithdrawl = i_data[5]
            success = self.withdrawalOnAccount(i_client, sumToWithdrawl)
        elif operationChoice == 3:
            sumToDepositOnAnotherAccount = i_data[5]
            anotherID = i_data[6]
            success = self.depositOnAnotherAccount(sumToDepositOnAnotherAccount, anotherID)
            pass
        del self.getTokenDB()[clientID]
        successStr = cPickle.dumps(success)
        i_clientSocket.send(successStr)
    def depositOnAccount(self, i_client, i_sum):
        return i_client.deposit(i_sum)
    def withdrawalOnAccount(self, i_client, i_sum):
        return i_client.withdrawal(i_sum)
    def depositOnAnotherAccount(self, i_sum, i_anotherID):
        arreyOfClients = self.getDB()
        for client in arreyOfClients:
            if client.getPersonId() == int(i_anotherID):
                if i_sum != None:
                    return self.depositOnAccount(client,i_sum)
                else:
                    return False
        return False

    #Exit bank
    def exit(self,i_clientSocket, i_serverSocket, i_clientAddr):
        self.getDB().saveClientsInDB()
        i_clientSocket.send("True")
        print "Connection from: " + str(i_clientAddr) + " ended."