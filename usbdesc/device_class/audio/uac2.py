"""USB Audio Class 2.0 (UAC 2.0) and MIDI Streaming descriptor definitions.

Defines the standard UAC 2.0 descriptor types including Audio Control Interface
(ACI) descriptors (Header, Input/Output Terminal, Feature/Mixer/Selector/Effect/
Processing/Extension Unit, Clock Source/Selector/Multiplier, Sample Rate
Converter), Audio Streaming descriptors (AS General, Format Type I, Encoder,
Decoder, Class-Specific Isochronous Endpoint), and MIDI Streaming descriptors
(MS Header, MIDI In/Out Jacks, MIDI Bulk Endpoints).
"""

from usbdesc.core.base import (
    DescriptorNode, u8, u16le, u32le,
    source_id_fields, controls_per_channel_fields,
)
from usbdesc.core.types import (
    CS_INTERFACE, CS_ENDPOINT,
    UAC2_BCD,
    DESC_TYPE_ENDPOINT,
    ACSubtype, ASSubtype, EPSubtype, MIDISubtype,
    CLOCK_INT_FIXED,
    FORMAT_TYPE_I,
    CHANNEL_STEREO,
)


def uac2_ctrl_pair(readonly, readwrite):
    """Encode a ReadOnly + ReadWrite 2-bit control pair into a nibble.

    D1..0 = ReadOnly access (0=none, 1=ReadOnly, 3=RW)
    D3..2 = ReadWrite access (0=none, 1=ReadOnly, 3=RW)
    """
    return ((readwrite & 0x03) << 2) | (readonly & 0x03)


class ACHeader(DescriptorNode):
    """UAC 2.0 Audio Control Interface Header. Includes bCategory and bmControls."""

    def __init__(self, bCategory, wTotalLength=0,
                 bmControls=0, bcdADC=UAC2_BCD, name=''):
        """Initialize an AC Interface Header descriptor.

        :param bCategory: Audio function category (e.g. speaker, headset, microphone).
        :param wTotalLength: Total length of all class-specific AC interface descriptors (bytes).
        :param bmControls: Bitmap of global AC interface controls (latency control bits).
        :param bcdADC: Audio Device Class specification release number in BCD (default: UAC 2.0).
        :param name: Optional descriptor label.
        """
        super().__init__(name)
        self.bCategory = bCategory
        self.wTotalLength = wTotalLength
        self.bmControls = bmControls
        self.bcdADC = bcdADC

    def _subfields(self):
        return [
            *u8('bDescriptorType', CS_INTERFACE),
            *u8('bDescriptorSubtype', ACSubtype.HEADER),
            *u16le('bcdADC', self.bcdADC),
            *u8('bCategory', self.bCategory),
            *u16le('wTotalLength', self.wTotalLength),
            *u8('bmControls', self.bmControls),
        ]


class InputTerminal(DescriptorNode):
    """UAC 2.0 Audio Control Input Terminal. Uses 32-bit bmChannelConfig."""

    def __init__(self, bTerminalID, wTerminalType, bCSourceID=0,
                 bNrChannels=2, bmChannelConfig=CHANNEL_STEREO,
                 bmControls=0x0000, bAssocTerminal=0,
                 iChannelNames=0, iTerminal=0, name=''):
        """Initialize an Input Terminal descriptor.

        :param bTerminalID: Unique terminal identifier.
        :param wTerminalType: Terminal type (e.g. USB streaming, microphone, line in).
        :param bCSourceID: ID of the Clock Source that provides clock for this terminal.
        :param bNrChannels: Number of logical audio channels.
        :param bmChannelConfig: Spatial location of channels (32-bit bitmap).
        :param bmControls: Copy-protect and connector controls (16-bit bitmap).
        :param bAssocTerminal: Associated output terminal ID (for bidirectional connections), or 0.
        :param iChannelNames: String descriptor index for channel names.
        :param iTerminal: String descriptor index for this terminal.
        :param name: Optional descriptor label.
        """
        super().__init__(name)
        self.bTerminalID = bTerminalID
        self.wTerminalType = wTerminalType
        self.bCSourceID = bCSourceID
        self.bNrChannels = bNrChannels
        self.bmChannelConfig = bmChannelConfig
        self.bmControls = bmControls
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
            *u8('bCSourceID', self.bCSourceID),
            *u8('bNrChannels', self.bNrChannels),
            *u32le('bmChannelConfig', self.bmChannelConfig),
            *u8('iChannelNames', self.iChannelNames),
            *u16le('bmControls', self.bmControls),
            *u8('iTerminal', self.iTerminal),
        ]


class OutputTerminal(DescriptorNode):
    """UAC 2.0 Audio Control Output Terminal. Represents an audio output connection with clock source association."""

    def __init__(self, bTerminalID, wTerminalType, bSourceID=0,
                 bCSourceID=0, bmControls=0x00, bAssocTerminal=0,
                 iTerminal=0, name=''):
        """Initialize an Output Terminal descriptor.

        :param bTerminalID: Unique terminal identifier.
        :param wTerminalType: Terminal type (e.g. speaker, headphone, line out).
        :param bSourceID: ID of the unit or terminal that feeds this output terminal.
        :param bCSourceID: ID of the Clock Source that provides clock for this terminal.
        :param bmControls: Copy-protect and connector controls (8-bit bitmap).
        :param bAssocTerminal: Associated input terminal ID (for bidirectional connections), or 0.
        :param iTerminal: String descriptor index for this terminal.
        :param name: Optional descriptor label.
        """
        super().__init__(name)
        self.bTerminalID = bTerminalID
        self.wTerminalType = wTerminalType
        self.bSourceID = bSourceID
        self.bCSourceID = bCSourceID
        self.bmControls = bmControls
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
            *u8('bCSourceID', self.bCSourceID),
            *u16le('bmControls', self.bmControls),
            *u8('iTerminal', self.iTerminal),
        ]


class FeatureUnit(DescriptorNode):
    """UAC 2.0 Audio Feature Unit. Provides basic audio controls (volume, mute, etc) with 32-bit bmaControls fields."""

    def __init__(self, bUnitID, bSourceID,
                 controls_per_channel=None, iFeature=0, name=''):
        """Initialize a Feature Unit descriptor.

        :param bUnitID: Unique unit identifier.
        :param bSourceID: ID of the unit or terminal that feeds this feature unit.
        :param controls_per_channel: List of 32-bit control bitmaps, one entry per channel (index 0 = master).
        :param iFeature: String descriptor index for this feature unit.
        :param name: Optional descriptor label.
        """
        super().__init__(name)
        self.bUnitID = bUnitID
        self.bSourceID = bSourceID
        self.controls_per_channel = controls_per_channel or []
        self.iFeature = iFeature

    def _subfields(self):
        fields = [
            *u8('bDescriptorType', CS_INTERFACE),
            *u8('bDescriptorSubtype', ACSubtype.FEATURE_UNIT),
            *u8('bUnitID', self.bUnitID),
            *u8('bSourceID', self.bSourceID),
        ]
        fields.extend(controls_per_channel_fields(self.controls_per_channel))
        fields.extend(u8('iFeature', self.iFeature))
        return fields


class MixerUnit(DescriptorNode):
    """UAC 2.0 Audio Mixer Unit. Mixes multiple audio input channels with 32-bit bmChannelConfig."""

    def __init__(self, bUnitID, baSourceID, bNrChannels=2,
                 bmChannelConfig=CHANNEL_STEREO, bmMixerControls=None,
                 bmControls=0x00, iChannelNames=0, iMixer=0, name=''):
        """Initialize a Mixer Unit descriptor.

        :param bUnitID: Unique unit identifier.
        :param baSourceID: List of source unit/terminal IDs feeding the mixer.
        :param bNrChannels: Number of logical output channels.
        :param bmChannelConfig: Spatial location of output channels (32-bit bitmap).
        :param bmMixerControls: List of byte-sized mixer programmability controls.
        :param bmControls: Spatial location control bitmap.
        :param iChannelNames: String descriptor index for channel names.
        :param iMixer: String descriptor index for this mixer unit.
        :param name: Optional descriptor label.
        """
        super().__init__(name)
        self.bUnitID = bUnitID
        self.baSourceID = list(baSourceID)
        self.bNrChannels = bNrChannels
        self.bmChannelConfig = bmChannelConfig
        self.bmMixerControls = bmMixerControls or []
        self.bmControls = bmControls
        self.iChannelNames = iChannelNames
        self.iMixer = iMixer

    def _subfields(self):
        fields = [
            *u8('bDescriptorType', CS_INTERFACE),
            *u8('bDescriptorSubtype', ACSubtype.MIXER_UNIT),
            *u8('bUnitID', self.bUnitID),
            *u8('bNrInPins', len(self.baSourceID)),
        ]
        fields.extend(source_id_fields(self.baSourceID))
        fields.extend([
            *u8('bNrChannels', self.bNrChannels),
            *u32le('bmChannelConfig', self.bmChannelConfig),
            *u8('iChannelNames', self.iChannelNames),
        ])
        for i, ctrl in enumerate(self.bmMixerControls):
            fields.extend(u8(f'bmMixerControls[{i}]', ctrl))
        fields.extend([
            *u8('bmControls', self.bmControls),
            *u8('iMixer', self.iMixer),
        ])
        return fields


class SelectorUnit(DescriptorNode):
    """UAC 2.0 Audio Selector Unit. Selects one of multiple audio input pins."""

    def __init__(self, bUnitID, baSourceID, bmControls=0x00,
                 iSelector=0, name=''):
        """Initialize a Selector Unit descriptor.

        :param bUnitID: Unique unit identifier.
        :param baSourceID: List of source unit/terminal IDs connected to selector input pins.
        :param bmControls: Selector control bitmap.
        :param iSelector: String descriptor index for this selector unit.
        :param name: Optional descriptor label.
        """
        super().__init__(name)
        self.bUnitID = bUnitID
        self.baSourceID = list(baSourceID)
        self.bmControls = bmControls
        self.iSelector = iSelector

    def _subfields(self):
        fields = [
            *u8('bDescriptorType', CS_INTERFACE),
            *u8('bDescriptorSubtype', ACSubtype.SELECTOR_UNIT),
            *u8('bUnitID', self.bUnitID),
            *u8('bNrInPins', len(self.baSourceID)),
        ]
        fields.extend(source_id_fields(self.baSourceID))
        fields.extend([
            *u8('bmControls', self.bmControls),
            *u8('iSelector', self.iSelector),
        ])
        return fields


class EffectUnit(DescriptorNode):
    """UAC 2.0 Audio Effect Unit. Applies vendor-defined audio effects to a single input pin."""

    def __init__(self, bUnitID, wEffectType, bSourceID=0,
                 controls_per_channel=None, iEffect=0, name=''):
        """Initialize an Effect Unit descriptor.

        :param bUnitID: Unique unit identifier.
        :param wEffectType: Effect algorithm identifier.
        :param bSourceID: ID of the unit or terminal that feeds this effect unit.
        :param controls_per_channel: List of 32-bit control bitmaps, one entry per channel (index 0 = master).
        :param iEffect: String descriptor index for this effect unit.
        :param name: Optional descriptor label.
        """
        super().__init__(name)
        self.bUnitID = bUnitID
        self.wEffectType = wEffectType
        self.bSourceID = bSourceID
        self.controls_per_channel = controls_per_channel or []
        self.iEffect = iEffect

    def _subfields(self):
        fields = [
            *u8('bDescriptorType', CS_INTERFACE),
            *u8('bDescriptorSubtype', ACSubtype.EFFECT_UNIT),
            *u8('bUnitID', self.bUnitID),
            *u16le('wEffectType', self.wEffectType),
            *u8('bSourceID', self.bSourceID),
        ]
        fields.extend(controls_per_channel_fields(self.controls_per_channel))
        fields.extend(u8('iEffect', self.iEffect))
        return fields


class ProcessingUnit(DescriptorNode):
    """UAC 2.0 Audio Processing Unit. Applies audio processing effects (e.g. up-down mix, Dolby Prologic)."""

    def __init__(self, bUnitID, wProcessType, baSourceID,
                 bNrChannels=2, bmChannelConfig=CHANNEL_STEREO,
                 bmControls=None, iChannelNames=0, iProcessing=0, name=''):
        """Initialize a Processing Unit descriptor.

        :param bUnitID: Unique unit identifier.
        :param wProcessType: Processing algorithm type (e.g. up-down mix, Dolby Prologic, 3D stereo).
        :param baSourceID: List of source unit/terminal IDs connected to processing input pins.
        :param bNrChannels: Number of logical output channels.
        :param bmChannelConfig: Spatial location of output channels (32-bit bitmap).
        :param bmControls: List of byte-sized processing controls.
        :param iChannelNames: String descriptor index for channel names.
        :param iProcessing: String descriptor index for this processing unit.
        :param name: Optional descriptor label.
        """
        super().__init__(name)
        self.bUnitID = bUnitID
        self.wProcessType = wProcessType
        self.baSourceID = list(baSourceID)
        self.bNrChannels = bNrChannels
        self.bmChannelConfig = bmChannelConfig
        self.bmControls = bmControls or []
        self.iChannelNames = iChannelNames
        self.iProcessing = iProcessing

    def _subfields(self):
        fields = [
            *u8('bDescriptorType', CS_INTERFACE),
            *u8('bDescriptorSubtype', ACSubtype.PROCESSING_UNIT),
            *u8('bUnitID', self.bUnitID),
            *u16le('wProcessType', self.wProcessType),
            *u8('bNrInPins', len(self.baSourceID)),
        ]
        fields.extend(source_id_fields(self.baSourceID))
        fields.extend([
            *u8('bNrChannels', self.bNrChannels),
            *u32le('bmChannelConfig', self.bmChannelConfig),
            *u8('iChannelNames', self.iChannelNames),
        ])
        for i, ctrl in enumerate(self.bmControls):
            fields.extend(u8(f'bmControls[{i}]', ctrl))
        fields.extend(u8('iProcessing', self.iProcessing))
        return fields


class ExtensionUnit(DescriptorNode):
    """UAC 2.0 Audio Extension Unit. Supports vendor-defined audio processing extensions."""

    def __init__(self, bUnitID, wExtensionCode, baSourceID,
                 bNrChannels=2, bmChannelConfig=CHANNEL_STEREO,
                 bmControls=0x01, iChannelNames=0, iExtension=0, name=''):
        """Initialize an Extension Unit descriptor.

        :param bUnitID: Unique unit identifier.
        :param wExtensionCode: Vendor-defined extension code.
        :param baSourceID: List of source unit/terminal IDs connected to extension input pins.
        :param bNrChannels: Number of logical output channels.
        :param bmChannelConfig: Spatial location of output channels (32-bit bitmap).
        :param bmControls: Extension control bitmap (default enables EnableControl).
        :param iChannelNames: String descriptor index for channel names.
        :param iExtension: String descriptor index for this extension unit.
        :param name: Optional descriptor label.
        """
        super().__init__(name)
        self.bUnitID = bUnitID
        self.wExtensionCode = wExtensionCode
        self.baSourceID = list(baSourceID)
        self.bNrChannels = bNrChannels
        self.bmChannelConfig = bmChannelConfig
        self.bmControls = bmControls
        self.iChannelNames = iChannelNames
        self.iExtension = iExtension

    def _subfields(self):
        fields = [
            *u8('bDescriptorType', CS_INTERFACE),
            *u8('bDescriptorSubtype', ACSubtype.EXTENSION_UNIT),
            *u8('bUnitID', self.bUnitID),
            *u16le('wExtensionCode', self.wExtensionCode),
            *u8('bNrInPins', len(self.baSourceID)),
        ]
        fields.extend(source_id_fields(self.baSourceID))
        fields.extend([
            *u8('bNrChannels', self.bNrChannels),
            *u32le('bmChannelConfig', self.bmChannelConfig),
            *u8('iChannelNames', self.iChannelNames),
            *u8('bmControls', self.bmControls),
            *u8('iExtension', self.iExtension),
        ])
        return fields


class ClockSource(DescriptorNode):
    """UAC 2.0 Clock Source. Defines a clock for the audio function."""

    def __init__(self, bClockID, bmAttributes=CLOCK_INT_FIXED,
                 bmControls=0x00, bAssocTerminal=0,
                 iClockSource=0, name=''):
        """Initialize a Clock Source descriptor.

        :param bClockID: Unique clock identifier.
        :param bmAttributes: Clock type and synchronization attributes (e.g. internal fixed, external).
        :param bmControls: Clock frequency and validity control bitmap.
        :param bAssocTerminal: Associated terminal ID for clock source terminal type, or 0.
        :param iClockSource: String descriptor index for this clock source.
        :param name: Optional descriptor label.
        """
        super().__init__(name)
        self.bClockID = bClockID
        self.bmAttributes = bmAttributes
        self.bmControls = bmControls
        self.bAssocTerminal = bAssocTerminal
        self.iClockSource = iClockSource

    def _subfields(self):
        return [
            *u8('bDescriptorType', CS_INTERFACE),
            *u8('bDescriptorSubtype', ACSubtype.CLOCK_SOURCE),
            *u8('bClockID', self.bClockID),
            *u8('bmAttributes', self.bmAttributes),
            *u8('bmControls', self.bmControls),
            *u8('bAssocTerminal', self.bAssocTerminal),
            *u8('iClockSource', self.iClockSource),
        ]


class ClockSelector(DescriptorNode):
    """UAC 2.0 Clock Selector. Selects one of multiple clock source inputs."""

    def __init__(self, bClockID, baCSourceID, bmControls=0x03,
                 iClockSelector=0, name=''):
        """Initialize a Clock Selector descriptor.

        :param bClockID: Unique clock selector identifier.
        :param baCSourceID: List of clock source IDs connected to selector input pins.
        :param bmControls: Clock selector control bitmap (default: ReadOnly + ReadWrite).
        :param iClockSelector: String descriptor index for this clock selector.
        :param name: Optional descriptor label.
        """
        super().__init__(name)
        self.bClockID = bClockID
        self.baCSourceID = list(baCSourceID)
        self.bmControls = bmControls
        self.iClockSelector = iClockSelector

    def _subfields(self):
        fields = [
            *u8('bDescriptorType', CS_INTERFACE),
            *u8('bDescriptorSubtype', ACSubtype.CLOCK_SELECTOR),
            *u8('bClockID', self.bClockID),
            *u8('bNrInPins', len(self.baCSourceID)),
        ]
        fields.extend(source_id_fields(self.baCSourceID, name='baCSourceID'))
        fields.extend([
            *u8('bmControls', self.bmControls),
            *u8('iClockSelector', self.iClockSelector),
        ])
        return fields


class ClockMultiplier(DescriptorNode):
    """UAC 2.0 Clock Multiplier. Multiplies a clock source frequency."""

    def __init__(self, bClockID, bCSourceID, bmControls=0x00,
                 iClockMultiplier=0, name=''):
        """Initialize a Clock Multiplier descriptor.

        :param bClockID: Unique clock multiplier identifier.
        :param bCSourceID: ID of the clock source to multiply.
        :param bmControls: Clock multiplier control bitmap.
        :param iClockMultiplier: String descriptor index for this clock multiplier.
        :param name: Optional descriptor label.
        """
        super().__init__(name)
        self.bClockID = bClockID
        self.bCSourceID = bCSourceID
        self.bmControls = bmControls
        self.iClockMultiplier = iClockMultiplier

    def _subfields(self):
        return [
            *u8('bDescriptorType', CS_INTERFACE),
            *u8('bDescriptorSubtype', ACSubtype.CLOCK_MULTIPLIER),
            *u8('bClockID', self.bClockID),
            *u8('bCSourceID', self.bCSourceID),
            *u8('bmControls', self.bmControls),
            *u8('iClockMultiplier', self.iClockMultiplier),
        ]


class SampleRateConverter(DescriptorNode):
    """UAC 2.0 Sample Rate Converter. Converts between different sample rates."""

    def __init__(self, bUnitID, bSourceID, bCSourceInID=0,
                 bCSourceOutID=0, iSRC=0, name=''):
        """Initialize a Sample Rate Converter descriptor.

        :param bUnitID: Unique unit identifier.
        :param bSourceID: ID of the unit or terminal feeding the converter.
        :param bCSourceInID: Input clock source ID, or 0.
        :param bCSourceOutID: Output clock source ID, or 0.
        :param iSRC: String descriptor index for this sample rate converter.
        :param name: Optional descriptor label.
        """
        super().__init__(name)
        self.bUnitID = bUnitID
        self.bSourceID = bSourceID
        self.bCSourceInID = bCSourceInID
        self.bCSourceOutID = bCSourceOutID
        self.iSRC = iSRC

    def _subfields(self):
        return [
            *u8('bDescriptorType', CS_INTERFACE),
            *u8('bDescriptorSubtype', ACSubtype.SAMPLE_RATE_CONVERTER),
            *u8('bUnitID', self.bUnitID),
            *u8('bSourceID', self.bSourceID),
            *u8('bCSourceInID', self.bCSourceInID),
            *u8('bCSourceOutID', self.bCSourceOutID),
            *u8('iSRC', self.iSRC),
        ]


class ASGeneral(DescriptorNode):
    """UAC 2.0 Audio Streaming General descriptor. Links to an Output Terminal with 32-bit bmFormats."""

    def __init__(self, bTerminalLink, bFormatType=FORMAT_TYPE_I,
                 bmFormats=0x00000001, bNrChannels=2,
                 bmChannelConfig=CHANNEL_STEREO,
                 bmControls=0x00, iChannelNames=0, name=''):
        """Initialize an AS General descriptor.

        :param bTerminalLink: ID of the Output Terminal this streaming interface connects to.
        :param bFormatType: Audio format type (e.g. FORMAT_TYPE_I for PCM).
        :param bmFormats: Supported audio data formats (32-bit bitmap).
        :param bNrChannels: Number of physical channels in the audio data stream.
        :param bmChannelConfig: Spatial location of channels (32-bit bitmap).
        :param bmControls: Audio streaming controls (FM tuner mode, active alternate setting).
        :param iChannelNames: String descriptor index for channel names.
        :param name: Optional descriptor label.
        """
        super().__init__(name)
        self.bTerminalLink = bTerminalLink
        self.bFormatType = bFormatType
        self.bmFormats = bmFormats
        self.bNrChannels = bNrChannels
        self.bmChannelConfig = bmChannelConfig
        self.bmControls = bmControls
        self.iChannelNames = iChannelNames

    def _subfields(self):
        return [
            *u8('bDescriptorType', CS_INTERFACE),
            *u8('bDescriptorSubtype', ASSubtype.AS_GENERAL),
            *u8('bTerminalLink', self.bTerminalLink),
            *u8('bmControls', self.bmControls),
            *u8('bFormatType', self.bFormatType),
            *u32le('bmFormats', self.bmFormats),
            *u8('bNrChannels', self.bNrChannels),
            *u32le('bmChannelConfig', self.bmChannelConfig),
            *u8('iChannelNames', self.iChannelNames),
        ]


class FormatTypeI(DescriptorNode):
    """UAC 2.0 Type I Format descriptor. Specifies PCM audio format with bSubslotSize and bBitResolution."""

    def __init__(self, bSubslotSize=2, bBitResolution=16, name=''):
        """Initialize a Type I Format descriptor.

        :param bSubslotSize: Bytes per audio subslot (sample).
        :param bBitResolution: Bits per sample.
        :param name: Optional descriptor label.
        """
        super().__init__(name)
        self.bSubslotSize = bSubslotSize
        self.bBitResolution = bBitResolution

    def _subfields(self):
        return [
            *u8('bDescriptorType', CS_INTERFACE),
            *u8('bDescriptorSubtype', ASSubtype.FORMAT_TYPE),
            *u8('bFormatType', FORMAT_TYPE_I),
            *u8('bSubslotSize', self.bSubslotSize),
            *u8('bBitResolution', self.bBitResolution),
        ]


class _CodingUnit(DescriptorNode):
    """Internal base class for UAC 2.0 Encoder and Decoder descriptors.

    Handles variable-length extra data fields and multi-byte bmControls.
    """

    def __init__(self, subtype, uid_label, type_label, i_label,
                 unit_id, w_unit_type,
                 bmControls=None, i_string=0, extra_data=None, name=''):
        """Initialize a coding unit descriptor.

        :param subtype: Descriptor subtype (Encoder or Decoder).
        :param uid_label: Field name for the unit ID (bEncoderID or bDecoderID).
        :param type_label: Field name for the unit type (wEncoderType or wDecoderType).
        :param i_label: Field name for the string index (iEncoder or iDecoder).
        :param unit_id: Unique unit identifier.
        :param w_unit_type: Coding type identifier.
        :param bmControls: List of byte-sized control bitmaps.
        :param i_string: String descriptor index for this unit.
        :param extra_data: Optional list of extra field descriptors (tuples/lists).
        :param name: Optional descriptor label.
        """
        super().__init__(name)
        self._subtype = subtype
        self._uid_label = uid_label
        self._type_label = type_label
        self._i_label = i_label
        self.unit_id = unit_id
        self.w_unit_type = w_unit_type
        self.bmControls = bmControls or []
        self.i_string = i_string
        self.extra_data = extra_data or []

    def _subfields(self):
        fields = [
            *u8('bDescriptorType', CS_INTERFACE),
            *u8('bDescriptorSubtype', self._subtype),
            *u8(self._uid_label, self.unit_id),
            *u16le(self._type_label, self.w_unit_type),
        ]
        for item in self.extra_data:
            if isinstance(item, tuple) and len(item) == 2:
                fields.extend(u8(*item))
            elif isinstance(item, list) and len(item) == 3:
                name, value, size = item
                if size == 1:
                    fields.extend(u8(name, value))
                elif size == 2:
                    fields.extend(u16le(name, value))
                elif size == 4:
                    fields.extend(u32le(name, value))
        for ctrl in self.bmControls:
            fields.extend(u8('bmControls', ctrl))
        fields.extend(u8(self._i_label, self.i_string))
        return fields


class Encoder(_CodingUnit):
    """UAC 2.0 Encoder descriptor. Defines an audio encoding format."""

    def __init__(self, bEncoderID, wEncoderType,
                 bmControls=None, iEncoder=0, extra_data=None, name=''):
        """Initialize an Encoder descriptor.

        :param bEncoderID: Unique encoder identifier.
        :param wEncoderType: Encoder type identifier (e.g. MPEG, AC-3, WMA).
        :param bmControls: List of byte-sized encoder control bitmaps.
        :param iEncoder: String descriptor index for this encoder.
        :param extra_data: Optional list of extra encoder-specific fields.
        :param name: Optional descriptor label.
        """
        super().__init__(ASSubtype.ENCODER, 'bEncoderID', 'wEncoderType', 'iEncoder',
                         bEncoderID, wEncoderType,
                         bmControls, iEncoder, extra_data, name)


class Decoder(_CodingUnit):
    """UAC 2.0 Decoder descriptor. Defines an audio decoding format."""

    def __init__(self, bDecoderID, wDecoderType,
                 bmControls=None, iDecoder=0, extra_data=None, name=''):
        """Initialize a Decoder descriptor.

        :param bDecoderID: Unique decoder identifier.
        :param wDecoderType: Decoder type identifier (e.g. MPEG, AC-3, WMA).
        :param bmControls: List of byte-sized decoder control bitmaps.
        :param iDecoder: String descriptor index for this decoder.
        :param extra_data: Optional list of extra decoder-specific fields.
        :param name: Optional descriptor label.
        """
        super().__init__(ASSubtype.DECODER, 'bDecoderID', 'wDecoderType', 'iDecoder',
                         bDecoderID, wDecoderType,
                         bmControls, iDecoder, extra_data, name)


class ClassSpecificIsoEP(DescriptorNode):
    """UAC 2.0 Class-Specific Isochronous Endpoint descriptor. Includes bmControls."""

    def __init__(self, bmAttributes=0x00, bmControls=0x00,
                 bLockDelayUnits=0, wLockDelay=0, name=''):
        """Initialize a Class-Specific Isochronous Endpoint descriptor.

        :param bmAttributes: Bitmap of endpoint attributes (MaxPacketsOnly).
        :param bmControls: Lock delay control bitmap.
        :param bLockDelayUnits: Units for wLockDelay (0=undef, 1=ms, 2=PCM samples).
        :param wLockDelay: Time to lock internal clock recovery on this endpoint.
        :param name: Optional descriptor label.
        """
        super().__init__(name)
        self.bmAttributes = bmAttributes
        self.bmControls = bmControls
        self.bLockDelayUnits = bLockDelayUnits
        self.wLockDelay = wLockDelay

    def _subfields(self):
        return [
            *u8('bDescriptorType', CS_ENDPOINT),
            *u8('bDescriptorSubtype', EPSubtype.EP_GENERAL),
            *u8('bmAttributes', self.bmAttributes),
            *u8('bmControls', self.bmControls),
            *u8('bLockDelayUnits', self.bLockDelayUnits),
            *u16le('wLockDelay', self.wLockDelay),
        ]


class MSHeader(DescriptorNode):
    """UAC 2.0 MIDI Streaming Header descriptor."""

    def __init__(self, wTotalLength=0, bcdMSC=0x0100, name=''):
        """Initialize a MIDI Streaming Header descriptor.

        :param wTotalLength: Total length of all MIDI streaming class-specific descriptors (bytes).
        :param bcdMSC: MIDI Streaming specification release number in BCD (default: 1.0).
        :param name: Optional descriptor label.
        """
        super().__init__(name)
        self.wTotalLength = wTotalLength
        self.bcdMSC = bcdMSC

    def _subfields(self):
        return [
            *u8('bDescriptorType', CS_INTERFACE),
            *u8('bDescriptorSubtype', MIDISubtype.MS_HEADER),
            *u16le('bcdMSC', self.bcdMSC),
            *u16le('wTotalLength', self.wTotalLength),
        ]


class MIDIInJack(DescriptorNode):
    """MIDI Streaming Input Jack. Receives MIDI data from the host or external sources."""

    def __init__(self, bJackID, bJackType=0x01, baSourceID=None,
                 iJack=0, name=''):
        """Initialize a MIDI In Jack descriptor.

        :param bJackID: Unique jack identifier.
        :param bJackType: Jack type (0x01=Embedded, 0x02=External).
        :param baSourceID: List of associated source jack/pin IDs for external jacks.
        :param iJack: String descriptor index for this jack.
        :param name: Optional descriptor label.
        """
        super().__init__(name)
        self.bJackID = bJackID
        self.bJackType = bJackType
        self.baSourceID = baSourceID or []
        self.iJack = iJack

    def _subfields(self):
        fields = [
            *u8('bDescriptorType', CS_INTERFACE),
            *u8('bDescriptorSubtype', MIDISubtype.MIDI_IN_JACK),
            *u8('bJackType', self.bJackType),
            *u8('bJackID', self.bJackID),
        ]
        for src in self.baSourceID:
            fields.extend(u8('BaSourceID[]', src))
        for _ in self.baSourceID:
            fields.extend(u8('BaSourcePin[]', 1))
        fields.extend(u8('iJack', self.iJack))
        return fields


class MIDIOutJack(DescriptorNode):
    """MIDI Streaming Output Jack. Sends MIDI data to the host or external destinations."""

    def __init__(self, bJackID, bJackType=0x01, baSourceID=None,
                 iJack=0, name=''):
        """Initialize a MIDI Out Jack descriptor.

        :param bJackID: Unique jack identifier.
        :param bJackType: Jack type (0x01=Embedded, 0x02=External).
        :param baSourceID: List of associated source jack/pin IDs feeding this jack.
        :param iJack: String descriptor index for this jack.
        :param name: Optional descriptor label.
        """
        super().__init__(name)
        self.bJackID = bJackID
        self.bJackType = bJackType
        self.baSourceID = baSourceID or []
        self.iJack = iJack

    def _subfields(self):
        fields = [
            *u8('bDescriptorType', CS_INTERFACE),
            *u8('bDescriptorSubtype', MIDISubtype.MIDI_OUT_JACK),
            *u8('bJackType', self.bJackType),
            *u8('bJackID', self.bJackID),
            *u8('bNrInputPins', len(self.baSourceID)),
        ]
        for src in self.baSourceID:
            fields.extend(u8('BaSourceID[]', src))
        for _ in self.baSourceID:
            fields.extend(u8('BaSourcePin[]', 1))
        fields.extend(u8('iJack', self.iJack))
        return fields


class MIDIBulkEP(DescriptorNode):
    """Internal base class for MIDI Bulk Data Endpoint descriptors. References associated MIDI Jacks."""

    def __init__(self, baAssocJackID, subtype=0x01, name=''):
        """Initialize a MIDI Bulk Endpoint descriptor.

        :param baAssocJackID: List of associated MIDI jack IDs.
        :param subtype: Descriptor subtype (0x01 for MIDI Bulk Out/In endpoint).
        :param name: Optional descriptor label.
        """
        super().__init__(name)
        self.baAssocJackID = list(baAssocJackID)
        self._subtype = subtype

    def _subfields(self):
        fields = [
            *u8('bDescriptorType', CS_ENDPOINT),
            *u8('bDescriptorSubtype', self._subtype),
            *u8('bNumEmbMIDIJack', len(self.baAssocJackID)),
        ]
        for i, jid in enumerate(self.baAssocJackID):
            fields.extend(u8(f'BaAssocJackID[{i}]', jid))
        return fields


class MIDIOutBulkEP(MIDIBulkEP):
    """UAC 2.0 MIDI Bulk Out Endpoint descriptor. References associated MIDI Out Jacks."""

    def __init__(self, baAssocJackID, name=''):
        """Initialize a MIDI Bulk Out Endpoint descriptor.

        :param baAssocJackID: List of associated MIDI Out jack IDs.
        :param name: Optional descriptor label.
        """
        super().__init__(baAssocJackID, subtype=0x01, name=name)


class MIDIInBulkEP(MIDIBulkEP):
    """UAC 2.0 MIDI Bulk In Endpoint descriptor. References associated MIDI In Jacks."""

    def __init__(self, baAssocJackID, name=''):
        """Initialize a MIDI Bulk In Endpoint descriptor.

        :param baAssocJackID: List of associated MIDI In jack IDs.
        :param name: Optional descriptor label.
        """
        super().__init__(baAssocJackID, subtype=0x01, name=name)
