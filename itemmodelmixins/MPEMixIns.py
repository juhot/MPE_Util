# -*- coding: utf-8 -*-
# Copyright (c) 2016-2018 Juho Hella

""" This module contains MPE-related mix-in classes. The mix-in class is adopted by itemModels mix_with_class function,
  which adds the mix-ins classes methods to the itemModel, then calls *_init -function.

"""
# TODO: enable using of other than default midi-sources, listener to first sub track, changes masters value which is
# TODO: inited from conf.

import Live

import types

from ..UtilContainer import log_message
from .. import conf
from .. import InstanceContainer


class MPEMasterTrackMix(object):
    """ Mix-in class for a MPE-master track. Adds listeners to the needed properties, and their callbacks which
      manipulate the subtracks. Included _add_mpe_subtrack -method is used to assign a track to be the master tracks
      subtrack.
      The listener functions generally check if the value has changed, then sets a delayed callback which iterates trough
      the subtrack-list setting the new value (or value derived from it) if needed.
    """

    def _MPEMasterTrackMix_init(self):

        #log_message("Processing _MPEMasterTrackMix_init,\n track:",self.itemModelPointer,
        #            "\nsubTracks output_routing_channel -target:"
        #            ,self._subtracks_target_output_routing_channel_name)

        self.mixedWithClasses.append("MPEMasterTrackMix")
        self._mpeSubtracks = {}
        self._mpeSubtracks_changed_listeners = []
        self._mpeArmState = self.item.arm
        self._mpeClipSlotToFireIndex = self._get_clip_slot_to_fire_index(self.item)
        self._mpeControllerInputTypeName = self._get_mpe_controller_input_type_name()
        self._subtracks_target_output_routing_channel_name = None

        def mpeMaster_playing_slot_index_changed():
            #log_message("mpeMaster_playing_slot_index_changed, now:",self.item.playing_slot_index)
            freshClipSlotToFireIndex = self._get_clip_slot_to_fire_index(self.item)
            if freshClipSlotToFireIndex != self._mpeClipSlotToFireIndex:
                self._mpe_clip_slot_to_fire_index_changed(freshClipSlotToFireIndex)

        def mpeMaster_fired_slot_index_changed():
            #log_message("mpeMaster_fired_slot_index_changed, now:",self.item.fired_slot_index)
            freshClipSlotToFireIndex = self._get_clip_slot_to_fire_index(self.item)
            if freshClipSlotToFireIndex != self._mpeClipSlotToFireIndex:
                self._mpe_clip_slot_to_fire_index_changed(freshClipSlotToFireIndex)

        def mpeMaster_arm_changed():
            if self.item.arm != self._mpeArmState:
                self._mpe_arm_changed(self.item.arm)

        def mpeMaster_name_changed():
            def delayedSubTrackNameChanger():

                for tempSubtrackModelId, tempSubtrackModel in self._mpeSubtracks.iteritems():
                    tempSubtrackModel.item.name = self.s_name+"Ch"+str(tempSubtrackModel._mpeChannelId)
                return True

            InstanceContainer.add_delayed_callback("CallbackForRenamingSubtracksFor"+self.itemModelPointer, delayedSubTrackNameChanger, [], {})

        def mpeMaster_color_changed():
            def delayedSubTrackColorChanger():

                for tempSubtrackModelId, tempSubtrackModel in self._mpeSubtracks.iteritems():
                    tempSubtrackModel.item.color = self.item.color
                return True

            InstanceContainer.add_delayed_callback("CallbackForUpdatingColorsOnSubtracksFor"+self.itemModelPointer, delayedSubTrackColorChanger, [], {})

        def _update_subtracks_target_output_routing_channel_name():
            foundName = None
            for tempDevice in self.item.devices:
                if tempDevice.type == Live.Device.DeviceType.instrument:
                    #log_message("[DEBUG] Found mpe-masters instrument:", tempDevice, "-", tempDevice.class_name, "-",
                    #            tempDevice.name)

                    if foundName is not None:
                        log_message("[WTF] found another instrument on track:", self.s_name,"named:",tempDevice.name)

                    foundName = tempDevice.name
            instrumentAdded = False
            if self._subtracks_target_output_routing_channel_name is None and foundName is not None:
                instrumentAdded = True

            self._subtracks_target_output_routing_channel_name = foundName
            if instrumentAdded:
                for tempMPESubtrackModelIMP, tempMPESubtrackModel in self._mpeSubtracks.iteritems():
                    if tempMPESubtrackModel._mpeChannelId == 1:
                        log_message("Setting output routing on ch1 to:",tempMPESubtrackModel.item.output_routing_type.display_name)
                        tempMPESubtrackModel._subtracksOutputRoutingUpdater(forceUpdateChannels=True)

        self.item.add_playing_slot_index_listener(mpeMaster_playing_slot_index_changed)
        self.item.add_fired_slot_index_listener(mpeMaster_fired_slot_index_changed)
        self.item.add_arm_listener(mpeMaster_arm_changed)
        self.add_s_name_listener(mpeMaster_name_changed)
        self.item.add_color_listener(mpeMaster_color_changed)
        self.item.add_devices_listener(_update_subtracks_target_output_routing_channel_name )

        _update_subtracks_target_output_routing_channel_name()

        self.isMPEMasterTrack = True
        InstanceContainer.itemModelDataHandler.add_external_property_for_itemModel(self, "isMPEMasterTrack", True)
        InstanceContainer.itemModelDataHandler.add_external_property_for_itemModel(self, "_mpeSubtracks", self._mpeSubtracks)

        log_message("Processed _MPEMasterTrackMix_init")

    def _get_mpe_controller_input_type_name(self):
        """ Used to fetch the input_type_name for the subtracks. Looks for available input_routing_type which starts
        with the prefixes defined in the conf.
        """
        for tempInputType in self.item.available_input_routing_types:
            for tempPrefix in conf.defaultMPEControllerNamePrefix:
                if tempInputType.display_name.startswith(tempPrefix):
                    return tempInputType.display_name

        return "Computer Keyboard"

    def _mpe_clip_slot_to_fire_index_changed(self, newValue):
        if newValue != self._mpeClipSlotToFireIndex:
            log_message("WEEEEE, should switch _mpeClipSlotToFireIndex to:",newValue)
            self._mpeClipSlotToFireIndex = newValue

            def delayedCallbackToFireMPESubtracksClipslots(mpeSubtrackList, slotToFire):
                for tempMpeSubtrack in mpeSubtrackList:
                    if slotToFire == -2:
                        tempMpeSubtrack.item.stop_all_clips()
                    else:
                        tempMpeSubtrack.item.clip_slots[slotToFire].fire()
                return True

            tempMPESubtrackList = []
            for tempMPESubtrackModelIMP, tempMPESubtrackModel in self._mpeSubtracks.iteritems():
                if self._mpeClipSlotToFireIndex != self._get_clip_slot_to_fire_index(tempMPESubtrackModel.item):
                    tempMPESubtrackList.append(tempMPESubtrackModel)

            if self._get_clip_slot_to_fire_index(self.item) != self._mpeClipSlotToFireIndex:
                if self.item.can_be_armed:
                    tempMPESubtrackList.append(self)
                else:
                    log_message("can_be_armed is false!")

            keyForCallback = "FireClipSlotByIndex_byMPEMasterTrack:" + str(self.s_name)
            InstanceContainer.add_delayed_callback(keyForCallback, delayedCallbackToFireMPESubtracksClipslots,
                               (tempMPESubtrackList, self._mpeClipSlotToFireIndex), {},
                               rewriteExisting=False)

        else:
            log_message("WTF, _mpe_clip_slot_to_fire_index_changed, got old value as new:",newValue)

    def _get_clip_slot_to_fire_index(self, trackItem):
        temp_mpeClipSlotToFireIndex = None
        if trackItem.fired_slot_index == -2:
            temp_mpeClipSlotToFireIndex = -2
        elif trackItem.fired_slot_index >= 0:
            temp_mpeClipSlotToFireIndex = trackItem.fired_slot_index
        else:
            temp_mpeClipSlotToFireIndex = trackItem.playing_slot_index

        return temp_mpeClipSlotToFireIndex

    def _mpe_arm_changed(self, newValue):
        if newValue != self._mpeArmState:
            def delayedCallbackForArmingMPESubtracks(mpeSubtrackList, armvalue):
                for tempMPESubtrack in mpeSubtrackList:
                    if tempMPESubtrack.item.arm != armvalue:
                        tempMPESubtrack.item.arm = armvalue
                return True

            self._mpeArmState = newValue
            tempSubtrackList = []
            for tempMPESubtrackModelIMP, tempMPESubtrackModel in self._mpeSubtracks.iteritems():
                if self._mpeArmState != tempMPESubtrackModel.item.arm:
                    tempSubtrackList.append(tempMPESubtrackModel)
            if self.item.arm != self._mpeArmState:
                if self.item.can_be_armed:
                    tempSubtrackList.append(self)
                else:
                    log_message("can_be_armed is false!")

            keyForCallback = "updateArmOn_"+str(self.itemId)+"_MPESubtracks"
            InstanceContainer.add_delayed_callback(keyForCallback, delayedCallbackForArmingMPESubtracks, (tempSubtrackList, self._mpeArmState), {}, rewriteExisting=False)

    def _add_mpe_subtrack(self, subTrackItemModel, mpeChannelId=None, creatingTrack=False):
        # log_message(self.itemModelPointer,"adding mpe-subtrack:", subTrackItemModel.itemModelPointer,"item:",
        #            subTrackItemModel.item, "mpeChannelId:",mpeChannelId)
        self._mpeSubtracks[subTrackItemModel.itemModelPointer] = subTrackItemModel
        self.call_mpeSubtracks_listeners()

        if not "MPESubTrackMix" in subTrackItemModel.mixedWithClasses:
            subTrackItemModel._mix_with_class("MPESubTrackMix", mpeChannelId, self, creatingTrack=creatingTrack)
        # subTrackItemModel._MPEMasterTrackModel = self
        # InstanceContainer.itemModelDataHandler.add_external_property_for_itemModel(subTrackItemModel, "_MPEMasterTrackModel", self)

    def add__mpeSubtracks_listener(self, callback):
        if not callback in self._mpeSubtracks_changed_listeners:
            self._mpeSubtracks_changed_listeners.append(callback)
        else:
            log_message("[WARNING], in add__mpeSubtracks_changed_listener on item:",
                        self.itemType+"-"+self.itemModelPointer,"callback:",callback,"exists already, can't add!")

    def remove__mpeSubtracks_listener(self, callback):
        if callback in self._mpeSubtracks_changed_listeners:
            self._mpeSubtracks_changed_listeners.remove(callback)
        else:
            log_message("[WARNING], in remove__mpeSubtracks_changed_listener on item:",
                        self.itemType+"-"+self.itemModelPointer,"callback:",callback,"doesn't exists, can't remove!")

    def call_mpeSubtracks_listeners(self):
        # log_message("call_mpeSubtracks_listeners, item:",self.itemModelPointer,"num of callbacks:",len(self._mpeSubtracks_changed_listeners))
        for tempCallback in self._mpeSubtracks_changed_listeners:
            tempCallback()

class MPESubTrackMix(object):
    """ Mix-in class for a MPE-sub track. Mainly sets the external data, but for the first sub-track, listeners to
      routing type changes are added, altering the values on the other subtracks if the value is changed on the first.

      _add_updating_of_* methods add listeners for *, and update the siblings when first the sub track gets changed.
    """

    def _MPESubTrackMix_init(self, subChannelId, MPEMasterTrackModel, creatingTrack=False):
        # log_message("Processing _MPESubTrackMix_init")
        # log_message("IMP:",self.itemModelPointer)
        self.mixedWithClasses.append("MPESubTrackMix")
        self._MPEMasterTrackModel = MPEMasterTrackModel
        self.isMPESubTrack = True
        if subChannelId is not None:
            self._mpeChannelId = subChannelId
        if creatingTrack:
            if self.item.arm != self._MPEMasterTrackModel.item.arm:
                self.item.arm = self._MPEMasterTrackModel.item.arm
            if self.item.color != self._MPEMasterTrackModel.item.color:
                self.item.color = self._MPEMasterTrackModel.item.color
            if self.s_name != self._MPEMasterTrackModel.s_name + "Ch" + str(self._mpeChannelId):
                self.item.name = self._MPEMasterTrackModel.s_name + "Ch" + str(self._mpeChannelId)
        self._target_input_routing_channel_display_name = "Ch. "+str(self._mpeChannelId)
        InstanceContainer.itemModelDataHandler.add_external_property_for_itemModel(self, "isMPESubTrack", True)
        InstanceContainer.itemModelDataHandler.add_external_property_for_itemModel(self, "_mpeChannelId", subChannelId)
        # log_message("Processed _MPESubTrackMix_init")
        if creatingTrack and self.item.input_routing_type.display_name != self._MPEMasterTrackModel._mpeControllerInputTypeName:
            self.set_input_routing_type_by_types_display_name(self._MPEMasterTrackModel._mpeControllerInputTypeName)
        if self._mpeChannelId == 1:
            self._target_input_routing_type_display_name = self.item.input_routing_type.display_name
            self._add_updating_of_input_routing_type()
            self._add_updating_of_input_routing_channel()
            self._add_updating_of_output_routing_channel()

    def _get_target_output_routing_channel_display_name(self):
        if self._MPEMasterTrackModel._subtracks_target_output_routing_channel_name is not None:
            return str(self._mpeChannelId)+"-"+self._MPEMasterTrackModel._subtracks_target_output_routing_channel_name
        else:
            return "Track In"

    def _add_updating_of_input_routing_type(self):
        def _input_routing_type_changed_listener():
            if self.item.input_routing_type.display_name == self._target_input_routing_type_display_name:
                # log_message("[DEBUG] MPESubtracks:",self.s_name,"input_routing_type not changed. Now:",
                #            self.item.input_routing_type.display_name)
                pass
            else:
                # log_message("[DEBUG] WEEEEE, MPESubtracks:", self.s_name,
                #            "input_routing_type changed. Now:",
                #            self.item.input_routing_type.display_name,
                #            "delaying callback to update siblings!")

                def delayedCallbackForUpdatingMPESubtracksInputRouting(siblingSubtrackList):
                    for tempSiblingMPESubtrack in siblingSubtrackList:
                        tempSiblingMPESubtrack.set_input_routing_type_by_types_display_name(
                            self._target_input_routing_type_display_name)
                    return True

                tempSiblingTrackList = []
                self._target_input_routing_type_display_name = self.item.input_routing_type.display_name
                for tempSiblingMPESubtrackId, tempSiblingMPESubtrack in self._MPEMasterTrackModel._mpeSubtracks.iteritems():
                    if tempSiblingMPESubtrack.item.input_routing_type.display_name != self._target_input_routing_type_display_name:
                        # log_message("Found sibling: ", tempSiblingMPESubtrack.s_name)
                        tempSiblingTrackList.append(tempSiblingMPESubtrack)


                InstanceContainer.add_delayed_callback("UpdateMPEMasters_"+self._MPEMasterTrackModel.s_name+"_SubtracksInputRoutingTypes", delayedCallbackForUpdatingMPESubtracksInputRouting, (tempSiblingTrackList,), {})
        self.item.add_input_routing_type_listener(_input_routing_type_changed_listener)

    def _add_updating_of_input_routing_channel(self):
        def _input_routing_channel_changed_listener():
            if self.item.input_routing_channel.display_name == self._target_input_routing_channel_display_name:
                # log_message("[DEBUG] MPESubtracks:",self.s_name,"input_routing_channel not changed. Now:",
                #            self.item.input_routing_channel.display_name)
                pass
            else:
                # log_message("[DEBUG] WEEEEE, MPESubtracks:", self.s_name,
                #            "input_routing_channel changed. Now:",
                #            self.item.input_routing_channel.display_name,
                #            "delaying callback to update siblings!")


                def delayedCallbackForUpdatingMPESubtracksInputRouting(siblingSubtrackList):
                    # log_message("Got siblinglist to update:")
                    for tempSiblingMPESubtrack in siblingSubtrackList:
                        # log_message("\n-",tempSiblingMPESubtrack._mpeChannelId)
                        if tempSiblingMPESubtrack.item.input_routing_channel.display_name != tempSiblingMPESubtrack._target_input_routing_channel_display_name:
                            tempSiblingMPESubtrack.set_input_routing_channel_by_channel_display_name(
                                tempSiblingMPESubtrack._target_input_routing_channel_display_name)
                    return True

                tempSiblingTrackList = []

                for tempSiblingMPESubtrackId, tempSiblingMPESubtrack in self._MPEMasterTrackModel._mpeSubtracks.iteritems():
                    tempSiblingTrackList.append(tempSiblingMPESubtrack)

                # InstanceContainer.clientUpdateScheduler.delayClientUpdates(2)
                InstanceContainer.add_delayed_callback("UpdateMPEMasters_"+self._MPEMasterTrackModel.s_name+"_SubtracksInputRoutingChannels", delayedCallbackForUpdatingMPESubtracksInputRouting, (tempSiblingTrackList,), {},delayCycles=2)
        self.item.add_input_routing_channel_listener(_input_routing_channel_changed_listener)

    def _add_updating_of_output_routing_channel(self):
        def _mpeTrack_output_routing_type_listener(self, forceUpdateChannels = False):
            if self.item.output_routing_type.display_name != self._MPEMasterTrackModel.item.name or forceUpdateChannels:
                def delayedCallbackForUpdatingMPESubtracksOutputRoutings(siblingSubtrackList):
                    doUpdate = forceUpdateChannels;

                    for tempSiblingMPESubtrack in siblingSubtrackList:
                        if tempSiblingMPESubtrack.item.output_routing_type.display_name != self._MPEMasterTrackModel.item.name:
                            tempSiblingMPESubtrack.set_output_routing_type_by_types_display_name(
                                self._MPEMasterTrackModel.item.name)
                            doUpdate = True

                    if doUpdate:
                        # InstanceContainer.clientUpdateScheduler.delayClientUpdates(2)
                        InstanceContainer.add_delayed_callback(
                            "UpdateMPEMasters_" + self._MPEMasterTrackModel.s_name + "_SubtracksOutputRoutingChannels",
                            delayedCallbackForUpdatingMPESubtracksOutputChannels, (tempSiblingTrackList,), {},
                            delayCycles=2)

                    return True

                def delayedCallbackForUpdatingMPESubtracksOutputChannels(siblingSubtrackList):
                    for tempSiblingMPESubtrack in siblingSubtrackList:
                        _tempsorcTargetName = tempSiblingMPESubtrack._get_target_output_routing_channel_display_name()
                        if tempSiblingMPESubtrack.item.output_routing_channel.display_name != _tempsorcTargetName:
                            tempSiblingMPESubtrack.set_output_routing_channel_by_channel_display_name(
                                _tempsorcTargetName)
                    return True

                tempSiblingTrackList = []
                for tempSiblingMPESubtrackId, tempSiblingMPESubtrack in self._MPEMasterTrackModel._mpeSubtracks.iteritems():
                    tempSiblingTrackList.append(tempSiblingMPESubtrack)

                InstanceContainer.add_delayed_callback("UpdateMPEMasters_"+self._MPEMasterTrackModel.s_name+"_SubtracksOutputRoutingTypes", delayedCallbackForUpdatingMPESubtracksOutputRoutings, (tempSiblingTrackList,), {},delayCycles=2)

        setattr(self, '_subtracksOutputRoutingUpdater', types.MethodType(_mpeTrack_output_routing_type_listener, self))

        self.item.add_output_routing_type_listener(self._subtracksOutputRoutingUpdater)

class MPEMasterClipMix(object):
    """ Mix-in class for a clip which is on the MPE Master track. Not yet utilized, but intended to enable simultaneous
      manipulation of e.g. loop_start and loop_length properties. The functionality may be added via the ClipSlot,
      though.
    """
    def _MPEMasterClipMix_init(self):
        log_message("Processing _MPEMasterClipMix_init")
        log_message("IMP:",self.itemModelPointer)
        self.mixedWithClasses.append("MPEMasterClipMix")
        self.isMPEMasterClip = True
        InstanceContainer.itemModelDataHandler.add_external_property_for_itemModel(self, "isMPEMasterClip", True)
        log_message("Processed _MPEMasterClipMix_init")

    # TODO: listeners for start_marker, end_marker, (notes)?, name
    # TODO: utilize addPropertyToClass for _MPESubClips
    # "Extend clip", anyone? Start recording in new scenes slot(s if MPE), when done, copy to-be-extended clip to the
    # end of the arrangement, recorded clip next to it, and split scenes time or copy the clips.

class MPESubClipMix(object):
    """ Mix-in class for a clip which is on the MPE sub track. Not yet utilized, see MPEMasterClipMix. """
    def _MPESubClipMix_init(self):
        # log_message("Processing _MPESubClipMix_init")
        # log_message("IMP:",self.itemModelPointer)
        self.mixedWithClasses.append("MPESubClipMix")
        self.isMPESubClip = True
        InstanceContainer.itemModelDataHandler.add_external_property_for_itemModel(self, "isMPESubClip", True)
        # log_message("Processed _MPESubClipMix_init")

class GhostMidiInputTrackMix(object):
    """ Mix-in class for the GhostMidiInputTrack. Very simple. """
    def _GhostMidiInputTrackMix_init(self):
        self.mixedWithClasses.append("GhostMidiInputTrackMix")
        self.isGhostMidiInputTrack = True
        InstanceContainer.itemModelDataHandler.add_external_property_for_itemModel(self, "isGhostMidiInputTrack", True)
        InstanceContainer.songModel._ghostMidiInputTrack = self
        InstanceContainer.songModel._call_ghostMidiInputTrack_listeners()
