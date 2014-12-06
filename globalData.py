import collections

# IP, PORT related variables
Address = collections.namedtuple('Address', ['ip', 'port', 'cmdTCPPort'])

CMD_TCP_PORT = 9999
ADDRESS = [Address(ip="localhost", port=9990, cmdTCPPort=CMD_TCP_PORT),
           Address(ip="localhost", port=9990+1, cmdTCPPort=CMD_TCP_PORT+1),
           Address(ip="localhost", port=9990+2, cmdTCPPort=CMD_TCP_PORT+2)]

# Paxos related variables
MAJORITY = 2
N_NODE = 3
