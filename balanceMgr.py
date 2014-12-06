import os
import time
import collections
import threading
import Queue
import paxosBasic as paxos

DEPOSIT = "deposit"
WITHDRAW = "withdraw"
INVALID_WITHDRAW = "invalidWithdraw"
LOGFILE = "balance_log"

LogItem = collections.namedtuple('LogItem', ['pid', 'time', 'type', 'amount'])
def convertItem2String(item):
    return " ".join([str(v) for v in item])
 
def convertString2Item(itemStr):
    tokens = itemStr.split()
    return LogItem(int(tokens[0]), float(tokens[1]), tokens[2], int(tokens[3])) 


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


    def getEntry(self, idx):
        """ Return the items of given index. 
       
        getEntry() -> Tuple of LogItem

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
    - deposit(val) -> string
    - withdraw(val) -> string
    - getBalance() -> int
    - getLogItem(idx) -> string
    - debugLog()
    - shutdown()
    - unfial()

    """
    
    def __init__(self, pid):
        """ Initiate a balance manager. """
        # Create local members
        self._pid = pid
        self._logMgr = LogMgr()
        
        nextEntry = self._logMgr.getSize()
        self._paxosNode = paxos.PaxosNode(pid, nextEntry, self.processConsensus, self.getPrevConsensus)
        self._withdrawResultQ = Queue.Queue() 

        # Initiate and start paxos node
        self._paxosNode.start()

    # -----
    # Public functions
    # -----
    def deposit(self, val):
        """ Increase balance by val. It's a blocking function.

        deposit() -> string
        
        Input argument:
            val: int

        Return string to users, so users can know the result. 
        """
        # Create commands
        item = LogItem(pid=self._pid, time=int(time.time()), 
                       type=DEPOSIT, amount=val)
        proposal = convertItem2String(item)

        # Run consensus algorithm
        status = self._paxosNode.request(proposal)

        # Check result
        if(status):
            return "Success. Deposit {0}".format(val)
        else:
            return "Fail. Please retry."

    def withdraw(self, val):
        """ Decrease balance by val. It's a blocking function. 
        
        deposit() -> True/False
        
        Input argument:
            val: int
        
        Return string to users, so users can know the result. 
        """
        # Create commands
        item = LogItem(pid=self._pid, time=int(time.time()), 
                       type=WITHDRAW, amount=val)
        proposal = convertItem2String(item)

        # Run consensus algorithm
        status = self._paxosNode.request(proposal)

        # Check result
        if(status):
            # Consensus algorithm completes. Wait for event to know if balance is enough.
            # result should have been ready in queue
            valid = self._withdrawResultQ.get(timeout=5)
            if(valid):
                msg = "Success. Withdraw {0}".format(val)
            else:
                msg = "Fail. Balance is not enough."
            self._withdrawResultQ.task_done()

        else:
            msg = "Fail. Please retry."
        
        return msg

    def getBalance(self):
        """ Return current balance amount. 
        
        getBalance() -> int
        """
        return self._logMgr.getBalance()
    
    def shutdown(self):
        self._paxosNode.shutdown()
    
    def unfail(self):
        self._paxosNode.start()

    def debugLog(self):
        """ Return log string. """
        result = ""
        for idx in range(self._logMgr.getSize()):
            items = self._logMgr.getEntry(idx)
            entryStr = "|".join([str(item) for item in items])
            result = "{0}\n{1}".format(result, entryStr)
        
        return result

    def getPrevConsensus(self, idx):
        """ Return log item at index 'idx'. 
        
        getPrevConsensus() -> list of string
        """
        
        return [convertItem2String(item) for item in self._logMgr.getEntry(idx)]

    def processConsensus(self, consensus):
        """  This function will be called when reaching a consensus.

        Input argument:
            consensus: list of string 

        When receiving consensus, write it to log.
        """
        # Convert string to LogItem
        items = [convertString2Item(s) for s in sorted(consensus)]

        # Sort it. Deposit commands will be before withdraw commands
        items = sorted(items, key=lambda item: item.type)

        # Check all items and prepare to update log
        balance = self.getBalance()
        validItems = []
        for item in items:
            if(item.type == DEPOSIT):
                # deposit, no further check is required
                balance += item.amount
                validItems.append(item)

            elif(item.type == WITHDRAW):
                # withdraw, first check if balance is enough. if it's not enough,
                # then discard this command.
                valid = (balance >= item.amount)
                if(valid):
                    balance -= item.amount
                    validItems.append(item)
                else:
                    invalidItem = LogItem(pid=item.pid, time=item.time, 
                                        type=INVALID_WITHDRAW, amount=item.amount)
                    validItems.append(invalidItem)
            elif(item.type == INVALID_WITHDRAW):
                validItems.append(item)
            else: 
                print "Unexpected entry"
        # Update log
        self._logMgr.append(validItems)
