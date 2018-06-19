# MPE_Util
MIDI Remote Script ("Control Surface") for Ableton Live 9/10, adding MPE-utilities such as:
* Automated creation and setup of channel tracks for MPE MIDI input device
* MPE channel track properties (e.g. arm and firing of clips) follow input of their instrument track

[Get it for free](https://github.com/juhot/MPE_Util/releases/latest)



###### Quick demonstration on youtube:
[![MPE Util demo video](https://img.youtube.com/vi/Hg0kUVCfxo0/0.jpg)](https://youtu.be/Hg0kUVCfxo0)

MPE stands for MIDI Polyphonic Expression, https://www.midi.org/articles/midi-polyphonic-expression-mpe

Ableton Live doesn't support MPE well, as all the incoming MIDI on a MIDI track goes to channel 1. However, one can
create "MPE sub tracks", individual MIDI tracks for receiving each of the MIDI channels from a MPE-source, and route
their output to an instrument on another MIDI track, the "MPE Master track". This requires a lot of manual
operations, such as setting of MIDI From and MIDI To parameters.. The MPE_Util MIDI Remote Script automates the
creation and configuring of the MPE sub tracks and it updates MPE sub tracks properties when the MPE Master track is
modified. Currently changes in MPE Master tracks arm, instrument, name, color and clip firing are handled.
Unfortunately the updates get applied with a tinyish (usually less than 100ms), varying delay (launch quantization
recommended).

By default, all MPE Master tracks utilize a GhostMidiInputTrack as MIDI Input. The GhostMidiInputTrack is a gray
MIDI track with no input and no output. It enables Arm button and 'ghost' clips on MPE Master track, while not
interfering the MPE input.

__Use the script at your own risk__, it may break your Live set or even installation! Try it first on a new set,
and backup your project before loading it while the script is active (selected as a Control Surface)! However, no
one has reported any issues so far.

The script should work on Live 10 and Live 9 (from 9.7, could work on older versions as well, but it
would require some work. I won't try unless at least some people are interested).

###### Supported Live versions:
* Live 9 (9.7->)
* Live 10

###### Supported MPE controllers:
All the MPE controllers should be supported, but here's a list of devices which have been tested:
* Roli Seaboard RISE
* Roli Lightpad Block

## Installation:
Ableton's instructions for using and installing 3rd party Control Surfaces:
https://help.ableton.com/hc/en-us/articles/209072009-How-to-install-a-third-party-Remote-Script

Download the latest [release](https://github.com/juhot/MPE_Util/releases/latest), or clone git or download zip from
github: (https://github.com/juhot/MPE_Util) and get the MPE_Util -dir to Live's MIDI Remote Scripts dir (if your folder
is named with github stuff, e.g. "MPE_Util-master", rename it to "MPE_Util"). Afterwards, script's dir should
look like as in the linked picture:
* [Win: [Live Install Dir]\Resources\MIDI Remote Scripts\MPE_Util](/img/win_dir.png)
* [OSX: /Applications/Ableton Live *.app/Contents/App-Resources/MIDI Remote Scripts/MPE_Util](/img/osx_dir.png)


Start Live, go to settings, and on Link MIDI tab select MPE_Util as a Control Surface on a free slot. You should see a
message at the bottom of the screen saying "MPE Util loaded!".

## Configuration:
You may configure default values for your MPE-Controllers MIDI port names, the number of MIDI channels to use, and
whether a GhostInputTrack will be created. The default settings may be changed by modifying file (instructions are in
the file):
MPE_Util/conf/config.txt

You may alter the list of keyphrases which activate the creation of the MPE-midi tracks from the conf as well.
Note: you will have to create a new or load an existing Live set for the changes to take effect!


## Usage:
As the automatic firing of clips on subtracks isn't perfectly synced, global launch quantization value other than None
is recommended.

When you want to create input tracks for individual MIDI channels, rename a track with an instrument by adding
"-createMPE" to the end of the track's name. MPE sub tracks should appear after a moment, and immeadately switch their
names, colors and arm-states to match the instrument track. You may define the number of MPE Subtracks to be created by
adding the number to the end of the postfix, e.g. "-createMPE8", otherwise the default value from MPE_Util/conf.txt is
used.

You may group the input tracks, but do not include the instrument track in the group. Group track's name and color
will follow the instrument track as well.

Input tracks will automatically update their "MIDI To" target whenever the instrument on the instrument track is
changed.

If you would like to change the "MIDI From" on the subtracks, select the new input source on the first input chanells
track, the rest will follow. If the "MIDI To" on the subtracks is pointing in wrong destination, e.g. MPE Master tracks
"Track In", change the "MIDI To" on the first MPE sub track to any other value. MPE Util will then try to fix the
routing on all MPE sub tracks.

## How it works:
MPE Util works as a Control Surface in Live. It is a python script which listens for changes, and extends functionality
in some objects in Live set. e.g. if track's name changes to end with a certain phrase, a method extending the track's
model is called, or if a track extended to be a MPE Master track is armed, a method arming its MPE sub tracks is called.
MPE Util saves some parameters of the extended items as a part of the set, and loads the information when the set is
loaded.


## Development:
I have a lot of stuff on my TODO list at the moment, but found bugs may be fixed more or less quickly. I'm planning to
include new features as well, but probably after the release of Live 10.


##### TODO (things to implement, sooner or later):
* verifying the support of other than listed MPE coontrollers
* add parameters (such as follow track colors) to conf.txt
* find out if a MIDI effect plugin could act as the midi receiver on a MPE Master track, instead of the instrument
* add support for manually adding and removing MPE Sub tracks

##### Unable to implement (lacking API functions or skill):
* controlling of clips in Arranger
* sub tracks clips looping parameters to follow master tracks clips changes
* perfectly synced operation (without quantization)
* automatic grouping of tracks
* adding controls (e.g. buttons and context menu items) to Live's GUI

## Contact:
If you encounter bugs, or would like to throw suggestions about new functionality, or altering the current, you can
email me, juhodev att gmail.com.

## Acknowledgments:
* Ableton for providing the python API (and Live:)
* Julien Bayle for his [Live API -documentation](https://julienbayle.studio/PythonLiveAPI_documentation/Live9.6.xml)
* stufisher at github for [LiveOSC2](https://github.com/stufisher/LiveOSC2), which I found a great example.
