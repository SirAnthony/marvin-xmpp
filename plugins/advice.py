import urllib2
import json
import re

class Advice:
    
    _marvinModule = True
    public = ['advice']
    aliases = {'advice': ['a', 'adv']}

    def advice(self, message):
        foo =  urllib2.urlopen('http://fucking-great-advice.ru/api/random')
        bar = foo.read()
        foo.close()
        advice = json.loads(bar)
        message.reply(self.encd(advice['text']))

    def encd(self, string):
        string = unicode(string)
        string = re.sub(ur"&nbsp;", ur" ", string)
        string = re.sub(ur"&#146;", ur"'", string)
        string = re.sub(ur"&quot;", ur"\"", string)
        return string
