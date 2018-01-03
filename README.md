# MPE_Util
MIDI Remote Script for Ableton's Live 9/10, adding MPE-utilities

MPE stands for MIDI Polyphonic Expression, https://www.midi.org/articles/midi-polyphonic-expression-mpe

Ableton Live doesn't support MPE, as all the incoming MIDI on a MIDI track goes to channel 1. However, one can create
"MPE sub tracks", individual MIDI tracks for receiving each of the MIDI channels from a MPE-source, and route their
output to an instrument on another MIDI track, the "MPE Master track". This requires a lot of manual operations, such as
setting of MIDI From and MIDI To parameters.. The MPE_Util MIDI Remote Script automates the creation and configuring of
the MPE sub tracks. It updates the MPE sub tracks properties when the MPE Master track is modified as well. Currently
arm, instrument, name, color and clip firing changes are handled. Unfortunately the updates get applied with a tinyish
(usually less than 100ms), varying delay.

Use the script at your own risk, it may brake your Live set or even installation! Try it first on a new set, and backup
your project when loading it while the script is active (selected as a Control Surface)!

##Installation:
While Live is not running, clone or download and extract zip from github: https://github.com/juhot/MPE_Util to Live's
MIDI Remote Scripts folder:
Win: Live Install Dir\Resources\MIDI Remote Scripts\
OSX: /Applications/Ableton Live *.app/Contents/App-Resources/MIDI Remote Scripts/

So that you'll find folder MPE_Util from the aforementioned MIDI Remote Scripts directory. MPE_Util should contain two
folders and some files, e.g. __init__.py and MPE_Util.py.

Start Live, go to settings, and on Link MIDI tab select MPE_Util as a Control Surface on a free slot. You should see a
message at the bottom of the screen saying "MPE Util loaded!".

##Configuration:
You may configure default values for your MPE-Controllers MIDI port's name, the number of MIDI channels to use, and
whether a GhostInputTrack will be created. The default settings may be changed by modifying file (instructions are in
file):
MPE_Util/conf/config.txt

You may alter the list of keyphrases which activate the creation of the MPE-midi tracks from the conf as well.

Note: you will have to create a new or load an existing Live set for the changes to take effect!


##Using:
When you want to create input tracks for individual MIDI channels, rename a track with an instrument by adding
"-createMPE" to the end of the track's name. MPE sub tracks should appear after a moment, and immeadately switch their
names, colors and arm-states to match the instrument track.

You may group the input tracks, but do not include the instrument track in the group. Group track's name and color
will follow the instrument track as well.

Input tracks will automatically update their "MIDI To" target whenever the instrument on the instrument track is changed.

If you would like to change the "MIDI From" on the subtracks, select the new input source on the first input chanells
track, the rest will follow.


##Developement:
I have a lot of stuff on my TODO list at the moment, but found bugs may be fixed more or less quickly. I'm planning to
include new features as well, but probably after the release of Live 10.