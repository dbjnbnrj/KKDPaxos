import threading
import SocketServer
import sys
import socket
from Queue import Queue

SERVERS = ['172.30.0.85']

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
			self.owner.send_promise(int(b[1]))
		if "ACK" in data:
			s = data.split()
			self.owner.recieve_ack( int(s[1]), int(s[2]), s[3] )
		if "ACCEPT" in data:
			s = data.split()
			self.owner.recieve_accept(int(s[1]), s[2], s[3])
		if "DECIDE" in data:
			s = data.split()
			self.owner.recieve_decide(s[1])
			 
		

class PaxosServer(threading.Thread):

        def __init__(self, node):
                self.node = node
		self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.server_address = ('', 10000)
                self.sock.bind(self.server_address)
                threading.Thread.__init__(self)

        def run(self):
                print >>sys.stderr, 'starting up on %s port %s' % self.sock.getsockname()
                self.sock.listen(1)

                while True:
                        print >>sys.stderr, 'waiting for a connection'
                        connection, client_address = self.sock.accept()
                        try:
                                print >>sys.stderr, 'client connected:', client_address
                                data = connection.recv(4096)
                                print >>sys.stderr, 'received "%s"' % data
                                if data:
					self.node.messenger.recv(data)

			finally:
				print "Closing connection"

class PaxosClient(threading.Thread):
	def __init__(self, address, message):
		self.address = address
		self.message = message
		self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		threading.Thread.__init__(self)
		
	def run(self):
		# Connect the socket to the port on the server given by the caller
		print >>sys.stderr, 'connecting to %s port %s' % self.address

		self.sock.connect(self.address)
		
		try:
    			print >>sys.stderr, 'sending "%s"' % self.message
    			self.sock.sendall(self.message)
        		data = self.sock.recv(4096)
        		print >>sys.stderr, 'received "%s"' % data

		finally:
			self.sock.close()


class Node(threading.Thread):
	def __init__(self, addr, port):
		threading.Thread.__init__(self)
		self.address= (addr, port)
		self.server = PaxosServer(self)
		self.q = Queue()
		self.messenger = Messenger(self)
		self.ballotNum = 0
		self.aBallotNum = 0
		self.acceptedNum = 0
		self.acceptedVal = "0"
		self.highestBallot = 0
		self.highestValue = "0"
		self.currentValue = "0"
		self.pInstance = 0
		self.aInstance = 0
		self.acks = 0
		self.accepts = 0
		self.quorum = 1
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

	def send_prepare(self):
		self.ballotNum += 1
		msg = "PREPARE: "+str(self.ballotNum)
		self.messenger.send(msg)
	
	def send_promise(self, b):
		if b >= self.aBallotNum:
			self.aBallotNum = b
		msg = "ACK {0} {1} {2}".format(b, self.aInstance, self.acceptedVal)
		self.messenger.send(msg)
	
	def recieve_ack(self, BallotNum, instance, val):
		if( BallotNum == self.ballotNum):
			self.acks += 1
			self.pInstance = instance
			self.highestValue = val
			if(self.acks >= self.quorum):
				if self.highestValue != "0":
					self.currentValue = str(self.highestValue)
				self.isLeader = True
				self.acks = 0
				self.send_accept(BallotNum, self.pInstance, self.currentValue)

	def send_accept(self,N, I, V):
		msg = "ACCEPT {0} {1} {2}".format(N, I, V)
		self.messenger.send(msg)
	
	def recieve_accept(self, N, I, V):
		if self.accepts >= self.quorum:
			msg = "DECIDE {0}".format(V)
			self.messenger.send(msg)
		else:
			self.accepts += 1
			self.send_accept(N,I,V)

	def recieve_decide(self, V):
		print "Decided on value {0}".format(V)
		self.event.set()
		self.currentValue = V

if __name__ == '__main__':

    addr = 'localhost'
    port = 0
    n = Node(addr, port)
    n.q.put("deposit100")
    n.q.put("deposit200")
    n.start()
    n.q.put("withdraw400")
