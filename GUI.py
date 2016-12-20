import os
import socket
import re
import cPickle


class ConsoleGUI:
    def __init__(self):
        global clear
        clear = lambda: os.system('cls')
        global numberOfBitsToRecv
        numberOfBitsToRecv = 1024
        self.dataArrey = list()
        pass
    def getDataArrey(self):
        return self.dataArrey
    def setDataArrey(self,i_choice):
        self.getDataArrey().append(i_choice)
    def resetDataArrey(self):
        length = len(self.dataArrey)
        for i in range(length - 1, -1, -1):
            del self.dataArrey[i]
        pass
    def ScanChoiceFromUser(self, optionsArrey):
        choice = None
        try:
            choice = int(raw_input())
        except ValueError:
            None
        while choice not in optionsArrey:
            print "You pressed illegal button, press again."
            try:
                choice = int(raw_input())
            except ValueError:
                None
        return choice
    def initializeSocket(self):
        host = '127.0.0.1'
        port = 5000
        s = socket.socket()
        s.connect((host, port))
        return s

    #Main loop
    def main(self):
        """
        The main menu loop.
        Displays to the user the operations he can do.
        After choosing the operation, the specific case is running.
        :return:
        """
        clientSocket = self.initializeSocket()
        userChoice = None
        while userChoice != 0:
            self.resetDataArrey()
            clear()
            print "Welcome to TAKSHAM bank ! \n" \
                  "For login press -----> 1 \n" \
                  "For Sign in press ---> 2 \n" \
                  "For exit press ------> 0"
            userChoice = self.ScanChoiceFromUser([0, 1, 2])
            clear()
            if userChoice == 1:
                self.loginMenu(clientSocket)
            elif userChoice == 2:
                self.scanNewClientMenu(clientSocket)
            elif userChoice == 0:
                self.exitMenu(clientSocket)

    # Login of excisting client
    def loginMenu(self, i_clientSocket):
        """
        Login menu - first, requires from the user his ID and password.
        If they are right, presents to the user the available operations he can do.
        :param i_clientSocket: Sends and recv data with the server.
        :return:
        """
        firstOperation = 1
        self.setDataArrey(firstOperation)
        inputID = self.scanPersonIdFromUser()
        inputPassword = self.scanPersonPasswordFromUser()
        self.setDataArrey(inputID)
        self.setDataArrey(inputPassword)
        virtualToken = "NoToken"
        self.setDataArrey(virtualToken)
        dataArrey = self.getDataArrey()
        dataArreyStr = cPickle.dumps(dataArrey)
        i_clientSocket.send(dataArreyStr)
        serverFeedbackStr = i_clientSocket.recv(numberOfBitsToRecv)
        serverFeedback = cPickle.loads(serverFeedbackStr) #serverFeedback = [client,token] or "False"
        if serverFeedback == "False":
            print "You entered illegal ID number or password!"
            raw_input("Press any key to continue:")
        else:
            self.getDataArrey()[3] = serverFeedback[1] #set this token to returned token
            thisClient = serverFeedback[0]
            clear()
            print "Hello " + thisClient.getPersonName() + "!\n"
            self.optionsMenu(i_clientSocket)
    def optionsMenu(self, i_clientSocket):
        print "For depositing press -----------------------> 1 \n" \
              "For withdrawaling press --------------------> 2 \n" \
              "For depositing on another account press ----> 3 "
        choice = self.ScanChoiceFromUser([1, 2, 3])
        clear()
        if choice == 1:
            secondOperation = 1
            self.setDataArrey(secondOperation)
            self.depositMenu(i_clientSocket)
        elif choice == 2:
            secondOperation = 2
            self.setDataArrey(secondOperation)
            self.withdrawalMenu(i_clientSocket)
        elif choice == 3:
            secondOperation = 3
            self.setDataArrey(secondOperation)
            self.depositOnAnotherAccountMenu(i_clientSocket)
    def depositMenu(self, i_clientSocket):
        check = False
        while check == False:
            print "Please enter the sum you would like to deposit:"
            sumToDeposit = raw_input()
            check = self.depositCheck(sumToDeposit)
            if check == False:
                print "Illegal number, try again:"
            else:
                self.setDataArrey(sumToDeposit)
                dataArreyStr = cPickle.dumps(self.getDataArrey())
                i_clientSocket.send(dataArreyStr)
                ifSucceedStr = i_clientSocket.recv(numberOfBitsToRecv)
                ifSucceed = cPickle.loads(ifSucceedStr)
                if ifSucceed == False:
                    print "The operation didn't succeed."
                else:
                    print "Done!"
        raw_input("Please press any key to continue:")
    def depositCheck(self, i_depositSum):
        for char in range(len(i_depositSum)):
            if i_depositSum[char].isdigit() == False or i_depositSum < 0:
                return False
            else:
                return True
    def withdrawalMenu(self, i_clientSocket):
        check = False
        while check == False:
            print "Please enter the sum you would like to withdrawal:"
            sumToWithdrawal = raw_input()
            check = self.withdrawalCheck(sumToWithdrawal)
            if check == False:
                print "Illegal number, try again:"
            else:
                self.setDataArrey(sumToWithdrawal)
                dataArreyStr = cPickle.dumps(self.getDataArrey())
                i_clientSocket.send(dataArreyStr)
                ifSucceedStr = i_clientSocket.recv(numberOfBitsToRecv)
                ifSucceed = cPickle.loads(ifSucceedStr)
                if ifSucceed == "Illegal Char":
                    print "You entered illegal char."
                elif ifSucceed == "Low Balance":
                    print "Your balance is too low."
                elif ifSucceed == "Done":
                    print "Done!"
        raw_input("Please press any key to continue:")
    def withdrawalCheck(self, i_withdrawalSum):
        for char in range(len(i_withdrawalSum)):
            if i_withdrawalSum[char].isdigit() == False or i_withdrawalSum < 0:
                return False
            else:
                return True
    def depositOnAnotherAccountMenu(self, i_clientSocket):
        anotherID = self.scanPersonIdFromUser()
        check = False
        while check == False:
            print "Please enter the sum you would like to deposit:"
            sumToDeposit = raw_input()
            check = self.depositCheck(sumToDeposit)
            if check == False:
                print "Illegal number, try again:"
            else:
                self.setDataArrey(sumToDeposit)
                self.setDataArrey(anotherID)
                dataArrey = self.getDataArrey()
                dataArreyStr = cPickle.dumps(dataArrey)
                i_clientSocket.send(dataArreyStr)
                ifSucceedStr = i_clientSocket.recv(numberOfBitsToRecv)
                ifSucceed = cPickle.loads(ifSucceedStr)
                if ifSucceed == False:
                    print "ID number is not excist ! "
                else:
                    print "Done!"
        raw_input("Please press any key to continue:")

    #Sign in a new client
    def scanNewClientMenu(self, i_clientSocket):
        """
        Scans from the user, the new client data that need to be signed in.
        After scanning each varaible, the method checks it.
        Then send to the server all the data.
        Finally, prints if the process succeed or not.
        :param i_clientSocket: The client socket after initalization
        :return: None
        """
        firstOperation = 2
        self.setDataArrey(firstOperation)
        personName = self.scanPersonNameFromUser()
        personId = self.scanPersonIdFromUser()
        personPassword = self.scanPersonPasswordFromUser()
        ClientBalance = self.scanClientBalanceFromUser()
        self.setDataArrey(personName)
        self.setDataArrey(personId)
        self.setDataArrey(personPassword)
        self.setDataArrey(ClientBalance)
        dataArrey = self.getDataArrey()
        dataArreyStr = cPickle.dumps(dataArrey)
        i_clientSocket.send(dataArreyStr)
        serverFeedback = i_clientSocket.recv(numberOfBitsToRecv)
        serverFeedbackStr = cPickle.loads(serverFeedback)
        if serverFeedbackStr == "True":
            print "You have joined to the bank!"
        else:
            print "You have entered illegal data, please try again."
        raw_input("Please press any key to continue:")
    def scanPersonIdFromUser(self):
        # TODO: check if the given ID is excist allready
        check = False
        while check == False:
            personID = raw_input("Please enter the ID number:")
            check = self.checkFromUserPersonID(personID)
            if check == False:
                print "Illegal ID number, try again:"
        personID = int(personID)
        return personID
    def scanPersonNameFromUser(self):
        check = False
        while check == False:
            personName = raw_input("Please enter your name:")
            check = self.checkFromUserPersonName(personName)
            if check == False:
                print "Illegal name, try again:"
        return personName
    def scanPersonPasswordFromUser(self):
        check = False
        while check == False:
            personPassword = raw_input("Please enter your password:")
            check = self.checkFromUserPersonPassword(personPassword)
            if check == False:
                print "Illegal password, try again:"
        return personPassword
    def scanClientBalanceFromUser(self):
        check = False
        while check == False:
            clientBalance = raw_input("Please enter your balance:")
            check = self.checkFromUserClientBalance(clientBalance)
            if check == False:
                print "Balance should be positive number, try again:"
        #clientBalance = float(clientBalance)
        return clientBalance
    def checkFromUserPersonID(self, i_personID):
        return self.parseIntRE(i_personID)
    def parseIntRE(self,i_strToCheck):
        match = re.search('(\d+)',i_strToCheck)
        if match != None and match.group() == i_strToCheck:
            return True
        return False
    def checkFromUserPersonName(self,i_personName):
        if i_personName.isalpha():
            return True
        else:
            return False
    def checkFromUserPersonPassword(self, i_personPassword):
        return True
    def checkFromUserClientBalance(self,i_clientBalance):
        for char in range(len(i_clientBalance)):
            if i_clientBalance[char].isdigit() == False or i_clientBalance < 0:
                return False
        return True

    # Exit bank
    def exitMenu(self, i_clientSocket):
        firstOperation = 0
        self.setDataArrey(firstOperation)
        dataArrey = self.getDataArrey()
        dataArreyStr = cPickle.dumps(dataArrey)
        i_clientSocket.send(dataArreyStr)
        approveExit = i_clientSocket.recv(numberOfBitsToRecv)
        if approveExit == "True":
            print "Good-Bye :)"
            i_clientSocket.close()
        pass