import threading
from random import randint
import collections
import socket

Address = collections.namedtuple('Address', ['ip', 'port', 'cmdTCPPort'])
CMD_TCP_PORT = 9999
ADDRESS = [Address(ip="localhost", port=9990, cmdTCPPort=CMD_TCP_PORT),
           Address(ip="localhost", port=9990+1, cmdTCPPort=CMD_TCP_PORT+1),
           Address(ip="localhost", port=9990+2, cmdTCPPort=CMD_TCP_PORT+2)]

command = ["deposit", "withdraw"]



def worker(address):
    """thread worker function"""
    
    
    # Connect to server and send data
    
    for dummy in range(100):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect(address)
        msg = "{0} {1}".format(command[randint(0,1)], randint(1,100))
        print dummy, msg
        sock.sendall(msg)
        sock.recv(1024)
        sock.close()

threads = []
for i in range(3):
    addr = (ADDRESS[i].ip, ADDRESS[i].cmdTCPPort)
    t = threading.Thread(target=worker, args=(addr,))
    threads.append(t)
    t.start()
