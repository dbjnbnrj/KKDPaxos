import socket
import sys
import threading

class PaxosServer(threading.Thread):

        def __init__(self):
                self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

                # Bind the socket to the address given on the command line
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
                        	while True:
                                	data = connection.recv(4096)
                                	print >>sys.stderr, 'received "%s"' % data
                                	if data:
                                        	connection.sendall(data)
                                	else:
                                        	break
                	finally:
				connection.close()

class PaxosClient(threading.Thread):

        def __init__(self, address, message):
                self.address = address
                self.message = message
		threading.Thread.__init__(self)

        def run(self):
                # Connect the socket to the port on the server given by the caller
                server_address = (self.address)
                print >>sys.stderr, 'connecting to %s port %s' % server_address

                self.sock.connect(server_address)
                try:
                        print >>sys.stderr, 'sending "%s"' % message
                        self.sock.sendall(message)
                        data = self.sock.recv(2096)
                        print >>sys.stderr, 'received "%s"' % data

                finally:
                        self.sock.close()

s = PaxosServer()
s.start()
