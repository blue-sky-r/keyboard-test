# What is kbd-tst (keyboard-test)
kbd-tst.py is a simple keyboard test program. It tests functionality of all keys providing graphical (well, only ASCII
semigraphics in text terminal) feedback to the user like:
- already tested keys are green
- currently pressed keys are red
- untested keys are white (see animated gif bellow). 
 
### Objective
Simple and user friendly keyboard test without external dependencies ()using only standard system utilities) ...

There is a way to test keyboard without any such utility like this one just by using text editor for example. In this case
you have to remember which keys have been tested and do not miss any untested ones. And everything is easier with visual 
feedback displayed live on the screen with kbd-test.

![1-2-3-4 keys tested](https://github.com/blue-sky-r/keyboard-test/blob/master/screenshots/1-2-3-4.gif)

### Typical usage scenarios
Here are few typical ones:
- buying new keyboard
- cleaning/repairing/modding existing keyboard
- non standard keyboard connections like protocol converters, level shifters, drivers, ...

### Dependencies
Despite minimalistic implementation there are following requirements:
- python 2.x
- xinput

_Note: Due to xinput dependency the kbd-tst can run only on linux-like systems with Xorg_

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
- check result status (single line report)

### xinput id
Due to dymanic nature and hot-plugging support of xinput ids we have to find the correct device id of KUT (keyboatd under test) 
This is the most important and in some cases also the most difficult part of the testing procedure.

Fortunatelly there is built-in user assisted autodetection modality. This requires connecting the KUT (keyboaard under test) if KUT 
is not connected yet. If KUT is already connected, reconnect is required. The autodetection function is watching system while
KUT is connected and then it can identify xinput id automatically. However, in some cases, two devices are created by HAL,
which makes it impossible for autodetect to choose. Then the first one is selected by autodetection. If this is not the correct
one you have to provide xinput id manually as a command line parameter:

    > kbd-tst.py 12
    
### layout file
Layout file is simple ASCII art visual representation of physical keyboard layout. Each key is represented by square brackets
with key label inside wrapped by spaces, for example: a key with the number one is represented as [ 1 ] which visualy looks like a key.
This file is loaded, parsed (parsing errors are shown if any) and then also used for visual on screen feedback. Check provided
layout files for details (apple.lay, at101.lay)

Name of required layout file to be loaded has to be specified as parameter:

    > kbd-tst.py at101.lay
    
If there is no layout file parameter provided, the first layout file in the directory is taken. This is usefull if there is only
single file in the directory. 

The button legend in layout file has to be translatable by rev_xmodmap dictionary in Layout class. This allows to use shorter
button labels to rpoperly design ASCII keyboard layout. If button label from layout file has no entry in rev_xmodmap dictionary
the error message is show. The test will continue, but there will be no way to test all keys. Therefore such execution will
end with (yellow/orange) warning (see screenshots bellow with warnings on layout load and test report).

Feel free to contribute your own specific layout files into layouts directory ...

![xinput id autodetection and missing keycode in rev_xmodmap](https://github.com/blue-sky-r/keyboard-test/blob/master/screenshots/autodetection-layour_err.png)

### report
At the end of test the single line report with summary is generated:
- test passed (green) ... all keys have been successfully tested
- test warning (yellow/orange) ... all testable keys have been tested but we have some missing keycodes 
- test failed ... not all keys has been tested (premature exit from test by typing quit, CTRL-C, etc ...)

![apple test ended with warning](https://github.com/blue-sky-r/keyboard-test/blob/master/screenshots/apple-warning.png)

### Files
The follwoing files:
- kbd-tst.py ... main keyboard test python executable file
- at101.lay ... standard default AT 101 keyboard layout file
- layouts/*.lay ... are optional layout files for kbd-tst
- rev_xmodmap.sh ... is shell script to build reverse xmodmap dictionary (in case of future maintenance and improvements)
- screenshots/1-2-3-4.gif ... animated gif of testing four keys 1-2-3-4
- screenshots/1-2-3-4.mp4 ... screencats of testing four keys 1-2-3-4
- screenshots/apple-warning.mp4 ... screencats of testing apple mitsumi keyboard ended with warning (4 keycodes are missing)
- screenshots/apple-warning.png ... screenshot of the result from abote 
- screenshots/autodetection-layout_err.png ... screenshot of the result of xinput autodetection and four errors from layout file loader

Hope it helps ...

#### History
 version 2017.07.27 - the initial GitHub release in 2017

**keywords**: keyboard, test, kbdtst, layout, kbd-tst, python, xinput, xmodmap
