
import json
import re
import urllib
from functions import goUrl

class Catalog:
    '''Catalog module 
This module uses anicat.net api, ororo.
anime <string> [results <number>]
aniget <number> <string>'''

    _marvinModule = True
    public = ['anime', 'aniget']
    aliases = {'anime': ('a',), 'aniget': ('aid',)}
    
    def __init__(self):
        self.csrf = self.getcsrf()
    
    def anime(self, message):
        '''
anime <string> [results <number>] [page <number>]:
    Search <string> as record name in catalog database and display matches.
    result - number of results to display. Default: 1. Maximum: 20.
    page - number of results page to display
    sort - not realised yet
    field - not supported by api yet.'''
        if not self.csrf:
            self.csrf = self.getcsrf()
        try: (text, page) = message.ctext.rsplit(' page ', 0)
        except ValueError:
            text = message.ctext
            page = 0
        try:
            (text, numresults) = text.rsplit(' results ', 1)
            numresults = int(numresults)
        except ValueError:
            numresults = 3
        ret = goUrl('http://anicat.net/ajax/search/', {'string': text, 'page': page, 'limit': numresults,
                    'csrfmiddlewaretoken': self.csrf}, True, {'csrftoken': self.csrf})
        ret = json.loads(ret)
        if not ret:
            message.reply('No!')
            return
        if ret['response'] == 'error':
            message.reply(ret['text'])
        else:
            
            if not ret['text']['count']:
                message.reply('NO WAI!')
            else:
                response = str(ret['text']['count']) +' results total. '
                response += 'Page %i of %i \n' % (ret['text']['page'] + 1, 
                            int(ret['text']['count'])/numresults)
                rescount = 0
                for elem in ret['text']['items']:
                    rescount += 1
                    if rescount > numresults:
                        break
                    response += '%s (%s), Translation: %s\n' % (self.encd(elem['name']),
                                elem['type'], elem['translation'])
                    response += 'Catalog id: %d http://anicat.net/card/%d/\n' % (elem['id'], elem['id'])
                message.reply(response)

    def aniget(self, message):
        '''
aniget <number> <string>:
    Return <string> parameter of record with id <number>.
    Multiple fields supported with comma separator between.'''
        if not self.csrf:
            self.csrf = self.getcsrf()
        try: 
            cid, text = message.ctext.split(' ', 1)
            int(cid)
        except Exception:
            message.reply('NO WAI!\nTry !help aniget')
            return
        ret = json.loads(goUrl('http://anicat.net/ajax/get/', {'id': cid, 'field': text,
                               'csrfmiddlewaretoken': self.csrf}, True, {'csrftoken': self.csrf}))
        if not ret:
            message.reply('No!')
            return
        if ret['response'] == 'error':
            message.reply(ret['text'])
        else:
            resp = ''
            r = ret['text']
            print r
            for o in r['order']:
                elem = r[o]
                if len(elem) > 0:
                    resp += '\n %s:' % o.capitalize()
                    if type(elem).__name__ == 'list':
                        for el in elem:
                            resp += '\n'
                            if type(el).__name__ == 'dict' and el.has_key('name') and el['name']:
                                resp += self.encd(el['name'])
                                if el.has_key('comm') and el['comm']: resp += '(%s)' % self.encd(el['comm'])
                                if el.has_key('role') and el['role']: resp += ' as ' + self.encd(el['role'])
                            else:
                                resp += self.encd(el)
                    else:
                        resp += self.encd(elem)
                message.reply(resp)

    def getcsrf(self):
        u = urllib.URLopener().open("http://anicat.net/settings/")
        return u.info()['set-cookie'].split('csrftoken=')[-1].split(';', 1)[0]
    
    def encd(self, string):
        "Convert codes into characters"
        string = re.sub(ur"&quot;", ur"\"", string)
        string = re.sub(ur"&#37;", ur"%", string)
        string = re.sub(ur"&#39; ", ur"'", string)
        string = re.sub(ur"&#92;", ur"\\", string)
        string = re.sub(ur"&#47;", ur"/", string)
        string = re.sub(ur"&#43;", ur"\+", string)
        string = re.sub(ur"&#61;", ur"=", string)
        string = re.sub(ur"&lt;", ur"<", string)
        string = re.sub(ur"&rt;", ur">", string)        
        string = re.sub(ur"&#35;", ur"#", string)
        string = re.sub(ur"&amp;", ur"&", string)
        return string