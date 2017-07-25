#!/bin/env python2

# Simple Keyboard Test Program
#
# - draws semi-graphics keyboard layout
# - shows actually pressed key in red
# - all already tested keys shows in green
#
# Press key by key until entire keyboard is green = test passed
#
# semi-graphical keyboard layout is editable in *.lay files
#
# Depends on xinput therefore it runs only on linux based systems !
#

__github__ = 'https://github.com/blue-sky-r/keyboard-test'

__about__  = 'Keyboard Test Program'

__version__ = '2017.7'

__copyright__  = '(c) 2017 by Robert P'


import sys
import re
import subprocess, os
import datetime


class Gui:
    """ GUI class using ANSI escape codes """

    # http://wiki.bash-hackers.org/scripting/terminalcodes
    #
    ESC = '\033'

    # video attributes
    ATTR = {
        'reset':    0,
        'bold':     1,
        'dim':      2,
        'standout': 3,
        'underline':4,
        'blink':    5,
        'inverse':  7,
        'hide':     8
    }

    # background
    BG = {
        'black':    40,
        'red':      41,
        'green':    42,
        'yellow':   43,
        'blue':     44,
        'magenta':  45,
        'cyan':     46,
        'white':    47
    }

    # foreground
    FG = {
        'black':    30,
        'red':      31,
        'green':    32,
        'yellow':   33,
        'blue':     34,
        'magenta':  35,
        'cyan':     36,
        'white':    37
    }

    header = '= %(about)s = version %(version)s = Press Key by Key until done = %(github)s = xinput %(xinputver)s = %(c)s ='

    footer = '= Total Keys: %(total)3d = Tested: %(tested)3d = To go: %(togo)3d = Missing keycodes: %(missing)3d = Last Key: '

    def __init__(self, xinputver):
        """ update header template with configurable strings and xinput version """
        data = {
            'about'     : __about__,
            'version'   : __version__,
            'github'    : __github__,
            'xinputver' : xinputver,
            'c'         : __copyright__
        }
        self.header = self.header % data

    def write(self, str):
        """ write directly to stdout """
        sys.stdout.write(str)

    def write_flush(self, str):
        """ write directly to stdout and flush """
        self.write(str)
        sys.stdout.flush()

    def beep(self):
        """ sound bell """
        self.write('\007')

    def write_esc(self, str):
        """ send ANSI escape sequence"""
        s = '%s[%s' % (self.ESC, str)
        self.write(s)

    def write_attr(self, attr):
        """ send attribute as string or as multiple as list """
        s = ';'.join(attr) if type(attr) == list else attr
        self.write_esc(s + 'm')

    def write_at(self, line1, col1):
        """ set cursor position at line,col (1-based) """
        str = '%d;%dH' % (line1, col1)
        self.write_esc(str)

    def home(self):
        """ set cursor home position = (1,1) """
        str = 'H'
        self.write_esc(str)
        self.atrow = 1

    def clear_screen(self):
        """ clear entire screen and set home position """
        str = '2J'
        self.write_esc(str)
        self.home()

    def clear_line(self):
        str = 'K'
        self.write_esc(str)

    def move_up(self, n=1):
        """ move cursor n lines up """
        s = '%dF' % n
        self.write_esc(s)

    def color(self, attr=None, fg=None, bg=None):
        """ send ANSI color """
        seq = []
        for var,dct in zip([attr, fg, bg], [self.ATTR, self.FG, self.BG]):
            if var is None: continue
            a = "%d" %  dct.get(var)
            if a: seq.append(a)
        self.write_attr(seq)

    def print_(self, str):
        """ print and stay on line """
        print str,

    def print_ln(self, str=''):
        """ print with newline """
        print str
        self.atrow += 1

    def set_map(self, map):
        """ set gui map layout """
        self.map = map

    def show_map(self):
        """ clears screen and draws layout map """
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

    def show_header(self):
        """ show header line and separator line """
        self.print_ln(self.header)
        self.print_ln()

    def update_stats(self, data):
        """ print/update status line = footer """
        self.print_(self.footer % data)

    def key_action(self, keydict, action):
        """ visualize key action press (red) / release (green) """
        if action == 'press':
            self.color(fg='black', bg='red')
        if action == 'release':
            self.color(fg='black', bg='green')
        row1,col1,txt = keydict['row']+1, keydict['col']+1, keydict['label']
        self.write_at(row1+self.maprow, col1)
        self.write_flush(txt)
        # set position for unwanted xinput output to the ends of status line
        self.color(attr='reset')
        self.write_at(self.statusrow,1)
        sys.stdout.flush()


class Xinput:
    """ executing xinput as subprocess """

    def __init__(self):
        self.exe = 'xinput'

    def version(self):
        """ get actual xinput version or error message if not found """
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
        """ list xinput devices """
        args = [self.exe, 'list']
        xinput = subprocess.Popen(args, stdout=subprocess.PIPE)
        (stdout,stderr) = xinput.communicate()
        return stdout

    def open(self, id='12'):
        """ open xinput device id """
        args = [self.exe, 'test', id]
        self.xinput = subprocess.Popen(args, stdout=subprocess.PIPE)

    def is_open(self):
        return self.xinput

    def close(self):
        """ terminate xinput subprocess """
        if self.xinput:
            #self.xinput.stdout.readline()
            self.xinput.terminate()

    def readline(self):
        """ read stdout line of xinput """
        return self.xinput.stdout.readline()


class Layout:
    """ keyboard layout """

    # reverse xmodmap -pk (use rev_xmodmap.sh for possible updates)
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
        '[': 34,
        ']': 35,
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
        '`': 49,
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
        '_*': 63,
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
        '_7': 79,
        '_8': 80,
        '_9': 81,
        '_-': 82,
        '_4': 83,
        '_5': 84,
        '_6': 85,
        '_+': 86,
        '_1': 87,
        '_2': 88,
        '_3': 89,
        '_0': 90,
        '_.': 91,
        'ISO_Level3_Shift': 92,
        'less': 94,
        'F11': 95,
        'F12': 96,
        'Katakana': 98,
        'Hiragana': 99,
        'Henkan_Mode': 100,
        'Muhenkan': 102,
        'ENT': 104,
        'RCTR': 105,
        '_/': 106,
        'PSCR': 107,
        'RALT': 108,
        'Linefeed': 109,
        'HOME': 110,
        'UP': 111,
        'PGUP': 112,
        'LEFT': 113,
        'RIGHT': 114,
        'END': 115,
        'DOWN': 116,
        'PGDN': 117,
        'INS': 118,
        'DEL': 119,
        '_=': 125,
        'plus-': 126,
        'PAUS': 127,
        'KP_Decimal': 129,
        'Hangul': 130,
        'Hangul_Hanja': 131,
        'Super_L': 133,
        'Super_R': 134,
        'Menu': 135,
        'Cancel': 136,
        'Redo': 137,
        'SunProps': 138,
        'Undo': 139,
        'SunFront': 140,
        'Help': 146,
        'parenleft': 187,
        'parenright': 188,
        'Redo': 190,
        'Mode_switch': 203,
    }

    def __init__(self):
        """ init required classes """
        # keycode -> (row,col), key, tested
        self.layout = {}
        self.xinput = Xinput()
        self.gui = Gui(self.xinput.version())

    def load(self, fname):
        """ load keyboard layout from fname map file and parse it (create layout dictionary) """
        self.missingkeycodes = 0
        map = []
        with open(fname) as f:
            for line in f:
                map.append(line.rstrip(os.linesep))
        # send map also to gui
        self.gui.set_map(map)
        # parse map
        for row,line in enumerate(map):
            if not line: continue
            self.parse_line(line, row)

    def parse_line(self, line, row):
        """ extract all keys from single line of map layout """
        for m in re.finditer(r'\[(\s+(\S+)\s+)\]', line):
            label,key,col = m.group(1),m.group(2),m.start(1)
            self.add_key(key, row, col, label)

    def add_key(self, key, row, col, label, tested=False):
        """ add single key to layout dictionary """
        # find keycode for key
        keycode = self.key_to_keycode(key)
        if keycode:
            # if found add to layout
            self.layout[keycode] = { 'row': row, 'col': col, 'key': key, 'label': label, 'tested': tested }
        else:
            # if not found shows error message
            self.missingkeycodes += 1
            print "ERR: missing keycode for key [ %s ]" % key

    def key_to_keycode(self, key):
        """ reverse xmodmap mapping lookup symbolic_key -> keycode """
        return self.rev_xmodmap.get(key)

    def test(self):
        """ main test loop"""
        # optional pause if we have parsing errors
        self.pause()
        # draw gui layout map and stats
        self.gui.show_map()
        self.update_stats()
        # start xinput subprocess
        self.xinput.open()
        # ignore the 1st RETURN key
        ign1stkeycode = self.rev_xmodmap['RET']
        # loop until all is tested
        while not self.all_tested():
            # key event from xinput
            action,keycode = self.keypress()
            # get keydict struct from layout with coordinates, label, etc
            keydict = self.keycode_to_key(keycode)
            # ignore unknown keys
            if not keydict: continue
            # ignore 1st keycode
            if ign1stkeycode:
                # just loop if key is ignored
                if ign1stkeycode == keycode:
                    continue
                # stop ignoring
                ign1stkeycode = None
            # gui visual feedback
            self.gui.key_action(keydict, action)
            # register key has been tested
            if action == 'release': keydict['tested'] = True
            # footer stats
            self.update_stats()
        # end xinput subprocess
        self.xinput.close()
        # mini report
        self.report()
        #self.gui.clear_line()

    def pause(self):
        """ optional pause only if we have missing keycodes so the user can see errors """
        if self.missingkeycodes == 0: return
        print
        _ = raw_input('Press ENTER to continue ...')

    def update_stats(self):
        """ update footer stats """
        tested = len([ k for k,v in self.layout.items() if v['tested'] ])
        total  = len(self.layout) + self.missingkeycodes
        stats = {
            'total': total,
            'tested': tested,
            'togo': total-tested,
            'missing': self.missingkeycodes
        }
        self.gui.update_stats(stats)

    def all_tested(self):
        """ are we doone = all keys has been tested """
        return all([ v['tested'] for k,v in self.layout.items() ])

    def keypress(self):
        """ xinput key event press/release and keycode"""
        # wait for key
        line = self.xinput.readline()
        # key press 128
        m = re.search('key (press|release)\s+(\d+)', line)
        action  = m.group(1)
        keycode = m.group(2)
        # return action (press/release0 and int keycode
        return action,int(keycode)

    def keycode_to_key(self, keycode):
        """ keycode entry from layout dictionary """
        return self.layout.get(keycode)

    def report(self):
        """ mini report - right now only timestamp """
        print
        print
        print "= TEST PASSED - all keys successfully tested @",datetime.datetime.now(),"="
        print


if __name__ == '__main__':

    l = Layout()
    l.load('at101.lay')
    l.test()
