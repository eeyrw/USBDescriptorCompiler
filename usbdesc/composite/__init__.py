"""Composite USB device assembly layer.

Provides ResourceAllocator (auto-assigns interface/endpoint/terminal IDs),
CompositeDevice (orchestrates full descriptor chains), and pre-built function
templates for every supported USB device class.
"""

from usbdesc.composite.allocator import ResourceAllocator
from usbdesc.composite.builder import CompositeDevice

# UAC2 primitives and convenience wrappers
from usbdesc.composite.audio_uac2 import (
    uac2_setup, uac2_audio_path,
    uac2_speaker, uac2_line_out,
    uac2_microphone, uac2_line_in,
    uac2_headset, uac2_line_in_out,
)

# UAC1 primitives and convenience wrappers
from usbdesc.composite.audio_uac1 import (
    uac1_setup, uac1_audio_path,
    uac1_speaker, uac1_line_out,
    uac1_microphone, uac1_line_in,
    uac1_headset, uac1_line_in_out,
)

# MIDI
from usbdesc.composite.midi import midi_function

# HID
from usbdesc.composite.hid import (
    _HID_KEYBOARD_REPORT, _HID_MOUSE_REPORT,
    _HID_JOYSTICK_REPORT, _HID_CONSUMER_REPORT,
    _HID_DIGITIZER_REPORT, _HID_SYSTEM_CONTROL_REPORT,
    hid_generic, hid_keyboard, hid_mouse,
    hid_joystick, hid_gamepad,
    hid_consumer_control, hid_digitizer, hid_system_control,
)

# CDC, MSC, WebUSB
from usbdesc.composite.cdc import cdc_acm
from usbdesc.composite.msc import msc_bulk_only, webusb_platform
