import urllib
import json

class Google:
    ''' Google module
google <string> [results <number>]
translate <string> [lang <language>|<language>]'''
    
    public = ['translate', 'google']
    
    def translate(self, sendfunc, msg):
        '''
translate <string> [lang <language>|<language>]:
    translate <string> using google api.
    lang option specifies the direction of translation. <language> it is 2-character code of language.
    Default direction: en|ru'''
        try: (text, lang) = msg.rsplit(' lang ', 1)
        except ValueError:
            text = msg
            lang = 'en|ru'
        
        if lang.find('jp') >= 0:
            sendfunc('Use ja, Luke.', 'groupchat')
            return
                    
        response = json.loads(self.goUrl('http://ajax.googleapis.com/ajax/services/language/translate?v=1.0&',
                                   {'q' : text,'langpair':lang}))
        if response and response.has_key('responseData') and response['responseData'] and response['responseData'].has_key('translatedText'):
            sendfunc(response['responseData']['translatedText'], 'groupchat')
        else:
            sendfunc('NO WAI!', 'groupchat')
    
    def google(self, sendfunc, msg):
        '''
google <string> [results <number>]:
    google <string> in google.
    results - number of printed search results.'''
        try: (text, numresults) = msg.rsplit(' results ', 1)
        except ValueError:
            text = msg
            numresults = 1
        
        try: numresults = int(numresults)
        except Exception: numresults = 1        
        
        response = json.loads(self.goUrl('http://ajax.googleapis.com/ajax/services/search/web?v=1.0&', 
                                   {'q' : text}))
        
        if response and response.has_key('responseData') and response['responseData'] and response['responseData'].has_key('results'):
            num = 0
            for result in response['responseData']['results']:
                if numresults > 0 and num >= numresults:
                    break
                result['content'] = result['content'].replace('<b>', '').replace('</b>', '')                
                sendfunc(' '.join([result['titleNoFormatting'], result['content'], result['url']]), 'groupchat')
                num += 1
        else:
            sendfunc('NO WAI!', 'groupchat')

    
    def goUrl(self, url=None, params = {}):
        if not url: return
        query = ''
        if len(params):
            query = urllib.urlencode(params)
        url = url + query
        results = urllib.urlopen(url)
        return results.read()
        
        