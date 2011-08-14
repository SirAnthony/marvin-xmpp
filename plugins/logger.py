
import json
import os
from collections import deque
from time import gmtime, strftime

class Logger:

    _marvinModule = True

    def __init__(self):
        self.logs = {}
        self.files = {}

    def __del__(self):
        self.flush()
        for f in self.files.values():
            f.close()

    def log(self, sender, text, mtype, resource):
        logname = None
        timestamp = strftime("%d.%m.%Y %H:%M:%S", gmtime())
        if mtype == 'groupchat':
            logname = unicode(sender).split('/', 1)[0]
        else:
            logname = sender
        if not self.logs.has_key(logname):
            self.logs[logname] = deque()
        self.logs[logname].append((timestamp, resource, text))
        print logname, len(self.logs[logname])
        if len(self.logs[logname]) > 20:
            self.flush(logname, 10)

    def logMessage(self, message):
        self.log(message.form, message.text, message.type, message.resource)

    def flush(self, name=None, count=None):
        logs = {}
        if not name:
            logs = self.logs
        else:
            logs[name] = self.logs.get(name)
        for name, value in logs.iteritems():
            if not value:
                continue
            counter = 0
            f = self.files.get(name)
            if not f:
                print os.path.join(os.getcwd(), 'logs', name)
                f = open(os.path.join(os.getcwd(), 'logs', name), 'ar')
                self.files[name] = f
            while len(value) and (not count or count >= counter):
                counter += 1
                text = value.popleft()
                f.write(json.dumps(text) + ',')
            f.write('\n')
            f.flush()

    def leave(self, name):
        self.flush(name)
        if name in self.logs:
            del self.logs[name]
        if name in self.files:
            self.files[name].close()
            del self.files[name]

