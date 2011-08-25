# -*- coding: utf-8 -*-
import lxml.html
import re
from functions import goUrl

class UrlHead:

    _marvinModule = True
    public = ['urlhead']
    
    def urlhead():
        None

    def _urlhead(self,message):
        if 'http://' or 'https://' in message.text:
            try:
                foo = re.findall(r'(htt[p|ps]s?://\S+)', message.text)
                for url in foo:
                # dirty code for cyrillic domains
                # TODO: punycode converter
                    if u'.рф' in url:
                        encodedHtml = goUrl('http://idnaconv.phlymail.de/index.php?decoded=' + url.encode('utf-8') + '&idn_version=2008&encode=Encode+>>')
                        temp = re.search(r'(https?://xn--\S+)', encodedHtml)
                        url = temp.group(0).replace('"','')
                # end of dirty code
                    try: 
                        html = lxml.html.fromstring(goUrl(url).decode('utf-8'))
                    except:
                        html = lxml.html.fromstring(goUrl(url))
                    title = " ".join(html.find('.//title').text.split())
                    message.reply('Title: ' + title)
            except IOError:
                message.reply('Link broken. Can\'t get header!')
            except AttributeError:
                pass
        else:
            return None
