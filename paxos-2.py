import threading
import SocketServer
import sys
import logging
import socket

logging.basicConfig(level=logging.DEBUG,
                    format='%(name)s: %(message)s',
                    )

class PaxosRequestHandler(SocketServer.BaseRequestHandler):
    
    def __init__(self, request, client_address, server):
        self.logger = logging.getLogger('PaxosRequestHandler')
        self.logger.debug('__init__')
        SocketServer.BaseRequestHandler.__init__(self, request, client_address, server)
        return

    def setup(self):
        self.logger.debug('setup')
        return SocketServer.BaseRequestHandler.setup(self)

    def handle(self):
        self.logger.debug('handle')

        # Echo the back to the client
        data = self.request.recv(1024)
        self.logger.debug('recv()->"%s"', data)
        self.request.send(data)
        return

    def finish(self):
        self.logger.debug('finish')
        return SocketServer.BaseRequestHandler.finish(self)


class PaxosServer(SocketServer.TCPServer):
    
    def __init__(self, server_address, handler_class=PaxosRequestHandler):
        SocketServer.TCPServer.__init__(self, server_address, handler_class)
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

#class PaxosClient:

class Node(threading.Thread):
	def __init__(self, addr, port):
		threading.Thread.__init__(self)
		self.address= (addr, port)
		self.server = PaxosServer(self.address, PaxosRequestHandler)
	
	def run(self):
		logger.debug('Running Node')
		t = threading.Thread(target=self.server.serve_forever)
		t.setDaemon(True)
		t.start()



if __name__ == '__main__':

    addr = 'localhost'
    port = 0
    n = Node(addr, port)
    n.start()
    ip, port = n.server.server_address 
    logger = logging.getLogger('client')
    logger.info('Server on %s:%s', ip, port)

    # Connect to the server
    logger.debug('creating socket')
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    logger.debug('connecting to server')
    s.connect((addr, port))

    # Send the data
    message = 'Hello, world'
    logger.debug('sending data: "%s"', message)
    len_sent = s.send(message)

    # Receive a response
    logger.debug('waiting for response')
    response = s.recv(len_sent)
    logger.debug('response from server: "%s"', response)

    # Clean up
    logger.debug('closing socket')
    s.close()
    logger.debug('closing node')
    n.server.socket.close()
    logger.debug('done')
