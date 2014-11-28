import balanceMgr
import paxos
import clientInterface


class BalanceSystem():

    def __init__(self):
        self.pid = self.determinePid()

        self.balanceMgr = balanceMgr.BalanceMgr(self.pid)
        self.paxosNode = paxos.PaxosNode(self.pid, 
                            self.balanceMgr.processConsensus,
                            self.balanceMgr.getLogItem)
        self.cli = clientInterface.CLI(self.balanceMgr)

        self.balanceMgr.setPaxosNode(self.paxosNode)


    def determinePid(self):
        """ Return process ID. """
        return 0

    def run(self):
        """ Start balance system. """
        self.cli.cmdloop()

if(__name__ == "__main__"):
    balanceSystem = BalanceSystem()
    balanceSystem.run()
