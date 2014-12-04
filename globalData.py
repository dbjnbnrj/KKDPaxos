import collections

Address = collections.namedtuple('Address', ['ip', 'port'])

CLIENT_TCP_PORT = 9999
ADDRESS = [Address(ip="localhost", port=9990)]
