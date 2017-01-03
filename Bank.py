import BankClient
import DB
import re
import socket
import cPickle
import os,binascii
import threading

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
        host = "localhost"
        port = 5000

        serverSocket = socket.socket()
        serverSocket.bind((host, port))

        serverSocket.listen(5)
        while True:
            clientSocket, addr = serverSocket.accept()
            threading.Thread(target = self.main, args = (clientSocket, addr)).start()
            print "Connection from: " + str(addr) + " started."

    #Main loop
    def main(self,i_clientSocket, i_clientAddr):
        while True:
            dataStr = i_clientSocket.recv(numberOfBitsToRecv)
            if dataStr: #check if there was recieved data from client
                data = cPickle.loads(dataStr)
                if data[0] == 1:
                    self.login(i_clientSocket, data)
                elif data[0] == 2:
                    self.joinNewClient(i_clientSocket, data)
                elif data[0] ==0:
                    self.exit(i_clientSocket, i_clientAddr)
                    break
            else:
                break

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
            newClient = BankClient.Client(None)
            newClient.setPersonName(personName)
            newClient.setPersonId(personId)
            newClient.setPersonPassword(personPassword)
            newClient.setClientBalance(float(ClientBalance))
            self.getDB().append(newClient)
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
        :param i_data: The client's input.|'Main menu choice'|'ID'|'Password'|'Token'|'Operation menu choice'|'relevant operation data'|
        :return:
        """
        listOfClients = self.getDB()
        IDToCheck = i_data[1]
        passwordToCheck = i_data[2]
        tokenToCheck = i_data[3]
        if self.getTokenDB().has_key(tokenToCheck) and self.getTokenDB()[tokenToCheck] == IDToCheck:
            for client in listOfClients:
                if client.getPersonId() == IDToCheck:
                    self.operationsMenu(i_clientSocket, i_data, client)
        else:
            feedback = self.clientRegistrationInFirstTime(listOfClients, IDToCheck, passwordToCheck)
            i_clientSocket.send(feedback)

    def clientRegistrationInFirstTime(self, i_listOfClients, i_IDToCheck, i_passwordToCheck):
        """
        Checks if the client data that was entered is right. If so, returns unique token to the client.
        Else returns false.
        :param i_listOfClients: DB of all clients of the bank.
        :param i_IDToCheck: ID entered from client.
        :param i_passwordToCheck: Password entered from client.
        :return: feedback: Data for sending to the client. If ID and password correct- the client's token.
                                                           Else, returns false.
        """
        tokenDB = self.getTokenDB()
        dataToSend = list()
        dataToSendStr = None
        searchInListOfClients = False
        for client in i_listOfClients:
            if client.getPersonId() == i_IDToCheck and client.getPersonPassword() == i_passwordToCheck:
                searchInListOfClients = True
                token = self.randomizeToken(tokenDB)
                self.tokenDB[token] = i_IDToCheck
                dataToSend.append(client)
                dataToSend.append(token)
                dataToSendStr = cPickle.dumps(dataToSend) # dataToSend = [client,token]
                break
        if searchInListOfClients == False:
            dataToSendStr = cPickle.dumps("False")
        return dataToSendStr

    def randomizeToken(self, i_tokenDB):
        """
        Rand token value and checks if ecist in tokenDB allready. If is, rand another time.
        :param i_tokenDB: DB of tokens.
        :return: Token value.
        """
        tokenExcistInTokenDB = True
        numberDigitsOfRand = 10
        token = binascii.b2a_hex(os.urandom(numberDigitsOfRand))
        while tokenExcistInTokenDB:
            if i_tokenDB.has_key(token) == False:
                tokenExcistInTokenDB = False
        return token

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
    def exit(self,i_clientSocket, i_clientAddr):
        self.getDB().saveClientsInDB()
        i_clientSocket.send("True")
        print "Connection from: " + str(i_clientAddr) + " ended."