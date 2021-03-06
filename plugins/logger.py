
import os
from skyfront import SQL
from collections import deque
from time import gmtime, strftime

class Logger:

    _marvinModule = True
    public = ['log',]

    def __init__(self):
        path = os.path.join(os.getcwd(), 'logs', 'logs.db')
        if not os.path.exists(path):
            open(path,'w').close()
        self.sql = SQL('sqlite', path)
        self.logs = {}

    def __del__(self):
        self._flush()

    def __stripLogName(self, sender, mtype):
        if mtype == 'groupchat':
            return unicode(sender).split('/', 1)[0]
        else:
            return unicode(sender)

    def _log(self, sender, text, mtype, resource):
        logname = self.__stripLogName(sender, mtype)
        timestamp = strftime("%Y-%m-%d %H:%M:%S", gmtime())
        if not self.logs.has_key(logname):
            self.logs[logname] = deque()
        self.logs[logname].append({'timestamp': timestamp,
                                    'resource': resource, 'text': text})
        if len(self.logs[logname]) > 20:
            self._flush(logname, 20)

    def _logMessage(self, message):
        self._log(message.form, message.text, message.type, message.resource)

    def _flush(self, name=None, count=None):
        logs = {}
        if not name:
            logs = self.logs
        else:
            logs[name] = self.logs.get(name)
        for name, value in logs.iteritems():
            if not value:
                continue
            self.sql.executeQuery("""CREATE TABLE IF NOT EXISTS `%s` (
                                            id INTEGER PRIMARY KEY autoincrement,
                                            resource TEXT NOT NULL,
                                            text TEXT NOT NULL,
                                            timestamp DATETIME NOT NULL)""" % name)
            counter = 0
            while len(value) and (not count or count >= counter):
                counter += 1
                data = value.popleft()
                self.sql.insertNew(name, **data)

    def _leave(self, name):
        self._flush(name)
        if name in self.logs:
            del self.logs[name]

    def _getTables(self):
        result, tables = self.sql.getRecords('sqlite_master', ['name'], type='table')
        if result:
            tables = [x[0] for x in tables if not x[0].startswith('sqlite_') \
                                          and x[0].find('/') < 0 ]
            return tables
        else:
            print tables

    def _getLog(self, jid, count=1, user=None, select=None, **kwargs):
        wop = None
        if not user:
            wop = "NOT LIKE"
            user = "Marvin%"
        return self.sql.getRecords(jid, select=select, limit=count,
                resource=user, WClauseOperator=wop, **kwargs)

    def _getLast(self, *args, **kwargs):
        return self._getLog(*args, order='timestamp DESC', **kwargs)

    def log(self, message):
        logname = self.__stripLogName(message.form, message.type)
        self._flush(logname)
        message.reply(self._getLast(logname))
