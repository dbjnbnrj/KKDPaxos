
import SocketServer, socket 
import threading
import globalData as gb

class PaxosRequestHandler(SocketServer.BaseRequestHandler):
    """
    The RequestHandler class for ClientTCPServer.

    It is instantiated once per connection to the server, and must
    override the handle() method to implement communication to the
    client.
    """
    def handle(self):
        # get date from client
        data = self.request.recv(1024).strip()
        
        # let its server process it
        self.server._receive(data)


class Messenger(SocketServer.TCPServer):
    """ A class that is responsible to paxos communication.

    This server will start a new thread to listen to incoming connection after 
    executing start(). To stop the server, execute shutdown()

    """
    PREPARE = '0'
    PROMISE = '1'
    ACCEPT = '2'
    ACCEPTED = '3'
    DECIDE = '4'
    def __init__(self, node, serverAddress):
        """ Initiate a TCP server. 

        Input:
            balanceMgr : BalanceMgr
            serverAddress : a tuple (ip, port)
        """
        # base class's constructor
        SocketServer.TCPServer.__init__(self, serverAddress, PaxosRequestHandler)
        
        # local variables
        self._node = node
        self._pid = node._pid

        # thread that runs self.serve_forever
        self.thread = threading.Thread(target=self.serve_forever)
        self.thread.setDaemon(True)

    # -----
    # Public functions
    # -----    
    def start(self):
        """ Create a new thread that listens to incoming connection. """
        self.thread.start()

    # To stop running, call Messenger.shutdown()

    # -----
    # Functions related to paxos message
    # -----
    def sendPrepare(self, roundIdx, ballotNum):
        """ Send prepare to all acceptors. 
        
        sendPrepare() -> True/False

        Return True is majority is active.
        Otherwise, return False.
        """
        msgList = [Messenger.PREPARE, self._pid, roundIdx, ballotNum]
        msg = self._myJoin(msgList)
        majorityActive = self._broadcast(msg)

        return majorityActive

    def sendPromise(self, targetPid, roundIdx, ballotNum, acceptedBallotNum, acceptedVal):
        """ Send promise to one proposer. """
        msgList = [Messenger.PROMISE, self._pid, roundIdx, ballotNum, 
                   acceptedBallotNum, acceptedVal]
        msg = self._myJoin(msgList)
        self._send(targetPid, msg)

    def sendAccept(self, roundIdx, ballotNum, val):
        """ Send accept to all acceptors. """
        msgList = [Messenger.ACCEPT, self._pid, roundIdx, ballotNum, val]
        msg = self._myJoin(msgList)
        self._broadcast(msg)

    def sendAccepted(self, roundIdx, acceptedBallotNum, val):
        """ Send accepted to all learners. """
        msgList = [Messenger.ACCEPTED, self._pid, roundIdx, acceptedBallotNum, val]
        msg = self._myJoin(msgList)
        self._broadcast(msg)

    def sendDecide(self, roundIdx, val):
        """ Send decide to all learners. """
        msgList = [Messenger.DECIDE, self._pid, roundIdx, val]
        msg = self._myJoin(msgList)
        self._broadcast(msg)
    
    # -----
    # Private functions
    # -----
    def _myJoin(self, inList):
        """ Return joined string. """
        return ",".join([str(v) for v in inList])

    def _receive(self, msg):
        """ Dispatch to corresponding functions in PaxosNode. """
        tokens = msg.split(',')
        msgType = tokens[0]
        
        if(msgType == Messenger.PREPARE):
            # prepare
            senderID, roundIdx, ballotNum = [int(v) for v in tokens[1:4]]
            self._node.recvPrepare(senderID, roundIdx, ballotNum)

        elif(msgType == Messenger.PROMISE):
            # promise
            senderID, roundIdx, ballotNum, b , val = [int(v) for v in tokens[1:5]] + [tokens[5]]
            self._node.recvPromise(senderID, roundIdx, ballotNum, b, val)

        elif(msgType == Messenger.ACCEPT):
            # accept
            senderID, roundIdx, ballotNum, val = [int(v) for v in tokens[1:4]] + [tokens[4]]
            self._node.recvAccept(senderID, roundIdx, ballotNum, val)

        elif(msgType == Messenger.ACCEPTED):
            # accepted
            senderID, roundIdx, ballotNum, val = [int(v) for v in tokens[1:4]] + [tokens[4]]
            self._node.recvAccepted(senderID, roundIdx, ballotNum, val)

        elif(msgType == Messenger.DECIDE):
            # decide
            senderID, roundIdx, val = [int(v) for v in tokens[1:3]] + [tokens[3]]
            self._node.recvDecide(senderID, roundIdx, val)

        else:
            raise ValueError("Unexpected message type: {0}".format(msgType))

    def _broadcast(self, msg):
        """ Send a message to all servers. 
        
        _broadcast() -> True/False

        Return True if majority servers are active.
        Otherwise, return False.

        """
        nActiveServers = 0
        for targetID in range(gb.N_NODE):
            noError = self._send(targetID, msg)
            if(noError):
                nActiveServers += 1

        return nActiveServers >= gb.MAJORITY

    def _send(self, targetID, msg):
        """ Send a message to target server. 
        
        _send() -> True/False

        Return True if communication is successful.
        Otherwise, return False.
        """
        noError = True
        # Create a socket (SOCK_STREAM means a TCP socket)
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
        # Get target address
        address = (gb.ADDRESS[targetID].ip, gb.ADDRESS[targetID].port)
        try:
            # Connect to server and send data
            sock.connect(address)
            sock.sendall(msg)
        except socket.error:
            noError = False 
        finally:
            sock.close()

        return noError


#class PaxosNode():
#    """ This class implements MultiPaxos. 
#
#    Methods for the caller:
#    - __init__(processConsensusFunc)
#        : processConsensusFunc: a function taking two inputs, round index and consensus value
#    - request(val)
#
#    This class will create new threads to run Paxos. Once reaching a consensus, 
#    'processConsensusFunc' will be called, which is a function that must be passed to the
#    constructor. Note that because a consensus can be initiated by other servers, 
#    'processConsensusFunc' may be called although 'request' is not called.
#
#    The function 'processConsensusFunc' is guaranteed to be called only once per consensus run.
#
#    """
#    def __init__(self, pid, processConsensusFunc, readLogFunc):
#        """ Initiate a Paxos node. """
#        # Unique process ID
#        self._pid = pid
#        # An interface to receive and send data
#        self._messenger = Messenger(self)
#        # Hook function executed just after reaching a consensus
#        self._processConsensusFunc = processConsensusFunc
#        # External function that return log content. readLogFunc(idx) -> item
#        self._readLogFunc = readLogFunc
#        # History that saves past consensus value
#        self._history = []
#        # Member variables for consensus algorithm
#        self._round = 0
#        self._roundCompelted = False
#        self._BallotNum = 0
#        self._acceptedBallotNum = 0
#        pass
#
#    # -----
#    # Functions called by external client
#    # -----
#    def request(self, val):
#        """ Run consensus algorithm until the given value is decided.
#        
#        Return False when not able to running consensus algorithm. (majority nodes are down)
#        Return True, otherwise.
#
#        This is a blocking function. When two threads call request at the same time, one 
#        thread will be blocked until the other thread's proposed value is decided.
#
#        """
#        print "Get request:" + val
#        return True
#
#    # -----
#    # Functions called by Messenger
#    # -----
#    def recvPromise(self, pid, roundIdx, ballotNum, acceptedBallotNum, val):
#        """ Process promise message. It's a proposer's function. 
#        
#        First, check roundIdx and current round. See function _checkRound() for detail.
#        
#        Before entering paxos algorithm, this function should request a lock to ensure 
#        that only one thread is executing this function.
#
#        If received ballot number is less than current ballot number, then neglect it. 
#        Otherwise, after receiving promise from majority, send accept to all nodes.
#        """
#        pass
#
#    def recvPrepare(self, pid, roundIdx, ballotNum):
#        """ Process prepare message. It's an acceptor's function in phase one. 
#        
#        First, check roundIdx and current round. See function _checkRound() for detail.
#        
#        Before entering paxos algorithm, this function should request a lock to ensure 
#        that only one thread is executing this function.
#
#        It received ballot number is less than current one, do nothing.
#        Otherwise, update ballot number and send promise back.
#        """
#        pass
#
#    def recvAccept(self, pid, roundIdx, ballotNum, val):
#        """ Process accept message. It's an acceptor's function in phase two.
#
#        First, check roundIdx and current round. See function _checkRound() for detail.
#        
#        Before entering paxos algorithm, this function should request a lock to ensure 
#        that only one thread is executing this function.
#
#        If received ballot number is less than current one, do nothing. 
#        Otherwise, update acceptedBallotNum and send accepted to all nodes.
#        """
#        pass
#
#    def recvAccepted(self, pid, roundIdx, acceptedBallotNum, val):
#        """ Process accepted message. It's a learner's function in phase two.
#
#        First, check roundIdx and current round. See function _checkRound() for detail.
#        
#        Before entering paxos algorithm, this function should request a lock to ensure 
#        that only one thread is executing this function.
#
#        It's a learner's function in phase two. If received acceptedBallotNum is less than 
#        current one, do nothing. Otherwise, record the number of accepted message. If 
#        receiving accepted from majority, then send decide to all other nodes.
#        """
#        pass
#
#    def recvDecide(self, pid, roundIdx, val):
#        """ Process decide message. It's a learner's function. 
#
#        First, check roundIdx and current round. See function _checkRound() for detail.
#        
#        Once receive decide message, current round is completed. If it's the first time 
#        receiving decide message, then set completed to true and process consensus. 
#        Otherwise, do nothing.
#        """
#        pass
#
#    # -----
#    # Private functions
#    # -----
#    def _checkRound(self, roundIdx):
#        """ Check received roundIdx and do corresponding action. This is a blocking function.
#        
#        If roundIdx < current round, then return False.
#        If roundIdx == current round, then return True.
#        If roundIdx > current round, then wait until roundIdx == current round
#        """
#        pass
#
#    def _propose(self, val):
#        """ Send propose message to all other Paxos nodes. 
#        
#        It's a proposer's function in phase one. This function will send propose message with 
#        increased ballot number to all other Paxos nodes.
#        """
#        # if current round is not completed
#        # -- increase ballot number 
#        # -- send message
#        pass
#
#    def _processConcensus(self):
#        #self._processConsensusFunc(roundIdx, val)
#        pass
