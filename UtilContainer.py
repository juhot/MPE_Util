# -*- coding: utf-8 -*-

# Copyright (c) 2017 Juho Hella

""" This module contains utility functions, such as logging. """

import logging

_infoLogger = logging.getLogger("AAOsc").info
_warningLogger = logging.getLogger("AAOsc").warning
_errorLogger = logging.getLogger("AAOsc").error


def log_message(*a, **kwargs):
    """ Prints the passed objects to Live's log file as warning. """
    _warningLogger(format_to_str(*a, **kwargs))
    
def log_error(*a, **kwargs):
    """ Prints the passed objects to Live's log file as error. """
    _errorLogger(format_to_str(*a, **kwargs))


def format_to_str(*a, **kwargs):
    """ Formats gotten objects to str. """
    result = ""
    if kwargs == {}:
        kwargs = {'keepNewlines': True}
    for x in range(0, len(a)):
        tempItem = a[x]
        if type(tempItem) is str:
            result += tempItem
        elif type(tempItem) in [list, dict, tuple]:
            result += str(tempItem)  # pformat(tempItem)
        elif hasattr(tempItem, "itemType"):
            result += "<" + tempItem.itemType + ":" + tempItem.itemModelPointer + ">"
        else:
            result += str(tempItem)

        if x < len(a) - 1:
            result += " "

        if not kwargs['keepNewlines']:
            result = result.replace("\n", "*nl*")

    return result


def getDictString(dictToPrint, lineToPrint="", currentIntendation=0):
    """ Creates a readable str from dict. """
    if type(dictToPrint) is dict:
        for tempKey in sorted(dictToPrint.keys()):
            tempObj = dictToPrint[tempKey]
            # lineToPrint = ""
            indentationStr= ""
            for x in range(0, currentIntendation):
                indentationStr+= " "

            lineToPrint += intendationStr
            if type(tempObj) == dict:
                lineToPrint += str(tempKey) + ":"
                if len(tempObj.keys()) == 1 and type(tempObj[tempObj.keys()[0]]) is str:
                    lineToPrint += getDictString(tempObj, currentIntendation=currentIntendation + 2)
                else:
                    # if tempObj == {}:
                    #    lineToPrint += "{}"
                    lineToPrint += "{\n"
                    lineToPrint += getDictString(tempObj,
                                                 currentIntendation=currentIntendation + 2) + indentationStr+ "}\n"
            else:
                objStr = str(tempObj).lstrip()
                objStr = objStr.replace('\n', ' ').replace('\r', ' ')

                lineToPrint += str(tempKey).lstrip() + ": " + objStr + "\n"
    else:
        listToPrint = sorted(dictToPrint)
        for x in range(0, len(listToPrint)):
            tempObj = listToPrint[x]
            # lineToPrint = ""
            indentationStr= ""
            for x in range(0, currentIntendation):
                indentationStr+= " "

            lineToPrint += indentationStr+ str(x) + ": [" + intendationStr
            if type(tempObj) == dict:
                if len(tempObj.keys()) == 1 and type(tempObj[tempObj.keys()[0]]) is str:
                    lineToPrint += getDictString(tempObj, currentIntendation=currentIntendation + 2)
                else:
                    # if tempObj == {}:
                    #    lineToPrint += "{}"
                    lineToPrint += "{\n"
                    lineToPrint += getDictString(tempObj,
                                                 currentIntendation=currentIntendation + 2) + indentationStr+ "}]\n"
            else:
                objStr = str(tempObj).lstrip()
                objStr = objStr.replace('\n', ' ').replace('\r', ' ')

                lineToPrint += objStr + "]\n"
    return lineToPrint
