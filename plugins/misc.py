# -*- coding: utf-8 -*-
import re
from string import maketrans

class Misc:
    ''' Misc functions
turn <string>'''

    _marvinModule = True
    public = ['turn']
    aliases = {'turn': ['t']}

    def turn(self, message):
        '''
turn <text>
Turn string from one to another keyboard variant. Only qwerty <-> йцукен supported now.'''
        if re.match(u'[А-я]+', message.ctext):
            trlist = [u'QWERTYUIOP{}ASDFGHJKL;"ZXCVBNM<>?qwertyuiop[]asdfghjkl;\'zxcvbnm,./', #'
                      u'ЙЦУКЕНГШЩЗХЪФЫВАПРОЛДЖЭЯЧСМИТЬБЮ,йцукенгшщзхъфывапролджэячсмитьбю.']
        else:
            trlist = [u'ЙЦУКЕНГШЩЗХЪФЫВАПРОЛДЖЭЯЧСМИТЬБЮ,йцукенгшщзхъфывапролджэячсмитьбю.',
                      u'QWERTYUIOP{}ASDFGHJKL;"ZXCVBNM<>?qwertyuiop[]asdfghjkl;\'zxcvbnm,./'] #'        

        msg = None
        for char in message.ctext:
            idx = trlist[1].index(char)
            msg = msg.replace(trlist[1][idx], trlist[0][idx])
        message.reply(msg)
