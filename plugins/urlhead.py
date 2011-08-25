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
                foundUrl = re.findall(r'(htt[p|ps]s?://\S+)', message.text)
                for selectUrl in foundUrl:
                # dirty code for cyrillic domains
                # TODO: punycode converter
                    if u'.рф' in selectUrl:
                        encodedHtml = goUrl('http://idnaconv.phlymail.de/index.php?decoded=' + selectUrl.encode('utf-8') + '&idn_version=2008&encode=Encode+>>')
                        temp = re.search(r'(https?://xn--\S+)', encodedHtml)
                        selectUrl = temp.group(0).replace('"','')
                # end of dirty code
                    try: 
                        html = lxml.html.fromstring(goUrl(selectUrl).decode('utf-8'))
                    except:
                        html = lxml.html.fromstring(goUrl(selectUrl))
                    sourceTitle = html.find('.//title').text
                    title = " ".join(sourceTitle.split())
                    message.reply('Title: ' + title)
            except IOError:
                message.reply('Link broken. Can\'t get header!')
            except AttributeError:
                pass
        else:
            return None
