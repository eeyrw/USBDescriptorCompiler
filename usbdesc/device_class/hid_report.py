"""HID Report Descriptor builder — programmatic construction of HID reports.

Usage:
    from usbdesc.device_class.hid_report import HIDReport

    report = HIDReport()
    report.usage_page(USAGE_PAGE.GENERIC_DESKTOP) \
          .usage(USAGES.GENERIC_DESKTOP.KEYBOARD) \
          .collection(COLL.APPLICATION) \
          .usage_page(USAGE_PAGE.KEYBOARD) \
          .usage_min(0xE0).usage_max(0xE7) \
          .logical_min(0).logical_max(1) \
          .report_size(1).report_count(8) \
          .input(IO.DATA | IO.VARIABLE | IO.ABSOLUTE) \
          .report_count(1).report_size(8) \
          .input(IO.CONSTANT | IO.VARIABLE | IO.ABSOLUTE) \
          .end_collection()
    raw = report.encode()  # bytes object ready for HIDDescriptor
"""

from enum import IntEnum


class USAGE_PAGE(IntEnum):
    GENERIC_DESKTOP = 0x01
    SIMULATION = 0x02
    VR = 0x03
    SPORT = 0x04
    GAME = 0x05
    GENERIC_DEVICE = 0x06
    KEYBOARD = 0x07
    LED = 0x08
    BUTTON = 0x09
    ORDINAL = 0x0A
    TELEPHONY = 0x0B
    CONSUMER = 0x0C
    DIGITIZER = 0x0D
    PID = 0x0F
    UNICODE = 0x10
    ALPHANUMERIC = 0x14
    MEDICAL = 0x40
    MONITOR = 0x80
    POWER = 0x84
    BARCODE = 0x8C
    SCALE = 0x8D
    CAMERA = 0x90
    ARCADE = 0x91
    VENDOR_MIN = 0xFF00
    VENDOR_MAX = 0xFFFF


class _GenericDesktop(IntEnum):
    POINTER = 0x01
    MOUSE = 0x02
    JOYSTICK = 0x04
    GAMEPAD = 0x05
    KEYBOARD = 0x06
    KEYPAD = 0x07
    MULTI_AXIS = 0x08
    TABLET = 0x09
    X = 0x30
    Y = 0x31
    Z = 0x32
    RX = 0x33
    RY = 0x34
    RZ = 0x35
    SLIDER = 0x36
    DIAL = 0x37
    WHEEL = 0x38
    HAT_SWITCH = 0x39
    COUNTED_BUFFER = 0x3A
    BYTE_COUNT = 0x3B
    MOTION_WAKEUP = 0x3C
    START = 0x3D
    SELECT = 0x3E
    VX = 0x40
    VY = 0x41
    VZ = 0x42
    VBRX = 0x43
    VBRY = 0x44
    VBRZ = 0x45
    VNO = 0x46
    FEATURE_NOTIFICATION = 0x47
    RESOLUTION_MULTIPLIER = 0x48
    SYSTEM_CONTROL = 0x80
    SYSTEM_POWER_DOWN = 0x81
    SYSTEM_SLEEP = 0x82
    SYSTEM_WAKE_UP = 0x83
    SYSTEM_CONTEXT_MENU = 0x84
    SYSTEM_MAIN_MENU = 0x85
    SYSTEM_APP_MENU = 0x86
    SYSTEM_MENU_HELP = 0x87
    SYSTEM_MENU_EXIT = 0x88
    SYSTEM_MENU_SELECT = 0x89
    SYSTEM_MENU_RIGHT = 0x8A
    SYSTEM_MENU_LEFT = 0x8B
    SYSTEM_MENU_UP = 0x8C
    SYSTEM_MENU_DOWN = 0x8D
    SYSTEM_COLD_RESTART = 0x8E
    SYSTEM_WARM_RESTART = 0x8F
    DPAD_UP = 0x90
    DPAD_DOWN = 0x91
    DPAD_RIGHT = 0x92
    DPAD_LEFT = 0x93
    SYSTEM_DOCK = 0xA0
    SYSTEM_UNDOCK = 0xA1
    SYSTEM_SETUP = 0xA2
    SYSTEM_BREAK = 0xA3
    SYSTEM_DEBUGGER_BREAK = 0xA4
    APPLICATION_BREAK = 0xA5
    APPLICATION_DEBUGGER_BREAK = 0xA6
    SYSTEM_SPEAKER_MUTE = 0xA7
    SYSTEM_HIBERNATE = 0xA8
    SYSTEM_DISPLAY_INVERT = 0xB0
    SYSTEM_DISPLAY_INTERNAL = 0xB1
    SYSTEM_DISPLAY_EXTERNAL = 0xB2
    SYSTEM_DISPLAY_BOTH = 0xB3
    SYSTEM_DISPLAY_DUAL = 0xB4
    SYSTEM_DISPLAY_TOGGLE = 0xB5
    SYSTEM_DISPLAY_SWAP = 0xB6
    SYSTEM_DISPLAY_LCD_AUTOSCALE = 0xB7


class _LED(IntEnum):
    NUM_LOCK = 0x01
    CAPS_LOCK = 0x02
    SCROLL_LOCK = 0x03
    COMPOSE = 0x04
    KANA = 0x05
    POWER = 0x06
    SHIFT = 0x07
    DO_NOT_DISTURB = 0x08
    MUTE = 0x09
    TONE_ENABLE = 0x0A
    HIGH_CUT_FILTER = 0x0B
    LOW_CUT_FILTER = 0x0C
    EQUALIZER_ENABLE = 0x0D
    SOUND_FIELD_ON = 0x0E
    SURROUND_ON = 0x0F
    REPEAT = 0x10
    STEREO = 0x11
    SAMPLING_RATE_DETECT = 0x12
    SPINNING = 0x13
    CAV = 0x14
    CLV = 0x15
    RECORDING_FORMAT_DETECT = 0x16
    OFF_HOOK = 0x17
    RING = 0x18
    MESSAGE_WAITING = 0x19
    DATA_MODE = 0x1A
    BATTERY_OPERATION = 0x1B
    BATTERY_OK = 0x1C
    BATTERY_LOW = 0x1D
    SPEAKER = 0x1E
    HEAD_SET = 0x1F
    HOLD = 0x20
    MICROPHONE = 0x21
    COVERAGE = 0x22
    NIGHT_MODE = 0x23
    SEND_CALLS = 0x24
    CALL_PICKUP = 0x25
    CONFERENCE = 0x26
    STAND_BY = 0x27
    CAMERA_ON = 0x28
    CAMERA_OFF = 0x29
    ON_LINE = 0x2A
    OFF_LINE = 0x2B
    BUSY = 0x2C
    READY = 0x2D
    PAPER_OUT = 0x2E
    PAPER_JAM = 0x2F
    REMOTE = 0x30
    FORWARD = 0x31
    REVERSE = 0x32
    STOP = 0x33
    REWIND = 0x34
    FAST_FORWARD = 0x35
    PLAY = 0x36
    PAUSE = 0x37
    RECORD = 0x38
    ERROR = 0x39
    USAGE_SELECTED_INDICATOR = 0x3A
    USAGE_IN_USE_INDICATOR = 0x3B
    MULTI_MODE_INDICATOR = 0x3C
    INDICATOR_ON = 0x3D
    INDICATOR_FLASH = 0x3E
    INDICATOR_SLOW_BLINK = 0x3F
    INDICATOR_FAST_BLINK = 0x40
    INDICATOR_OFF = 0x41
    FLASH_ON_TIME = 0x42
    SLOW_BLINK_ON_TIME = 0x43
    SLOW_BLINK_OFF_TIME = 0x44
    FAST_BLINK_ON_TIME = 0x45
    FAST_BLINK_OFF_TIME = 0x46
    USAGE_INDICATOR_COLOR = 0x47
    INDICATOR_RED = 0x48
    INDICATOR_GREEN = 0x49
    INDICATOR_AMBER = 0x4A
    GENERIC_INDICATOR = 0x4B
    SYSTEM_SUSPEND = 0x4C
    EXTERNAL_POWER = 0x4D


class _Consumer(IntEnum):
    CONSUMER_CONTROL = 0x01
    NUMERIC_KEY_PAD = 0x02
    PROGRAMMABLE_BUTTONS = 0x03
    MICROPHONE = 0x04
    HEADPHONE = 0x05
    GRAPHIC_EQUALIZER = 0x06
    PLAY = 0xB0
    PAUSE = 0xB1
    RECORD = 0xB2
    FAST_FORWARD = 0xB3
    REWIND = 0xB4
    SCAN_NEXT_TRACK = 0xB5
    SCAN_PREVIOUS_TRACK = 0xB6
    STOP = 0xB7
    EJECT = 0xB8
    RANDOM_PLAY = 0xB9
    SELECT_DISC = 0xBA
    ENTER_DISC = 0xBB
    REPEAT = 0xBC
    TRACKING = 0xBD
    TRACK_NORMAL = 0xBE
    SLOW_TRACKING = 0xBF
    FRAME_FORWARD = 0xC0
    FRAME_BACK = 0xC1
    MARK = 0xC2
    CLEAR_MARK = 0xC3
    REPEAT_FROM_MARK = 0xC4
    RETURN_TO_MARK = 0xC5
    SEARCH_MARK_FORWARD = 0xC6
    SEARCH_MARK_BACKWARDS = 0xC7
    COUNTER_RESET = 0xC8
    SHOW_COUNTER = 0xC9
    TRACKING_INCREMENT = 0xCA
    TRACKING_DECREMENT = 0xCB
    STOP_EJECT = 0xCC
    PLAY_PAUSE = 0xCD
    PLAY_SKIP = 0xCE
    VOLUME = 0xE0
    BALANCE = 0xE1
    MUTE = 0xE2
    BASS = 0xE3
    TREBLE = 0xE4
    BASS_BOOST = 0xE5
    SURROUND_MODE = 0xE6
    LOUDNESS = 0xE7
    MPX = 0xE8
    VOLUME_INCREMENT = 0xE9
    VOLUME_DECREMENT = 0xEA
    SPEED_SELECT = 0xF0
    PLAYBACK_SPEED = 0xF1
    STANDARD_PLAY = 0xF2
    LONG_PLAY = 0xF3
    EXTENDED_PLAY = 0xF4
    SLOW = 0xF5
    FAN_ENABLE = 0x100
    FAN_SPEED = 0x101
    LIGHT_ENABLE = 0x102
    LIGHT_ILLUMINANCE_LEVEL = 0x103
    CLIMATE_CONTROL_ENABLE = 0x104
    ROOM_TEMPERATURE = 0x105
    SECURITY_ENABLE = 0x106
    FIRE_ALARM = 0x107
    POLICE_ALARM = 0x108
    PROXIMITY = 0x109
    MOTION = 0x10A
    DURESS_ALARM = 0x10B
    HOLDUP_ALARM = 0x10C
    MEDICAL_ALARM = 0x10D
    AC_SEARCH = 0x201
    AC_GOTO = 0x202
    AC_HOME = 0x203
    AC_BACK = 0x204
    AC_FORWARD = 0x205
    AC_STOP = 0x206
    AC_REFRESH = 0x207
    AC_PREVIOUS = 0x208


USAGES = type('USAGES', (), {
    'GENERIC_DESKTOP': _GenericDesktop,
    'LED': _LED,
    'CONSUMER': _Consumer,
})()


class COLL(IntEnum):
    PHYSICAL = 0x00
    APPLICATION = 0x01
    LOGICAL = 0x02
    REPORT = 0x03
    NAMED_ARRAY = 0x04
    USAGE_SWITCH = 0x05
    MODIFIER = 0x06


class IO(IntEnum):
    DATA = 0x00
    CONSTANT = 0x01
    ARRAY = 0x00
    VARIABLE = 0x02
    ABSOLUTE = 0x00
    RELATIVE = 0x04
    NO_WRAP = 0x00
    WRAP = 0x08
    LINEAR = 0x00
    NON_LINEAR = 0x10
    PREFERRED_STATE = 0x00
    NO_PREFERRED = 0x20
    NULL_STATE = 0x40
    NO_NULL = 0x00
    VOLATILE = 0x80
    NON_VOLATILE = 0x00
    BUFFERED = 0x100



_ITEM_TYPE_MAIN = 0
_ITEM_TYPE_GLOBAL = 1
_ITEM_TYPE_LOCAL = 2

_TAGS = {
    'MAIN_INPUT': 8, 'MAIN_OUTPUT': 9, 'MAIN_FEATURE': 11,
    'MAIN_COLLECTION': 10, 'MAIN_END_COLLECTION': 12,
    'GLOBAL_USAGE_PAGE': 0, 'GLOBAL_LOGICAL_MIN': 1,
    'GLOBAL_LOGICAL_MAX': 2, 'GLOBAL_PHYSICAL_MIN': 3,
    'GLOBAL_PHYSICAL_MAX': 4, 'GLOBAL_UNIT_EXPONENT': 5,
    'GLOBAL_UNIT': 6, 'GLOBAL_REPORT_SIZE': 7,
    'GLOBAL_REPORT_ID': 8, 'GLOBAL_REPORT_COUNT': 9,
    'GLOBAL_PUSH': 10, 'GLOBAL_POP': 11,
    'LOCAL_USAGE': 0, 'LOCAL_USAGE_MIN': 1, 'LOCAL_USAGE_MAX': 2,
    'LOCAL_DESIGNATOR_INDEX': 3, 'LOCAL_DESIGNATOR_MIN': 4,
    'LOCAL_DESIGNATOR_MAX': 5, 'LOCAL_STRING_INDEX': 7,
    'LOCAL_STRING_MIN': 8, 'LOCAL_STRING_MAX': 9,
    'LOCAL_DELIMITER': 10,
}


def _encode_item(item_type, tag, data=None):
    """Encode a single HID report item to bytes.

    Size is auto-detected: 0 (no data), 1 (fits in 1 byte),
    2 (fits in 2 bytes), or 3 (4 bytes).
    Negative values are stored as two's complement.
    """
    if data is None:
        size = 0
        val = 0
    elif data < 0:
        neg = -data
        if neg <= 0x80:
            size, val = 1, (0x100 + data) & 0xFF
        elif neg <= 0x8000:
            size, val = 2, (0x10000 + data) & 0xFFFF
        else:
            size, val = 3, (0x100000000 + data) & 0xFFFFFFFF
    elif 0 <= data <= 0xFF:
        size, val = 1, data
    elif 0 <= data <= 0xFFFF:
        size, val = 2, data
    else:
        size, val = 3, data

    prefix = (tag << 4) | (item_type << 2) | size
    result = bytearray([prefix])
    if size >= 1:
        result.append(val & 0xFF)
    if size >= 2:
        result.append((val >> 8) & 0xFF)
    if size == 3:
        result.append((val >> 16) & 0xFF)
        result.append((val >> 24) & 0xFF)
    return bytes(result)


class HIDReport:
    def __init__(self):
        self._bytes = bytearray()

    def _add(self, tag, item_type, data=None):
        self._bytes.extend(_encode_item(item_type, tag, data))
        return self

    def usage_page(self, page):
        self._add(_TAGS['GLOBAL_USAGE_PAGE'], _ITEM_TYPE_GLOBAL, page)
        return self

    def usage(self, usage):
        self._add(_TAGS['LOCAL_USAGE'], _ITEM_TYPE_LOCAL, usage)
        return self

    def usage_min(self, val):
        self._add(_TAGS['LOCAL_USAGE_MIN'], _ITEM_TYPE_LOCAL, val)
        return self

    def usage_max(self, val):
        self._add(_TAGS['LOCAL_USAGE_MAX'], _ITEM_TYPE_LOCAL, val)
        return self

    def logical_min(self, val):
        self._add(_TAGS['GLOBAL_LOGICAL_MIN'], _ITEM_TYPE_GLOBAL, val)
        return self

    def logical_max(self, val):
        self._add(_TAGS['GLOBAL_LOGICAL_MAX'], _ITEM_TYPE_GLOBAL, val)
        return self

    def physical_min(self, val):
        self._add(_TAGS['GLOBAL_PHYSICAL_MIN'], _ITEM_TYPE_GLOBAL, val)
        return self

    def physical_max(self, val):
        self._add(_TAGS['GLOBAL_PHYSICAL_MAX'], _ITEM_TYPE_GLOBAL, val)
        return self

    def report_size(self, val):
        self._add(_TAGS['GLOBAL_REPORT_SIZE'], _ITEM_TYPE_GLOBAL, val)
        return self

    def report_count(self, val):
        self._add(_TAGS['GLOBAL_REPORT_COUNT'], _ITEM_TYPE_GLOBAL, val)
        return self

    def report_id(self, val):
        self._add(_TAGS['GLOBAL_REPORT_ID'], _ITEM_TYPE_GLOBAL, val)
        return self

    def unit(self, val):
        self._add(_TAGS['GLOBAL_UNIT'], _ITEM_TYPE_GLOBAL, val)
        return self

    def unit_exponent(self, val):
        self._add(_TAGS['GLOBAL_UNIT_EXPONENT'], _ITEM_TYPE_GLOBAL, val)
        return self

    def push(self):
        self._add(_TAGS['GLOBAL_PUSH'], _ITEM_TYPE_GLOBAL)
        return self

    def pop(self):
        self._add(_TAGS['GLOBAL_POP'], _ITEM_TYPE_GLOBAL)
        return self

    def input(self, flags=0):
        self._add(_TAGS['MAIN_INPUT'], _ITEM_TYPE_MAIN, flags)
        return self

    def output(self, flags=0):
        self._add(_TAGS['MAIN_OUTPUT'], _ITEM_TYPE_MAIN, flags)
        return self

    def feature(self, flags=0):
        self._add(_TAGS['MAIN_FEATURE'], _ITEM_TYPE_MAIN, flags)
        return self

    def collection(self, kind):
        self._add(_TAGS['MAIN_COLLECTION'], _ITEM_TYPE_MAIN, kind)
        return self

    def end_collection(self):
        self._add(_TAGS['MAIN_END_COLLECTION'], _ITEM_TYPE_MAIN)
        return self

    def designator_index(self, val):
        self._add(_TAGS['LOCAL_DESIGNATOR_INDEX'], _ITEM_TYPE_LOCAL, val)
        return self

    def designator_min(self, val):
        self._add(_TAGS['LOCAL_DESIGNATOR_MIN'], _ITEM_TYPE_LOCAL, val)
        return self

    def designator_max(self, val):
        self._add(_TAGS['LOCAL_DESIGNATOR_MAX'], _ITEM_TYPE_LOCAL, val)
        return self

    def string_index(self, val):
        self._add(_TAGS['LOCAL_STRING_INDEX'], _ITEM_TYPE_LOCAL, val)
        return self

    def string_min(self, val):
        self._add(_TAGS['LOCAL_STRING_MIN'], _ITEM_TYPE_LOCAL, val)
        return self

    def string_max(self, val):
        self._add(_TAGS['LOCAL_STRING_MAX'], _ITEM_TYPE_LOCAL, val)
        return self

    def delimiter(self, val):
        self._add(_TAGS['LOCAL_DELIMITER'], _ITEM_TYPE_LOCAL, val)
        return self

    def encode(self):
        return bytes(self._bytes)

    def __bytes__(self):
        return self.encode()

    def __len__(self):
        return len(self._bytes)


_HID_USAGE_PAGE_NAMES = {0x01: 'Desktop', 0x07: 'Keyboard', 0x08: 'LED',
                          0x09: 'Button', 0x0C: 'Consumer', 0x0D: 'Digitizer'}

_HID_DESKTOP_USAGES = {0x01: 'Pointer', 0x02: 'Mouse', 0x04: 'Joystick',
                        0x05: 'Gamepad', 0x06: 'Keyboard', 0x07: 'Keypad',
                        0x30: 'X', 0x31: 'Y', 0x32: 'Z', 0x38: 'Wheel',
                        0x80: 'SysCtl', 0x82: 'Sleep', 0x83: 'WakeUp',
                        0x81: 'PowerDown'}

_HID_LED_USAGES = {0x01: 'NumLock', 0x02: 'CapsLock', 0x03: 'ScrlLock'}

_HID_CONSUMER_USAGES = {0x01: 'ConsCtl', 0xB0: 'Play', 0xB1: 'Pause',
                         0xB5: 'Next', 0xB6: 'Prev', 0xE0: 'Vol', 0xE2: 'Mute',
                         0xE9: 'Vol+', 0xEA: 'Vol-', 0xCD: 'Play/Pause'}

_HID_IO_EXTRA = {
    0x04: 'Rel', 0x08: 'Wrap', 0x10: 'NonLin', 0x20: 'NoPref',
    0x40: 'Null', 0x80: 'Vol', 0x100: 'Buff',
}
_HID_MAIN_NAMES = {8: 'Input', 9: 'Output', 11: 'Feature'}
_HID_COLL_NAMES = {0: 'Physical', 1: 'Application', 2: 'Logical',
                    3: 'Report', 4: 'NamedArray', 5: 'UsageSw', 6: 'Modifier'}


def parse_hid_report(raw):
    raw_bytes = raw if isinstance(raw, bytes) else raw.encode()
    lines = []
    off = 0
    depth = 0
    st = {'page': 0, 'usage': 0, 'umin': 0, 'umax': 0,
          'lmin': 0, 'lmax': 0, 'size': 0, 'count': 0, 'id': None}

    def _page_name(p):
        return _HID_USAGE_PAGE_NAMES.get(p, f'0x{p:04X}')

    def _usage_desc(page, usage):
        if page == 0x01:
            return _HID_DESKTOP_USAGES.get(usage, f'0x{usage:04X}')
        if page == 0x08:
            return _HID_LED_USAGES.get(usage, f'0x{usage:04X}')
        if page == 0x0C:
            return _HID_CONSUMER_USAGES.get(usage, f'0x{usage:04X}')
        return f'0x{usage:04X}'

    while off < len(raw_bytes):
        prefix = raw_bytes[off]
        size_bits = prefix & 3
        tag = (prefix >> 4) & 15
        itype = (prefix >> 2) & 3

        data_len = {0: 0, 1: 1, 2: 2, 3: 4}[size_bits]
        data = 0
        if data_len > 0 and off + 1 + data_len <= len(raw_bytes):
            for b in range(data_len):
                data |= raw_bytes[off + 1 + b] << (8 * b)
        off += 1 + data_len

        if itype == 0:
            indent = '  ' * depth
            if tag == 12:
                depth = max(0, depth - 1)
                if depth == 0:
                    lines.append('')
            elif tag in (8, 9, 11):
                name = _HID_MAIN_NAMES.get(tag, f'Main#{tag}')
                bits = st['size'] * st['count']
                extras = ', '.join(v for k, v in _HID_IO_EXTRA.items() if data & k)
                flags = 'Const' if data & 1 else 'Data'
                flags += ' Var' if data & 2 else ' Array'
                if extras:
                    flags += ', ' + extras
                line = f'{indent}{name}({flags}) [{bits} bits]'
                if st['id'] is not None:
                    line += f'  <- RptID={st["id"]}'
                lines.append(line)
            elif tag == 10:
                cname = _HID_COLL_NAMES.get(data, f'0x{data:02X}')
                uref = ''
                if st['usage']:
                    uref = ' -> ' + _usage_desc(st['page'], st['usage'])
                elif st['umin'] or st['umax']:
                    u1 = _usage_desc(st['page'], st['umin'])
                    u2 = _usage_desc(st['page'], st['umax'])
                    uref = f' -> {u1}..{u2}'
                lines.append(f'{indent}{cname}{uref}')
                depth += 1
            st['usage'] = st['umin'] = st['umax'] = 0
            st['id'] = None
        elif itype == 1:
            if tag == 0:
                st['page'] = data
            elif tag == 1:
                st['lmin'] = data
            elif tag == 2:
                st['lmax'] = data
            elif tag == 7:
                st['size'] = data
            elif tag == 8:
                st['id'] = data
            elif tag == 9:
                st['count'] = data
        elif itype == 2:
            if tag == 0:
                st['usage'] = data
            elif tag == 1:
                st['umin'] = data
            elif tag == 2:
                st['umax'] = data

    return lines
