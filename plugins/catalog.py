import urllib
import json
import re

class Catalog:
    '''Catalog module 
This module uses anicat.net api, ororo.
anime <string> [results <number>]
aniget <number> <string>'''
    public = ['anime', 'aniget']
    
    def anime(self, sendfunc, msg):
        '''
anime <string> [results <number>]:
    Search <string> as record name in catalog database and display matches.
    result - number of results to display. Default: 1. Maximum: 30.
    page - not realised yet
    sort - not realised yet
    field - not supported by api yet.'''
        try: (text, numresults) = msg.rsplit(' results ', 1)
        except ValueError:
            text = msg
            numresults = 1
        ret = json.loads(self.goUrl('http://anicat.net/cgi-bin/anicat.py?', {'search': 'name', 'string': text,
                    'results': numresults}))
        if ret and ret['response'] != 'error':
            if ret['text']['data'] == 'none':
                sendfunc('NO WAI!')
            else:
                response = str(ret['text']['count']) +' results total.\n'
                for elem in ret['text']['data']:
                    response += 'Catalog id: ' + str(elem['id'])
                    response += ' http://anicat.net/card/'+ str(elem['id']) + '\n'
                    for head in ret['text']['header']:
                        if elem[head['name']]:
                            response += head['value'].capitalize() + ': '
                            response += self.encd(elem[head['name']]) + ' '
                    response += '\n'
                sendfunc(response)
        else:
            if ret['response'] == 'error':
                sendfunc(ret['text'])
            else:
                sendfunc('No!')
       
    def aniget(self, sendfunc, msg):
        '''
aniget <number> <string>:
    Return <string> parameter of record with id <number>.
    Multiple fields supported with comma separator between.'''
        try: cid, text = msg.split(' ', 1)
        except Exception:
            sendfunc('NO WAI!\nTry !help aniget')
            return
        ret = json.loads(self.goUrl('http://anicat.net/cgi-bin/anicat.py?', {'get': cid, 'string': text}))
        if ret and ret['response'] != 'error':
            resp = ''
            for o in ret['text']['order']:
                elem = ret['text'][o]
                if len(elem) > 0:                    
                    resp += '\n' + o.capitalize() + ':'
                    if type(elem).__name__ == 'list':
                        for el in elem:
                            resp += '\n'
                            if type(el).__name__ == 'dict' and el.has_key('name') and el['name']:
                                resp += self.encd(el['name'])
                                if el.has_key('comm') and el['comm']: resp += '(' + self.encd(el['comm']) + ')'
                                if el.has_key('role') and el['role']: resp += ' as ' + self.encd(el['role'])
                            else:                            
                                resp += self.encd(el)
                    else:
                        resp += self.encd(elem)
            if resp and resp != '':
                sendfunc(resp)
        else:
            if ret['response'] == 'error':
                sendfunc(ret['text'])
            else:
                sendfunc('No!')
        
        
    def goUrl(self, url=None, params = {}):
        if not url: return
        query = ''
        if len(params):
            query = urllib.urlencode(params)
        url = url + query
        results = urllib.urlopen(url)
        return results.read()
    
    def encd(self, string):
        "Convert codes into characters"
        string = re.sub(r"&quot;", r"\"", string)
        string = re.sub(r"&#37;", r"%", string)
        string = re.sub(r"&#39; ", r"'", string)        
        string = re.sub(r"&#92;", r"\\", string)
        string = re.sub(r"&#47;", r"/", string)
        string = re.sub(r"&#43;", r"\+", string)
        string = re.sub(r"&#61;", r"=", string)
        string = re.sub(r"&lt;", r"<", string)
        string = re.sub(r"&rt;", r">", string)        
        string = re.sub(r"&#35;", r"#", string)
        string = re.sub(r"&amp;", r"&", string)
        return string