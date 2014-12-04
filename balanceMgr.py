import os
import time
import collections
import threading
import paxos

DEPOSIT = 0
WITHDRAW = 1
LOGFILE = "balance_log.txt"

LogItem = collections.namedtuple('LogItem', ['pid', 'time', 'type', 'amount'])
def convertItem2String(item):
    return " ".join([str(v) for v in item])
 
def convertString2Item(itemStr):
    tokens = itemStr.split()
    return LogItem(int(tokens[0]), int(tokens[1]), int(tokens[2]), int(tokens[3])) 


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
    def append(self, items):
        """ Append items to a single log entry, then update balance. 
        
        Input argument:
            items: Tuple of LogItem
        """
        balance = self._balance
        for item in items:
            # Calculate result balance
            if(item.type == DEPOSIT):
                balance += item.amount
            elif(item.type == WITHDRAW):
                balance -= item.amount

        # Create a message that will be written in log
        itemsStr = ",".join(convertItem2String(item) for item in items)
        msg = "{0};{1}".format(itemsStr, balance)

        # Update local log and balance
        self._log.append(tuple(items))
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
        """ Return the items of given index. 
       
        getItem() -> Tuple of LogItem

        Return None if there is no item of given index. It's expected that when a 
        caller aquires an item, the item is already in the log.
        """
        if(idx < len(self._log)):
            return self._log[idx]
        else:
            return None

    def getSize(self):
        """ Return the number of log items. """
        return len(self._log)

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
                itemsStr = line.split(';')[0]
                self._log.append(tuple(convertString2Item(itemStr) for itemStr in itemsStr.split(',')))
                lastValidLine = line
        
        # Get balance
        balanceStr = lastValidLine.split(';')[1]
        self._balance = int(balanceStr)            

class BalanceMgr():
    """ Class for managing balance.

    This class use paxos to ensure that operations are identical in all replica.
    
    Methods for the caller:

    - __init__()
    - deposit(val) -> True/False
    - withdraw(val) -> True/False
    - getBalance() -> int
    - getLogItem(idx) -> string

    """
    
    def __init__(self, pid):
        """ Initiate a balance manager. """
        self._pid = pid
        self._logMgr = LogMgr()
        self._paxosNode = paxos.PaxosNode(pid, self.processConsensus, self.getPrevConsensus)

    # -----
    # Public functions
    # -----
    def deposit(self, val):
        """ Increase balance by val. It's a blocking function.

        deposit() -> True/False
        
        Input argument:
            val: int

        Return True if deposition is completed. Otherwise, return False.
        """
        item = LogItem(pid=self._pid, time=int(time.time()), 
                       type=DEPOSIT, amount=val)
        proposal = convertItem2String(item)
        return self._paxosNode.request(proposal)

    def withdraw(self, val):
        """ Decrease balance by val. It's a blocking function. 
        
        deposit() -> True/False
        
        Input argument:
            val: int
        
        Return True if deposition is completed. Otherwise, return False.
        Note: Overwithdraw is allowed.
        """
        item = LogItem(pid=self._pid, time=int(time.time()), 
                       type=WITHDRAW, amount=val)
        proposal = convertItem2String(item)
        return self._paxosNode.request(proposal)

    def getBalance(self):
        """ Return current balance amount. 
        
        getBalance() -> int
        """
        return self._logMgr.getBalance()

    def getPrevConsensus(self, idx):
        """ Return log item at index 'idx'. 
        
        getPrevConsensus() -> string
        """
        return convertItem2String(self._logMgr.getItem(idx))

    def processConsensus(self, consensus):
        """  This function will be called when reaching a consensus.

        Input argument:
            consensus: string 

        When receiving consensus, write it to log.
        """
        item = convertString2Item(consensus)
        self._logMgr.append(item)
