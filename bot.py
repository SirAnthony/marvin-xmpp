# -*- coding: utf-8 -*-
import sys
import xmpp
import os
import signal
import time
from datetime import datetime
import ConfigParser

conference = 'animuchan1@conference.hitroe.com'

def loadConfig():
  config = ConfigParser.ConfigParser()
  config.read('config.ini')
  login = config.get('connect', 'jid')
  password = config.get('connect', 'password')
  nick = config.get('connect', 'nick')

  return {'login':login,'password':password, 'nick': nick }

def loadPlugins():
    commands = []

    for fname in os.listdir('plugins/'):
        if fname.endswith('.py'):
            plugin_name = fname[:-3]

            if plugin_name != '__init__':
                plugins=__import__('plugins.'+plugin_name)
                
                plugin = getattr(plugins,plugin_name)
                commands.append(plugin_name)

    return {'plugins':plugins,'commands':commands }

def runPlugin(command,bot,mess):
  plugin = getattr(bot.plugins['plugins'],command)
  plugin.run(bot, mess, conference)

def message(conn,msg):
    global bot
    text = msg.getBody()
    command = text.split(' ')
    if text == None:
        return
    if not msg.timestamp:
        if bot.config['nick'] in command : 
            runPlugin('fortune', bot, bot.config['nick'])

        if 'php' in text and msg.getFrom() != conference+'/'+bot.config['nick']:
            bot.send(xmpp.Message(conference, u'php-какашка', 'groupchat'))
            return

        if '!modules' in text:
            bot.send(xmpp.Message(conference, bot.plugins['commands'], 'groupchat'))
            return

        if '!reload' in text:
            bot.send(xmpp.Message(conference, u'Reloading modules...', 'groupchat'))
            bot.plugins = loadPlugins()
            return

        if command[0] in bot.plugins['commands']:
            runPlugin(command[0], bot, text)
            return

def StepOn(conn):
    try:
        conn.Process(1)
    except KeyboardInterrupt:
        return 0
    return 1

def StartBot(conn):
    while StepOn(conn):
        pass
  
config = loadConfig()
jid = xmpp.JID(config['login'])
bot = xmpp.Client(jid.getDomain(),debug=[])
print "Parsing config"
bot.config = config
print "Loading plugins"
bot.plugins = loadPlugins()
print "Connecting"
bot.connect()
bot.auth(jid.getNode(),bot.config['password'])
bot.sendInitPresence()
bot.RegisterHandler('message', message)
bot.send(xmpp.Presence(to=conference+'/'+config['nick']))

print "Bot started"
StartBot(bot)


