import threading
from random import randint
import collections
import socket

Address = collections.namedtuple('Address', ['ip', 'port', 'cmdTCPPort'])
ADDRESS = [Address(ip="54.86.219.155", port=9990, cmdTCPPort=9999),
           Address(ip="54.149.109.117", port=9990, cmdTCPPort=9999),
           Address(ip="54.77.248.101", port=9990, cmdTCPPort=9999),
           Address(ip="54.169.73.215", port=9990, cmdTCPPort=9999),
           Address(ip="54.94.231.250", port=9990, cmdTCPPort=9999)]


command = ["deposit", "withdraw"]



def worker(address):
    """thread worker function"""
    
    
    # Connect to server and send data
    
    for dummy in range(30):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect(address)
        msg = "{0} {1}".format(command[randint(0,1)], randint(1,100))
        print dummy, msg
        sock.sendall(msg)
        sock.recv(1024)
        sock.close()

threads = []
for i in range(4):
    addr = (ADDRESS[i].ip, ADDRESS[i].cmdTCPPort)
    t = threading.Thread(target=worker, args=(addr,))
    threads.append(t)
    t.start()
