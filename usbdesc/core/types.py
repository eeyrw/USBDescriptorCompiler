"""USB specification constants — descriptor types, class codes, terminal types,
feature unit controls, format types, endpoint attributes, and name tables.

This module is the single source of truth for all USB constant values used
across the library. Constants are organized by USB spec section (Audio, HID,
CDC, MIDI, etc.) with human-readable name dictionaries for export and topology."""

from enum import IntEnum

# ────────────────────────────────────────────────────────────
# USB Base Descriptor Types
# ────────────────────────────────────────────────────────────

DESC_TYPE_DEVICE        = 0x01
DESC_TYPE_CONFIGURATION = 0x02
DESC_TYPE_STRING        = 0x03
DESC_TYPE_INTERFACE     = 0x04
DESC_TYPE_ENDPOINT      = 0x05
DESC_TYPE_DEVICE_QUAL   = 0x06
DESC_TYPE_OTHER_SPEED   = 0x07
DESC_TYPE_IAD           = 0x0B
DESC_TYPE_BOS           = 0x0F

CS_INTERFACE  = 0x24
CS_ENDPOINT   = 0x25

# ────────────────────────────────────────────────────────────
# USB Class Codes
# ────────────────────────────────────────────────────────────

CLASS_AUDIO    = 0x01
CLASS_CDC      = 0x02
CLASS_HID      = 0x03
CLASS_PHYSICAL = 0x05
CLASS_IMAGE    = 0x06
CLASS_PRINTER  = 0x07
CLASS_MASS_STORAGE = 0x08
CLASS_HUB      = 0x09
CLASS_CDC_DATA = 0x0A
CLASS_SMART_CARD = 0x0B
CLASS_VIDEO    = 0x0E
CLASS_WIRELESS = 0xE0
CLASS_MISC     = 0xEF
CLASS_VENDOR   = 0xFF

MISC_SUBCLASS_COMMON = 0x02
MISC_PROTOCOL_IAD    = 0x01

# ────────────────────────────────────────────────────────────
# Audio Interface Subclass & Protocol
# ────────────────────────────────────────────────────────────

AUDIO_SUBCLASS_UNDEFINED = 0x00
AUDIO_SUBCLASS_CONTROL   = 0x01
AUDIO_SUBCLASS_STREAMING = 0x02
AUDIO_SUBCLASS_MIDI      = 0x03

AUDIO_PROTOCOL_UNDEFINED = 0x00
AUDIO_PROTOCOL_V1        = 0x00
AUDIO_PROTOCOL_V2        = 0x20

# ────────────────────────────────────────────────────────────
# UAC version BCDs
# ────────────────────────────────────────────────────────────

UAC1_BCD = 0x0100
UAC2_BCD = 0x0200

# ────────────────────────────────────────────────────────────
# Audio Control Interface Descriptor Subtypes
# ────────────────────────────────────────────────────────────

class ACSubtype(IntEnum):
    HEADER              = 0x01
    INPUT_TERMINAL      = 0x02
    OUTPUT_TERMINAL     = 0x03
    MIXER_UNIT          = 0x04
    SELECTOR_UNIT       = 0x05
    FEATURE_UNIT        = 0x06
    EFFECT_UNIT         = 0x07  # UAC2; was PROCESSING_UNIT in UAC1
    PROCESSING_UNIT     = 0x08  # UAC2; was 0x07 in UAC1, EXTENSION_UNIT in UAC1
    EXTENSION_UNIT      = 0x09  # UAC2; was 0x08 in UAC1
    CLOCK_SOURCE        = 0x0A  # UAC2 only
    CLOCK_SELECTOR      = 0x0B  # UAC2 only
    CLOCK_MULTIPLIER    = 0x0C  # UAC2 only
    SAMPLE_RATE_CONVERTER = 0x0D  # UAC2 only

# Audio Streaming Interface Descriptor Subtypes
class ASSubtype(IntEnum):
    AS_GENERAL   = 0x01
    FORMAT_TYPE  = 0x02
    ENCODER      = 0x03  # UAC2 only
    DECODER      = 0x04  # UAC2 only

# CS Endpoint Descriptor Subtypes
class EPSubtype(IntEnum):
    EP_GENERAL = 0x01

# MIDI Streaming Subtypes
class MIDISubtype(IntEnum):
    MS_HEADER          = 0x01
    MIDI_IN_JACK       = 0x02
    MIDI_OUT_JACK      = 0x03
    ELEMENT            = 0x04

# ────────────────────────────────────────────────────────────
# Terminal Types
# ────────────────────────────────────────────────────────────

# USB Terminal Types
TERM_USB_UNDEFINED   = 0x0100
TERM_USB_STREAMING   = 0x0101
TERM_USB_VENDOR_SPEC = 0x01FF

# Input Terminal Types
TERM_MICROPHONE             = 0x0201
TERM_DESKTOP_MICROPHONE     = 0x0202
TERM_PERSONAL_MICROPHONE    = 0x0203
TERM_OMNI_DIR_MICROPHONE    = 0x0204
TERM_MICROPHONE_ARRAY       = 0x0205
TERM_PROCESSING_MIC_ARRAY   = 0x0206

# Output Terminal Types
TERM_SPEAKER                = 0x0301
TERM_HEADPHONES             = 0x0302
TERM_HEAD_MOUNTED_DISPLAY   = 0x0303
TERM_DESKTOP_SPEAKER        = 0x0304
TERM_ROOM_SPEAKER           = 0x0305
TERM_COMMUNICATION_SPEAKER  = 0x0306
TERM_LOW_FREQ_EFFECTS       = 0x0307

# Bidirectional Terminal Types
TERM_HANDSET             = 0x0401
TERM_HEADSET             = 0x0402
TERM_SPEAKERPHONE        = 0x0403
TERM_ECHO_SUPPRESSING    = 0x0404
TERM_ECHO_CANCELING      = 0x0405

# Telephony Terminal Types
TERM_PHONE_LINE     = 0x0501
TERM_TELEPHONE      = 0x0502
TERM_DOWN_LINE_PHONE = 0x0503

# External Terminal Types
TERM_ANALOG_CONNECTOR     = 0x0601
TERM_DIGITAL_AUDIO_IFACE  = 0x0602
TERM_LINE_CONNECTOR       = 0x0603
TERM_LEGACY_AUDIO_CONN    = 0x0604
TERM_SPDIF_INTERFACE      = 0x0605
TERM_1394_DA_INTERFACE    = 0x0606
TERM_1394_DV_INTERFACE    = 0x0607

# Embedded Function Terminal Types
TERM_EMBEDDED_FUNC_BASE   = 0x0700
TERM_EMBEDDED_FUNC_RANGE  = 0x07FF

TERMINAL_TYPE_NAMES = {
    TERM_USB_STREAMING: 'USB Streaming',
    TERM_SPEAKER: 'Speaker',
    TERM_HEADPHONES: 'Headphones',
    TERM_MICROPHONE: 'Microphone',
    TERM_LINE_CONNECTOR: 'Line',
    TERM_ANALOG_CONNECTOR: 'Analog',
    TERM_SPDIF_INTERFACE: 'S/PDIF',
}

# ────────────────────────────────────────────────────────────
# UAC2 Audio Function Categories (bCategory)
# ────────────────────────────────────────────────────────────

FUNCTION_OTHER             = 0x00
FUNCTION_DESKTOP_SPEAKER   = 0x01
FUNCTION_HOME_THEATER      = 0x02
FUNCTION_MICROPHONE        = 0x03
FUNCTION_HEADSET           = 0x04
FUNCTION_TELEPHONE         = 0x05
FUNCTION_CONVERTER         = 0x06
FUNCTION_VOICE_RECORDER    = 0x07
FUNCTION_IO_BOX            = 0x08
FUNCTION_MUSICAL_INSTRUMENT = 0x09
FUNCTION_PRO_AUDIO         = 0x0A
FUNCTION_AUDIO_VIDEO       = 0x0B
FUNCTION_CONTROL_PANEL     = 0x0C
FUNCTION_HEADPHONE         = 0x0D
FUNCTION_GENERIC_SPEAKER   = 0x0E
FUNCTION_HEADSET_ADAPTER   = 0x0F
FUNCTION_SPEAKERPHONE      = 0x10
FUNCTION_OTHER_FF          = 0xFF

# ────────────────────────────────────────────────────────────
# Clock Source Attributes (bmAttributes)
# ────────────────────────────────────────────────────────────

CLOCK_EXTERNAL       = 0x00
CLOCK_INT_FIXED      = 0x01
CLOCK_INT_VARIABLE   = 0x02
CLOCK_INT_PROGRAMMABLE = 0x03
CLOCK_SOF_SYNCHRONOUS = 0x04

# ────────────────────────────────────────────────────────────
# Format Types
# ────────────────────────────────────────────────────────────

FORMAT_TYPE_I   = 0x01
FORMAT_TYPE_II  = 0x02
FORMAT_TYPE_III = 0x03
FORMAT_TYPE_IV  = 0x04

FORMAT_EXT_TYPE_I   = 0x81
FORMAT_EXT_TYPE_II  = 0x82
FORMAT_EXT_TYPE_III = 0x83

# bmFormats bitmask (UAC2)
BM_FORMAT_PCM          = 1 << 0
BM_FORMAT_PCM8         = 1 << 1
BM_FORMAT_IEEE_FLOAT   = 1 << 2
BM_FORMAT_ALAW         = 1 << 3
BM_FORMAT_MULAW        = 1 << 4
BM_FORMAT_RAW          = 1 << 5  # UAC2
BM_FORMAT_TYPE_II      = 1 << 6  # UAC2
BM_FORMAT_TYPE_III     = 1 << 7  # UAC2
BM_FORMAT_TYPE_IV      = 1 << 8  # UAC2

# ────────────────────────────────────────────────────────────
# Channel Configuration (bmChannelConfig / wChannelConfig)
# ────────────────────────────────────────────────────────────

CHANNEL_FRONT_LEFT          = 1 << 0
CHANNEL_FRONT_RIGHT         = 1 << 1
CHANNEL_FRONT_CENTER        = 1 << 2
CHANNEL_LOW_FREQ            = 1 << 3
CHANNEL_BACK_LEFT           = 1 << 4
CHANNEL_BACK_RIGHT          = 1 << 5
CHANNEL_FRONT_LEFT_CENTER   = 1 << 6
CHANNEL_FRONT_RIGHT_CENTER  = 1 << 7
CHANNEL_BACK_CENTER         = 1 << 8
CHANNEL_SIDE_LEFT           = 1 << 9
CHANNEL_SIDE_RIGHT          = 1 << 10
CHANNEL_TOP_CENTER          = 1 << 11
CHANNEL_TOP_FRONT_LEFT      = 1 << 12
CHANNEL_TOP_FRONT_CENTER    = 1 << 13
CHANNEL_TOP_FRONT_RIGHT     = 1 << 14
CHANNEL_TOP_BACK_LEFT       = 1 << 15
CHANNEL_TOP_BACK_CENTER     = 1 << 16
CHANNEL_TOP_BACK_RIGHT      = 1 << 17

CHANNEL_MONO  = CHANNEL_FRONT_LEFT
CHANNEL_STEREO = CHANNEL_FRONT_LEFT | CHANNEL_FRONT_RIGHT

# ────────────────────────────────────────────────────────────
# Feature Unit Controls
# ────────────────────────────────────────────────────────────

# UAC1 control bits (single-bit per control)
UAC1_FU_MUTE       = 0x0001
UAC1_FU_VOLUME     = 0x0002
UAC1_FU_BASS       = 0x0004
UAC1_FU_MID        = 0x0008
UAC1_FU_TREBLE     = 0x0010
UAC1_FU_GRAPHIC_EQ = 0x0020
UAC1_FU_AGC        = 0x0040
UAC1_FU_DELAY      = 0x0080
UAC1_FU_BASS_BOOST = 0x0100
UAC1_FU_LOUDNESS   = 0x0200

# UAC2 control encoding helpers (2-bit per control)
CTRL_NONE = 0x00
CTRL_READ = 0x01
CTRL_RW   = 0x03

# UAC2 control bit offsets (2-bit fields at each offset)
UAC2_FU_MUTE        = 0
UAC2_FU_VOLUME      = 2
UAC2_FU_BASS        = 4
UAC2_FU_MID         = 6
UAC2_FU_TREBLE      = 8
UAC2_FU_GRAPHIC_EQ  = 10
UAC2_FU_AGC         = 12
UAC2_FU_DELAY       = 14
UAC2_FU_BASS_BOOST  = 16
UAC2_FU_LOUDNESS    = 18
UAC2_FU_INPUT_GAIN  = 20
UAC2_FU_GAIN_PAD    = 22
UAC2_FU_PHASE_INVERT = 24
UAC2_FU_UNDERFLOW   = 26
UAC2_FU_OVERFLOW    = 28
UAC2_FU_HIGH_PASS   = 30

# ────────────────────────────────────────────────────────────
# Processing Unit Types
# ────────────────────────────────────────────────────────────

PROCESS_UNDEFINED       = 0x00
PROCESS_UP_DOWN_MIX     = 0x01
PROCESS_DOLBY_PROLOGIC  = 0x02
PROCESS_STEREO_EXTENDER = 0x03
PROCESS_REVERBERATION   = 0x04
PROCESS_CHORUS          = 0x05
PROCESS_DYN_RANGE_COMP  = 0x06

# ────────────────────────────────────────────────────────────
# Effect Unit Types (UAC2 only)
# ────────────────────────────────────────────────────────────

EFFECT_UNDEFINED          = 0x00
EFFECT_PARAM_EQ_SECTION   = 0x01
EFFECT_REVERBERATION      = 0x02
EFFECT_MOD_DELAY          = 0x03
EFFECT_DYN_RANGE_COMP     = 0x04

# ────────────────────────────────────────────────────────────
# Endpoint Attributes
# ────────────────────────────────────────────────────────────

EP_ATTR_CONTROL           = 0x00
EP_ATTR_ISOCHRONOUS       = 0x01
EP_ATTR_BULK              = 0x02
EP_ATTR_INTERRUPT         = 0x03

EP_ISO_SYNC_NONE          = 0x00
EP_ISO_SYNC_ASYNC         = 0x04
EP_ISO_SYNC_ADAPTIVE      = 0x08
EP_ISO_SYNC_SYNC          = 0x0C

EP_USAGE_DATA             = 0x00
EP_USAGE_FEEDBACK         = 0x10
EP_USAGE_IMPLICIT_FB      = 0x20

EP_MAX_PACKETS_ONLY       = 0x80

# ────────────────────────────────────────────────────────────
# Audio Control Requests
# ────────────────────────────────────────────────────────────

REQ_SET_CUR  = 0x01
REQ_GET_CUR  = 0x81
REQ_SET_MIN  = 0x02
REQ_GET_MIN  = 0x82
REQ_SET_MAX  = 0x03
REQ_GET_MAX  = 0x83
REQ_SET_RES  = 0x04
REQ_GET_RES  = 0x84
REQ_SET_MEM  = 0x05
REQ_GET_MEM  = 0x85

# UAC2 Range request (replaces MIN/MAX)
REQ_GET_RANGE = 0x82

# Audio Control Selectors
AC_CS_CONTROL_UNDEF    = 0x00
AC_CS_CONTROL_IF       = 0x01  # Entire interface
AC_CS_CONTROL_ENDPOINT = 0x02  # Entire endpoint

# ────────────────────────────────────────────────────────────
# MIDI Streaming Constants
# ────────────────────────────────────────────────────────────

MIDI_JACK_EMBEDDED = 0x01
MIDI_JACK_EXTERNAL = 0x02

MIDI_JACK_IN  = 'IN'
MIDI_JACK_OUT = 'OUT'

# ────────────────────────────────────────────────────────────
# HID Constants
# ────────────────────────────────────────────────────────────

HID_SUBCLASS_NONE  = 0x00
HID_SUBCLASS_BOOT  = 0x01

HID_PROTOCOL_NONE      = 0x00
HID_PROTOCOL_KEYBOARD  = 0x01
HID_PROTOCOL_MOUSE     = 0x02

HID_DESC_TYPE_HID      = 0x21
HID_DESC_TYPE_REPORT   = 0x22
HID_DESC_TYPE_PHYSICAL = 0x23

HID_BCD = 0x0111

HID_COUNTRY_NONE        = 0x00
HID_COUNTRY_US          = 0x21
HID_COUNTRY_CN          = 0x2D

# ────────────────────────────────────────────────────────────
# CDC Constants
# ────────────────────────────────────────────────────────────

CDC_DESC_TYPE_CS_INTERFACE = 0x24
CDC_DESC_TYPE_CS_ENDPOINT  = 0x25

class CDCSubtype(IntEnum):
    HEADER            = 0x00
    CALL_MANAGEMENT   = 0x01
    ABSTRACT_CONTROL  = 0x02
    DIRECT_LINE       = 0x03
    TELEPHONE_RINGER  = 0x04
    TELEPHONE_CALL    = 0x05
    UNION             = 0x06
    COUNTRY_SELECTION = 0x07
    TELEPHONE_OP_MODES = 0x08
    USB_TERMINAL      = 0x09
    NETWORK_CHANNEL   = 0x0A
    PROTOCOL_UNIT     = 0x0B
    EXTENSION_UNIT    = 0x0C
    MULTI_CHANNEL     = 0x0D
    CAPI_CONTROL      = 0x0E
    ETHERNET_NETWORKING = 0x0F
    ATM_NETWORKING    = 0x10
    WIRELESS_HANDSET  = 0x11
    MOBILE_DIRECT_LINE = 0x12
    MDLM_DETAIL       = 0x13
    DEVICE_MANAGEMENT = 0x14
    OBEX              = 0x15
    COMMAND_SET       = 0x16
    COMMAND_SET_DETAIL = 0x17
    TELEPHONE_CONTROL = 0x18
    OBEX_SERVICE      = 0x19
    NCM               = 0x1A

CDC_DATA_CLASS = 0x0A

# ────────────────────────────────────────────────────────────
# Configuration Attributes
# ────────────────────────────────────────────────────────────

CONFIG_ATTR_REMOTE_WAKEUP = 0x20
CONFIG_ATTR_SELF_POWERED  = 0x40
CONFIG_ATTR_BUS_POWERED   = 0x80

# ────────────────────────────────────────────────────────────
#  Reverse-lookup dicts — single source of truth for all
#  value→name mappings used by exporters, topology, etc.
# ────────────────────────────────────────────────────────────

DESC_TYPE_NAMES = {
    DESC_TYPE_DEVICE: 'DEVICE',
    DESC_TYPE_CONFIGURATION: 'CONFIGURATION',
    DESC_TYPE_STRING: 'STRING',
    DESC_TYPE_INTERFACE: 'INTERFACE',
    DESC_TYPE_ENDPOINT: 'ENDPOINT',
    DESC_TYPE_DEVICE_QUAL: 'DEVICE_QUALIFIER',
    DESC_TYPE_OTHER_SPEED: 'OTHER_SPEED_CONFIG',
    DESC_TYPE_IAD: 'IAD',
    DESC_TYPE_BOS: 'BOS',
    HID_DESC_TYPE_HID: 'HID',
    HID_DESC_TYPE_REPORT: 'REPORT',
    HID_DESC_TYPE_PHYSICAL: 'PHYSICAL',
    CS_INTERFACE: 'CS_INTERFACE',
    CS_ENDPOINT: 'CS_ENDPOINT',
}

CLASS_NAMES = {
    0x00: 'per-iface',
    CLASS_AUDIO: 'Audio',
    CLASS_CDC: 'CDC',
    CLASS_HID: 'HID',
    CLASS_MASS_STORAGE: 'MSC',
    CLASS_CDC_DATA: 'CDC-Data',
    CLASS_VIDEO: 'Video',
    CLASS_MISC: 'Misc',
    CLASS_VENDOR: 'Vendor',
}

ENDPOINT_ATTR_NAMES = {
    EP_ATTR_CONTROL: 'Control',
    EP_ATTR_ISOCHRONOUS: 'Iso',
    EP_ATTR_BULK: 'Bulk',
    EP_ATTR_INTERRUPT: 'Intr',
}

AC_SUBTYPE_NAMES = {m.value: m.name for m in ACSubtype}
AS_SUBTYPE_NAMES = {m.value: m.name for m in ASSubtype}
MIDI_SUBTYPE_NAMES = {m.value: m.name for m in MIDISubtype}
CDC_SUBTYPE_NAMES = {m.value: m.name for m in CDCSubtype}

AUDIO_CATEGORY_NAMES = {
    FUNCTION_OTHER: 'Other',
    FUNCTION_DESKTOP_SPEAKER: 'DesktopSpeaker',
    FUNCTION_HOME_THEATER: 'HomeTheater',
    FUNCTION_MICROPHONE: 'Microphone',
    FUNCTION_HEADSET: 'Headset',
    FUNCTION_TELEPHONE: 'Telephone',
    FUNCTION_CONVERTER: 'Converter',
    FUNCTION_VOICE_RECORDER: 'VoiceRecorder',
    FUNCTION_IO_BOX: 'IOBox',
    FUNCTION_MUSICAL_INSTRUMENT: 'MusicalInstrument',
    FUNCTION_PRO_AUDIO: 'ProAudio',
    FUNCTION_AUDIO_VIDEO: 'AudioVideo',
    FUNCTION_CONTROL_PANEL: 'ControlPanel',
    FUNCTION_HEADPHONE: 'Headphone',
    FUNCTION_GENERIC_SPEAKER: 'GenericSpeaker',
    FUNCTION_HEADSET_ADAPTER: 'HeadsetAdapter',
    FUNCTION_SPEAKERPHONE: 'Speakerphone',
}

PROCESS_TYPE_NAMES = {
    PROCESS_UNDEFINED: 'Undefined',
    PROCESS_UP_DOWN_MIX: 'UpDownMix',
    PROCESS_DOLBY_PROLOGIC: 'DolbyPrologic',
    PROCESS_STEREO_EXTENDER: 'StereoExtender',
    PROCESS_REVERBERATION: 'Reverberation',
    PROCESS_CHORUS: 'Chorus',
    PROCESS_DYN_RANGE_COMP: 'DynRangeComp',
}

EFFECT_TYPE_NAMES = {
    EFFECT_UNDEFINED: 'Undefined',
    EFFECT_PARAM_EQ_SECTION: 'ParametricEQ',
    EFFECT_REVERBERATION: 'Reverberation',
    EFFECT_MOD_DELAY: 'ModDelay',
    EFFECT_DYN_RANGE_COMP: 'DynRangeComp',
}

CLOCK_TYPE_NAMES = {
    CLOCK_EXTERNAL: 'External',
    CLOCK_INT_FIXED: 'Fixed',
    CLOCK_INT_VARIABLE: 'Variable',
    CLOCK_INT_PROGRAMMABLE: 'Programmable',
}

TERMINAL_TYPE_LOOKUP = {
    TERM_USB_UNDEFINED: 'USB Undefined',
    TERM_USB_STREAMING: 'USB Streaming',
    TERM_USB_VENDOR_SPEC: 'USB Vendor',
    TERM_MICROPHONE: 'Microphone',
    TERM_SPEAKER: 'Speaker',
    TERM_HEADPHONES: 'Headphones',
    TERM_HEADSET: 'Headset',
    TERM_LINE_CONNECTOR: 'Line',
    TERM_ANALOG_CONNECTOR: 'Analog',
    TERM_SPDIF_INTERFACE: 'S/PDIF',
}
