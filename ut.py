import unittest
import Bank

class serverTest(unittest.TestCase):
    bank = Bank.BankLogic()
    def test1(self):
        self.failIf(self.bank.checkFromUserClientBalance("ABC"))
        pass
    def test2(self):
        self.failUnless(self.bank.checkFromUserClientBalance("0"))
        pass