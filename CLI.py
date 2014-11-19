import cmd
import string, sys

class CLI(cmd.Cmd):

    amount = 0
    def __init__(self):
        cmd.Cmd.__init__(self)
        self.prompt = '> '
        self.amount = 0

    def do_deposit(self, arg):
        print "Depositing ",arg, "!"
        self.amount += int(arg)

    def help_deposit(self):
        print "syntax: Deposit [amount]",
        print "-- = deposits amount in the bank"

    def do_withdraw(self, arg):
        print "Withdraw ", arg, "!"
        self.amount -= int(arg)

    def help_withdraw(self):
        print "syntax: Withdraw [amount]",
        print "-- = withdraws amount in the bank"

    def do_balance(self, arg):
        print "Balance: ", self.amount, "!"

    def help_balance(self):
        print "syntax: Balance",
        print "-- = gets User Balance"

    def do_quit(self, arg):
        sys.exit(1)

    def help_quit(self):
        print "syntax: quit",
        print "-- terminates the application"

    # shortcuts
    do_q = do_quit

#
# try it out

cli = CLI()
cli.cmdloop()
