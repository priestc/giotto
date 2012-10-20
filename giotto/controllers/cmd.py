import os

from giotto.core import parse_kwargs
from giotto.controllers import GiottoController

cmd_execution_snippet = """
args = sys.argv
mock = '--model-mock' in args
if mock:
    # remove the mock argument so the controller doesn't get confused
    args.pop(args.index('--model-mock'))
from giotto.controllers.cmd import CMDController, CMDRequest
request = CMDRequest(sys.argv)
controller = CMDController(request=request, programs=programs, model_mock=mock)
controller.get_concrete_response()"""

class CMDRequest(object):
    def __init__(self, argv):
        self.enviornment = os.environ
        self.argv = argv

class CMDController(GiottoController):
    """
    Basic command line cntroller class. self.request will be the value found
    in sys.argv; a list of commandline arguments with the first item being the 
    name of the script ('giotto'), the second being the name of th program
    and the rest being commandline arguments.
    """
    name = 'cmd'
    default_mimetype = 'text/cmd'

    def get_program_name(self):
        prog = self.request.argv[1]
        if prog.startswith('--'):
            # if the first argument is a commandline-style keyword argument,
            # then the program name is blank. (root program)
            prog = ''
        return prog

    def get_controller_name(self):
        return 'cmd'

    def get_data(self):
        """
        Parse the raw commandline arguments (from sys.argv) to a dictionary
        that is understandable to the rest of the framework.
        """
        arguments = self.request.argv[1:]
        if not arguments[0].startswith('--'):
            # first argument is the program name
            arguments = arguments[1:]
        return parse_kwargs(arguments)

    def get_concrete_response(self):
        result = self._get_generic_response_data()
        
        response = {
            'stdout': [result['body']],
            'stderr': [],
        }

        # now do middleware
        response = self.execute_output_middleware_stream(response)
        stdout = response['stdout']

        if hasattr(stdout, 'write'):
            # returned is a file, print out the contents through stdout
            print stdout.write()
        else:
            for line in stdout:
                print line

        for line in response['stderr']:
            sys.stderr.write(line)


    def get_primitive(self, name):
        return "ff"