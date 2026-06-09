"""USB Audio Class 1.0 (UAC 1.0) descriptor definitions.

Defines the standard UAC 1.0 descriptor types including Audio Control Interface
(ACI) descriptors (Header, Input/Output Terminal, Feature/Mixer/Selector/
Processing/Extension Unit) and Audio Streaming (AS) descriptors (AS General,
Type I Format, Class-Specific Isochronous Endpoint).
"""

from usbdesc.core.base import DescriptorNode, u8, u16le, u24le
from usbdesc.core.types import (
    CS_INTERFACE, CS_ENDPOINT,
    UAC1_BCD,
    DESC_TYPE_ENDPOINT,
    ACSubtype, ASSubtype, EPSubtype,
    FORMAT_TYPE_I,
    CHANNEL_STEREO,
)

_UAC1_PROCESSING_UNIT = 0x07
_UAC1_EXTENSION_UNIT  = 0x08


class ACHeader(DescriptorNode):
    """UAC 1.0 Audio Control Interface Header. Contains the interface collection list via baInterfaceNr."""

    def __init__(self, baInterfaceNr, wTotalLength=0, bcdADC=UAC1_BCD, name=''):
        """Initialize an AC Interface Header descriptor.

        :param baInterfaceNr: List of interface numbers belonging to this audio control interface.
        :param wTotalLength: Total length of all class-specific AC interface descriptors (bytes).
        :param bcdADC: Audio Device Class specification release number in BCD (default: UAC 1.0).
        :param name: Optional descriptor label.
        """
        super().__init__(name)
        self.baInterfaceNr = list(baInterfaceNr)
        self.wTotalLength = wTotalLength
        self.bcdADC = bcdADC

    def _subfields(self):
        fields = [
            *u8('bDescriptorType', CS_INTERFACE),
            *u8('bDescriptorSubtype', ACSubtype.HEADER),
            *u16le('bcdADC', self.bcdADC),
            *u16le('wTotalLength', self.wTotalLength),
            *u8('bInCollection', len(self.baInterfaceNr)),
        ]
        for i, nr in enumerate(self.baInterfaceNr):
            fields.extend(u8(f'baInterfaceNr[{i}]', nr))
        return fields


class InputTerminal(DescriptorNode):
    """UAC 1.0 Audio Control Input Terminal. Represents an audio input connection."""

    def __init__(self, bTerminalID, wTerminalType, bNrChannels=2,
                 wChannelConfig=CHANNEL_STEREO, bAssocTerminal=0,
                 iChannelNames=0, iTerminal=0, name=''):
        """Initialize an Input Terminal descriptor.

        :param bTerminalID: Unique terminal identifier.
        :param wTerminalType: Terminal type (e.g. USB streaming, microphone, line in).
        :param bNrChannels: Number of logical audio channels.
        :param wChannelConfig: Spatial location of channels (16-bit bitmap, e.g. left/right).
        :param bAssocTerminal: Associated output terminal ID (for bidirectional connections), or 0.
        :param iChannelNames: String descriptor index for channel names.
        :param iTerminal: String descriptor index for this terminal.
        :param name: Optional descriptor label.
        """
        super().__init__(name)
        self.bTerminalID = bTerminalID
        self.wTerminalType = wTerminalType
        self.bNrChannels = bNrChannels
        self.wChannelConfig = wChannelConfig
        self.bAssocTerminal = bAssocTerminal
        self.iChannelNames = iChannelNames
        self.iTerminal = iTerminal

    def _subfields(self):
        return [
            *u8('bDescriptorType', CS_INTERFACE),
            *u8('bDescriptorSubtype', ACSubtype.INPUT_TERMINAL),
            *u8('bTerminalID', self.bTerminalID),
            *u16le('wTerminalType', self.wTerminalType),
            *u8('bAssocTerminal', self.bAssocTerminal),
            *u8('bNrChannels', self.bNrChannels),
            *u16le('wChannelConfig', self.wChannelConfig),
            *u8('iChannelNames', self.iChannelNames),
            *u8('iTerminal', self.iTerminal),
        ]


class OutputTerminal(DescriptorNode):
    """UAC 1.0 Audio Control Output Terminal. Represents an audio output connection."""

    def __init__(self, bTerminalID, wTerminalType, bSourceID=0,
                 bAssocTerminal=0, iTerminal=0, name=''):
        """Initialize an Output Terminal descriptor.

        :param bTerminalID: Unique terminal identifier.
        :param wTerminalType: Terminal type (e.g. speaker, headphone, line out).
        :param bSourceID: ID of the unit or terminal that feeds this output terminal.
        :param bAssocTerminal: Associated input terminal ID (for bidirectional connections), or 0.
        :param iTerminal: String descriptor index for this terminal.
        :param name: Optional descriptor label.
        """
        super().__init__(name)
        self.bTerminalID = bTerminalID
        self.wTerminalType = wTerminalType
        self.bSourceID = bSourceID
        self.bAssocTerminal = bAssocTerminal
        self.iTerminal = iTerminal

    def _subfields(self):
        return [
            *u8('bDescriptorType', CS_INTERFACE),
            *u8('bDescriptorSubtype', ACSubtype.OUTPUT_TERMINAL),
            *u8('bTerminalID', self.bTerminalID),
            *u16le('wTerminalType', self.wTerminalType),
            *u8('bAssocTerminal', self.bAssocTerminal),
            *u8('bSourceID', self.bSourceID),
            *u8('iTerminal', self.iTerminal),
        ]


class FeatureUnit(DescriptorNode):
    """UAC 1.0 Audio Feature Unit. Provides basic audio controls (volume, mute, etc). Supports variable bControlSize."""

    def __init__(self, bUnitID, bSourceID, controls_per_channel=None,
                 bControlSize=1, iFeature=0, name=''):
        """Initialize a Feature Unit descriptor.

        :param bUnitID: Unique unit identifier.
        :param bSourceID: ID of the unit or terminal that feeds this feature unit.
        :param controls_per_channel: List of control bitmaps, one entry per channel (index 0 = master).
        :param bControlSize: Size in bytes of each bmaControls element (typically 1 for UAC 1.0).
        :param iFeature: String descriptor index for this feature unit.
        :param name: Optional descriptor label.
        """
        super().__init__(name)
        self.bUnitID = bUnitID
        self.bSourceID = bSourceID
        self.controls_per_channel = controls_per_channel or []
        self.bControlSize = bControlSize
        self.iFeature = iFeature

    def _subfields(self):
        fields = [
            *u8('bDescriptorType', CS_INTERFACE),
            *u8('bDescriptorSubtype', ACSubtype.FEATURE_UNIT),
            *u8('bUnitID', self.bUnitID),
            *u8('bSourceID', self.bSourceID),
            *u8('bControlSize', self.bControlSize),
        ]
        for i, ctrl in enumerate(self.controls_per_channel):
            channel_label = 'master' if i == 0 else f'ch{i}'
            for b in range(self.bControlSize):
                val = (ctrl >> (8 * b)) & 0xFF
                fields.extend(u8(f'bmaControls[{channel_label}][{b}]', val))
        fields.extend(u8('iFeature', self.iFeature))
        return fields


class MixerUnit(DescriptorNode):
    """UAC 1.0 Audio Mixer Unit. Mixes multiple audio input channels into a single output channel."""

    def __init__(self, bUnitID, baSourceID, bNrChannels=2,
                 wChannelConfig=CHANNEL_STEREO, bmControls=None,
                 iChannelNames=0, iMixer=0, name=''):
        """Initialize a Mixer Unit descriptor.

        :param bUnitID: Unique unit identifier.
        :param baSourceID: List of source unit/terminal IDs feeding the mixer.
        :param bNrChannels: Number of logical output channels.
        :param wChannelConfig: Spatial location of output channels (16-bit bitmap).
        :param bmControls: List of byte-sized mixer controls.
        :param iChannelNames: String descriptor index for channel names.
        :param iMixer: String descriptor index for this mixer unit.
        :param name: Optional descriptor label.
        """
        super().__init__(name)
        self.bUnitID = bUnitID
        self.baSourceID = list(baSourceID)
        self.bNrChannels = bNrChannels
        self.wChannelConfig = wChannelConfig
        self.bmControls = bmControls or []
        self.iChannelNames = iChannelNames
        self.iMixer = iMixer

    def _subfields(self):
        fields = [
            *u8('bDescriptorType', CS_INTERFACE),
            *u8('bDescriptorSubtype', ACSubtype.MIXER_UNIT),
            *u8('bUnitID', self.bUnitID),
            *u8('bNrInPins', len(self.baSourceID)),
        ]
        for i, src_id in enumerate(self.baSourceID):
            fields.extend(u8(f'baSourceID[{i}]', src_id))
        fields.extend([
            *u8('bNrChannels', self.bNrChannels),
            *u16le('wChannelConfig', self.wChannelConfig),
            *u8('iChannelNames', self.iChannelNames),
        ])
        for i, ctrl in enumerate(self.bmControls):
            fields.extend(u8(f'bmControls[{i}]', ctrl))
        fields.extend(u8('iMixer', self.iMixer))
        return fields


class SelectorUnit(DescriptorNode):
    """UAC 1.0 Audio Selector Unit. Selects one of multiple audio input pins."""

    def __init__(self, bUnitID, baSourceID, iSelector=0, name=''):
        """Initialize a Selector Unit descriptor.

        :param bUnitID: Unique unit identifier.
        :param baSourceID: List of source unit/terminal IDs connected to selector input pins.
        :param iSelector: String descriptor index for this selector unit.
        :param name: Optional descriptor label.
        """
        super().__init__(name)
        self.bUnitID = bUnitID
        self.baSourceID = list(baSourceID)
        self.iSelector = iSelector

    def _subfields(self):
        fields = [
            *u8('bDescriptorType', CS_INTERFACE),
            *u8('bDescriptorSubtype', ACSubtype.SELECTOR_UNIT),
            *u8('bUnitID', self.bUnitID),
            *u8('bNrInPins', len(self.baSourceID)),
        ]
        for i, src_id in enumerate(self.baSourceID):
            fields.extend(u8(f'baSourceID[{i}]', src_id))
        fields.extend(u8('iSelector', self.iSelector))
        return fields


class ProcessingUnit(DescriptorNode):
    """UAC 1.0 Audio Processing Unit. Applies audio processing effects (e.g. up-down mix, Dolby Prologic)."""

    def __init__(self, bUnitID, wProcessType, baSourceID,
                 bNrChannels=2, wChannelConfig=CHANNEL_STEREO,
                 bmControls=None, bControlSize=1,
                 iChannelNames=0, iProcessing=0, name=''):
        """Initialize a Processing Unit descriptor.

        :param bUnitID: Unique unit identifier.
        :param wProcessType: Processing algorithm type (e.g. up-down mix, Dolby Prologic, 3D stereo).
        :param baSourceID: List of source unit/terminal IDs connected to processing input pins.
        :param bNrChannels: Number of logical output channels.
        :param wChannelConfig: Spatial location of output channels (16-bit bitmap).
        :param bmControls: List of byte-sized processing controls.
        :param bControlSize: Size in bytes of each bmControls element.
        :param iChannelNames: String descriptor index for channel names.
        :param iProcessing: String descriptor index for this processing unit.
        :param name: Optional descriptor label.
        """
        super().__init__(name)
        self.bUnitID = bUnitID
        self.wProcessType = wProcessType
        self.baSourceID = list(baSourceID)
        self.bNrChannels = bNrChannels
        self.wChannelConfig = wChannelConfig
        self.bmControls = bmControls or []
        self.bControlSize = bControlSize
        self.iChannelNames = iChannelNames
        self.iProcessing = iProcessing

    def _subfields(self):
        fields = [
            *u8('bDescriptorType', CS_INTERFACE),
            *u8('bDescriptorSubtype', _UAC1_PROCESSING_UNIT),
            *u8('bUnitID', self.bUnitID),
            *u16le('wProcessType', self.wProcessType),
            *u8('bNrInPins', len(self.baSourceID)),
        ]
        for i, src_id in enumerate(self.baSourceID):
            fields.extend(u8(f'baSourceID[{i}]', src_id))
        fields.extend([
            *u8('bNrChannels', self.bNrChannels),
            *u16le('wChannelConfig', self.wChannelConfig),
            *u8('iChannelNames', self.iChannelNames),
            *u8('bControlSize', self.bControlSize),
        ])
        for i, ctrl in enumerate(self.bmControls):
            fields.extend(u8(f'bmControls[{i}]', ctrl))
        fields.extend(u8('iProcessing', self.iProcessing))
        return fields


class ExtensionUnit(DescriptorNode):
    """UAC 1.0 Audio Extension Unit. Supports vendor-defined audio processing extensions."""

    def __init__(self, bUnitID, wExtensionCode, baSourceID,
                 bNrChannels=2, wChannelConfig=CHANNEL_STEREO,
                 bmControls=None, bControlSize=1,
                 iChannelNames=0, iExtension=0, name=''):
        """Initialize an Extension Unit descriptor.

        :param bUnitID: Unique unit identifier.
        :param wExtensionCode: Vendor-defined extension code.
        :param baSourceID: List of source unit/terminal IDs connected to extension input pins.
        :param bNrChannels: Number of logical output channels.
        :param wChannelConfig: Spatial location of output channels (16-bit bitmap).
        :param bmControls: List of byte-sized extension controls.
        :param bControlSize: Size in bytes of each bmControls element.
        :param iChannelNames: String descriptor index for channel names.
        :param iExtension: String descriptor index for this extension unit.
        :param name: Optional descriptor label.
        """
        super().__init__(name)
        self.bUnitID = bUnitID
        self.wExtensionCode = wExtensionCode
        self.baSourceID = list(baSourceID)
        self.bNrChannels = bNrChannels
        self.wChannelConfig = wChannelConfig
        self.bmControls = bmControls or []
        self.bControlSize = bControlSize
        self.iChannelNames = iChannelNames
        self.iExtension = iExtension

    def _subfields(self):
        fields = [
            *u8('bDescriptorType', CS_INTERFACE),
            *u8('bDescriptorSubtype', _UAC1_EXTENSION_UNIT),
            *u8('bUnitID', self.bUnitID),
            *u16le('wExtensionCode', self.wExtensionCode),
            *u8('bNrInPins', len(self.baSourceID)),
        ]
        for i, src_id in enumerate(self.baSourceID):
            fields.extend(u8(f'baSourceID[{i}]', src_id))
        fields.extend([
            *u8('bNrChannels', self.bNrChannels),
            *u16le('wChannelConfig', self.wChannelConfig),
            *u8('iChannelNames', self.iChannelNames),
            *u8('bControlSize', self.bControlSize),
        ])
        for i, ctrl in enumerate(self.bmControls):
            fields.extend(u8(f'bmControls[{i}]', ctrl))
        fields.extend(u8('iExtension', self.iExtension))
        return fields


class ASGeneral(DescriptorNode):
    """UAC 1.0 Audio Streaming General descriptor. Links to an Output Terminal."""

    def __init__(self, bTerminalLink, wFormatTag=0x0001,
                 bDelay=1, name=''):
        """Initialize an AS General descriptor.

        :param bTerminalLink: ID of the Output Terminal this streaming interface connects to.
        :param wFormatTag: Audio format tag (e.g. 0x0001 for PCM).
        :param bDelay: Interface delay in frame units.
        :param name: Optional descriptor label.
        """
        super().__init__(name)
        self.bTerminalLink = bTerminalLink
        self.wFormatTag = wFormatTag
        self.bDelay = bDelay

    def _subfields(self):
        return [
            *u8('bDescriptorType', CS_INTERFACE),
            *u8('bDescriptorSubtype', ASSubtype.AS_GENERAL),
            *u8('bTerminalLink', self.bTerminalLink),
            *u8('bDelay', self.bDelay),
            *u16le('wFormatTag', self.wFormatTag),
        ]


class FormatTypeI(DescriptorNode):
    """UAC 1.0 Type I Format descriptor. Specifies PCM audio format with 3-byte sample rates."""

    def __init__(self, bNrChannels=2, bSubframeSize=2,
                 bBitResolution=16, sample_rates=None, name=''):
        """Initialize a Type I Format descriptor.

        :param bNrChannels: Number of physical audio channels.
        :param bSubframeSize: Bytes per audio subframe (sample).
        :param bBitResolution: Bits per sample.
        :param sample_rates: List of supported sample rates in Hz (stored as 3-byte LE values).
        :param name: Optional descriptor label.
        """
        super().__init__(name)
        self.bNrChannels = bNrChannels
        self.bSubframeSize = bSubframeSize
        self.bBitResolution = bBitResolution
        self.sample_rates = sample_rates or [48000]

    def _subfields(self):
        fields = [
            *u8('bDescriptorType', CS_INTERFACE),
            *u8('bDescriptorSubtype', ASSubtype.FORMAT_TYPE),
            *u8('bFormatType', FORMAT_TYPE_I),
            *u8('bNrChannels', self.bNrChannels),
            *u8('bSubframeSize', self.bSubframeSize),
            *u8('bBitResolution', self.bBitResolution),
            *u8('bSamFreqType', len(self.sample_rates)),
        ]
        for i, freq in enumerate(self.sample_rates):
            fields.extend(u24le(f'tSamFreq[{i}]', freq))
        return fields


class ClassSpecificIsoEP(DescriptorNode):
    """UAC 1.0 Class-Specific Isochronous Endpoint descriptor."""

    def __init__(self, bmAttributes=0x00, bLockDelayUnits=0, wLockDelay=0, name=''):
        """Initialize a Class-Specific Isochronous Endpoint descriptor.

        :param bmAttributes: Bitmap of endpoint attributes (MaxPacketsOnly, Sampling Frequency Control).
        :param bLockDelayUnits: Units for wLockDelay (0=undef, 1=ms, 2=PCM samples).
        :param wLockDelay: Time to lock internal clock recovery on this endpoint.
        :param name: Optional descriptor label.
        """
        super().__init__(name)
        self.bmAttributes = bmAttributes
        self.bLockDelayUnits = bLockDelayUnits
        self.wLockDelay = wLockDelay

    def _subfields(self):
        return [
            *u8('bDescriptorType', CS_ENDPOINT),
            *u8('bDescriptorSubtype', EPSubtype.EP_GENERAL),
            *u8('bmAttributes', self.bmAttributes),
            *u8('bLockDelayUnits', self.bLockDelayUnits),
            *u16le('wLockDelay', self.wLockDelay),
        ]
