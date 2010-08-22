#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import xmpp
import os
import signal
import time
from datetime import datetime
import ConfigParser

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
        
        self.bot = None
        self.modules = {}
        self.objects = {}
        self.functions = {}
        
        self.connect()
        print "Bot started"
        self.process()
        
        
    def connect(self):
        jid = xmpp.JID(self.login)
        self.client = xmpp.Client(jid.getDomain(),debug=[])
        print "Loading plugins"
        self.loadPlugins()
        print "Connecting"
        self.client.connect()
        self.client.auth(jid.getNode(), self.password)
        self.client.sendInitPresence()
        self.client.RegisterHandler('message', self.message)
        self.client.send(xmpp.Presence(to = self.conference + '/' + self.nick))
    
    def loadPlugins(self):
        self.functions.clear()
        self.objects.clear()
        for fname in os.listdir('plugins/'):
            if fname.endswith('.py'):
                funcs = []
                plugin_name = fname[:-3]
                if plugin_name != '__init__':
                    print "Loading " + plugin_name
                    if plugin_name in self.modules:
                        try: plugin = reload(self.modules[plugin_name])
                        except Exception, e:
                            del self.modules[plugin_name]
                            print "Could not load" + plugin_name + ": " + str(e)
                            continue
                    else:
                        try: plugin = __import__('plugins.'+plugin_name)
                        except Exception, e:
                            print "Could not load" + plugin_name + ": " + str(e)
                            continue
                    self.modules[plugin_name] = plugin
                    obj = getattr(plugin, plugin_name)
                    try: obj = getattr(obj, plugin_name)
                    except Exception, AttributeError:
                        try: obj = getattr(obj, plugin_name.capitalize())
                        except Exception, e:
                            print "Could not load" + plugin_name + ": " + str(e)
                            continue
                    try: obj = obj()
                    except Exception, e:
                        print "Could not load" + plugin_name + ": " + str(e)
                        continue 
                    try: funs = getattr(obj, 'public')
                    except Exception, e:
                        print "Could not load" + plugin_name + ": " + str(e)
                        continue
                    self.objects[plugin_name] = obj
                    for func in funs:
                        self.functions[func] = plugin_name
    
    def process(self):
        def StepOn():
            try: self.client.Process(1)
            except KeyboardInterrupt: return 1
        while not StepOn(): pass
        
    def sayChat(self, text, *arg):
        self.client.send(xmpp.Message(self.conference, text, 'groupchat'))
        
    def execute(self, command, text):
        module = self.functions[command]
        if module in self.objects.keys():
            func = getattr(self.objects[module], command)
            func(self.sayChat, text)
        

    def message(self, conn, msg):
        text = unicode(msg.getBody()).encode('utf8')
        user = unicode(msg.getFrom()).encode('utf8')
        if not text: return
        command = text.split(' ')
        if not msg.timestamp and user != self.conference+'/'+self.nick:
            if 'php' in text:
                self.sayChat(u'php-какашка') #coding-utf8 badbad
                return
            if '!modules' in text:
                print self.modules.keys()
                self.sayChat(self.modules.keys())
                return
            if '!functions' in text:
                self.sayChat(self.functions.keys())
                return
            if command[0] in self.functions.keys():
                self.execute(command[0], text)
                return
            if '!reload' in text:
                self.sayChat('Reloading modules...')
                self.loadPlugins()
            if '!eval' in text and user == self.conference + '/' + self.admin:
                estr = str(text.split(' ', 1)[1])
                try: exec(estr)
                except Exception, e: print estr + ' ' + str(e)

Bot()