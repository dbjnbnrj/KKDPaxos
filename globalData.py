import collections

# IP, PORT related variables
Address = collections.namedtuple('Address', ['ip', 'port', 'cmdTCPPort'])

CMD_TCP_PORT = 9999
ADDRESS = [Address(ip="localhost", port=9990, cmdTCPPort=CMD_TCP_PORT)]

# Paxos related variables
MAJORITY = 1
N_NODE = 1
