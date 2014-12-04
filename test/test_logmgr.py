import os, sys
import unittest
from cStringIO import StringIO

this_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append( os.path.dirname(this_dir) )

from balanceMgr import LogMgr, LOGFILE, LogItem, DEPOSIT, WITHDRAW

class TestSequenceFunctions(unittest.TestCase):
    
    def setUp(self):
        """ This function will be called before each test. """
        try:
            os.remove(LOGFILE)
        except:
            pass
        self.logmgr = LogMgr()

    def test_recover(self):
        # Create log file
        balance = 987
        items = [(LogItem(1,2,3,4), LogItem(11,22,33,44)), 
                 (LogItem(5,6,7,8), )] 
        lines = ["1 2 3 4,11 22 33 44;123", "5 6 7 8;{0}".format(balance)]
        with open(LOGFILE, 'w') as fp:
            for line in lines:
                fp.write(line+';'+LogMgr.ENDING_STR+"\n")
            fp.flush()
        
        # Create logMgr and automatically read log
        logmgr = LogMgr()
        for idx, item in enumerate(items):
            # check log content
            self.assertEquals(logmgr.getItem(idx), item)
        
        # check getBalance
        self.assertEquals(logmgr.getBalance(), balance)

        # check getSize
        self.assertEquals(logmgr.getSize(), len(items))
    
    def test_recover_corrupted(self):
        # Redirect stdout
        self.held, sys.stdout = sys.stdout, StringIO()
        
        # Create log file
        balance = 987
        items = [(LogItem(1,2,3,4),), (LogItem(5,6,7,8),)]
        lines = ["1 2 3 4;123", "5 6 7 8;{0}".format(balance)]
        with open(LOGFILE, 'w') as fp:
            for line in lines:
                fp.write(line+';'+LogMgr.ENDING_STR+"\n")
            fp.write("corrupted line;22\n")
            fp.write("good line;344"+';'+LogMgr.ENDING_STR+"\n")
            fp.flush()
       
        # Create logMgr and automatically read log
        logmgr = LogMgr()
       
        # check items
        self.assertEquals(logmgr._log, items)
        
        # check getBalance
        self.assertEquals(logmgr.getBalance(), balance)

        # check msg
        self.assertEqual(sys.stdout.getvalue(), 'Loading log... Line 3 is corrupted.\n')

    def test_append(self):
        balance = 20+10-8
        items = [(LogItem(1,2,DEPOSIT,20),LogItem(1,2,DEPOSIT,10)), (LogItem(5,6,WITHDRAW,8),)]
        for item in items:
            self.logmgr.append(item)

        # check items
        self.assertEquals(self.logmgr._log, items)

        # check balance
        self.assertEquals(self.logmgr.getBalance(), balance)

        

#    def test_choice(self):
#        element = random.choice(self.seq)
#        self.assertTrue(element in self.seq)
#
#    def test_sample(self):
#        with self.assertRaises(ValueError):
#            random.sample(self.seq, 20)
#        for element in random.sample(self.seq, 5):
#            self.assertTrue(element in self.seq)

if __name__ == '__main__':
    unittest.main()
