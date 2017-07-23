#!/bin/env python2

#
#
#

import sys
import re

class Print:

    ESC = '\033'

    @classmethod
    def print_esc(cls, str):
        s = '%s[%s' % (cls.ESC, str)
        sys.stdout.write(s)
        sys.stdout.flush()

    @classmethod
    def at(cls, line, col):
        str = '%d;%dH' % (line. col)
        cls.print_esc(str)

    @classmethod
    def cls(cls):
        str = '2J'
        cls.print_esc(str)

    @classmethod
    def up(cls, n, str):
        s = '%d;%dH' % (n, str)
        cls.print_esc(s)


class Layout:

    scancode = {}
    gui_map  = []

    def __init__(self):
        # scancode -> (row,col)
        self.layout = {}

    def load(self, fname):
        with open(fname) as f:
            self.gui_map = f.readlines()
        #
        for row,line in enumerate(self.gui_map):
            if not line: continue
            self.parse_line(line, row)

    def parse_line(self, line, row):
        for m in re.finditer(r'\[\s+(\S+)\s+\]', line):
            key,col = m.group(0), m.start(0)
            self.add_key(key, row, col)

    def add_key(self, key, row, col, tested=False):
        scancode = self.key_to_scancode(key)
        self.layout[scancode] = { 'row': row, 'col': col, 'key': key, 'tested': tested }

    def key_to_scancode(self, key):
        return self.scancode.get(key, '?')

    def display(self):
        pass

    def test(self):
        while not self.all_tested():
            code = self.keypress()
            key = self.code2key(code)
            self.key_pressed(key)

l = Layout()
l.load('apple.lay')
l.test()
