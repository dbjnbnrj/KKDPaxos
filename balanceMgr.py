import os
import collections
import threading
import pickle

DEPOSIT = 0
WITHDRAW = 1
LOGFILE = "balance_log.txt"

LogItem = collections.namedtuple('LogItem', ['pid', 'time', 'type', 'amount'])

class LogMgr():
    """ A class to handle log. 

    Log should be written into disc to overcome failures.
    """
  
    # To check whether the file is corrupted or not, we add ENDING_STR at 
    # the end of each line.
    ENDING_STR = "OK"
    def __init__(self):
        self._log = []
        self._balance = 0 
        
        # Read log
        self._recover()
    
    # -----
    # Public functions
    # -----
    def appendLog(self, item):
        """ Append an item to log, then update balance. 
        
        Input argument:
            item: LogItem
        """
        # Calculate result balance
        balance = self._balance
        if(item.type == DEPOSIT):
            balance += item.amount
        elif(item.type == WITHDRAW):
            balance -= item.amount

        # Create a message that will be written in log
        itemStr = self._convertItem2String(item) 
        msg = "{0};{1}".format(itemStr, balance)

        # Update local log and balance
        self._log.append(item)
        self._balance = balance

        # Write hard drive
        with open(LOGFILE, 'a') as fp:
            fp.write(msg+";"+self.ENDING_STR+"\n")
            fp.flush()
    
    def getBalance(self):
        """ Return current balance. 
        
        getBalance() -> int
        """
        return self._balance

    def getItem(self, idx):
        """ Return the LogItem of given index. 
       
        getItem() -> LogItem

        Return None if there is no item of given index. It's expected that when a 
        caller aquires an item, the item is already in the log.
        """
        if(idx < len(self._log)):
            return self._log[idx]
        else:
            return None

    # -----
    # Private functions
    # -----
    def _recover(self):
        """ Read log from hard drive. """
        # Check if file exists
        if(not os.path.isfile(LOGFILE)):
            return
        
        # Read file
        with open(LOGFILE, 'r') as fp:
            lines = [ line.strip() for line in fp.readlines() ]
        
        # Check if there is corrupted line
        # We can get balance from the latest line
        lastValidLine = ""
        for idx, line in enumerate(lines):
            if(not line.endswith(LogMgr.ENDING_STR)):
                # If it's corrupted, then stop reading log
                print "Loading log... Line {0} is corrupted.".format(idx+1)
                break
            else:
                # Else, add item to log
                itemStr = line.split(';')[0]
                self._log.append(self._convertString2Item(itemStr))
                lastValidLine = line
        
        # Get balance
        balanceStr = lastValidLine.split(';')[1]
        self._balance = int(balanceStr)            

    def _convertItem2String(self, item):
        return " ".join([str(v) for v in item])
     
    def _convertString2Item(self, itemStr):
        tokens = itemStr.split()
        return LogItem(int(tokens[0]), int(tokens[1]), int(tokens[2]), int(tokens[3])) 

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
    
    def __init__(self, pid):
        """ Initiate a balance manager. """
        self._pid = pid
        self._paxosNode = None
        self._logmgr = LogMgr()

    # -----
    # Public functions
    # -----
    def setPaxosNode(self, node):
        self._paxosNode = node

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
        return 0

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
