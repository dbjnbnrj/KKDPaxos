import threading
import SocketServer
import sys
import logging
import socket
from Queue import Queue


logging.basicConfig(level=logging.DEBUG,
                    format='%(name)s: %(message)s',
                    )

class Messenger:
	def __init__(self, owner):
		self.owner = owner

	def recv(self, data):
		print('messenger recieves data',data)
		if "PREPARE" in data:
			b = data.split()
			self.owner.send_promise(int(b[1]))
		if "ACK" in data:
			s = data.split()
			self.owner.recieve_ack( int(s[1]), int(s[2]), int(s[3]) ) 
		

class PaxosRequestHandler(SocketServer.BaseRequestHandler):
    
    def __init__(self, request, client_address, server):
        self.logger = logging.getLogger('PaxosRequestHandler')
        print('__init__')
        SocketServer.BaseRequestHandler.__init__(self, request, client_address, server)
        return

    def setup(self):
        print('setup')
        return SocketServer.BaseRequestHandler.setup(self)

    def handle(self):
        print('handle')

        # Echo the back to the client
        data = self.request.recv(1024)
        print('recv()->"%s"', data)
	self.server.owner.messenger.recv(data)
        self.request.send(data)
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
	def __init__(self, address, data):
		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    		s.connect(address)
		 
   		 # Send the data
		print('sending msg %s', data)
    		len_sent = s.send(data)

    		# Receive a response
    		print('waiting for response')
    		#response = s.recv(len_sent)
    		#print('response from server: "%s"', response)

    		# Clean up
    		print('closing socket')
    		s.close()

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
		self.acceptedVal = 0
		self.highestBallot = 0
		self.highestValue = 0
		self.currentValue = ""
		self.acks = 0
		self.quorum = 1

	def run(self):
		print('running node')
		t = threading.Thread(target=self.server.serve_forever)
		t.setDaemon(True)
		t.start()
		while True:
			self.currentValue = self.q.get()
			self.send_propose()
			self.q.task_done()

	def send_propose(self):
		self.ballotNum += 1
		msg = "PREPARE: "+str(self.ballotNum)
		print self.server.server_address
		client = PaxosClient(self.server.server_address, msg)
	
	def send_promise(self, b):
		if b >= self.aBallotNum:
			self.aBallotNum = b
		msg = "ACK {0} {1} {2}".format(b,self.acceptedNum,self.acceptedVal)
		print self.server.server_address
		client = PaxosClient(self.server.server_address, msg)
	
	def recieve_ack(self, BallotNum, b, val):
		if( BallotNum == self.ballotNum):
			self.acks += 1
			val = 0
			if(self.highestBallot < b):
				self.highestBallot = b
				self.highestValue = val
			if(self.acks >= self.quorum):
				if self.highestValue != None:
					self.currentValue = str(self.highestValue)
				self.acks = 0
				msg = "ACCEPT {0} {1}".format(BallotNum, self.currentValue)
				client = PaxosClient(self.server.server_address, msg)
		

if __name__ == '__main__':

    addr = 'localhost'
    port = 0
    n = Node(addr, port)
    n.q.put("deposit")
    n.start()
