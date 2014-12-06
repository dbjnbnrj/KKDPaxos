import threading
import SocketServer
import sys
import socket
from Queue import Queue

SERVERS = ['172.30.0.85','172.30.0.179']

class Messenger:
	def __init__(self, owner):
		self.owner = owner

	def send(self, msg):
		for S in SERVERS: 
			client = PaxosClient((S,10000), msg)
			client.start()

	def recv(self, data):
		print('messenger recieves data',data)
		if "PREPARE" in data:
			b = data.split()
			self.owner.send_promise( int(b[1]), int(b[2]) )
		if "ACK" in data:
			s = data.split()
			self.owner.recieve_ack( int(s[1]), int(s[2]), int(s[3]), s[4] )
		if "ACCEPT" in data:
			s = data.split()
			self.owner.recieve_accept(int(s[1]), s[2], s[3])
		if "DECIDE" in data:
			s = data.split()
			self.owner.recieve_decide(int(s[1]), s[2])
			 
		

class PaxosServer(threading.Thread):

        def __init__(self, node):
                self.node = node
		self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.server_address = ('', 10000)
                self.sock.bind(self.server_address)
                threading.Thread.__init__(self)

        def run(self):
                print >>sys.stderr, 'server: starting up on %s port %s' % self.sock.getsockname()
                self.sock.listen(1)

                while True:
                        print >>sys.stderr, 'server: waiting for a connection'
                        connection, client_address = self.sock.accept()
                        try:
                                print >>sys.stderr, 'server: client connected:', client_address
                                data = connection.recv(4096)
                                print >>sys.stderr, 'server: received "%s"' % data
                                if data:
					self.node.messenger.recv(data)

			finally:
				print "server: closing connection"

class PaxosClient(threading.Thread):
	def __init__(self, address, message):
		self.address = address
		self.message = message
		self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		threading.Thread.__init__(self)
		
	def run(self):
		# Connect the socket to the port on the server given by the caller
		print >>sys.stderr, 'client: connecting to %s port %s' % self.address

		self.sock.connect(self.address)
		
		try:
    			print >>sys.stderr, 'client: sending "%s"' % self.message
    			self.sock.sendall(self.message)
        		self.sock.recv(4096)

		finally:
			self.sock.close()


class Node(threading.Thread):
	def __init__(self, addr, port):
		threading.Thread.__init__(self)
		""" These are node specific variables """
		self.address= (addr, port)
		self.server = PaxosServer(self)
		self.q = Queue()
		self.messenger = Messenger(self)
		
		""" These are proposer specific variables """
		self.pballotNum = 0
		self.highestBallot = 0
		self.highestValue = "0"
		self.currentValue = "0"
		self.acks = 0
		self.accepts = 0

		""" These are acceptor specific variables """
		self.aballotNum = 0
		self.acceptedNum = 0
		self.acceptedVal = "0"

		self.instance = 0
		self.quorum = 2
		self.event = threading.Event()

	def run(self):
		self.server.start()
		while True:
			self.event.clear()
			self.currentValue = self.q.get()
			print "Current Value is ",self.currentValue
			self.send_prepare()
			self.event.wait()
			self.q.task_done()

	def reset(self):
                """ These are proposer specific variables """
                self.pballotNum = 0
                self.highestBallot = 0
                self.highestValue = "0"
                self.currentValue = "0"
                self.acks = 0
                self.accepts = 0

                """ These are acceptor specific variables """
                self.aballotNum = 0
                self.acceptedNum = 0
                self.acceptedVal = "0"

	def send_prepare(self):
		self.pballotNum += 1
		msg = "PREPARE: {0} {1}".format(self.instance, self.pballotNum)
		self.messenger.send(msg)
	
	def send_promise(self, instance, pBallotNum):
		if instance != self.instance:
			print "expected instance {0}; actual instance: {1}".format(self.instance, instance)
		elif pBallotNum >= self.aballotNum:
			self.aballotNum = pBallotNum
			msg = "ACK {0} {1} {2} {3}".format(self.instance, self.aballotNum, self.acceptedNum, self.acceptedVal)
			self.messenger.send(msg)
	
	def recieve_ack(self, instance, aBallotNum, acceptedNum, acceptedVal):
		if( instance == self.instance):
			self.acks += 1
			
			if self.highestBallot < acceptedNum:
				self.highestBallot = acceptedNum
				self.highestValue = acceptedVal

			if(self.acks >= self.quorum):
				if self.highestValue != "0":
					self.currentValue = str(self.highestValue)
				self.send_accept(self.instance, aBallotNum, self.currentValue)

	def send_accept(self, instance, ballotNum, value):
		msg = "ACCEPT {0} {1} {2}".format(instance, ballotNum, value)
		self.messenger.send(msg)
	
	def recieve_accept(self, instance, ballotNum, value):
		if instance == self.instance:
			if self.accepts >= self.quorum:
				msg = "DECIDE {0} {1}".format(instance, value)
				self.messenger.send(msg)
			else:
				self.accepts += 1
				self.send_accept(instance, ballotNum, value)

	def recieve_decide(self, instance, value):
		if instance == self.instance:
			print "Decided on value {0} in round {1}".format(value, instance)
			self.event.set()
			self.currentValue = value
			self.instance = instance + 1
			self.reset()

if __name__ == '__main__':
    addr = 'localhost'
    port = 10000
    n = Node(addr, port)
    n.start()
