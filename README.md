# What is kbd-tst
kbd-tst.py is a simple keyboard test program. It tests functionality of all keys providing graphical (well, only ASCII
semigraphics in text terminal) feedback to the user like already tested keys are green, currently pressed keys are 
red and untested keys are white. 
 
### Objective
Simple and user friendly keyboard test without external dependencies using only standard system utilities ...

There is a way to test keyboard without any such utility like this one just by using text editor for example. In this case
you have to remember which keys have been tested and do not miss any untested ones. And everything is easier with visual 
feedback displayed live on screen with kbd-test.

[[https://github.com/blue-sky-r/keyboard-test/blob/master/screenshots/1-2-3-4.gif]]

### Typical usage scenarios
Here are few typical ones:
- buying new keyboard
- cleaning/repairing/modding existing keyboard
- non standard keyboard connections like protocol/level converters, drivers, ...

### Dependencies
Despite minimalistic implementation there are following requirements:
- python 2.x
- xinput

_Note: Due to xinput dependency the kbd-tst can run only on linux-like sytems with Xorg_

### Internals
Entire kbd-tst implementation is 'xinput test' centered. Xinput is executed as a subprocess and output events are
parsed and visualised as on screen keyboard layout with additional infos and statistics. Visual part is implemented
using ANSI escape sequences to control text terminal cursor postion and color. The keyboard layout is provided from
external ASCII layout (*.lay) files like 'apple.lay' or 'at101.lay'.  

## Usage
For kbd-tst to work we have to somehow specify following:
- which device to test by providing xinput device id (see bellow for details)
- physical layout of all keys on this device id for visual and user friendly feedback (ASCII layout file)

To display usage help we can provide standard '-h' or '--help' parametr

    = Keyboard Test Program version 2017.7.28 = (c) 2017 by Robert P =

    Usage: kbd-tst.py [id] [layout] [-h|--help]
           kbd-tst.py [-h|--help] [layout] [id]
    
        -h     ... shows this usage help and quits
        --help ... shows this usage help and quits
        id     ... optional keyboard device id as shown in 'xinput list' output (default user assisted autodetection)
        layout ... optional keyboard ASCII layout file [*.lay] (default the first file in kbd-tst dir)
    
    Notes:
        * parameters are optional
        * not providing device id will initiate a user assisted autodetection sequence requiring physical disconneting
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
        - if more than one device id is found by autodetection sequence only the first one is used, which is some cases
          might be incorrect. In this case provide the correct device id as a parameter (id can be found by trial and error
          from 'xinput list' and verified by 'xinput test id' to show 'key press xx' and 'key release xx' events)
          [ xinput double entries related bug: https://bugs.launchpad.net/ubuntu/+source/hal/+bug/277946 ]

The testing procedure simply consists of the steps:
- execute kbd-tst.py with some optional parameters (see bellow)
- pressing each untested key at least once (shown white on visual layout, pressing the key changes its color to red/green)
- repeat until all keys are tested (recognized by kbd-tst)
- check result status (single line)

### device id
Due to dymanic nature and hot-lugging support of device ids we have to find the correct device id of KUT (keyboatd under test) 
This is the most important and in some cases also the most difficult part of the testing procedure.

There is built-in user assisted autodetection modality. This requires connecting the KUT (keyboaard under test) if KUT 
is not connected yet. If KUT i already connected, reconnect is required. The autodetection section is watching system while
KUT is connected and then can identify device id automatically. However, in some cases, two devices are created by HAL,
which makes it impossible for autodetect to choose. Then the first one is selected by autodetection. If this is not correct
you have to provide device id manually as parameter:

    > kbd-tst.py 12
    
### layout file
Layout file is simple ASCII art visual representation of physical keyboard layout. Each key is represented by square brackets
with key label inside wrapped by spaces, for example: key number one is represented as [ 1 ] which visualy looks like key.
This file is loaded, parsed (parsing errors are shown if any) and then also used for visual on screen feedback. Check provided
layout files for details (apple.lay, at101.lay)

Name of required layout file to be loaded has to be specified as parameter:

    > kbd-tst.py at101.lay
    
If there is no layout file parameter privided, the first layout file in directory is taken. This is usefull if there is only
single file in the directory. 

Feel free to contribute your own specific layout files into layouts directory ...

### Files
The follwoing files:
- kbd-tst.py ... is keyboard test python executable file
- apple.lay, at101.lay ... are layout files used by kbd-tst
- rev_xmodmap.sh ... is shell script to build reverse xmodmap dictionary (in case of future maintenance and improvements)

Hope it helps ...

#### History
 version 2017.07.27 - the initial GitHub release in 2017

**keywords**: keyboard, test, kbdtst, layout, kbd-tst, python, xinput, xmodmap
