import sys 
import socket 
import string 
import os
import traceback

try:
  import irc.bot
except ImportError:
  raise ImportError("Requires irclib; pip install irc")

from giotto.controllers import GiottoController
from giotto.exceptions import ProgramNotFound
from giotto.utils import parse_kwargs

irc_execution_snippet = """
parser = argparse.ArgumentParser(description='Giotto Project Creator')
parser.add_argument('--model-mock', action='store_true', help='Mock out the model')
args = parser.parse_args()

config = {
    'host': '',
    'port': 6667,
    'nick': '',
    'ident': 'giotto',
    'realname': 'Giotto IRC Bot',
    'owner': '',
    'channels': '', # comma seperated
    'magic_token': '!giotto ',
}
from giotto.controllers.irc_ import listen
listen(manifest, config, model_mock=args.model_mock)"""

class IRCController(GiottoController):
    name = 'irc'
    default_mimetype = 'text/x-irc'

    def get_invocation(self):
        return self.request.program

    def get_controller_name(self):
        return 'irc'

    def get_raw_data(self):
        kwargs = self.request.args
        return parse_kwargs(kwargs)

    def get_concrete_response(self):
        try:
            result = self.get_data_response()
        except ProgramNotFound:
            result = {'body': "Program not found"}

        # convert to a format appropriate to the IRC Response api.
        return dict(
            response=result['body'],
            say_to=self.request.sent_to,
        )

    def get_primitive(self, primitive):
        if primitive == 'RAW_PAYLOAD':
            return self.get_data()


class IRCRequest(object):

    # the program name requested
    program = ''
    
    # the usr/channel the message was sent to
    sent_to = ''

    # PRIVMSG or whatever else...
    msg_type = ''

    # The message after the magic token has been removed
    # eg: !giotto multiply --x=1 --y=2  --> multiply --x=1 --y=2
    # note, invocations given through private message have no magic token
    # so this value will be the same as `message`
    message_token_removed = ''

    # the raw message with the magic token still attached
    raw_message = ''

    # boolean, was this request sent to a channel (True) or through private msg?
    channel_msg = None

    # opposite of `channel_msg`
    private_msg = None

    # the username of the person who made the request
    username = ''

    # the ident of the user who made the request
    ident = ''

    def __init__(self, event, magic_token, nick):
        self.ident = event.source()
        self.username = self.ident.split("!")[0]
        self.msg_type = event.eventtype()
        self.sent_to = event.target()
        self.private_message = self.msg_type == "privmsg"
        self.raw_message = event.arguments()[0]
        self.program, self.args = self.get_program_and_args(self.raw_message,magic_token)
        #print self.__repr__()

    def get_program_and_args(self, message, magic_token):
        if self.private_message == True:
            program = message.split()[0]
            args = message.split()[1:]
        else:
            # channel invocationa
            l = len(magic_token)
            parsed_message = message[l:]
            args = parsed_message.split()[1:]
            program = parsed_message.split()[0]
      
        return program, args

    def __repr__(self):
        return "program: %s, args: %s" % (self.program, self.args)

class IrcBot(irc.bot.SingleServerIRCBot):
    def __init__(self, config):
        if not config['host']:
            raise SystemExit('Error: IRC controller needs to be configured with a hostname')

        if not config['nick']:
            raise SystemExit('Error: IRC controller needs to be configured with a nick')

        print "Connecting to %s:%s as %s" % (config['host'],config['port'], config['nick'])

        irc.bot.SingleServerIRCBot.__init__(
            self, 
            [(config['host'],config['port'])], 
            config['nick'], 
            config['realname']
        )

        channels = config['channels']
        if channels:
            self.channel = channels
            print "Joining Channels: %s" % channels
        self.config = config
  
    def on_nicknameinuse(self, c, e):
        c.nick(c.get_nickname() + "_")

    def on_welcome(self, c, e):
        c.join(self.channel)

    def on_privmsg(self, c, e):
        self.process_message(c, e)

    def on_pubmsg(self, c, e):
        if e.arguments()[0].startswith(self.config['magic_token']) == False: return
        self.process_message(c, e)
 
    def process_message(self, c, e):
        request = IRCRequest(e,self.config['magic_token'],c.get_nickname())
        
        try:
            controller = IRCController(request, self.config['manifest'], self.config['model_mock'])
            result = controller.get_response()
        except Exception as exc:
            cls = exc.__class__.__name__
            c.privmsg(request.sent_to, "\x0304%s - %s: %s" % (request.program, cls, exc))
            traceback.print_exc(file=sys.stdout)
        else:
            msg = "%s: %s" % (request.username, result['response'])
            if request.private_message:
                c.privmsg(request.username, msg)
            else:
                c.privmsg(request.sent_to, msg)


def listen(manifest, config, model_mock=False):
    """
    IRC listening process.
    """
    config['manifest'] = manifest
    config['model_mock'] = model_mock
    IRC = IrcBot(config)
    IRC.start()
