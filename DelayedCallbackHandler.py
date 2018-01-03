# -*- coding: utf-8 -*-
# Copyright (c) 2016 Juho Hella

""" Instance of DelayedCallbackHandler takes care of scheduling and calling of functions/methods which need to be
  delayed, e.g. when reacting to LOM-objects property change by changing LOM-objects property.

  DelayedCallbackHandler can add callbacks to queue optionally rewriting existing callback with the same key and/or
  delaying the calling of the callback for more than one cycle.
"""

from UtilContainer import log_message

class DelayedCallbackHandler():
    def __init__(self):
        self._delayedCallbacks = {}

    def add_delayed_callback(self, key, callback, params, keywordParams={}, rewriteExisting=True, delayCycles=1):
        """ Adds a delayed callback to the queue. Key identifies the callback, params and keywordParams are passed to
          the callback on calling. If rewriteExisting is true, an existing callback with the key will be overwritten,
          otherwise the new callback won't be added. delayCycles determines for how many cycles the calling will be
          delayed.
        """
        if rewriteExisting or key not in self._delayedCallbacks:
            self._delayedCallbacks[key] = {'func': callback, 'params': params, 'keywordParams': keywordParams,
                                           'delayCycles': delayCycles}
        else:
            log_message("Not adding cb to queue, rewriteExisting=False and key:",key,"exists already!")
            
        
    def get_delayed_callback_exists(self, key):
        """ Returns True if a callback with the key exists, False otherwise. """
        return key in self._delayedCallbacks

    def run_cycles_delayed_callbacks(self):
        """ Runs the delayed callbacks. Should only be called once per cycle (at parse). """
        finishedCallbacks = []
        for x in self._delayedCallbacks.keys():
            delayedCallbackInfo = self._delayedCallbacks[x]
            delayedCallbackInfo['delayCycles'] -= 1
            if delayedCallbackInfo['delayCycles'] < 1:
                if self._delayedCallbacks[x]['func'](*delayedCallbackInfo['params'], **delayedCallbackInfo['keywordParams']):
                    finishedCallbacks.append(x)
        for x in finishedCallbacks:
            del self._delayedCallbacks[x]
