#!/bin/env python2

#
#
#

import sys
import re
import subprocess, os


class Gui:
    """ GUI class using ANSI escape codes """

    # http://ascii-table.com/ansi-escape-sequences.php
    #
    ESC = '\033'

    NORMAL  = '0'
    BOLD    = '1'
    BLINK   = '5'
    INVERSE = '7'

    def beep(self):
        sys.stdout.write('\007')

    def print_esc(self, str):
        s = '%s[%s' % (cls.ESC, str)
        sys.stdout.write(s)
        sys.stdout.flush()

    def print_attr(self, attr):
        s = ';'.join(attr) if type(attr) == 'list' else attr
        self.print_esc(s+'m')

    def print_at(self, line, col):
        str = '%d;%dH' % (line. col)
        self.print_esc(str)

    def clear_screen(self):
        self.row = 0
        str = '2J'
        self.print_esc(str)

    def move_up(self, n, str):
        s = '%d;%dH' % (n, str)
        self.print_esc(s)

    def vid_normal(self):
        self.print_attr(self.NORMAL)

    def vid_bold(self):
        self.print_attr(self.BOLD)

    def vid_blink(self):
        self.print_attr(self.BLINK)

    def vid_inverse(self):
        self.print_attr(self.INVERSE)

    def set_map(self, guimap):
        self.guimap = guimap

    def print_(self, str):
        self.row += 1
        print str,

    def print_ln(self, str):
        self.row += 1
        print str

    def map(self):
        self.print_ln
        self.print_ln "Keyboard Test - press any key until all keys are tested"
        self.print_ln
        self.map0 = self.row
        for line in self.guimap:
            self.print_ line

    def key_action(self, keydict, action):
        txt = keydict['key']
        self.print_at(keydict['row']+self.map0, keydict['col'], txt)

class Xinput:

    def __init__(self):
        self.exe = 'xinput'

    def list(self):
        args = [self.exe, 'list']
        xinput = subprocess.Popen(args, stdout=subprocess.PIPE)
        (stdout,stderr) = xinput.communicate()
        return stdout

    def open(self, num=8):
        args = [self.exe, 'test', num]
        self.xinput = subprocess.Popen(args, stdout=subprocess.PIPE)

    def is_open(self):
        return self.xinput

    def close(self):
        if self.xinput: self.xinput.terminate()

    def get_line(self):
        line = []
        fd = self.xinput.stdout.fileno()
        while True:
            try:
                c = os.read(fd, 1)
            except:
                continue
            line.append(c)
            if c == '\n': break
        return ''.join(line)


class Layout:

    # xmodmap -pk
    # key -> keycode
    rev_xmodmap = {
        'ESC': 9,
        '1': 10,
        '2': 11,
        '3': 12,
        '4': 13,
        '5': 14,
        '6': 15,
        '7': 16,
        '8': 17,
        '9': 18,
        '0': 19,
        '-': 20,
        '=': 21,
        'BS': 22,
        'TAB': 23,
        'q': 24,
        'w': 25,
        'e': 26,
        'r': 27,
        't': 28,
        'y': 29,
        'u': 30,
        'i': 31,
        'o': 32,
        'p': 33,
        '(': 34,
        ')': 35,
        'RET': 36,
        'LCTR': 37,
        'a': 38,
        's': 39,
        'd': 40,
        'f': 41,
        'g': 42,
        'h': 43,
        'j': 44,
        'k': 45,
        'l': 46,
        ';': 47,
        "'": 48,
        '~': 49,
        'LSHIFT': 50,
        '\\': 51,
        'z': 52,
        'x': 53,
        'c': 54,
        'v': 55,
        'b': 56,
        'n': 57,
        'm': 58,
        ',': 59,
        '.': 60,
        '/': 61,
        'RSHIFT': 62,
        '*n': 63,
        'LALT': 64,
        'SPACEBAR': 65,
        'CAPS': 66,
        'F1': 67,
        'F2': 68,
        'F3': 69,
        'F4': 70,
        'F5': 71,
        'F6': 72,
        'F7': 73,
        'F8': 74,
        'F9': 75,
        'F10': 76,
        'NUML': 77,
        'SCRL': 78,
    }

    def __init__(self):
        # keycode -> (row,col), key, tested
        self.layout = {}
        self.xinput = Xinput()
        self.gui = Gui()

    def load(self, fname):
        with open(fname) as f:
            map = f.readlines()
        #
        self.gui.set_map(map)
        #
        for row,line in enumerate(self.map):
            if not line: continue
            self.parse_line(line, row)

    def parse_line(self, line, row):
        for m in re.finditer(r'\[\s+(\S+)\s+\]', line):
            key,col = m.group(0), m.start(0)
            self.add_key(key, row, col)

    def add_key(self, key, row, col, tested=False):
        keycode = self.key_to_keycode(key)
        self.layout[keycode] = { 'row': row, 'col': col, 'key': key, 'tested': tested }

    def key_to_keycode(self, key):
        return self.keycode.get(key, '?')

    def test(self):
        while not self.all_tested():
            action,keycode = self.keypress()
            key = self.keycode_to_key(keycode)
            self.gui_key_action(action, key)

    def all_tested(self):
        return all([ l['tested'] for l in self.layout.items() ])

    def keypress(self):
        # start xinput if not running
        if not self.xinput.is_open():
            self.xinput.open()
        # wait for key
        line = self.xinput.get_line()
        m = re.search('key (press|release)\s+(\d+)', line)
        action  = m.group(1)
        keycode = m.group(2)
        return action,int(keycode)

    def keycode_to_key(self, keycode):
        return self.layout.get(keycode)


l = Layout()
l.load('apple.lay')
l.gui_display()
l.test()
