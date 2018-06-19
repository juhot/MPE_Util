# -*- coding: utf-8 -*-

# Copyright (c) 2016 Juho Hella

# Contains info concerning nameable itemType's name. E.G. format of the name and renaming callback functionality.

# To add a callback to be called when item is named with a postfix, one can add a new dict to itemType's
# 'postfixCallableFunctions' -dict, with key matching the callback funtion's name. List of strs 'postfixes' and
# 'regexBase' -str is required. 'regexBase' must contain grouping for item_name, and a placeholder #POSTFIX# to be
# replaced with the strs from 'postfixes' -list. Args may be added as groups. Callback will be called as object's method
# with regex.search result match as an argument.

_itemTypeNamingInfos = {
    'Track.AudioTrack': {
    },
    'Track.MidiTrack': {
        'postfixCallableFunctions': {
            'create_mpe_input_tracks': {
                'postfixes': [
                    "-creatempe",
                    "-mpe"
                ],
                'regexBase': r'(?P<item_name>.*?)(?P<command>#POSTFIX#)(?P<num_arg>-?\s?\d*)$',
                'callback': "_create_mpe_input_tracks_caller"
            }
        }
    }
}