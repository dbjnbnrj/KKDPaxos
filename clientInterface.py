import cmd
import string, sys

class CLI(cmd.Cmd):

    def __init__(self, balanceMgr, paxosNode):
        cmd.Cmd.__init__(self)
        self.prompt = '> '
        self.balanceMgr = balanceMgr
        self.paxosNode = paxosNode

    def processMgrReturn(self, mgrReturn):
        """ Hook method to process return value from balanceMgr. """
        pass

    # ===================
    # The following are valid commands
    # ===================
    def do_deposit(self, arg):
        print "Depositing ",arg, "!"

    def help_deposit(self):
        print "syntax: deposit [amount]",
        print "-- = deposits amount in the bank"

    # -------------------
    def do_withdraw(self, arg):
        print "Withdraw ", arg, "!"

    def help_withdraw(self):
        print "syntax: withdraw [amount]",
        print "-- = withdraws amount in the bank"

    # -------------------
    def do_balance(self, arg):
        print "Balance: ", self.amount, "!"

    def help_balance(self):
        print "syntax: balance",
        print "-- = gets User Balance"

    # -------------------
    def do_fail(self):
        print "Fail"

    def help_fail(self):
        print "syntax: fail",
        print "-- = Simulate a server failure"

    # -------------------
    def do_unfail(self):
        print "Unfail"

    def help_unfail(self):
        print "syntax: unfail",
        print "-- = resume from failure"

    # -------------------
    def do_quit(self, arg):
        sys.exit(1)

    def help_quit(self):
        print "syntax: quit",
        print "-- terminates the application"

    # shortcuts
    do_q = do_quit
