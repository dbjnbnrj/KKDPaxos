import cmd
import string, sys

class CLI(cmd.Cmd):

    def __init__(self, balanceMgr):
        cmd.Cmd.__init__(self)
        self.prompt = '> '
        self._balanceMgr = balanceMgr

    # ===================
    # The following are valid commands
    # ===================
    def do_deposit(self, arg):
        try:
            val = int(arg)
        except ValueError:
            self.stdout.write("Amount must be an interger. Received: {0}\n".format(arg))
            return
        
        if(val < 0):
            self.stdout.write("Amount must be non-negative. Received: {0}\n".format(arg))
            return
        
        self._balanceMgr.deposit(val)
        print "Depositing ",arg, "!"


    def help_deposit(self):
        print "syntax: deposit [amount]",
        print "-- = deposits amount in the bank"

    # -------------------
    def do_withdraw(self, arg):
        try:
            val = int(arg)
        except ValueError:
            self.stdout.write("Amount must be an interger. Received: {0}\n".format(arg))
            return
        
        if(val < 0):
            self.stdout.write("Amount must be non-negative. Received: {0}\n".format(arg))
            return
        
        self._balanceMgr.withdraw(val)
        print "Withdraw ", arg, "!"

    def help_withdraw(self):
        print "syntax: withdraw [amount]",
        print "-- = withdraws amount in the bank"

    # -------------------
    def do_balance(self, arg):
        balance = self._balanceMgr.getBalance()
        print "Balance: ", balance, "!"

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
