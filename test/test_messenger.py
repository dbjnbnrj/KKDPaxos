import os, sys
import unittest
from cStringIO import StringIO
import Queue
import socket

this_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append( os.path.dirname(this_dir) )

from paxosBasic import Messenger
import globalData as gb

class Foo():
    def __init__(self):
        self._pid = 0
 
address = (gb.ADDRESS[0].ip, gb.ADDRESS[0].port)
msgr = Messenger(Foo(),address)
msgr.start()


class TestSequenceFunctions(unittest.TestCase):
   
    def setUp(self):
        self._pid = 0
        self.q = Queue.Queue()
        
        self.msgr = msgr
        self.msgr._node = self

    def printResult(self, msg):
        self.q.put(msg)

    def test_sendPrepare(self):
        roundIdx, ballotNum = 123, 456
        self.msgr.sendPrepare(roundIdx, ballotNum)
        result = self.q.get(timeout=1)
        self.assertEqual(result, (self._pid, roundIdx, ballotNum))
       
    def recvPrepare(self, senderID, roundIdx, ballotNum):
        self.q.put((senderID, roundIdx, ballotNum))

    def test_sendPromise(self):
        targetID, roundIdx, ballotNum, b, val = 0,2,3,4,'5'
        self.msgr.sendPromise(targetID, roundIdx, ballotNum, b, val)
        result = self.q.get(timeout=1)
        self.assertEqual(result, (self._pid, roundIdx, ballotNum, b, val))

    def recvPromise(self, senderID, roundIdx, ballotNum, b, val):
        self.q.put((senderID, roundIdx, ballotNum, b, val))

    def test_sendAccept(self):
        roundIdx, ballotNum, val = 8,10,'12'
        self.msgr.sendAccept(roundIdx, ballotNum, val)
        result = self.q.get(timeout=1)
        self.assertEqual(result, (self._pid, roundIdx, ballotNum, val))
    
    def recvAccept(self, senderID, roundIdx, ballotNum, val):
        self.q.put((senderID, roundIdx, ballotNum, val))
       
    def test_sendAccepted(self):
        roundIdx, ballotNum, val = 88,1110,'1112'
        self.msgr.sendAccepted(roundIdx, ballotNum, val)
        result = self.q.get(timeout=1)
        self.assertEqual(result, (self._pid, roundIdx, ballotNum, val))
    
    def recvAccepted(self, senderID, roundIdx, ballotNum, val):
        self.q.put((senderID, roundIdx, ballotNum, val))
       
    def test_sendDecide(self):
        roundIdx, val = 51110,'1112'
        self.msgr.sendDecide(roundIdx, val)
        result = self.q.get(timeout=1)
        self.assertEqual(result, (self._pid, roundIdx, val))
    
    def recvDecide(self, senderID, roundIdx, val):
        self.q.put((senderID, roundIdx, val))

if __name__ == '__main__':
    unittest.main()

self.assertEqual(result, (self._pid, roundIdx, ballotNum, b, val))

