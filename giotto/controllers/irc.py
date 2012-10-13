import sys 
import socket 
import string 
import os

from giotto.controllers import GiottoController
from giotto.exceptions import ProgramNotFound
from giotto.core import parse_kwargs

irc_execution_snippet = """
if controller == 'irc':
    config = {
        'host': 'chat.freenode.org',
        'port': 6667,
        'nick': 'giotto-bot',
        'ident': 'giotto',
        'realname': 'Giotto',
        'owner': '',
        'channel_list': '#botwar',
        'magic_token': '!giotto ',
    }
    from giotto.controllers.irc import listen
    listen(programs, config, model_mock=mock, cache=cache)
"""

class IRCController(GiottoController):
    name = 'irc'
    default_mimetype = 'text/irc'

    def get_mimetype(self):
        return self.default_mimetype

    def get_program_name(self):
        return self.request.program

    def get_controller_name(self):
        return 'irc'

    def get_data(self):
        kwargs = self.request.args
        return parse_kwargs(kwargs)

    def get_concrete_response(self):
        result = self._get_generic_response_data()
        # convert to a format appropriate to the wsgi Response api.
        response = dict(
            response=result['body'],
            say_to=self.request.sent_to,
        )

        # now do middleware
        return self.execute_output_middleware_stream(response) 

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

    def __init__(self, line, magic_token, nick):
        self.ident = line[0][1:]
        self.username = self.ident.split("!")[0]
        self.msg_type = line[1]
        self.sent_to = line[2]
        self.private_message = not self.sent_to.startswith('#')
        self.raw_message = " ".join(line[3:])[1:]
        self.program, self.args = self.get_program_and_args(self.raw_message, magic_token)
        #print self.__repr__()

    def get_program_and_args(self, message, magic_token):
        if message.startswith(magic_token):
            # channel invocation
            l = len(magic_token)
            parsed_message = message[l:]
            args = parsed_message.split()[1:]
            program = parsed_message.split()[0]
            return program, args
        if self.private_message:
            # private message invocation
            items = message.split()
            if len(items) < 2:
                return items[0], ""
            return items[0], items[1:]
        else:
            # some other invocation that is not valid
            return None, None

    @property
    def looks_legit(self):
        return '@' in self.ident and self.msg_type.lower() == 'privmsg'

    def __repr__(self):
        return "program: %s, args: %s" % (self.program, self.args)

def listen(programs, config, model_mock=False, cache=None):
    """
    IRC listening process.
    """
    #open a socket to handle the connection
    IRC = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    #simple function to send data through the socket
    def send_data(command):
        print "->", command
        IRC.send(command + '\n')

    def say(target, message):
        send_data("PRIVMSG %s :%s\r" % (target, message))

    # connect to server
    IRC.connect((config['host'], config['port']))

    # login to server
    send_data("USER %s %s %s :%s" % (config['ident'], 'hostname', '*', config['realname']))
    send_data("NICK %s" % config['nick'])

    # join channels
    send_data("JOIN %s" % config['channel_list'])

    while True:
        buff = IRC.recv(1024)
        msg = string.split(buff)
        if msg[0] == "PING":
            #answer with pong as per RFC 1459
            send_data("PONG %s" % msg[1])
            continue

        request = IRCRequest(msg, config['magic_token'], config['nick'])
        if not request.looks_legit:
            continue

        print "@@@ LEGIT @@@", request

        try:
            controller = IRCController(request, programs, model_mock, cache)
            result = controller.get_concrete_response()
        except ProgramNotFound:
            print "No program found: %s -- %s" % (request.program, request.args)
        except Exception as exc:
            cls = exc.__class__.__name__
            say(request.sent_to, "04%s - %s: %s" % (request.program, cls, exc))
        else:
            msg = "%s: %s" % (request.username, result['response'])
            if request.private_message:
                say(request.username, msg)
            else:
                say(request.sent_to, msg)









