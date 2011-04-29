# -*- coding: utf-8 -*-
import re
from string import maketrans

MainObject = 'Misc'

class Misc:
    ''' Misc functions
turn <string>'''

    public = ['turn']
    
    def turn(self, sendfunc, msg):
        if re.match(u'[А-я]+', msg):
            trlist = [u'QWERTYUIOP{}ASDFGHJKL;"ZXCVBNM<>?qwertyuiop[]asdfghjkl;\'zxcvbnm,./', #'
                      u'ЙЦУКЕНГШЩЗХЪФЫВАПРОЛДЖЭЯЧСМИТЬБЮ,йцукенгшщзхъфывапролджэячсмитьбю.']
        else:
            trlist = [u'ЙЦУКЕНГШЩЗХЪФЫВАПРОЛДЖЭЯЧСМИТЬБЮ,йцукенгшщзхъфывапролджэячсмитьбю.',
                      u'QWERTYUIOP{}ASDFGHJKL;"ZXCVBNM<>?qwertyuiop[]asdfghjkl;\'zxcvbnm,./'] #'        
        
        print trlist
        trstring = ''.join(map(lambda x: trlist[1][trlist[0].find(x)], msg))
        sendfunc(trstring)
