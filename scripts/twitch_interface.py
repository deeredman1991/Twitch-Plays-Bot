import socket
import time
import threading

class TwitchInterface(object):
    def __init__(self, oAuth, bot_name, streamer_name, host='irc.chat.twitch.tv', port=6667, connected_message = "GO!"):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        self.host = host
        self.port = port
        
        self.oAuth = ''
        if oAuth[0:6].lower() != 'oauth:':
            self.oAuth = 'oauth:'
        self.oAuth += oAuth
        
        self.showOAuth = False

        self.bot_name = bot_name

        self.streamer_name = streamer_name

        self.connected_message = connected_message

    #Public Connection Method(s).
    def start(self):
        self._connect()
        self._login()
        self._join()
        self._cap_req()
        time.sleep(3)
        self.say( self.connected_message )

    #Public Input Method(s).
    def listen(self, *on_recvd_args, on_recvd_callback=None, **on_recvd_kwargs):
        #All args and kwargs passed to the 'listen' method (besides 'on_recvd_callback')
        #   will be passed on to the on_recvd_callback function as arguments.
        #   the on_recvd_callback function will also be passed a kwarg called "recvd"
        #   containing the username of a user sending a message plus the message that 
        #   user sent and should be unpacked as follows;
        #       user, msg = recvd
        on_recvd_kwargs['on_recvd_callback'] = on_recvd_callback
        listen_thread = threading.Thread(target=self._listen, 
                                         args=on_recvd_args,
                                         kwargs=on_recvd_kwargs,
                                         daemon=True)
        listen_thread.start()

    #Public Output Method(s).
    def say(self, msg):
        self._send( 'PRIVMSG #{0} :{1}'.format( self.streamer_name, msg ) )

    def whisper(self, user, msg):
        self.say( '/w {0} {1}'.format(user, msg) )

    #Private Connection Method(s).
    def _connect(self):
        self.socket.connect((self.host, self.port))

    def _login(self):
        self._send( 'PASS {0}\nNICK {1}'.format(self.oAuth, self.bot_name) )
        self._print_incoming(self.host, self._read_buffer())

    def _join(self):
        self._send( 'JOIN #{0}'.format(self.streamer_name) )
        self._print_incoming(self.host, self._read_buffer())

    def _cap_req(self):
        self._send( 'CAP REQ :twitch.tv/tags twitch.tv/commands' )
        self._print_incoming(self.host, self._read_buffer())

    #Private Input Method(s).
    def _read_buffer(self):
        time.sleep(.5)
        buffer = self.socket.recv(1024).decode()
        if buffer[-1] != '\n':
            buffer_end = '\n'
        else:
            buffer_end = ''
        return buffer + buffer_end

    def _format_msg(self, buffer):
        buffer = buffer.split('\r\n')
        msgs = []

        for line in buffer:
            buffer_list = line.split(':')

            try:
                formatting_junk = buffer_list[0] or None
                twitch_junk = buffer_list[-2] or None
                issuing_user = twitch_junk.split('!')[0] or None
                if len( buffer_list ) > 2:
                    msg = buffer_list[-1]
                    msgs.append({ issuing_user: msg })
            except IndexError:
                pass

        return msgs

    def _print_incoming(self, username, msg):
        msg = msg.split('\n')
        if username == self.host:
            msg.pop(-1)
        for line in msg:
            print('[{:20.20}] {:20.20}: {}'.format(self.host, username, line))

    def _listen( self, *on_recvd_args, **on_recvd_kwargs ):
        on_recvd_callback = on_recvd_kwargs.pop('on_recvd_callback', None)
        while True:
            buffer = self._read_buffer()
            msg = buffer.split(' ')
            if msg[0] == 'PING':
                self._print_incoming(self.host, ' '.join(msg))
                self._send('PONG {0}'.format(msg[1]))
            else:
                if on_recvd_callback and callable(on_recvd_callback):
                    for msg in self._format_msg( buffer ):
                        for user, text in msg.items():
                            self._print_incoming(user, text)
                            on_recvd_kwargs['recvd'] = user, text
                            on_recvd_callback( *on_recvd_args, **on_recvd_kwargs )

    #Private Output Method(s).
    def _send(self, msg):
        msg = msg.split('\n')
        for line in msg:
            self.socket.send( '{0}\r\n'.format( line ).encode() )
            if line[:4] == "PASS" and self.showOAuth == False:
                line = 'PASS *****'
            print('[{:20.20}] {:20.20}> {}'.format(self.host, self.bot_name, line))

if __name__ == '__main__':
    def testCB(recvd=None):
        print("Callback Working - recvd: ", end='')
        print(recvd)

    my_username = '<Your Username Here>'
    my_oAuth = '<Your oAuthHere>'

    streamer_name = my_username

    bot_name = my_username
    oAuth = my_oAuth

    bot = TwitchInterface(oAuth, bot_name, streamer_name)
    bot.start()
    bot.listen( on_recvd_callback=testCB )

    bot.say("Noodles!")
    time.sleep(2)
    bot.say("More Noodles!")
    #bot.whisper(streamer_name, "Even More Noodles!")