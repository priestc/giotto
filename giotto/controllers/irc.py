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
        'channelist': '#test',
        'magic_token': '!giotto',
    }
    from giotto.controllers.irc import listen
    listen(programs, config)
"""

class IRCController(GiottoController):
    name = 'irc'
    default_mimetype = 'text/irc'

    def get_mimetype(self):
        return self.default_mimetype

    def get_program_name(self):
        return self.request['program']

    def get_controller_name(self):
        return 'irc'

    def get_data(self):
        kwargs = self.request['message_token_removed'].split()[1:]
        return parse_kwargs(kwargs)

    def get_concrete_response(self):
        result = self._get_generic_response_data()
        # convert to a format appropriate to the wsgi Response api.
        response = dict(
            response=result['body'],
            say_to=self.request['sent_to'],
        )

        # now do middleware
        return self.execute_output_middleware_stream(response) 

    def get_primitive(self, primitive):
        if primitive == 'RAW_PAYLOAD':
            return self.get_data()

def parse_line(line):
    ident = line[0]
    username = ident.split('!')[0][1:]
    sent_to = line[2]
    request = {
        'sent_from_ident': ident,
        'sent_from_username': username,
        'msg_type': line[1],
        'sent_to': sent_to,
        'channel_msg': sent_to.startswith('#'),
        'message': " ".join(line[3:])[1:],
    }
    return request

def listen(programs, config):
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
        else:
            request = parse_line(msg)
            request['private_mgs'] = msg[1] == 'PRIVMSG' and msg[2] == config['nick']
            if request['message'].startswith(config['magic_token']):
                offset = len(config['magic_token'])
                request['message_token_removed'] = request['message'][offset:]
                request['program'] = request['message_token_removed'].split()[0]
            if request['private_mgs']:
                request['message_token_removed'] = request['message']
                request['program'] = request['message'].split()[0]
            
            if 'program' in request:
                try:
                    controller = IRCController(request, programs)
                    result = controller.get_concrete_response()
                except ProgramNotFound:
                    print "No program found: %s" % request['message']
                else:
                    msg = "%s: %s" % (request['sent_from_username'], result['response'])
                    say(request['sent_to'], msg)









