# Copyright (c) 2016-2017 Juho Hella

""" Instance of ItemModelDataHandler handles the saving and loading of any external data (the data which is created
  and maintained by the script, not saved in the Live set itself, e.g. track's property isMPETrack).

  ItemModelDataHandler stores the data in Live's song instance, with the method set_data. All the data is saved with
  one key, the rootDictkey, which may be given at init. Live 10 would seem to enable saving data to track-instances
  as well, but to support Live 9, the song's data is utilized for all the data.

  All the stored data is assigned to LOM-object models. Data is added with the method
  add_external_property_for_itemModel, which needs an LOM-object-model, attribute name, and a value (value needs to be
  serializable, though references to other LOM-object-models are handled). Each LOM-object has a dict in the
  _externalContentDicts -dict by its itemModelPointer, containing the added values by the attribute names. Each
  LOM-object has its path (a list containing all the attribute names and list indexes to get the LOM-object, e.g.
  ["song","tracks",0]) which is used to identify the new itemModelPointer when a Live set is loaded. Changes in
  LOM-objects paths (list indexes) are listened and the paths updated accordingly.

  IMP = itemModelPointer
"""

# TODO: The data should be set only once per cycle, or when there are no delayedCallbacks in queue.

from datetime import datetime

import InstanceContainer
from UtilContainer import log_message, log_error, getDictString


class ItemModelDataHandler(object):
    def __init__(self, rootDictKey="test"):
        self.log_message = log_message
        self.song = InstanceContainer.song
        self.rootDictKey = rootDictKey
        self.dataEmptyNote = "This data is completely empty, nothing here. Nada"
        self.songData = self._get_raw_song_data()
        self._pendingFoundItemModelPaths = {}
        self.loadedItemModelPointersToCurrentItemModels = {}
        #log_message("Initing ItemModelDataHandler, Data before initing:\n", self._get_raw_song_data())
        if self.songData == self.dataEmptyNote:
            self.songData = {"info": "this is data for "+self.rootDictKey, "externalContentDicts": {}, "pathsForItemModels": {}}
            self._externalContentDicts = self.songData["externalContentDicts"]
            self._pathsForItemModels = self.songData["pathsForItemModels"]
            self.song.set_data(self.rootDictKey, self.songData)

            #log_message("info: Inserted '"+self.rootDictKey+"' dict:", self.songData,"to song's data. Now:",self.song.get_data(self.rootDictKey, "Still empty wtf"))

        else:
            self._externalContentDicts = self.songData["externalContentDicts"]
            self._pathsForItemModels = self.songData["pathsForItemModels"]
            for tempItemModelPointer, tempItemModelPath in self._pathsForItemModels.iteritems():
                self._pendingFoundItemModelPaths[unicode(tempItemModelPath)] = tempItemModelPointer

        #log_message("Initing ItemModelDataHandler, Data after initing:\n", self._get_raw_song_data())

    def get_itemModels_external_data(self, itemModel):
        """ Returns the itemModels external data. """
        if not itemModel.itemModelPointer in self._pathsForItemModels:
            # A new itemModel, it hasn't got a path yet. Create path and check if it would exist in loaded data.
            self._create_itemModels_path(itemModel)
            itemModelPathStr = unicode(self._pathsForItemModels[itemModel.itemModelPointer])

            if itemModelPathStr in self._pendingFoundItemModelPaths:
                # The itemModel has loaded data. Create listeners, remove the pending old IMP, assing the old data for
                # the new IMP, add the ref from old IMP to the new one. Set the updated data to song.
                self._create_itemModels_path(itemModel, createListeners=True)
                oldItemModelPointer = self._pendingFoundItemModelPaths.pop(itemModelPathStr)
                self._externalContentDicts[itemModel.itemModelPointer] = self._externalContentDicts.pop(oldItemModelPointer)
                del self._pathsForItemModels[oldItemModelPointer]
                self.loadedItemModelPointersToCurrentItemModels[oldItemModelPointer] = itemModel
                self._set_song_data()

        # Return the itemModels data
        return self._get_itemModels_external_data(itemModel.itemModelPointer)

    def add_external_property_for_itemModel(self, itemModel, paramName, paramValue):
        """ Adds the paramValue to itemModels external data with key paramName. """

        if not itemModel.itemModelPointer in self._externalContentDicts:
            # If the itemModel isn't recognized, it is added.
            self._add_itemModel(itemModel)

        # If the paramValue can be listened for changes, add a listener function. If the paramValue is or references an
        # itemModel, serialize the object to its IMP.
        addListenerFunction = getattr(itemModel, "add_"+paramName+"_listener", None)

        if addListenerFunction is not None:
            def externalDataValueChangedListener():
                freshValue = getattr(itemModel, paramName)
                # TODO: improve the serialization!
                if hasattr(freshValue, 'itemModelPointer'):
                    freshValue = freshValue.itemModelPointer
                elif type(freshValue) is dict:
                    serializedDict = {}
                    for tempKey, tempValue in freshValue.iteritems():
                        if hasattr(tempValue, 'itemModelPointer'):
                            serializedDict[tempKey] = tempValue.itemModelPointer
                        else:
                            serializedDict[tempKey] = tempValue

                    freshValue = serializedDict

                self._update_itemModels_parameter_value(itemModel.itemModelPointer, paramName, freshValue)

            addListenerFunction(externalDataValueChangedListener)
        """
        else:
            self.log_message("[WARNING] unable to find listener adding fn by name:",
                             "add_"+paramName+"_listener, for itemModels:",
                             itemModel.itemType+"-"+itemModel.itemModelPointer,"external property named:",
                            paramName,"init value:",paramValue)
        """
        self._update_itemModels_parameter_value(itemModel.itemModelPointer, paramName, paramValue)

    def remove_item_models_external_data(self, itemModel):
        """ Removes itemModels external data. """

        #  TODO: Remove listeners.
        if itemModel.itemModelPointer in self._pathsForItemModels:
            del self._pathsForItemModels[itemModel.itemModelPointer]
        if itemModel.itemModelPointer in self._externalContentDicts:
            del self._externalContentDicts[itemModel.itemModelPointer]
        self._set_song_data()

    """
    # This method would update the externalContentDicts, and could be called at init. It is not utilized however, for the
    # itemModels currently query for the data themselves.
    def _initItemModelPointers(self, itemModelInstanceHandler):
        freshPathsForItemModels = {}
        freshItemModelContentDicts = {}
        # self.log_message("_initItemModelPointers")
        for tempItemModelPointer, tempItemModelPath in self._pathsForItemModels.iteritems():
            # self.log_message("Checking found itemPath. IMP:",tempItemModelPointer,"And path:\n",tempItemModelPath)
            currentItem = None

            for tempPathPart in tempItemModelPath:
                if tempPathPart == "/live":
                    currentItem = self.song
                elif type(tempPathPart) is str or type(tempPathPart) is unicode:
                    currentItem = getattr(currentItem, str(tempPathPart))
                elif type(tempPathPart) is int:
                    currentItem = currentItem[tempPathPart]
                else:
                    self.log_message("[ERROR], in _initItemModelPointers, got IMPs:",tempItemModelPointer,
                                     "path:",tempItemModelPath,"in which the part:",tempPathPart,
                                     "is of unhandled type:",type(tempPathPart))
                # self.log_message("iterated pathpart:",tempPathPart,"Got currentItem:",currentItem)
            freshItemModel = itemModelInstanceHandler._getItemModelByItem(currentItem)
            if freshItemModel is not None and freshItemModel is not False:
                tempImp = freshItemModel.itemModelPointer
                freshPathsForItemModels[tempImp] = tempItemModelPath
                freshItemModelContentDicts[tempImp] = self._externalContentDicts[tempItemModelPointer]
            else:
                self.log_message("[ERROR], in _initItemModelPointers, got IMPs:", tempItemModelPointer, "path:",
                                 tempItemModelPath, "found item:", currentItem, "but can't find it's itemModel!")
            # self.log_message("Found saved external data for item:", currentItem, "containing:", self._externalContentDicts[tempItemModelPointer])

        self.songData["externalContentDicts"] = freshItemModelContentDicts
        self.songData["pathsForItemModels"] = freshPathsForItemModels
        self._set_song_data()

        # for tempItemModelIdPathPart, tempItemModelIdDict in self._itemModelIdPathsz2zzzz.iteritems():
    """

    def _get_raw_song_data(self):
        return self.song.get_data(self.rootDictKey, self.dataEmptyNote)

    def _set_song_data(self):
        #TODO: optimize?
        newData = {"externalContentDicts": self._externalContentDicts, "pathsForItemModels": {}}

        for tempItemModelPointer in self._externalContentDicts:
            newData["pathsForItemModels"][tempItemModelPointer] = self._pathsForItemModels[tempItemModelPointer]

        self.song.set_data(self.rootDictKey, newData)

    def _get_itemModels_external_data(self, itemModelPointer):
        if itemModelPointer in self._externalContentDicts:
            return self._externalContentDicts[itemModelPointer]
        else:
            return None

    def _add_itemModel(self, itemModel):
        self._create_itemModels_path(itemModel, createListeners=True)

        if not itemModel.itemModelPointer in self._externalContentDicts:
            self._externalContentDicts[itemModel.itemModelPointer] = {"created_timestamp": str(datetime.now())}
        self._set_song_data()

    def _create_itemModels_path(self, itemModel, refresh=False, createListeners=False):
        if not itemModel.itemModelPointer in self._pathsForItemModels or refresh or createListeners:
            currentItemModel = itemModel
            tempParentItemModel = itemModel.parentItemModel
            tempItemModelPath = []
            while tempParentItemModel is not None:
                # TODO: Will break if itemList is in itemList..
                if currentItemModel.itemType == "Base.ItemList":
                    tempItemModelPath.insert(0, unicode(currentItemModel.itemNameOnParentItem))

                elif tempParentItemModel.itemType == "Base.ItemList":
                    tempItemModelPath.insert(0, currentItemModel.itemId)
                    if createListeners:
                        self._add_itemModels_pathpart_listener(itemModel, currentItemModel)
                    # TODO: insert changed listeners

                elif tempParentItemModel is not None:
                    tempItemModelPath.insert(0, unicode(currentItemModel.itemNameOnParentItem))


                currentItemModel = tempParentItemModel
                tempParentItemModel = currentItemModel.parentItemModel
            tempItemModelPath.insert(0, unicode(currentItemModel.itemModelPointer))
            self._pathsForItemModels[itemModel.itemModelPointer] = tempItemModelPath

    def _add_itemModels_pathpart_listener(self, itemModelWithData, itemModelToListen):
        def itemModelsPathUpdatedListener():
            self._create_itemModels_path(itemModelWithData, refresh=True)
            self._set_song_data()
        itemModelToListen.add_itemId_listener(itemModelsPathUpdatedListener)

    def _update_itemModels_parameter_value(self, itemModelPointer, paramName, value):
        self._externalContentDicts[itemModelPointer][paramName] = value
        self._set_song_data()
