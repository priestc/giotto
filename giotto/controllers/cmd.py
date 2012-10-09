from collections import defaultdict
from giotto.controllers import GiottoController

class CMDController(GiottoController):
    """
    Basic command line cntroller class. self.request will be the value found
    in sys.argv; a list of commandline arguments with the first item being the 
    name of the script ('giotto'), the second being the name of th program
    and the rest being commandline arguments.
    """
    name = 'cmd'

    def get_program_name(self):
        return self.request[1]

    def get_controller_name(self):
        return 'cmd'

    def get_data(self):
        arguments = self.request[2:]
        d=defaultdict(list)
        for k, v in ((k.lstrip('-'), v) for k,v in (a.split('=') for a in arguments)):
            d[k].append(v)

        return d