# -*- coding: utf-8 -*-

# Copyright (c) 2017 Juho Hella

""" Contains the configuration for the script."""

import os

import ItemTypeNamingInfos
from ..UtilContainer import log_error


itemTypeNamingInfos = ItemTypeNamingInfos._itemTypeNamingInfos
utilizeGhostInputTrack = True
defaultMPEControllerNamePrefix = "Seaboard"
defaultMpeChannelCount = 11

_strToBoolDict = {
    "1": True,
    "True": True,
    "true": True,
    "TRUE": True,
    "Yes": True,
    "YES": True,
    "yes": True,
    
    "0": False,
    "False": False,
    "false": False,
    "FALSE": False,
    "No": False,
    "NO": False,
    "no": False
}

def _parseBool(strValue):
    try:
        return _strToBoolDict[strValue]
    except KeyError:
        log_error("ERROR While reading config, unable to parse bool from str: '"+strValue+"', returning False")
        return False

def _parseInt(strValue, min=1, max=16):
    theValue = None
    try:
        theValue = int(strValue)
        if theValue < min or theValue > max:
            theValue = None
    except ValueError as e:
        #log_message("Exception when parsing int, got strvalue:",strValue,"Exception:",e.__class__,e.errstr)
        pass

    return theValue

def _parseStr(strValue):
    if strValue.startswith('"') and strValue.endswith('"'):
        return strValue[1:-1]
    else:
        return None

def _parseStrList(strValue):
    theValue = []
    for tempPart in strValue.split(","):
        theValue.append(_parseStr(tempPart.strip()))
        if theValue[-1] is None:
            return None
    return theValue

confPath = os.path.dirname(os.path.abspath(__file__))+"/../conf.txt"
try:
    with open(confPath) as confTxtFile:
        confLines = confTxtFile.readlines()

    for tempLine in confLines:
        tempLine = tempLine.strip()
        if len(tempLine) > 0 and not tempLine.startswith("#"):
            tempLineSplitted = tempLine.split(":")
            if len(tempLineSplitted) == 2:
                tempArgName = tempLineSplitted[0].strip()
                tempArgValue = tempLineSplitted[1].strip()
                # log_message("Found line: '" + tempLine + "'")
                if tempArgName == "utilizeGhostInputTrack":
                    utilizeGhostInputTrack = _parseBool(tempArgValue)
                    # log_message("Found utilizeGhostInputTrack from conf.txt, setting:", utilizeGhostInputTrack)
                elif tempArgName == "defaultMPEControllerNamePrefix":
                    tempArgValue = _parseStr(tempArgValue)
                    if tempArgValue is not None:
                        defaultMPEControllerNamePrefix = tempArgValue
                        # log_message("Found defaultMPEControllerNamePrefix from conf.txt, setting:",
                        #             defaultMPEControllerNamePrefix)
                elif tempArgName == "defaultMpeChannelCount":
                    tempArgValue = _parseInt(tempArgValue, min=1, max=16)
                    if tempArgValue is not None:
                        defaultMpeChannelCount = tempArgValue
                        # log_message("Found defaultMpeChannelCount from conf.txt, setting:", defaultMpeChannelCount)
                elif tempArgName == "createMPEPostfixes":
                    tempPostfixList = _parseStrList(tempArgValue)
                    if tempPostfixList is not None:
                        # log_message("Found createMPEPostfixes from conf.txt, setting:", utilizeGhostInputTrack)
                        itemTypeNamingInfos['Track.MidiTrack']['postfixesForFunctions']['create_mpe_input_tracks']\
                            = tempPostfixList

except IOError as e:
    pass

