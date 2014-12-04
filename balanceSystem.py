import sys
import globalData as gb
import balanceMgr
import clientInterface

class BalanceSystem():

    def __init__(self):
        self.pid = self.determinePid()

        self.balanceMgr = balanceMgr.BalanceMgr(self.pid)

        clientTCPAddress = (gb.ADDRESS[self.pid].ip, gb.CLIENT_TCP_PORT)
        self.clientTCP = clientInterface.ClientTCPServer(self.balanceMgr, clientTCPAddress)
        self.cli = clientInterface.CLI(self.balanceMgr)


    def determinePid(self):
        """ Return process ID. 
        
        Besides returning process ID, this function also check whether corresponding 
        IP is correct.
        """
        pid = int(sys.argv[1])
        print "PID is {0}. Corresponding address is {1}".format(pid, gb.ADDRESS[pid])
        return pid

    def run(self):
        """ Start balance system. """
        self.clientTCP.start()
        self.cli.cmdloop()

if(__name__ == "__main__"):
    balanceSystem = BalanceSystem()
    balanceSystem.run()
