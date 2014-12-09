import collections

# IP, PORT related variables
Address = collections.namedtuple('Address', ['ip', 'port', 'cmdTCPPort'])

ADDRESS = [Address(ip="54.86.219.155", port=9990, cmdTCPPort=9999),
           Address(ip="54.149.109.117", port=9990, cmdTCPPort=9999),
           Address(ip="54.77.248.101", port=9990, cmdTCPPort=9999),
           Address(ip="54.169.73.215", port=9990, cmdTCPPort=9999),
           Address(ip="54.94.231.250", port=9990, cmdTCPPort=9999)]

#CMD_TCP_PORT = 9999
#ADDRESS = [Address(ip="localhost", port=9990, cmdTCPPort=CMD_TCP_PORT),
#           Address(ip="localhost", port=9990+1, cmdTCPPort=CMD_TCP_PORT+1),
#           Address(ip="localhost", port=9990+2, cmdTCPPort=CMD_TCP_PORT+2)]

# Paxos related variables
MAJORITY = 3
N_NODE = 5
