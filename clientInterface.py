import cmd
import SocketServer 
import threading

class CLI(cmd.Cmd):
    """ This class implements command line interface of balance system. 
    
    CAUTION: Do not use print() in this class. Please use self.stdout.write() instead.

    Valid commands:
        - deposit [val]
        - withdraw [val]
        - balance
        - fail
        - unfail
        - print
        - quit, q, ctrl+d
    """
    
    def __init__(self, balanceMgr):
        """ Initiate a balance command line interface. """
        cmd.Cmd.__init__(self)
        self.prompt = '> '
        self._balanceMgr = balanceMgr

    # ===================
    # The following are valid commands
    # ===================
    def do_deposit(self, arg):
        try:
            val = int(arg)
        except ValueError:
            self.stdout.write("Amount must be an interger. Received: {0}\n".format(arg))
            return
        
        if(val < 0):
            self.stdout.write("Amount must be non-negative. Received: {0}\n".format(arg))
            return
        
        self.stdout.write(self._balanceMgr.deposit(val)+"\n")
        #self.stdout.write("Depositing {0}!\n".format(val))

    def help_deposit(self):
        msg = "syntax: deposit [amount]\n"
        msg += "\t-- = deposits amount in the bank\n"
        self.stdout.write(msg)

    # -------------------
    def do_withdraw(self, arg):
        try:
            val = int(arg)
        except ValueError:
            self.stdout.write("Amount must be an interger. Received: {0}\n".format(arg))
            return
        
        if(val < 0):
            self.stdout.write("Amount must be non-negative. Received: {0}\n".format(arg))
            return
        
        self.stdout.write(self._balanceMgr.withdraw(val)+"\n")
        #self.stdout.write("Withdraw {0}!\n".format(val))

    def help_withdraw(self):
        msg = "syntax: withdraw [amount]\n"
        msg += "\t-- = withdraws amount in the bank\n"
        self.stdout.write(msg)

    # -------------------
    def do_balance(self, arg):
        balance = self._balanceMgr.getBalance()
        self.stdout.write("Balance: {0}!\n".format(balance))

    def help_balance(self):
        msg = "syntax: balance\n"
        msg += "\t-- = gets user balance\n"
        self.stdout.write(msg)

    # -------------------
    def do_fail(self, arg):
        self._balanceMgr.shutdown()
        self.stdout.write("Fail\n")

    def help_fail(self):
        msg = "syntax: fail\n"
        msg += "\t-- = simulate a server failure\n"
        self.stdout.write(msg)

    # -------------------
    def do_unfail(self, arg):
        self._balanceMgr.unfail()
        self.stdout.write("Unfail\n")

    def help_unfail(self):
        msg = "syntax: unfail\n"
        msg += "\t-- = resume from failure\n"
        self.stdout.write(msg)

    # -------------------
    def do_print(self, arg):
        log = self._balanceMgr.debugLog()
        self.stdout.write("{0}\n".format(log))

    def help_print(self):
        msg = "syntax: print\n"
        msg += "\t-- = print current log\n"
        self.stdout.write(msg)

    # -------------------
    def do_quit(self, arg):
        self._balanceMgr.shutdown()
        self.stdout.write("\nSee you ~\n")
        return True

    def help_quit(self):
        msg = "syntax: quit\n"
        msg += "\t-- = terminates the application\n"
        self.stdout.write(msg)

    # shortcuts
    do_q = do_quit
    do_EOF = do_quit


class ClientRequestHandler(SocketServer.BaseRequestHandler):
    """
    The RequestHandler class for ClientTCPServer.

    It is instantiated once per connection to the server, and must
    override the handle() method to implement communication to the
    client.
    """
    class FakeStdio():
        """ This is a fake stdio class that will pass to cmd_processor. 
        
        The only important function is write(). cmd_processor will call its 
        stdout.write() to output messages.
        """
        def __init__(self, socket):
            self.socket = socket
        def write(self, msg):
            self.socket.sendall(msg)
    
    def handle(self):
        # create fake stdio
        fakeStdio = ClientRequestHandler.FakeStdio(self.request)
        # get command processor
        cmd_processor = self.server.cmd_processor
        # redirect stdout
        cmd_processor.stdout = fakeStdio

        # get date from client
        data = self.request.recv(1024).strip()
        # process command
        cmd_processor.onecmd(data)

class ClientTCPServer(SocketServer.TCPServer):
    """ A class that receives client commands from TCP.

    This server will start a new thread to listen to incoming connection after 
    executing start(). To stop the server, execute shutdown()

    """
    def __init__(self, balanceMgr, serverAddress):
        """ Initiate a TCP server. 

        Input:
            balanceMgr : BalanceMgr
            serverAddress : a tuple (ip, port)
        """
        # base class's constructor
        SocketServer.TCPServer.__init__(self, serverAddress, ClientRequestHandler)
        
        # command processor will be used by ClientRequestHandler
        # it parse the input and dispatch commands 
        self.cmd_processor = CLI(balanceMgr)
        
        # thread that runs self.serve_forever
        self.thread = threading.Thread(target=self.serve_forever)
        self.thread.setDaemon(True)

    def start(self):
        """ Create a new thread that listens to incoming connection. """
        self.thread.start()

    # To stop running, call ClientTCPServer.shutdown()
