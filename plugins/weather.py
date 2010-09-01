import urllib
from xml.dom import minidom
from pprint import pprint

class Weather:
    public = ['weather']
    
    def weather(self, sendfunc, msg):
    	location = msg.split(' ')
        source = "http://www.google.com/ig/api?weather=%s" % location[0]
        target = urllib.urlopen(source)
        xmlraw = minidom.parse(target)
        try:
            result_tmp = xmlraw.getElementsByTagName('current_conditions')
            weather = result_tmp[0].childNodes[2].attributes['data'].value
            humidity = result_tmp[0].childNodes[3].attributes['data'].value
            message = 'Weather in %s is %sC. %s' % (location[0], weather, humidity)
        except:
            message = '%s not found on this planet. Please try another one.' % location[0]
        sendfunc(message, 'groupchat')
    
        
        
