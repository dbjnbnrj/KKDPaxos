import balanceMgr
import clientInterface

class BalanceSystem():

    def __init__(self):
        self.pid = self.determinePid()

        self.balanceMgr = balanceMgr.BalanceMgr(self.pid)

        address = ("localhost", 9999)
        self.clientTCP = clientInterface.ClientTCPServer(self.balanceMgr, address)
        self.cli = clientInterface.CLI(self.balanceMgr)


    def determinePid(self):
        """ Return process ID. """
        return 0

    def run(self):
        """ Start balance system. """
        self.clientTCP.start()
        self.cli.cmdloop()

if(__name__ == "__main__"):
    balanceSystem = BalanceSystem()
    balanceSystem.run()
