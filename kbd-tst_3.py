#!/usr/bin/python3

# Simple Keyboard Test Program - inspired by old DOS CheckIt / QA Plus
#
# - draws ASCII-graphics keyboard layout
# - shows actually pressed key in red
# - all already tested keys shows in green
#
# How to use: Press key by key until entire keyboard is green = test passed
#
# ASCII-graphical keyboard layout is editable in *.lay files (see provided files for details)
#
# Depends on xinput - therefore it runs only on linux Xorg based systems !
#

__github__ = 'https://github.com/blue-sky-r/keyboard-test'

__about__  = 'Keyboard Test Program'

__version__ = '2017.7.30'

__copyright__  = '(c) 2017 by Robert P'

__usage__ = \
"""
Usage: kbd-tst.py [id] [layout] [-h|--help]
       kbd-tst.py [-h|--help] [layout] [id]
       
    -h     ... shows this usage help and quits
    --help ... shows this usage help and quits
    id     ... optional keyboard xinput id as shown in 'xinput list' output (default user assisted autodetection)
    layout ... optional keyboard ASCII layout file [*.lay] (default the first file in kbd-tst dir)
    
Notes: 
    * parameters are optional
    * not providing xinput id will initiate a user assisted autodetection sequence requiring physical disconneting 
      and reconecting the keyboard under test (KUT)
    * not providing the layout file is usefull if there is only single layout file in kbd-tst directory
    * all unrecognized keys from layout file are shown as errors and counted as [ missing_keycodes ]
    * all parameters can be supplied in arbitrary order
    * in case of multiple specification the last one wins,
      for example in sequence of parameters 'id1 layout1 layout2 id2' id2/layout2 pair wins
    * test ends when all successfully recognized keys from layout file are tested [ to_go = 0 ]
    * to end test prematurely just type phrase 'quit' (without the quotes)
    
Known issues:
    - keys ike apple keyb VOL+/VOL-/MUTE/EJECT do not generate xinput events and therefore cannot be tested right now 
    - if more than one xinput id is found by autodetection sequence only the first one is used, which is some cases
      might be incorrect. In this case provide the correct xinput id as a parameter (id can be found by trial and error
      from 'xinput list' and verified by 'xinput test id' to check 'key press xx' and 'key release xx' events) 
      [ xinput double entries related bug: https://bugs.launchpad.net/ubuntu/+source/hal/+bug/277946 ]
    
"""

import sys
import re
import subprocess, os
import datetime, time
import termios


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
        'white':    47,
        'reset':    49
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
        'white':    37,
        'reset':    39
    }

    header = '= %(about)s = version %(version)s = Press Key by Key until done = %(github)s = xinput %(xinputver)s = %(c)s ='

    footer = '= x.id: %(id)d [ %(devname)s ] = File: %(layout)s = Keys: %(total)3d = Tested: %(tested)3d = To go: %(togo)3d = Missing keycodes: %(missing)3d ='

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

    def flush(self):
        sys.stdout.flush()

    def write(self, str):
        """ write directly to stdout """
        sys.stdout.write(str)

    def write_flush(self, str):
        """ write directly to stdout and flush """
        self.write(str)
        self.flush()

    def beep(self):
        """ sound bell """
        self.write_flush('\007')

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
        """ clear entire line """
        str = '2K'
        self.write_esc(str)

    def rclear_line(self):
        """ clear line right from cursor """
        str = '0K'
        self.write_esc(str)

    def lclear_line(self):
        """ clear line left from cursor """
        str = '1K'
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

    def color_reset(self):
        """ reset attr, fg, bg """
        self.color(attr='reset', fg='reset', bg='reset')
        self.flush()

    def cursor_off(self):
        """ no cursor is shown """
        self.write_esc('?25l')

    def cursor_on(self):
        """ show cursor """
        self.write_esc('?25h')

    def print_(self, str):
        """ print and stay on line """
        print(str, end=' ')

    def print_ln(self, str=''):
        """ print with newline """
        print(str)
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
        self.write_at(self.statusrow, 1)
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
        # reset color back to normal
        self.color(attr='reset')

    def banner(self, txt, bg='cyan', above=1, bellow=1):
        for i in range(above):
            print()
        #
        self.color(fg='black', bg=bg)
        print(txt)
        self.color_reset()
        self.flush()
        #
        for i in range(bellow):
            print()

    def dbg(self, txt):
        self.write_at(25,1)
        print(txt)

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
            if line.startswith(pat.encode()):
                return line.replace(pat.encode(), ''.encode())
        #
        return '?'

    def list(self, filter='keyboard'.encode(), trim=True):
        """ list xinput devices with optional filter """
        args = [self.exe, 'list']
        xinput = subprocess.Popen(args, stdout=subprocess.PIPE)
        (stdout,stderr) = xinput.communicate()
        return [ line.strip() if trim else line for line in stdout.splitlines() if filter in line ]

    def name_by_id(self, id):
        # get also ascii name for id (strip junk)
        name = [ dev.decode().strip() for dev in self.list() if "id="+str(id) in dev.decode() ]
        return name[0] if name else '?'

    def start(self, id=8):
        """ open xinput device id """
        args = [self.exe, 'test', "%d" % id]
        try:
            self.xinput = subprocess.Popen(args, stdout=subprocess.PIPE)
        except OSError as e:
            self.xinput = None
            return "%s - %s" % (self.exe, e.strerror)

    def is_running(self):
        return self.xinput and (self.xinput.poll() is None)

    def stop(self):
        """ terminate xinput subprocess """
        if self.is_running():
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
        'XF86LaunchD': 101,
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
        'XF86AudioMute': 121,
        'XF86AudioLowerVolume': 122,
        'XF86AudioRaiseVolume': 123,
        'XF86PowerOff': 124,
        '_=': 125,
        'plus-': 126,
        'PAUS': 127,
        'XF86LaunchA': 128,
        'KP_Decimal': 129,
        'Hangul': 130,
        'Hangul_Hanja': 131,
        'XF86LightBulb': 132,
        'LAPPLE': 133,
        'RAPPLE': 134,
        'Menu': 135,
        'Cancel': 136,
        'Redo': 137,
        'SunProps': 138,
        'Undo': 139,
        'SunFront': 140,
        'XF86Copy': 141,
        'XF86Open': 142,
        'XF86Paste': 143,
        'XF86AudioPrev': 144,
        'XF86Cut': 145,
        'Help': 146,
        'XF86MenuKB': 147,
        'XF86Calculator': 148,
        'XF86Sleep': 150,
        'XF86WakeUP': 151,
        'XF86Explorer': 152,
        'XF86AudioPGDN': 153,
        'XF86Xfer': 155,
        'XF86Launch1': 156,
        'XF86Launch2': 157,
        'XF86WWW': 158,
        'XF86LaunchA': 159,
        'XF86AudioMute': 160,
        'XF86Calculator': 161,
        'XF86AudioPAUS': 162,
        'XF86Mail': 163,
        'XF86AudioStop': 164,
        'XF86Sleep': 165,
        'XF86Back': 166,
        'XF86Forward': 167,
        'XF86Eject': 169,
        'XF86Eject': 170,
        'XF86AudioPGDN': 171,
        'XF86AudioPlay': 172,
        'XF86AudioPrev': 173,
        'XF86AudioLowerVolume': 174,
        'XF86AudioRecord': 175,
        'XF86AudioRaiseVolume': 176,
        'XF86Phone': 177,
        'XF86WWW': 178,
        'F13': 179,
        'XF86HOMEPage': 180,
        'XF86Reload': 181,
        'XF86Close': 182,
        'XF86ScrollUP': 185,
        'XF86ScrollDOWN': 186,
        'parenleft': 187,
        'parenright': 188,
        'XF86New': 189,
        'Redo': 190,
        'F13': 191,
        'F14': 192,
        'F15': 193,
        'XF86Launch7': 194,
        'XF86Launch8': 195,
        'XF86Launch9': 196,
        'XF86AudioMicMute': 198,
        'XF86TouchpadToggle': 199,
        'XF86TouchpadOn': 200,
        'XF86TouchpadOff': 201,
        'Mode_switch': 203,
        'XF86Eject': 204,
        'XF86LaunchC': 205,
        'XF86AudioPlay': 208,
        'XF86AudioPAUS': 209,
        'XF86Launch3': 210,
        'XF86Launch4': 211,
        'XF86LaunchE': 212,
        'XF86Suspend': 213,
        'XF86Close': 214,
        'XF86AudioPlay': 215,
        'XF86AudioForward': 216,
        'XF86WebCam': 220,
        'XF86Standby': 223,
        'XF86Messenger': 224,
        'XF86Search': 225,
        'XF86Go': 226,
        'XF86Finance': 227,
        'XF86Game': 228,
        'XF86Search': 229,
        'XF86Favorites': 230,
        'XF86Refresh': 231,
        'XF86Stop': 232,
        'XF86Forward': 233,
        'XF86Back': 234,
        'XF86MyComputer': 235,
        'XF86Mail': 236,
        'XF86AudioMedia': 237,
        'XF86KbdBrightnessUP': 238,
        'XF86Send': 239,
        'XF86Reply': 240,
        'XF86LaunchB': 241,
        'XF86Save': 242,
        'XF86Documents': 243,
        'XF86Battery': 244,
        'XF86Launch0': 245,
        'XF86WLAN': 246,
        'HELP': 118,
    }

    def __init__(self):
        """ init required classes """
        # keycode -> (row,col), key, tested
        self.layout = {}

    def load_gmap(self, fname):
        """ load keyboard layout from fname map file and parse it (create layout dictionary) """
        gmap = []
        if fname:
            with open(fname) as f:
                for line in f:
                    gmap.append(line.rstrip(os.linesep))
        return gmap

    def parse_gmap(self, gmap):
        errs = []
        # parse map
        for row,line in enumerate(gmap):
            if not line: continue
            errs += self._parse_line(line, row)
        return errs

    def _parse_line(self, line, row):
        """ extract all keys from single line of map layout """
        errs = []
        for m in re.finditer(r'\[(\s+(\S+)\s+)\]', line):
            label,key,col = m.group(1),m.group(2),m.start(1)
            err = self._add_key(key, row, col, label)
            if err: errs.append(err)
        return errs

    def _add_key(self, key, row, col, label, tested=False):
        """ add single key to layout dictionary """
        # find keycode for key
        keycode = self.key_to_keycode(key)
        if not keycode:
            # if not found retrtns error message
            return "missing keycode for key [ %s ]" % key
        # if found add to layout
        self.layout[keycode] = { 'row': row, 'col': col, 'key': key, 'label': label, 'tested': tested }

    def key_to_keycode(self, key):
        """ reverse xmodmap mapping lookup symbolic_key -> keycode """
        return self.rev_xmodmap.get(key)

    def keycode_to_key(self, keycode):
        """ keycode entry from layout dictionary """
        return self.layout.get(keycode)


class Test:
    """ test the keyboard key by key """

    def __init__(self):
        """ init required classes """
        # keycode -> (row,col), key, tested
        self.layout = Layout()
        self.xinput = Xinput()
        self.gui = Gui(self.xinput.version())

    def find_1st(self, path='.', mask='.lay'):
        """ find the 1st file matching mask in directory path """
        for f in os.listdir(path):
            if f.endswith(mask):
                return f

    def gmap_filename(self, gmapfname=None):
        """ returns either specific gmap filename or the first from local dir """
        # specified fname or the 1st in local dir
        if gmapfname and len(gmapfname) and os.path.isfile(gmapfname):
            return gmapfname
        return self.find_1st()

    def load_gmap(self, gmapfname):
        """ load specified graphic map file """
        self.gui.banner(" = Loading keyboard layout file: %s = " % gmapfname)
        # load graphical layout from file
        gmap = self.layout.load_gmap(gmapfname)
        # set to gui
        self.gui.set_map(gmap)
        # parse
        err = self.layout.parse_gmap(gmap)
        # store only count of missing keys
        self.key_missing = len(err)
        # show errors if any and wait for user confirmation
        self.show_err(err)

    def show_err(self, err):
        """ optional pause only if we have missing keycodes so the user can see errors """
        if len(err) == 0: return
        for e in err:
            self.gui.banner(" ERR: %s " % e, bg='red', above=0, bellow=0)
        print("This is caused either by:")
        print("\t - problems in layout file: %s (incorrect [ key_labels ] etc )" % self.gmapfname)
        print("\t - missing dictionary entries in rev_xmodmap = {...} ( Layout class )")
        _ = input('Press ENTER to continue ...')

    def kut_id(self, id=None):
        """ returns either specific keyboard unde test id or guide user with autodetection """
        try:
            int(id)
        except TypeError as e:
            id = self.autodetect_id()
        return id

    def autodetect_id(self):
        """ checking changes in xinput list when connecting unknown kbd reveals its id """
        self.gui.banner(" = Autodetection process started ... = ")
        print("Connect or Reconnect keyboard you want to test ", end=' ')
        ref = self.xinput.list()
        while True:
            act = self.xinput.list()
            # no change - loop again
            if len(act) == len(ref):
                self.gui.write_flush('.')
                time.sleep(1)
                continue
            # something disconnected - take new reference nad loop again
            if len(act) < len(ref):
                removed = list(set(ref) - set(act))
                removed_str = list(map(lambda x: x.decode(), removed))
                print("Device disconnected:", ' / '.join(removed_str))
                ref = act
                continue
            # something connected - find out id
            if len(act) > len(ref):
                added = list(set(act) - set(ref))
                added_str = list(map(lambda x: x.decode(), added))
                print("Device connected   :", ' / '.join(added_str))
                break
        # extract minimal id = first of sorted list
        # Mitsumi Electric Apple Extended USB Keyboard      id=8    [slave  keyboard (3)]
        id = sorted([int(part.replace('id='.encode(), ''.encode())) for item in added for part in item.split() if part.startswith('id='.encode())])[0]
        self.gui.banner(" = Autodetection done = detected xinput id:%d [ %s ] = " % (id, self.xinput.name_by_id(id)))
        time.sleep(1)
        return id

    def pars_setup(self, gmapfname, id):
        """ load gmap layout, open xinput dev.id """
        # gmap file either specific or first in dir
        self.gmapfname = self.gmap_filename(gmapfname)
        # device id either specific or auto detected by user actions
        self.id = self.kut_id(id)
        # dev name
        self.devname = self.xinput.name_by_id(self.id)

    def test_setup(self):
        """ process prerequisites - load layout file, start xinput process """
        # load gmap file and show errors if any
        self.load_gmap(self.gmapfname)
        # terminal
        self.terminal_setup()
        # start xinput subprocess
        err = self.xinput.start(self.id)
        # draw gui layout map and stats
        self.gui.show_map()
        self.update_stats()

    def terminal_setup(self):
        """ setup terminal """
        # termios - no echo
        self.stdinfd = sys.stdin.fileno()
        self.saveattr = termios.tcgetattr(self.stdinfd)
        noecho = self.saveattr[:]
        noecho[3] = noecho[3] & ~termios.ECHO
        termios.tcsetattr(self.stdinfd, termios.TCSADRAIN, noecho)
        # switch off cursor
        self.gui.cursor_off()

    def test_run(self):
        """ main test loop"""
        # ignore the 1st RETURN key
        self.ignore_1st(ignorekey='RET')
        # setup quit phrase
        self.quit(phrase='quit')
        # loop until all is tested
        while not self.all_tested() and self.xinput.is_running():
            # key event from xinput
            action,keycode = self.keypress()
            # get keydict struct from layout with coordinates, label, etc
            keydict = self.layout.keycode_to_key(keycode)
            # ignore unknown keys
            if not keydict: continue
            # ignore 1st keycode
            if self.ignore_1st(keycode=keycode): continue
            # gui visual feedback
            self.gui.key_action(keydict, action)
            # register key as tested
            self.key_tested(action, keydict)
            # footer stats
            self.update_stats()
            # detect quit phrase
            if self.quit(key=keydict['key']): break
        #
        self.test_teardown()

    def ignore_1st(self, ignorekey=None, keycode=None):
        """ setup and evaluate ignoring the first key (usually ENTER) """
        # has keycode = evaluate mode
        if keycode:
            # do not ignore if no ignore keycode is stored
            if not self.ikeycode: return False
            # ignore only ignore keycode
            if keycode == self.ikeycode: return True
            # other than ignore keycode disable ignoring
            self.ikeycode = None
            return False
        # setup mode - store ignore keycode
        self.ikeycode = self.layout.key_to_keycode(ignorekey)

    def quit(self, key=None, phrase=None):
        """ setup and detect phrase sequence """
        # setup quit phrase
        if phrase:
            self.phrase = phrase
            self.lastkeys = [chr(31)] * len(phrase)
            return
        # detect
        # ignore duplicate keys
        if key == self.lastkeys[len(self.lastkeys)-1]: return False
        self.lastkeys.append(key)
        self.lastkeys.pop(0)
        self.gui.write_at(20,0)
        return ''.join(self.lastkeys) == self.phrase

    def test_teardown(self):
        # end xinput subprocess
        self.xinput.stop()
        # terminal back to normal
        self.terminal_reset()

    def terminal_reset(self):
        """ reset terminal back to normal """
        # saved attributes back
        termios.tcsetattr(self.stdinfd, termios.TCSADRAIN, self.saveattr)
        # activate cursor back on
        self.gui.cursor_on()
        # clear the xinput junk from stdin
        termios.tcflush(self.stdinfd, termios.TCIFLUSH)

    def key_tested(self, action, keydict):
        """ mark key as tested """
        if action == 'release': keydict['tested'] = True

    def update_stats(self):
        """ update footer stats """
        tested = len([ k for k,v in list(self.layout.layout.items()) if v['tested'] ])
        total  = len(self.layout.layout) + self.key_missing
        stats = {
            'total': total,
            'tested': tested,
            'togo': total - tested - self.key_missing,
            'missing': self.key_missing,
            'id': self.id,
            'devname': self.devname,
            'layout': self.gmapfname
        }
        self.gui.update_stats(stats)

    def all_tested(self):
        """ are we doone = all keys has been tested """
        return all([ v['tested'] for k,v in list(self.layout.layout.items()) ])

    def keypress(self):
        """ xinput key event press/release and keycode"""
        # wait for key
        line = self.xinput.readline()
        # key press 128
        m = re.search('key (press|release)\s+(\d+)', line.decode())
        # this should not happen: return if not key press|release
        if not m: return '',0
        action  = m.group(1)
        keycode = m.group(2)
        # return action (press/release0 and int keycode
        return action,int(keycode)

    def report(self):
        """ mini report - right now only timestamp """
        now = datetime.datetime.now()
        tested = len([k for k, v in list(self.layout.layout.items()) if v['tested']])
        total = len(self.layout.layout) + self.key_missing
        untested = total - tested
        if self.all_tested():
            if untested == 0:
                self.gui.banner(" = TEST PASSED = All %d keys has been successfully tested @ %s = " % (tested, now), \
                                bg='green', above=2, bellow=1)
            else:
                self.gui.banner(" = TEST WARNING = Only %d of %d [ %.1f%% ] keys has been successfully tested @ %s = " \
                                % (tested, total, 100.0*tested/total, now), bg='yellow', above=2, bellow=1)
        else:
            self.gui.banner(" = TEST FAILED = Only %d of %d [ %.1f%% ] keys has been successfully tested @ %s = " \
                        % (tested, total, 100.0*tested/total, now), bg='red', above=2, bellow=1)


def parse_argv(argv):
    """ process parameters in arbitrary order """
    id, layout = None, None
    for par in argv:
        if par in ['-h', '--help']:
            print("=",__about__,"version",__version__,"=",__copyright__,"=")
            print(__usage__)
            sys.exit()
        if par.isdigit():
            id = int(par)
        else:
            layout = par
    return id, layout


if __name__ == '__main__':

    tst = Test()
    #
    id, layout = parse_argv(sys.argv[1:])
    tst.pars_setup(layout, id)
    #
    tst.test_setup()
    tst.test_run()
    tst.test_teardown()
    #
    tst.report()

