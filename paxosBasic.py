
import SocketServer, socket 
import threading
import Queue
import random
import globalData as gb

class BallotNum():
    def __init__(self, pid, num):
        self.pid = pid
        self.num = num

    def increase(self):
        self.num += random.randint(1,5)

    def __cmp__(self, obj):
        if(self.num < obj.num):
            return -1
        elif(self.num > obj.num):
            return 1
        else:
            if(self.pid < obj.pid):
                return -1
            elif(self.pid > obj.pid):
                return 1
            else:
                return 0
        
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
        t = threading.Thread(target=self.server._receive, args=(data,)) 
        t.start()
        #self.server._receive(data)


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
    INQUIRE = '5'
    RESULT = '6'
    def __init__(self, node):
        """ Initiate a TCP server. 

        Input:
            balanceMgr : BalanceMgr
            serverAddress : a tuple (ip, port)
        """
        # local variables
        self._node = node
        self._pid = node._pid
        self._active = False

        # base class's constructor
        #serverAddress = (gb.ADDRESS[self._pid].ip, gb.ADDRESS[self._pid].port)
        serverAddress = ('', gb.ADDRESS[self._pid].port)
        SocketServer.TCPServer.__init__(self, serverAddress, PaxosRequestHandler, bind_and_activate=False)
        

    # -----
    # Public functions
    # -----    
    def start(self):
        """ Create a new thread that listens to incoming connection. """
        # create new socket
        self.socket = socket.socket(self.address_family,
                                    self.socket_type)
        self.server_bind()
        self.server_activate()
        # thread that runs self.serve_forever
        self.thread = threading.Thread(target=self.serve_forever)
        self.thread.setDaemon(True)
        self.thread.start()
        self._active = True

    def shutdown(self):
        SocketServer.TCPServer.shutdown(self)
        # close socket
        self.server_close()
        self._active = False

    # -----
    # Functions related to paxos message
    # -----
    def sendPrepare(self, roundIdx, ballotNum, val):
        """ Send prepare to all acceptors. 
        
        sendPrepare() -> True/False

        Return True is majority is active.
        Otherwise, return False.
        """
        msgList = [Messenger.PREPARE, self._pid, roundIdx, ballotNum.pid, ballotNum.num, val]
        msg = self._myJoin(msgList)
        majorityActive = self._broadcast(msg)

        return majorityActive

    def sendPromise(self, targetPid, roundIdx, ballotNum, acceptedBallotNum, acceptedVal):
        """ Send promise to one proposer. """
        msgList = [Messenger.PROMISE, self._pid, roundIdx, ballotNum.pid, ballotNum.num, 
                   acceptedBallotNum.pid, acceptedBallotNum.num, acceptedVal]
        msg = self._myJoin(msgList)
        self._send(targetPid, msg)

    def sendAccept(self, roundIdx, ballotNum, val):
        """ Send accept to all acceptors. """
        msgList = [Messenger.ACCEPT, self._pid, roundIdx, ballotNum.pid, ballotNum.num, val]
        msg = self._myJoin(msgList)
        self._broadcast(msg)

    def sendAccepted(self, roundIdx, ballotNum, val):
        """ Send accepted to all learners. """
        msgList = [Messenger.ACCEPTED, self._pid, roundIdx, ballotNum.pid, ballotNum.num, val]
        msg = self._myJoin(msgList)
        self._broadcast(msg)

    def sendDecide(self, roundIdx, val):
        """ Send decide to all learners. """
        msgList = [Messenger.DECIDE, self._pid, roundIdx, val]
        msg = self._myJoin(msgList)
        self._broadcast(msg)
   
    def sendInquire(self, targetPid, myRoundIdx):
        """ Send Inquire message to ask for sync. """
        msgList = [Messenger.INQUIRE, self._pid, myRoundIdx]
        msg = self._myJoin(msgList)
        if(targetPid == None):
            for offset in range(1,gb.N_NODE):
                targetPid = (self._pid + offset )%gb.N_NODE
                noError = self._send(targetPid, msg)
                if(noError):
                    break
        else:
            self._send(targetPid, msg)

    def sendResult(self, targetPid, initRoundIdx, val):
        """ Send previous result(with given index) to target node. """
        msgList = [Messenger.RESULT, self._pid, initRoundIdx, val]
        msg = self._myJoin(msgList)
        self._send(targetPid, msg)

    # -----
    # Private functions
    # -----
    def _myJoin(self, inList):
        """ Return joined string. """
        return ",".join([str(v) for v in inList])

    def _receive(self, msg):
        """ Create a new thread, then dispatch to corresponding functions in PaxosNode. """
        #print "Recieved ", msg
	tokens = msg.split(',')
        msgType = tokens[0]
         
        if(msgType == Messenger.PREPARE):
            # prepare
            senderID, roundIdx, bPid, bNum, val = [int(v) for v in tokens[1:5]]+[tokens[5]]
            self._node.recvPrepare(senderID, roundIdx, BallotNum(bPid, bNum), val)

        elif(msgType == Messenger.PROMISE):
            # promise
            senderID, roundIdx, bPid, bNum, abPid, abNum , val = [int(v) for v in tokens[1:7]] + [tokens[7]]
            self._node.recvPromise(senderID, roundIdx, BallotNum(bPid, bNum),
                                    BallotNum(abPid, abNum), val)

        elif(msgType == Messenger.ACCEPT):
            # accept
            senderID, roundIdx, bPid, bNum, val = [int(v) for v in tokens[1:5]] + [tokens[5]]
            self._node.recvAccept(senderID, roundIdx, BallotNum(bPid, bNum), val)

        elif(msgType == Messenger.ACCEPTED):
            # accepted
            senderID, roundIdx, bPid, bNum, val = [int(v) for v in tokens[1:5]] + [tokens[5]]
            self._node.recvAccepted(senderID, roundIdx, BallotNum(bPid, bNum), val)

        elif(msgType == Messenger.DECIDE):
            # decide
            senderID, roundIdx, val = [int(v) for v in tokens[1:3]] + [tokens[3]]
            self._node.recvDecide(senderID, roundIdx, val)

        elif(msgType == Messenger.INQUIRE):
            # inquire
            senderID, senderRoundIdx = [int(v) for v in tokens[1:3]]
            self._node.recvInquire(senderID, senderRoundIdx)

        elif(msgType == Messenger.RESULT):
            # result
            senderID, initRoundIdx, val = [int(v) for v in tokens[1:3]] + [tokens[3]]
            self._node.recvResult(senderID, initRoundIdx, val)

        else:
            raise ValueError("Unexpected message type: {0}".format(msgType))

    def _broadcast(self, msg):
        """ Send a message to all servers. 
        
        _broadcast() -> True/False

        Return True if majority servers are active.
        Otherwise, return False.

        """
        nActiveServers = 0

        resultQ = Queue.Queue()
        for targetID in range(gb.N_NODE):
            t=threading.Thread(target=self._threadingSend, args=(targetID, msg, resultQ))
            t.start()
        
        for dummy in range(gb.N_NODE):
            noError = resultQ.get()
            if(noError):
                nActiveServers += 1
            if(nActiveServers >= gb.MAJORITY):
                break

        #for targetID in range(gb.N_NODE):
        #    noError = self._send(targetID, msg)
        #    if(noError):
        #        nActiveServers += 1

        return nActiveServers >= gb.MAJORITY

    def _send(self, targetID, msg):
        """ Send a message to target server. 
        
        _send() -> True/False

        Return True if communication is successful.
        Otherwise, return False.
        """
        #print "Is sending something to {0} ... ".format(targetID),msg
        if(not self._active):
            return False
        
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

    def _threadingSend(self, targetID, msg, resultQ):
        """ Send a message to target server. 
        
        _send() -> True/False

        Return True if communication is successful.
        Otherwise, return False.
        """
        #print "Is sending something to {0} ... ".format(targetID),msg
        if(not self._active):
            return False
        
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

        resultQ.put( noError)


class PaxosNode():
    """ This class implements MultiPaxos. 

    Methods for the caller:
    - __init__(pid, processConsensusFunc, readLogFunc)
        : processConsensusFunc(consensus) -> None
            consensus : list of string
        : readLogFunc(idx) -> List of string
            idx : int
    - request(string)
    - start()
    - shutdown()

    This class will create new threads to run Paxos. Once reaching a consensus, 
    'processConsensusFunc' will be called, which is a function that must be passed to the
    constructor. Note that because a consensus can be initiated by other servers, 
    'processConsensusFunc' can be called although 'request' is not called.

    The function 'processConsensusFunc' is guaranteed to be called one time per round.

    """
    def __init__(self, pid, nextRound, processConsensusFunc, readLogFunc):
        """ Initiate a Paxos node. """
        # Unique process ID
        self._pid = pid
        # An interface to receive and send data
        self._msgr = Messenger(self)
        # Hook function executed just after reaching a consensus
        self._processConsensusFunc = processConsensusFunc
        # External function that return log content. readLogFunc(idx) -> item
        self._readLogFunc = readLogFunc
        # Indicate this node is active or not
        self._active = False
        # Multi-thread control
        # -- request may be called from multiple client
        self._requestLock = threading.Lock()
        # -- paxos can be run from request() or receiving messages
        self._paxosLock = threading.Lock()
        # Member variables for multi-paxos
        self._consensusQ = Queue.Queue()
        self._round = nextRound
        # Member variables for proposer
        self._pBallotNum = BallotNum(self._pid, 0)
        self._pNReceived = 0
        self._pHighestBallotNum = BallotNum(0, 0)
        self._pHighestVal = '0'
        self._pDesiredVal = '0'
        # Member variables for acceptor
        self._aBallotNum = BallotNum(0, 0)
        self._aAcceptedBallotNum = BallotNum(0, 0)
        self._aAcceptedVal = '0'
        # Member variables for learner
        self._lBallotNum = BallotNum(0, 0)
        self._lNReceived = 0

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
        # Only one thread can propose a value at one time.
        self._requestLock.acquire()
        
        aquiredRound = None
        isDecided = False
        majorityActive = True 
        while(not isDecided):
            # Start propose
            majorityActive, aquiredRound = self._propose(aquiredRound, val)
            if(not majorityActive):
                break
            
            # Check consensus result
            try:
                while(True):
                    timeout = 2+10*random.random()
                    resultRound, consensus = self._consensusQ.get(timeout=timeout)
                    if(resultRound == aquiredRound):
                        if(val in consensus):
                            isDecided = True
                        else:
                            aquiredRound = None
                        break
                                
            except Queue.Empty:
                # If timeout, then send propose again
                pass

        self._requestLock.release()

        return majorityActive

    def start(self):
        """ Start server. """
        if(not self._active):
            self._msgr.start()
            # Inquire log
            self._msgr.sendInquire(None, self._round)
            self._active = True

    def shutdown(self):
        """ Shutdown server. Stop receiving and sending message. """
        if(self._active):
            self._active = False
            self._msgr.shutdown()

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

                # Find Highest BallotNum and its value
                if(self._pHighestBallotNum < acceptedBallotNum):
                    self._pHighestBallotNum = acceptedBallotNum
                    self._pHighestVal = val
                
                # After receiving from majority, send accept
                if(self._pNReceived == gb.MAJORITY):
                    proposedVal = self._pDesiredVal 
                    if(self._pHighestVal != '0'):
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
        print "Receive prepare at round", roundIdx
        if(self._checkRound(pid, roundIdx, isPrepare=True)):
            # React if received ballot number is greater or equal than current one
            if(ballotNum >= self._aBallotNum):
                self._aBallotNum = ballotNum
                self._msgr.sendPromise(pid, roundIdx, ballotNum, 
                                        self._aAcceptedBallotNum, self._aAcceptedVal)
        self._paxosLock.release()

    def recvAccept(self, pid, roundIdx, ballotNum, val):
        """ Process accept message. It's an acceptor's function in phase two.

        First, check roundIdx and current round. See function _checkRound() for detail.
        
        Before entering paxos algorithm, this function should request a lock to ensure 
        that only one thread is executing this function.

        If received ballot number is less than current one, do nothing. 
        Otherwise, update acceptedBallotNum and send accepted to all nodes.
        """
        self._paxosLock.acquire()
        
        if(self._checkRound(pid, roundIdx)):
            if(ballotNum >= self._aBallotNum):
                self._aAcceptedBallotNum = ballotNum
                self._aAcceptedVal = val
                self._msgr.sendAccepted(roundIdx, ballotNum, val)
        
        self._paxosLock.release()

    def recvAccepted(self, pid, roundIdx, ballotNum, val):
        """ Process accepted message. It's a learner's function in phase two.

        First, check roundIdx and current round. See function _checkRound() for detail.
        
        Before entering paxos algorithm, this function should request a lock to ensure 
        that only one thread is executing this function.

        It's a learner's function in phase two. If received acceptedBallotNum is less than 
        current one, do nothing. Otherwise, record the number of accepted message. If 
        receiving accepted from majority, then send decide to all other nodes.
        """
        self._paxosLock.acquire()

        if(self._checkRound(pid, roundIdx)):
            if(ballotNum > self._lBallotNum):
                self._lBallotNum = ballotNum
                self._lNReceived = 0 
            
            if(self._lBallotNum == ballotNum and self._lNReceived < gb.MAJORITY):
                self._lNReceived += 1
                if(self._lNReceived == gb.MAJORITY):
                    self._msgr.sendDecide(roundIdx, val)
        
        self._paxosLock.release()

    def recvDecide(self, pid, roundIdx, val):
        """ Process decide message. It's a learner's function. 

        First, check roundIdx and current round. See function _checkRound() for detail.
        
        Once receive decide message, current round is completed. If it's the first time 
        receiving decide message, then set completed to true and process consensus. 
        Otherwise, do nothing.
        """
        self._paxosLock.acquire()

        if(self._checkRound(pid, roundIdx)):
            print "Decide at round", roundIdx, ",val:", val
            self._processConcensus(val)

        self._paxosLock.release()

    def recvInquire(self, senderID, senderRoundIdx):
        """ Send all result from senderRoundIdx to the latest round. """
        if(senderRoundIdx >= self._round):
            return
        
        result = "|".join(self._readLogFunc(senderRoundIdx))
        self._msgr.sendResult(senderID, senderRoundIdx, result)
 
    def recvResult(self, senderID, initRoundIdx, val):
        if(initRoundIdx >= self._round):
            self.recvDecide(senderID, initRoundIdx, val)
            self._msgr.sendInquire(senderID, initRoundIdx+1)

    # -----
    # Private functions
    # -----
    def _checkRound(self, senderID, roundIdx, isPrepare=False):
        """ Check received roundIdx and do corresponding action.
        
        If roundIdx < current round, then return False.
        If roundIdx == current round, then return True.
        If roundIdx > current round, then ask for missing result and return False.
        """
        if(roundIdx < self._round):
            # The request is from previous round. This is common because the message may
            # come from the rest of majority.
            if(isPrepare):
                # If it's preparation, then this message may come from a node that just comes back
                self.recvInquire(senderID, roundIdx)
            return False
        elif(roundIdx == self._round):
            return True
        else:
            # Current node is recovering from failure so it is not up-to-date
            self._msgr.sendInquire(senderID, self._round)
            return False
            

    def _propose(self, aquiredRound, val):
        """ Send propose message to all other Paxos nodes. 
        
        It's a proposer's function in phase one. This function will send propose message with 
        increased ballot number to all other Paxos nodes.
        """
        # if current round is not completed
        # -- increase ballot number 
        # -- send message
        self._paxosLock.acquire()
        
        majorityActive = True
        if(aquiredRound == None):
            # First propose of this round
            aquiredRound = self._round
            self._pDesiredVal = val
            self._prepareNewPropose()
            majorityActive = self._msgr.sendPrepare(self._round, self._pBallotNum, val)
        elif(aquiredRound == self._round):
            # Subsequent propose of the same round
            self._prepareNewPropose()
            majorityActive = self._msgr.sendPrepare(self._round, self._pBallotNum, val)
        else:
            # Current round is completed but the caller missed it
            # Do nothing. Let caller check the result.
            pass

        self._paxosLock.release()
        return majorityActive, aquiredRound

    def _prepareNewPropose(self):
        self._pBallotNum.increase()
        self._pNReceived = 0
        self._pHighestBallotNum = BallotNum(self._pid, 0)
        self._pHighestVal = '0' 

    def _startNewRound(self, nextRound):
        """ Reset all paxos related variables. """
        self._round = nextRound
        self._pBallotNum = BallotNum(self._pid, 0)
        self._pNReceived = 0
        self._pHighestBallotNum = BallotNum(0, 0)
        self._pHighestVal = '0'
        self._pDesiredVal = '0'
        self._aBallotNum = BallotNum(0, 0)
        self._aAcceptedBallotNum = BallotNum(0, 0)
        self._aAcceptedVal = '0'
        self._lBallotNum = BallotNum(0, 0)
        self._lNReceived = 0 

    def _processConcensus(self, val):
        """ This function will be called after reaching a consensus. """

        vals = val.split('|')
        # Call the hook function _processConsensusFunc, which will update log
        self._processConsensusFunc(vals)
        
        # Send result to inform another thread in request()
        self._consensusQ.put((self._round ,vals))

        # Current round is end. Start a new round
        self._startNewRound(self._round+1)
