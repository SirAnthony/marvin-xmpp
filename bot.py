#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json
import signal
import sys
import time
import xmpp
from collections import deque
from datetime import datetime
from modulemanager import Manager
from random import randint
from traceback import format_exception

class ReloadData(Exception):
    pass

class BotException(Exception):
    pass
class ConnectError(BotException):
    pass
class AuthException(BotException):
    pass
class MessageError(BotException):
    pass

def sigTermProcess(signum, frame):
    raise SystemExit()
def sigHupProcess(signum, frame):
    raise ReloadData()

class Message:

    def __init__(self, msg, func=None):
        self.type = msg.getType()
        self.form = msg.getFrom()
        self.user = self.form.getStripped()
        self.resource = self.form.getResource()
        self.text = self.forceUnicode(msg.getBody())
        self.ctext = None
        self.reply = None
        if self.type != 'groupchat':
            #FIXME: works wrong I think.
            self.reply = self.__createReplyFunction(func, self.form, self.type)
        else:
            self.reply = self.__createReplyFunction(func, self.user)

    def __createReplyFunction(self, func, recipient, mtype='groupchat'):
        if not func:
            def _say(message):
                raise MessageError('''Cannot send message, no function exists.
Message variables:
''' + unicode(self.__dict__))
        else:
            def _say(message):
                func(recipient, self.forceUnicode(message), mtype)
        return _say

    def __setitem__(self, item, value):
        if type(value) is str:
            value = self.forceUnicode(value)
        super(Message, self).__setitem__(item, value)

    @classmethod
    def forceUnicode(cls, string, encoding='utf-8'):
        if type(string) is str:
            string = string.decode(encoding)
        if type(string) is not unicode:
            string = unicode(string)
        return string

class Bot:
    '''
Core commands:
!modules
    Lists all loaded modules.
!functions
    Lists all available commands.
!aliases
    Lists all aliases for commands.
!load [modulename]
!reload [modulename]
    Reloads module modulename or reloads pluggins directory.
!help [module name]
    With module name given prints module info.
    Without arguments prints this help.
'''

    version = '0.7.0'

    def __init__(self):
        self.__quit = False
        signal.signal(signal.SIGTERM, sigTermProcess)
        signal.signal(signal.SIGHUP,  sigHupProcess)
        print "Parsing config"
        config = json.loads(open('config.json').read())
        self.admin = config.get('admin')
        self.login = config.get('jid')
        self.password = config.get('password')
        self.nick = config.get('nick')
        self.rooms = config.get('conference')
        self.client = None
        self.iq = True
        self.last = datetime(1, 1, 1)
        self.__repeats = deque((), 10)
        self.manager = Manager()
        self.process()

    def connect(self):
        self.client = None #remove old client
        jid = xmpp.JID(self.login)
        client = xmpp.Client(jid.getDomain(),debug=[])

        print 'Connecting'
        if not client.connect():
            raise ConnectError('Unable to connect.')
        if not client.auth(jid.getNode(), self.password):
            raise AuthException('Unable to authorize.')

        self.client = client #Make new main client

        for room, params in self.rooms.items():
            self._joinPresence(room, params)

        client.RegisterHandler('message', self.messageProcess)
        client.RegisterHandler('presence', self.presenceProcess)
        client.RegisterHandler('iq', self.iqProcess, typ='result', ns=xmpp.NS_TIME)
        client.sendInitPresence()
        print 'Connected'
        return True

    def process(self):
        print "Bot started"
        while not self.__quit:
            try:
                self.checkReconnect()
                if self.client:
                    if self.client.Process(1) == 0:
                        self.connect()
                else:
                    if not self.connect():
                        raise ConnectError('Unknown connection error.')
            except xmpp.protocol.XMLNotWellFormed:
                logging.error('CONNECTION: reconnect (detected not valid XML)')
                self.conn = None
            except KeyboardInterrupt:
                self.exit('EXIT: interrupted by keyboard')
            except SystemExit:
                self.exit('EXIT: interrupted by SIGTERM')
            except ReloadData:
                print 'Reload: SIGHUP'
                self.manager.load_dir()
                self.connect()
            except AuthException:
                self.exit('EXIT: auth problems, check config.')
            except ConnectError, e:
                print str(e)
                time.sleep(300)
            except:
                print 'Catch exception:'
                print ''.join(format_exception(*sys.exc_info()))

    def checkReconnect(self):
        now = datetime.now()
        delta = (now - self.last).seconds
        if not self.iq and delta > 15:
            print 'CONNECTION: reconnect (iq reply timeout)'
            self.client = None
            self.iq = True
        if self.client:
            if delta > 120:
                if self.iq:
                    self.iq = None
                self.last = now
                self.client.send(xmpp.protocol.Iq(to='headcounter.org', typ='get', queryNS=xmpp.NS_TIME))

    def _joinPresence(self, room, params={}, client=None):
        nick = params.get('anothernick') or params.get('nick') or self.nick
        presence = None
        if not client:
            client = self.client
        if params and params.has_key('password'):
            presence = '<presence to=\'%s/%s\'><x xmlns=\'..http://jabber.org/protocol/muc\'><password>%s</password></x></presence>' \
                      % (room, nick, params['password'])
        else:
            presence = xmpp.Presence(to='%s/%s' %(room, nick))
        client.send(presence)

    def joinRoom(self, room, params={}):
        if not room in self.rooms:
            self._joinPresence(room, params)
            self.room[room] = params
            return True

    def leaveRoom(self, room):
        if room in self.rooms:
            lroom = self.rooms[room]
            nick = lroom.get('anothernick') or lroom.get('nick') or self.nick
            self.client.send(xmpp.Presence(to='%s/%s' % (room, nick), typ='unavailable', status='offline'))
            del self.rooms[room]
            l = self.manager.get('pluggins.logger')
            if l and l.functions:
                l.functions['_leave'](room)
            return True

    def say(self, *args):
        "Takes: recipient, message, type"
        self.__repeats.append(args[1])
        if self.__repeats.count(args[1]) > 5:
            return
        try:
            l = self.manager.get('plugins.logger')
            getattr(l.object, '_log')(args[0], args[1], args[2], self.nick)
        except:
            pass
        self.client.send(xmpp.Message(*args))

    def messageProcess(self, conn, msg):
        if msg.getTimestamp():
            return
        message = Message(msg, self.say)

        if not message.text:
            return

        try:
            room = self.rooms[message.user]
            nick = room.get('anothernick') or room.get('nick') or self.nick
        except:
            nick = self.nick
        if not message.resource or message.resource == nick:
            return

        try:
            l = self.manager.get('plugins.logger')
            getattr(l.object, '_logMessage')(message)
        except:
            pass

        try:
            l = self.manager.get('plugins.urlhead')
            getattr(l.object, '_urlhead')(message)
        except:
            pass
                
        if 'php' in message.text:
            message.reply(u'php-какашка') #coding-utf8 badbad
        if message.text.startswith('!modules'):
            message.reply(self.manager.modules.keys())
            return
        elif message.text.startswith('!functions'):
            message.reply(self.manager.functions.keys())
            return
        elif message.text.startswith('!aliases'):
            message.reply(self.manager.aliases)
            return
        elif message.text.startswith('!load') or message.text.startswith('!reload'):
            modules = message.text.split()[1:]
            message.reply('Reloading modules %s' % ', '.join(modules))
            if not modules:
                self.manager.load_dir()
            else:
                for module in modules:
                    self.manager.load_module(module)
                self.manager.update_functions()
            return
        elif message.text.startswith('!help'):
            modulename = message.text.split(None, 1)[1:]
            if not modulename:
                message.reply(self.__doc__)
            else:
                modulename = modulename[0]
                module = self.manager.get(modulename)
                if not module:
                    message.reply('No module "%s" loaded.' % modulename)
                else:
                    message.reply(module.object.__doc__)
            return
        elif nick in message.text:
            try:
                l = self.manager.get('plugins.markov')
                getattr(l.object, 'say')(message)
            except:
                pass
        elif message.text.startswith('!eval') and message.resource == self.admin:
            #too dangerous
            #estr = str(text.split(' ', 1)[1])
            #try: exec(estr)
            #except Exception, e: print estr + ' ' + str(e)
            message.reply('NO U!')
            return
        try:
            self.execute(message)
        except:
            print ''.join(format_exception(*sys.exc_info()))
            message.reply('Fail in message process.')

    def execute(self, message):
        modulename = None
        try: command, stext = message.text.split(' ', 1)
        except ValueError:
            command = message.text
            stext = ''
        text = stext.strip()
        #FIXME: crap
        #first - looking for commands
        try:
            modulename = self.manager.functions[command]
        except KeyError:
            #next looks for aliases
            try:
                alias, text = message.text.split('%')[-1].split(' ', 1)
                command = self.manager.aliases[alias]
                modulename = self.manager.functions[command]
            except:
                pass
        if not modulename:
            return
        message.ctext = text
        module = self.manager.get(modulename)
        if not module:
            raise NameError("Module %s not exist." % modulename)
        if command not in module.functions.keys():
            message.reply('NO WAI!')
            raise NameError('Error. %s not exists in %s.' % (command, module.name))
        function = module.functions[command]
        if text == 'help':
            if function.__doc__:
                message.reply(function.__doc__)
            else:
                self.sayChat('No documentation on %s avaliable.' % command)
        elif text == 'help module':
            if module.object.__doc__:
                message.reply(('Module: %s\n' % modulename) + module.object.__doc__)
            else:
                message.reply('No documentation on %s avaliable.' % module.name)
        else:
            function(message)

    def presenceProcess(self, conn, pres):
        ptype = pres.getType()
        roomname = None
        room = None
        mainnick = None
        nick = None
        try:
            roomname = pres.getFrom().getStripped()
            room = self.rooms[roomname]
            mainnick = room.get('nick') or self.nick
            nick = room.get('anothernick') or mainnick
        except KeyError: # private
            pass
        except:
            print 'Please debug this:'
            print ''.join(format_exception(*sys.exc_info()))
            print 'Presence:' + unicode(pres)

        if ptype == 'error':
            if pres.getErrorCode() == u'409': #name conflict
                try:
                    l = len(room.get('nick'))
                except TypeError:
                    l = len(self.nick)
                if nick[l:].isalnum():
                    nick = room.get('nick') or self.nick
                nick = nick + str(randint(1, 100))
                self.rooms[roomname]['anothernick'] = nick
                self._joinPresence(roomname, self.rooms[roomname])
            return

        if ptype == 'subscribe' and roomname == self.admin:
            self.client.send(xmpp.Presence(to=pres.getFrom(), typ='subscribed'))

        if ptype == 'unavailable':
            #Explanation: http://xmpp.org/registrar/mucstatus.html
            status = pres.getStatusCode()
            if status in [u'303',  u'307']: #change nick or kicked
                resource = pres.getFrom().getResource()
                if  resource == mainnick:
                    #Our name is free
                    p = xmpp.Presence('%s/%s' % (roomname, nick), 'unavailable')
                    p.setTag('x', {}, xmpp.NS_MUC_USER).setTag('affiliation',{'nick': mainnick})
                    p.setTag('x', {}, xmpp.NS_MUC_USER).setTag('status',{'code': '303'})
                    self.client.send(p)
                    self.client.send(xmpp.Presence('%s/%s' % (roomname, mainnick)))
                    try:
                        self.rooms[roomname]['nick'] = mainnick
                        del self.rooms[roomname]['anothernick']
                    except:
                        pass
                    self.say(roomname, 'ГАГАГА', 'groupchat')
                elif resource == nick:
                    self._joinPresence(roomname, self.rooms[roomname])
                    self.say(roomname, 'Я все понял.', 'groupchat')
            if pres.getFrom().getResource() == nick and pres.getStatus() == 'Replaced by new connection':
                if room:
                    self._joinPresence(roomname, room)

    def iqProcess(self, conn, node):
        self.iq = node

    def exit(self, msg='exit'):
        if self.client:
            for room in self.rooms.keys():
                self.leaveRoom(room)
            self.client = None

        self.__quit = True
        print msg

if __name__ == '__main__':
    Bot()
