

check roundIdx and current round. See function _checkRound() for detail.
        
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
