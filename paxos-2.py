import threading
import SocketServer
import sys
import socket
from Queue import Queue

class Messenger:
	def __init__(self, owner):
		self.owner = owner

	def send_promise(self, msg):
		client = PaxosClient(self.owner.server.server_address)
		client.send(msg)
		client.close()

	def send_propose(self, msg):
		client = PaxosClient(self.owner.server.server_address)
		client.send(msg)
		client.close()

	def send_accept(self, msg):
		client = PaxosClient(self.owner.server.server_address)
		client.send(msg)
		client.close()

	def send_decide(self, msg):
		client = PaxosClient(self.owner.server.server_address)
		client.send(msg)
		client.close()

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
			self.owner.recieve_accept(int(s[1]), s[2])
		if "DECIDE" in data:
			s = data.split()
			self.owner.recieve_decide(s[1])
			 
		

class PaxosRequestHandler(SocketServer.BaseRequestHandler):
    
    def __init__(self, request, client_address, server):
        print('__init__')
        SocketServer.BaseRequestHandler.__init__(self, request, client_address, server)
        return

    def setup(self):
        print('setup')
        return SocketServer.BaseRequestHandler.setup(self)

    def handle(self):
        print('handle')
        data = self.request.recv(1024)
        print('recv()->"%s"', data)
	self.server.owner.messenger.recv(data)
        return

    def finish(self):
        print('finish')
        return SocketServer.BaseRequestHandler.finish(self)


class PaxosServer(SocketServer.TCPServer):
    
    def __init__(self, owner, server_address, handler_class=PaxosRequestHandler):
        SocketServer.TCPServer.__init__(self, server_address, handler_class)
        self.owner = owner
	return

    def server_activate(self):
        print('server_activate')
        SocketServer.TCPServer.server_activate(self)
        return

    def serve_forever(self):
        print('waiting for request')
        while True:
            self.handle_request()
        return

    def handle_request(self):
        print('handle_request')
        return SocketServer.TCPServer.handle_request(self)

    def verify_request(self, request, client_address):
        print('verify_request(%s, %s)', request, client_address)
        return SocketServer.TCPServer.verify_request(self, request, client_address)

    def process_request(self, request, client_address):
        print('process_request(%s, %s)', request, client_address)
        return SocketServer.TCPServer.process_request(self, request, client_address)

    def server_close(self):
        print('server_close')
        return SocketServer.TCPServer.server_close(self)

    def finish_request(self, request, client_address):
        print('finish_request(%s, %s)', request, client_address)
        return SocketServer.TCPServer.finish_request(self, request, client_address)

    def close_request(self, request_address):
        print('close_request(%s)', request_address)
        return SocketServer.TCPServer.close_request(self, request_address)

class PaxosClient:
	def __init__(self, address):
		self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    		self.client.connect(address)
	
	def send(self, msg):	 
		print('sending msg %s', msg)
    		len_sent = self.client.send(msg)
    		
	def close(self):
		print('closing socket')
    		self.client.close()

class Node(threading.Thread):
	def __init__(self, addr, port):
		threading.Thread.__init__(self)
		self.address= (addr, port)
		self.server = PaxosServer(self, self.address, PaxosRequestHandler)
		self.q = Queue()
		self.messenger = Messenger(self)
		self.ballotNum = 0
		self.aBallotNum = 0
		self.acceptedNum = 0
		self.acceptedVal = "0"
		self.highestBallot = 0
		self.highestValue = "0"
		self.currentValue = "0"
		self.acks = 0
		self.accepts = 0
		self.quorum = 1

	def run(self):
		t = threading.Thread(target=self.server.serve_forever)
		t.setDaemon(True)
		t.start()
		while True:
			self.currentValue = self.q.get()
			print "Current Value is ",self.currentValue
			self.send_propose()
			self.q.task_done()

	def send_propose(self):
		self.ballotNum += 1
		msg = "PREPARE: "+str(self.ballotNum)
		self.messenger.send_propose(msg)
	
	def send_promise(self, b):
		if b >= self.aBallotNum:
			self.aBallotNum = b
		msg = "ACK {0} {1} {2}".format(b,self.acceptedNum,self.acceptedVal)
		self.messenger.send_promise(msg)
	
	def recieve_ack(self, BallotNum, b, val):
		if( BallotNum == self.ballotNum):
			self.acks += 1
			val = 0
			if(self.highestBallot < b):
				self.highestBallot = b
				self.highestValue = val
			if(self.acks >= self.quorum):
				if self.highestValue != "0":
					self.currentValue = str(self.highestValue)
				self.acks = 0
				msg = "ACCEPT {0} {1}".format(BallotNum, self.currentValue)
				self.messenger.send_accept(msg)
	
	def recieve_accept(self, b, v):
		if self.accepts >= self.quorum:
			msg = "DECIDE {0}".format(v)
			self.messenger.send_decide(msg)
		else:
			if b >= self.ballotNum:
				self.accepts += 1
				self.acceptedNum = b
				self.acceptedValue = v
				msg =  "ACCEPT {0} {1}".format(self.ballotNum, self.currentValue)
				self.messenger.send_accept(msg)

	def recieve_decide(self, v):
		print "Decided on value {0}".format(v)
		self.currentValue = v

if __name__ == '__main__':

    addr = 'localhost'
    port = 0
    n = Node(addr, port)
    n.q.put("deposit100")
    n.start()
