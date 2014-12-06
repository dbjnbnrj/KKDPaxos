from paxosBasic import PaxosNode, BallotNum
import globalData as gb

class PaxosNodeImprov(PaxosNode):
    def __init__(self, pid, nextRound, processConsensusFunc, readLogFunc):
        PaxosNode.__init__(self, pid, nextRound, processConsensusFunc, readLogFunc)
        """ Initiate a Paxos node. """
        # Member variables for proposer
        self._pCollectedVal = '0'
        # Member variables for acceptor
        self._aWatchedVal = '0'
    
    # -----
    # Functions called by Messenger
    # -----
    def recvPromise(self, pid, roundIdx, ballotNum, acceptedBallotNum, val):
        """ Process promise message. It's a proposer's function. 
        
        First, check roundIdx and current round. See function _checkRound() for detail.
        
        Before entering paxos algorithm, this function should request a lock to ensure 
        that only one thread is executing this function.

        If received ballot number is less than current ballot number, then neglect it. 
        Otherwise, after receiving promise from majority, send accept to all nodes.
        """
        self._paxosLock.acquire()

        if(self._checkRound(pid, roundIdx)):
            # React only when received ballot number is equal to current one
            if(ballotNum == self._pBallotNum and self._pNReceived < gb.MAJORITY):
                # Increase number of received promise
                self._pNReceived += 1

                # Collect watched value
                if(self._pHighestBallotNum.num == 0 and acceptedBallotNum.num == 0):
                    self._pCollectedVal = self._unionValue(self._pCollectedVal, val)
                
                # Find Highest BallotNum and its value
                if(self._pHighestBallotNum < acceptedBallotNum):
                    self._pHighestBallotNum = acceptedBallotNum
                    self._pHighestVal = val
                
                # After receiving from majority, send accept
                if(self._pNReceived == gb.MAJORITY):
                    proposedVal = self._unionValue(self._pDesiredVal, self._pCollectedVal) 
                    if(self._pHighestBallotNum.num != 0):
                        proposedVal = self._pHighestVal
                    self._msgr.sendAccept(roundIdx, ballotNum, proposedVal)

        self._paxosLock.release()


    def recvPrepare(self, pid, roundIdx, ballotNum, val):
        """ Process prepare message. It's an acceptor's function in phase one. 
        
        First, check roundIdx and current round. See function _checkRound() for detail.
        
        Before entering paxos algorithm, this function should request a lock to ensure 
        that only one thread is executing this function.

        If received ballot number is less than current one, do nothing.
        Otherwise, update ballot number and send promise back.
        """
        self._paxosLock.acquire()
        if(self._checkRound(pid, roundIdx, isPrepare=True)):
            # React if received ballot number is greater or equal than current one
            
            self._aWatchedVal = self._unionValue(self._aWatchedVal, val)
            if(ballotNum >= self._aBallotNum):
                self._aBallotNum = ballotNum
                if(self._aAcceptedBallotNum.num == 0):
                    value = self._aWatchedVal
                else:
                    value = self._aAcceptedVal
                self._msgr.sendPromise(pid, roundIdx, ballotNum, 
                                        self._aAcceptedBallotNum, value)
            
        self._paxosLock.release()

    # -----
    # Private functions
    # -----
    def _unionValue(self, val1, val2):
        item = set()
        if(val1 != '0'): 
            item = item.union(set(val1.split('|')))
        if(val2 != '0'):
            item = item.union(set(val2.split('|')))
        return "|".join(item)
        
    def _prepareNewPropose(self):
        self._pBallotNum.increase()
        self._pNReceived = 0
        self._pHighestBallotNum = BallotNum(self._pid, 0)
        self._pHighestVal = '0' 

    def _startNewRound(self, nextRound):
        """ Reset all paxos related variables. """
        PaxosNode._startNewRound(self, nextRound)
        self._pCollectedVal = '0'
        self._aWatchedVal = '0'

    def _processConcensus(self, val):
        """ This function will be called after reaching a consensus. """

        # Call the hook function _processConsensusFunc, which will update log
        result = val.split('|')

        self._processConsensusFunc(result)
        
        # Send result to inform another thread in request()
        self._consensusQ.put((self._round ,result))

        # Current round is end. Start a new round
        self._startNewRound(self._round+1)
