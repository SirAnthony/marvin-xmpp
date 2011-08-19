# -*- coding: utf-8 -*-

from hashlib import sha1
from random import choice, randint

def sliding_window(n):
    def _cover(f):
        def _f(self, *args):
            while len(args) >= n:
                f(self, *args[:n])
                args = args[1:]
        return _f
    return _cover

class Markov:

    prefix_length = 2

    _marvinModule = True
    depends = ['plugins.logger',]
    public = [ ]

    def normalize(self, s):
        return self._aliases.get(s, s)

    def denormalize(self, s):
        aliases = self._groups.get(s)
        return s if aliases is None else choice(aliases)

    def __make_group(self, *words):
        key_length = 0xC
        k = sha1(' '.join(words)).hexdigest()[:key_length]
        self._groups[k] = words
        for s in words:
            self._aliases[s] = k

    def __add_to_group(self, word, words):
        k = self._aliases.get(word)
        if k:
            for w in words:
                self._aliases[w] = k
        else:
            self.__make_group(word, *words)

    def __init__(self):
        self._groups = {}
        self._aliases = {}
        self._markov = {}
        self.__add_to_group('возвестил', ['воскликнул', 'ответил', 'подумал', 'прошептал', 'сказал', 'спросил'])
        self.load_texts()
        self.load_logs()

    def generate(self):
        result = []
        word_count = randint(4,  15)
        if not self._markov.keys():
            return 'NO!'
        prefix = choice(self._markov.keys())
        result.extend(map(self.denormalize, prefix))
        n = self.prefix_length
        while n < word_count:
            next = self._markov.get(prefix)
            if next is None:
                # FIXME
                prefix = choice(self._markov.keys())
                result.extend(map(self.denormalize, prefix))
                n += self.prefix_length
            else:
                s = choice(next)
                prefix = prefix[1:] + (s,)
                result.append(self.denormalize(s))
                n += 1
        return ' '.join(result)

    @sliding_window(prefix_length + 1)
    def _push(self, *args):
        args = map(self.normalize, args)
        k = tuple(args[:self.prefix_length])
        if k in self._markov:
            self._markov[k] += [args[self.prefix_length]]
        else:
            self._markov[k] = [args[self.prefix_length]]

    def load_data(self, table):
        logger = None
        try:
            logger = self.depends['plugins.logger']
        except:
            pass
        if not logger:
            return
        result, log = logger._getLog(table, select=['text'], count=0)
        if not result:
            print log
            return
        for text in log:
            self._push(*(text[0].split()))

    def load_texts(self):
        self.load_data('paste_texts')

    def load_logs(self):
        tables = None
        try:
            tables = self.depends['plugins.logger']._getTables()
        except:
            return
        for table in tables:
            if table != 'paste_texts':
                self.load_data(table)

    def say(self, message):
        message.reply(message.resource + ': ' + self.generate())
