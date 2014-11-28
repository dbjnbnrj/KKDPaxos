import collections

DEPOSIT = 0
WITHDRAW = 1

LogItem = collections.namedtuple('LogItem', ['pid', 'time', 'type', 'amount'])

class LogMgr():
    """ A class to handle log. 

    Log should be written into disc to overcome failures. However, this 
    implementation use main memory for simplicity.
    """
    def __init__(self):
        self.log = []
        self.balance = 0

    def appendLog(self, item):
        """ Append an item to log, then update balance. """
        pass

    def getBalance(self):
        """ Return current balance. """
        pass

    def getNextIdx(self):
        """ Return the next available index. """
        pass

    def __getitem__(self, idx):
        """ Overload operator []. Return the item of given index. """
        pass

class BalanceMgr():
    """ Class for managing balance.

    This class use paxos to ensure that operations are identical in all replica.
    
    Methods for the caller:

    - __init__()
    - deposit(val) -> SUCCESS/FAIL
    - withdraw(val) -> SUCCESS/FAIL
    - getBalance() -> int
    - getLogItem(idx) -> LogItem

    """
    
    def __init__(self, paxosNode):
        """ Initiate a balance manager. """
        self._paxosNode = node
        self._logmgr = LogMgr()

    # -----
    # Public functions
    # -----
    def deposit(self, val):
        """ Increase balance by val . It's a blocking function. 
        Return: SUCCESS/FAIL
        
        """

    def withdraw(self, val):
        """ Decrease balance by val. It's a blocking function. 
        Return: SUCCESS/FAIL
        
        Note: Overwithdraw is allowed.

        """

    def getBalance(self):
        """ Return current balance amount. """
        pass

    def getLogItem(self, idx):
        """ Return log item at index 'idx'. """
        pass

    def processConsensus(self, consensusRound, item):
        """  This function will be called when reaching a consensus.

        The function is responsible for
        1) Send message back to _requestConsensus(), so it can know the result of 
           current round.
        2) Update log
        
        """
    # -----
    # Private functions
    # -----
    def _requestConsensus(self, item):
        """ Run consensus algorithm until "action, val" is decided. It may take severals 
            consensus rounds.

        Return SUCCESS if reaching a consensus with proposed value.
               FAIL if not able to run consensus algorithm. (ex. majority nodes are down)

        This is a blocking function. A thread will be blocked until the proposed value is 
        decided.
        
        """
