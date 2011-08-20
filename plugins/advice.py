import json
import re
from function import goUrl

class Advice:
    
    _marvinModule = True
    public = ['advice']
    aliases = {'advice': ['a', 'adv']}

    def advice(self, message):
        url = 'http://fucking-great-advice.ru/api/random'
        advice = json.loads(goUrl(url))
        message.reply(self.encd(advice['text']))

    def encd(self, string):
        string = unicode(string)
        string = re.sub(ur"&nbsp;", ur" ", string)
        string = re.sub(ur"&#146;", ur"'", string)
        string = re.sub(ur"&quot;", ur"\"", string)
        return string
