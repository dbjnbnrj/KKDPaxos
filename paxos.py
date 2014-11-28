
class Messenger():
    def __init__(self, node):
        self._node = node
        self._pid = node._pid

    # -----
    # Functions called by PaxosNode
    # -----
    def sendPrepare(self, roundIdx, ballotNum):
        """ Send prepare to all acceptors. """
        pass

    def sendPromise(self, targetPid, roundIdx, ballotNum, acceptedBallotNum, val):
        """ Send promise to one proposer. """
        pass

    def sendAccept(self, roundIdx, ballotNum, val):
        """ Send accept to all acceptors. """
        pass

    def sendAccepted(self, roundIdx, acceptedBallotNum, val):
        """ Send accepted to all learners. """
        pass

    def sendDecide(self, roundIdx, val):
        """ Send decide to all learners. """
        pass
    
    # -----
    # Private functions
    # -----
    def _receive(self, msg):
        """ Dispatch to corresponding functions in PaxosNode. """


class PaxosNode():
    """ This class implements MultiPaxos. 

    Methods for the caller:
    - __init__(processConsensusFunc)
        : processConsensusFunc: a function taking two inputs, round index and consensus value
    - request(val)

    This class will create new threads to run Paxos. Once reaching a consensus, 
    'processConsensusFunc' will be called, which is a function that must be passed to the
    constructor. Note that because a consensus can be initiated by other servers, 
    'processConsensusFunc' may be called although 'request' is not called.

    The function 'processConsensusFunc' is guaranteed to be called only once per consensus run.

    """
    def __init__(self, pid, processConsensusFunc, readLogFunc):
        """ Initiate a Paxos node. """
        # Unique process ID
        self._pid = pid
        # An interface to receive and send data
        self._messenger = Messenger(self)
        # Hook function executed just after reaching a consensus
        self._processConsensusFunc = processConsensusFunc
        # External function that return log content. readLogFunc(idx) -> item
        self._readLogFunc = readLogFunc
        # History that saves past consensus value
        self._history = []
        # Member variables for consensus algorithm
        self._round = 0
        self._roundCompelted = False
        self._BallotNum = 0
        self._acceptedBallotNum = 0
        pass

    # -----
    # Functions called by external client
    # -----
    def request(self, val):
        """ Run consensus algorithm until the given value is decided.
        
        Return False when not able to running consensus algorithm. (majority nodes are down)
        Return True, otherwise.

        This is a blocking function. When two threads call request at the same time, one 
        thread will be blocked until the other thread's proposed value is decided.

        """
        pass

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
        pass

    def recvPrepare(self, pid, roundIdx, ballotNum):
        """ Process prepare message. It's an acceptor's function in phase one. 
        
        First, check roundIdx and current round. See function _checkRound() for detail.
        
        Before entering paxos algorithm, this function should request a lock to ensure 
        that only one thread is executing this function.

        It received ballot number is less than current one, do nothing.
        Otherwise, update ballot number and send promise back.
        """
        pass

    def recvAccept(self, pid, roundIdx, ballotNum, val):
        """ Process accept message. It's an acceptor's function in phase two.

        First, check roundIdx and current round. See function _checkRound() for detail.
        
        Before entering paxos algorithm, this function should request a lock to ensure 
        that only one thread is executing this function.

        If received ballot number is less than current one, do nothing. 
        Otherwise, update acceptedBallotNum and send accepted to all nodes.
        """
        pass

    def recvAccepted(self, pid, roundIdx, acceptedBallotNum, val):
        """ Process accepted message. It's a learner's function in phase two.

        First, check roundIdx and current round. See function _checkRound() for detail.
        
        Before entering paxos algorithm, this function should request a lock to ensure 
        that only one thread is executing this function.

        It's a learner's function in phase two. If received acceptedBallotNum is less than 
        current one, do nothing. Otherwise, record the number of accepted message. If 
        receiving accepted from majority, then send decide to all other nodes.
        """
        pass

    def recvDecide(self, pid, roundIdx, val):
        """ Process decide message. It's a learner's function. 

        First, check roundIdx and current round. See function _checkRound() for detail.
        
        Once receive decide message, current round is completed. If it's the first time 
        receiving decide message, then set completed to true and process consensus. 
        Otherwise, do nothing.
        """
        pass

    # -----
    # Private functions
    # -----
    def _checkRound(self, roundIdx):
        """ Check received roundIdx and do corresponding action. This is a blocking function.
        
        If roundIdx < current round, then return False.
        If roundIdx == current round, then return True.
        If roundIdx > current round, then wait until roundIdx == current round
        """
        pass

    def _propose(self, val):
        """ Send propose message to all other Paxos nodes. 
        
        It's a proposer's function in phase one. This function will send propose message with 
        increased ballot number to all other Paxos nodes.
        """
        # if current round is not completed
        # -- increase ballot number 
        # -- send message
        pass

    def _processConcensus(self):
        #self._processConsensusFunc(roundIdx, val)
        pass
