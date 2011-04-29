#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import xmpp
import os
import signal
import time
from datetime import datetime
import ConfigParser
from modulemanager import Manager

class Bot:
    
    def __init__(self):
        config = ConfigParser.ConfigParser()
        print "Parsing config"
        config.read('config.ini')
        self.admin = config.get('connect', 'admin')
        self.login = config.get('connect', 'jid')
        self.password = config.get('connect', 'password')
        self.nick = config.get('connect', 'nick')
        self.conference = config.get('connect', 'conference')
        self.presence = xmpp.Presence(to = self.conference + '/' + self.nick)
        self.bot = None
        self.manager = Manager()
        
        print "Loading plugins"
        self.loadPlugins()
        self.connect()
        print "Bot started"
        self.process()
        
        
    def connect(self):
        jid = xmpp.JID(self.login)
        self.client = xmpp.Client(jid.getDomain(),debug=[])
        print "Connecting"
        self.client.connect()
        self.client.auth(jid.getNode(), self.password)
        self.client.sendInitPresence()
        self.client.RegisterHandler('message', self.message)
        self.client.send(self.presence)
        print self.presence.getStatusCode()
    
    def loadPlugins(self):
        for fname in os.listdir('plugins/'):
            if fname.endswith('.py'):
                plugin_name = fname.rsplit('.', 1)[0]
                if plugin_name != '__init__':
                    print "Loading " + plugin_name
                    try:
                        self.manager.load('plugins.%s' % plugin_name)
                    except Exception, e:
                        "Could not load %s: %s" % (plugin_name, e)
        self.manager.update_functions()
    
    def process(self):
        def StepOn():
            if not self.client.isConnected():
                self.connect()
            try:
                self.client.Process(1)
            except KeyboardInterrupt:
                return 1
        while not StepOn(): pass
        
    def sayChat(self, text, *arg):
        self.client.send(xmpp.Message(self.conference, text, 'groupchat'))
        
    def execute(self, command, text):
        module = self.manager.modules[self.manager.functions[command]]
        if command not in module.functions.keys():
            self.sayChat('NO WAI!')
            print 'Error. %s not exists in %s.' % (command, module.name) 
            return
        function = module.functions[command]
        if text == 'help':
            if function.__doc__:
                self.sayChat(function.__doc__)
            else:
                self.sayChat('No documentation on %s avaliable.' % command)
        elif text == 'help module':
            if module.object.__doc__:
                self.sayChat(module.object.__doc__)
            else:
                self.sayChat('No documentation on %s avaliable.' % module.name)
        else:
            try:
                function(self.sayChat, text)
            except Exception, e:
                print str(e)
                self.sayChat('Fail')

    def message(self, conn, msg):
        text = msg.getBody()
        user = msg.getFrom()
        if not text: return
        try: command, stext = text.split(' ', 1)
        except ValueError:
            command = text
            stext = '' 
        if not msg.timestamp and user != self.conference+'/'+self.nick:
            if 'php' in text and text != 'php-какашка':
                self.sayChat(u'php-какашка') #coding-utf8 badbad
                return
            if '!modules' in text:
                self.sayChat(self.manager.modules.keys())
                return
            if '!functions' in text:
                self.sayChat(self.manager.functions.keys())
                return
            if command in self.manager.functions.keys():
                self.execute(command, stext.strip())
                return
            if '!reload' in text:
                self.sayChat('Reloading modules...')
                self.loadPlugins()
            #FIXME: eval not begin string. 
            if '!eval' in text and user == self.conference + '/' + self.admin:
                estr = str(text.split(' ', 1)[1])
                try: exec(estr)
                except Exception, e: print estr + ' ' + str(e)

Bot()