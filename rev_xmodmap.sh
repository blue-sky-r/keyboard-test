#!/usr/bin/env bash

# create reverse xmodmap dictionary for python kbd-tst.py
#
# the output has to be copy-pasted into source code of kbd-tst.py
# just after the line rev_xmodmap between { } to replace existing content there
#
# Using this utility is only necessary for future extension of handling special or non-standard
# keyboard layouts with special keys
#
# GITHUB: https://github.com/blue-sky-r/keyboard-test
#
# (c) 2017 by Robert P

# translate descriptive values to shorter ones (more user friendly for map files)
#
TR="Escape:ESC BackSpace:BS Tab:TAB Return:RET space:SPACEBAR \
    minus:- equal:= bracketleft:\[ bracketright:\] \
    Control_L:LCTR Shift_L:LSHIFT Alt_L:LALT \
    Control_R:RCTR Shift_R:RSHIFT Alt_R:RALT \
    semicolon:; apostrophe:\' grave:\` backslash:\\\\ comma:, \
    period:. slash:\/ Multi_key:CAPS \
    Print:PSCR Scroll_Lock:SCRL Pause:PAUS Num_Lock:NUML \
    KP_Subtract:_\- KP_Add:_\+ KP_Delete:_\. KP_Divide:_\/ KP_Equal:_= KP_Multiply:_\* KP_Enter:ENT \
    KP_Home:_7 KP_Up:_8 KP_Prior:_9 KP_Left:_4 KP_Begin:_5 KP_Right:_6 KP_End:_1 KP_Down:_2 KP_Next:_3 KP_Insert:_0 \
    Home:HOME End:END Up:UP Down:DOWN Prior:PGUP Next:PGDN Left:LEFT Right:RIGHT \
    Insert:INS Delete:DEL \
    Super_L:LAPPLE Super_R:RAPPLE XF86Tools:F13 XF86Launch5:F14 XF86Launch6:F15"


# construct sed substitues
#
for fr in $TR
{
    find=$( echo "$fr" | cut -f 1 -d : )
    repl=$( echo "$fr" | cut -f 2 -d : )
    e="$e -e s/$find/$repl/"
}

# keycode  15 = 6 asciicircum 6 asciicircum
#
# awk - extract only keycode and key
# grep - filter out unwanted NoSymbol, XF86 and duplicate print (keycode 218)
# sed - substitue from above and two special subst ''' -> "'" and '\' -> '\\'
#
xmodmap -pke | awk 'NF>4 {printf "'"'""%s""'"': %s,\n",$4,$2}' \
| grep -v NoSymbol | grep -v '218' \
| sed $e -e "s/'''/\"'\"/" -e "s/'\\\'/'\\\\\\\'/"

# special apple keys
#
echo "'HELP': 118,"
