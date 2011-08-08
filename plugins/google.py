
import json
from functions import goUrl

class Google:
    ''' Google module
google <string> [results <number>]
translate <string> [lang <language>|<language>]'''

    _marvinModule = True
    public = ['translate', 'google']
    aliases = {'google': ['g', 'ggl'], 'translate': ['tr', 'tran']}
    
    def translate(self, message):
        '''
translate <string> [lang <language>|<language>]:
    translate <string> using google api.
    lang option specifies the direction of translation. <language> it is 2-character code of language.
    Default direction: en|ru'''
        try: (text, lang) = message.ctext.rsplit(' lang ', 1)
        except ValueError:
            text = message.ctext
            lang = 'en|ru'
        
        if lang.find('jp') >= 0:
            message.reply('Use ja, Luke.')
            return
        
        langs = lang.split('|')
        response = ''
        for i in range(0, len(langs)-1):
            response = json.loads(goUrl('http://ajax.googleapis.com/ajax/services/language/translate?v=1.0&',
                                   {'q' : text,'langpair':langs[i]+'|'+langs[i+1]}))
            if response and response.has_key('responseData') and response['responseData'] and response['responseData'].has_key('translatedText'):
                text = response['responseData']['translatedText']
            else:
                message.reply('Translate from ' + langs[i] + ' to ' + langs[i+1] + ' fail. Last: ' + text)
                return
        if response and response.has_key('responseData') and response['responseData'] and response['responseData'].has_key('translatedText'):
            message.reply(response['responseData']['translatedText'])
        else:
            message.reply('NO WAI!')
    
    def google(self, message):
        '''
google <string> [results <number>]:
    google <string> in google.
    results - number of printed search results.'''
        try: (text, numresults) = message.ctext.rsplit(' results ', 1)
        except ValueError:
            text = message.ctext
            numresults = 1
        
        try: numresults = int(numresults)
        except Exception: numresults = 1        
        
        response = json.loads(goUrl('http://ajax.googleapis.com/ajax/services/search/web?v=1.0&', {'q' : text}))
        
        if response and response.has_key('responseData') and response['responseData'] and response['responseData'].has_key('results'):
            num = 0
            for result in response['responseData']['results']:
                if numresults > 0 and num >= numresults:
                    break
                result['content'] = result['content'].replace('<b>', '').replace('</b>', '')                
                message.reply(' '.join([result['titleNoFormatting'], result['content'], result['url']]))
                num += 1
        else:
            message.reply('NO WAI!')
