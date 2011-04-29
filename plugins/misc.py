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
        
        d = msg
        for char in d:
            idx = trlist[1].index(char)
            msg = msg.replace(trlist[1][idx], trlist[0][idx])
        sendfunc(msg)
