#!/bin/env python2

#
#
#

__github__ = 'https://github.com/blue-sky-r/keyboard-test'

__about__  = 'Keyboard Test Program'

__version__ = '2017.7'

__copyright__  = '(c) 2017 by Robert P'

import sys
import re
import subprocess, os


class Gui:
    """ GUI class using ANSI escape codes """

    # http://wiki.bash-hackers.org/scripting/terminalcodes
    #
    ESC = '\033'

    # video attributes
    ATTR = {
        'reset':    '0',
        'bold':     '1',
        'dim':      '2',
        'standout': '3',
        'underline':'4',
        'blink':    '5',
        'inverse':  '7',
        'hide':     '8'
    }

    # background
    BG = {
        'black':    '40',
        'red':      '41',
        'green':    '42',
        'yellow':   '43',
        'blue':     '44',
        'magenta':  '45',
        'cyan':     '46',
        'white':    '47'
    }

    # foreground
    FG = {
        'black':    '30',
        'red':      '31',
        'green':    '32',
        'yellow':   '33',
        'blue':     '34',
        'magenta':  '35',
        'cyan':     '36',
        'white':    '37'
    }

    header = '= %(about)s = version %(version)s = Press Key by Key until done = %(github)s = xinput %(xinputver)s = %(c)s ='

    footer = '= Total Keys: %(total)3d = Tested: %(tested)3d = To go: %(togo)3d = Last Key: '

    def __init__(self, xinputver):
        data = {
            'about'     : __about__,
            'version'   : __version__,
            'github'    : __github__,
            'xinputver' : xinputver,
            'c'         : __copyright__
        }
        self.header = self.header % data

    def write(self, str):
        sys.stdout.write(str)

    def write_flush(self, str):
        self.write(str)
        sys.stdout.flush()

    def beep(self):
        self.write('\007')

    def write_esc(self, str):
        s = '%s[%s' % (self.ESC, str)
        self.write(s)

    def write_attr(self, attr):
        s = ';'.join(attr) if type(attr) == list else attr
        self.write_esc(s + 'm')

    def write_at(self, line1, col1):
        str = '%d;%dH' % (line1, col1)
        self.write_esc(str)

    def home(self):
        str = 'H'
        self.write_esc(str)
        self.atrow = 1

    def clear_screen(self):
        str = '2J'
        self.write_esc(str)
        self.home()

    def move_up(self, n, str):
        s = '%d;%dH' % (n, str)
        self.write_esc(s)

    def color(self, attr=None, fg=None, bg=None):
        seq = []
        for var,dct in zip([attr, fg, bg], [self.ATTR, self.FG, self.BG]):
            if var is None: continue
            a = dct.get(var)
            if a: seq.append(a)
        self.write_attr(seq)

    def print_(self, str):
        print str,

    def print_ln(self, str=''):
        print str
        self.atrow += 1

    def show_map(self, stats):
        self.clear_screen()
        self.show_header()
        self.maprow = self.atrow-1
        #
        for line in self.map:
            self.print_ln(line)
        #
        self.print_ln()
        # footer = status line
        self.statusrow = self.atrow
        self.update_stats(stats)

    def show_header(self):
        self.print_ln(self.header)
        self.print_ln()

    def update_stats(self, data):
        self.print_(self.footer % data)

    def key_action(self, keydict, action):
        if action == 'press':
            self.color(fg='black', bg='red')
        if action == 'release':
            self.color(fg='black', bg='green')
        row1,col1,txt = keydict['row']+1, keydict['col']+1, keydict['label']
        self.write_at(row1+self.maprow, col1)
        self.write_flush(txt)
        #
        self.color(attr='reset')
        self.write_at(self.statusrow,1)


class Xinput:

    def __init__(self):
        self.exe = 'xinput'

    def version(self):
        args = [self.exe, '--version']
        try:
            xinput = subprocess.Popen(args, stdout=subprocess.PIPE)
            (stdout,stderr) = xinput.communicate()
        except OSError as e:
            return e.strerror
        # stdout
        for line in stdout.splitlines():
            pat = 'xinput version '
            if line.startswith(pat):
                return line.replace(pat, '')
        # stderr
        for line in stderr.splitlines():
            pass
        # last line
        return line

    def list(self):
        args = [self.exe, 'list']
        xinput = subprocess.Popen(args, stdout=subprocess.PIPE)
        (stdout,stderr) = xinput.communicate()
        return stdout

    def open(self, id='8'):
        args = [self.exe, 'test', id]
        self.xinput = subprocess.Popen(args, stdout=subprocess.PIPE)

    def is_open(self):
        return self.xinput

    def close(self):
        if self.xinput:
            #self.xinput.stdout.readline()
            self.xinput.terminate()

    def readline(self):
        # return stdout
        return self.xinput.stdout.readline()


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
        self.gui = Gui(self.xinput.version())
        self.stats = { 'total': 0, 'tested': 0, 'togo':0 }

    def load(self, fname):
        map = []
        with open(fname) as f:
            for line in f:
                map.append(line.rstrip(os.linesep))
        #
        self.gui.map = map
        #
        for row,line in enumerate(map):
            if not line: continue
            self.parse_line(line, row)
        # update stats total
        self.stats['total'] = len(self.layout)

    def parse_line(self, line, row):
        for m in re.finditer(r'\[(\s+(\S+)\s+)\]', line):
            label,key,col = m.group(1),m.group(2),m.start(1)
            self.add_key(key, row, col, label)

    def add_key(self, key, row, col, label, tested=False):
        keycode = self.key_to_keycode(key)
        self.layout[keycode] = { 'row': row, 'col': col, 'key': key, 'label': label, 'tested': tested }

    def key_to_keycode(self, key):
        return self.rev_xmodmap.get(key, '?')

    def test(self):
        # stats
        self.update_stats()
        self.gui.show_map(self.stats)
        self.xinput.open()
        ign1stkeycode = self.rev_xmodmap['RET']
        while not self.all_tested():
            action,keycode = self.keypress()
            keydict = self.keycode_to_key(keycode)
            # ignore 1st keycode
            if ign1stkeycode:
                if ign1stkeycode == keycode:
                    continue
                ign1stkeycode = None
            # gui feedback
            self.gui.key_action(keydict, action)
            # register
            if action == 'press': keydict['tested'] = True
            # stats
            self.update_stats()
            self.gui.update_stats(self.stats)
        self.xinput.close()

    def update_stats(self):
        tested, togo = 0,0
        for k, v in self.layout.items():
            if v['tested']:
                tested += 1
            else:
                togo += 1
        self.stats['tested'] = tested
        self.stats['togo'] = togo

    def all_tested(self):
        #return all([ v['tested'] for k,v in self.layout.items() ])
        return self.stats['tested'] == self.stats['total']

    def keypress(self):
        # wait for key
        line = self.xinput.readline()
        #print 'keypress():line=',line
        m = re.search('key (press|release)\s+(\d+)', line)
        action  = m.group(1)
        keycode = m.group(2)
        return action,int(keycode)

    def keycode_to_key(self, keycode):
        return self.layout.get(keycode)


if __name__ == '__main__':
    l = Layout()

    # print l.xinput.list()

    l.load('apple.lay')
    l.test()
