import threading
import SocketServer
import sys
import socket
from Queue import Queue

class Messenger:
	def __init__(self, owner):
		self.owner = owner

	def send_promise(self, msg):
		self.client = PaxosClient(self.owner.server.server_address)
		self.client.send(msg)
		self.client.close()

	def send_prepare(self, msg):
		self.client = PaxosClient(self.owner.server.server_address)
		self.client.send(msg)
		self.client.close()


	def send_accept(self, msg):
		self.client = PaxosClient(self.owner.server.server_address)
		self.client.send(msg)
		self.client.close()

	def send_decide(self, msg):
		self.client = PaxosClient(self.owner.server.server_address)
		self.client.send(msg)
		self.client.close()

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
		self.pInstance = 0
		self.aInstance = 0
		self.acks = 0
		self.accepts = 0
		self.quorum = 1
		self.isLeader = False
		self.event = threading.Event()

	def run(self):
		t = threading.Thread(target=self.server.serve_forever)
		t.setDaemon(True)
		t.start()
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
		self.messenger.send_prepare(msg)
	
	def send_promise(self, b):
		if b >= self.aBallotNum:
			self.aBallotNum = b
		msg = "ACK {0} {1} {2}".format(b, self.aInstance, self.acceptedVal)
		self.messenger.send_promise(msg)
	
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
		self.messenger.send_accept(msg)
	
	def recieve_accept(self, N, I, V):
		if self.accepts >= self.quorum:
			msg = "DECIDE {0}".format(V)
			self.messenger.send_decide(msg)
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
