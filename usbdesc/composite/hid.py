"""HID function templates — pre-built report descriptors and composite device functions.

Provides standard HID report descriptors (keyboard, mouse, joystick, consumer
control, digitizer, system control) and convenience functions that wire them
into complete USB interfaces with endpoints.
"""

from usbdesc.standard.interface import InterfaceDescriptor
from usbdesc.standard.endpoint import EndpointDescriptor

from usbdesc.device_class.hid import HIDDescriptor
from usbdesc.device_class.hid_report import HIDReport, USAGE_PAGE, USAGES, COLL, IO

from usbdesc.core.types import (
    CLASS_HID,
    HID_SUBCLASS_BOOT, HID_SUBCLASS_NONE,
    HID_PROTOCOL_NONE, HID_PROTOCOL_KEYBOARD, HID_PROTOCOL_MOUSE,
    HID_DESC_TYPE_REPORT,
    EP_ATTR_INTERRUPT,
)


# ── Pre-built HID report descriptors ─────────────────────────────────

# Standard 101-key HID keyboard report descriptor (boot protocol).
_kb = HIDReport()
_kb.usage_page(USAGE_PAGE.GENERIC_DESKTOP)\
   .usage(USAGES.GENERIC_DESKTOP.KEYBOARD)\
   .collection(COLL.APPLICATION)\
   .usage_page(USAGE_PAGE.KEYBOARD)\
   .usage_min(0xE0).usage_max(0xE7)\
   .logical_min(0).logical_max(1)\
   .report_size(1).report_count(8)\
   .input(IO.DATA | IO.VARIABLE | IO.ABSOLUTE)\
   .report_count(1).report_size(8)\
   .input(IO.CONSTANT | IO.VARIABLE | IO.ABSOLUTE)\
   .report_count(5).report_size(1)\
   .usage_page(USAGE_PAGE.LED)\
   .usage_min(0x01).usage_max(0x05)\
   .output(IO.DATA | IO.VARIABLE | IO.ABSOLUTE)\
   .report_count(1).report_size(3)\
   .output(IO.CONSTANT | IO.VARIABLE | IO.ABSOLUTE)\
   .report_count(6).report_size(8)\
   .logical_min(0).logical_max(0x00FF)\
   .usage_page(USAGE_PAGE.KEYBOARD)\
   .usage_min(0).usage_max(0x91)\
   .input(IO.DATA | IO.ARRAY | IO.ABSOLUTE)\
   .end_collection()
_HID_KEYBOARD_REPORT = _kb.encode()

# Standard HID mouse report descriptor (boot protocol) — 3 buttons, X/Y/Wheel.
_mouse = HIDReport()
_mouse.usage_page(USAGE_PAGE.GENERIC_DESKTOP)\
       .usage(USAGES.GENERIC_DESKTOP.MOUSE)\
       .collection(COLL.APPLICATION)\
       .usage(USAGES.GENERIC_DESKTOP.POINTER)\
       .collection(COLL.PHYSICAL)\
       .usage_page(USAGE_PAGE.BUTTON)\
       .usage_min(1).usage_max(3)\
       .logical_min(0).logical_max(1)\
       .report_size(1).report_count(3)\
       .input(IO.DATA | IO.VARIABLE | IO.ABSOLUTE)\
       .report_count(1).report_size(5)\
       .input(IO.CONSTANT | IO.VARIABLE | IO.ABSOLUTE)\
       .usage_page(USAGE_PAGE.GENERIC_DESKTOP)\
       .usage(USAGES.GENERIC_DESKTOP.X)\
       .usage(USAGES.GENERIC_DESKTOP.Y)\
       .usage(USAGES.GENERIC_DESKTOP.WHEEL)\
       .logical_min(-127).logical_max(127)\
       .report_size(8).report_count(3)\
       .input(IO.DATA | IO.VARIABLE | IO.RELATIVE)\
       .end_collection()\
       .end_collection()
_HID_MOUSE_REPORT = _mouse.encode()

# 4-axis joystick with hat switch, 12 buttons, X/Y/Z/RZ axes.
_joy = HIDReport()
_joy.usage_page(USAGE_PAGE.GENERIC_DESKTOP)\
    .usage(USAGES.GENERIC_DESKTOP.JOYSTICK)\
    .collection(COLL.APPLICATION)\
    .report_id(1)\
    .usage(USAGES.GENERIC_DESKTOP.POINTER)\
    .collection(COLL.PHYSICAL)\
    .usage_page(USAGE_PAGE.BUTTON)\
    .usage_min(1).usage_max(12)\
    .logical_min(0).logical_max(1)\
    .report_size(1).report_count(12)\
    .input(IO.DATA | IO.VARIABLE | IO.ABSOLUTE)\
    .usage_page(USAGE_PAGE.GENERIC_DESKTOP)\
    .usage(USAGES.GENERIC_DESKTOP.HAT_SWITCH)\
    .logical_min(0).logical_max(7)\
    .physical_min(0).physical_max(315)\
    .unit(0x14).unit_exponent(0)\
    .report_size(4).report_count(1)\
    .input(IO.DATA | IO.VARIABLE | IO.ABSOLUTE)\
    .report_count(1).report_size(4)\
    .input(IO.CONSTANT | IO.VARIABLE | IO.ABSOLUTE)\
    .usage(USAGES.GENERIC_DESKTOP.X)\
    .usage(USAGES.GENERIC_DESKTOP.Y)\
    .usage(USAGES.GENERIC_DESKTOP.Z)\
    .usage(USAGES.GENERIC_DESKTOP.RZ)\
    .logical_min(-32768).logical_max(32767)\
    .report_size(16).report_count(4)\
    .input(IO.DATA | IO.VARIABLE | IO.ABSOLUTE)\
    .end_collection()\
    .end_collection()
_HID_JOYSTICK_REPORT = _joy.encode()

# Consumer control (media keys): Play/Pause, Next, Prev, Stop, Mute, Vol+, Vol-.
_cons = HIDReport()
_cons.usage_page(USAGE_PAGE.CONSUMER)\
     .usage(0x01)\
     .collection(COLL.APPLICATION)\
     .report_id(2)\
     .usage(0xCD).usage(0xB5).usage(0xB6).usage(0xB7)\
     .usage(0xE2).usage(0xE9).usage(0xEA)\
     .logical_min(0).logical_max(1)\
     .report_size(1).report_count(7)\
     .input(IO.DATA | IO.VARIABLE | IO.ABSOLUTE)\
     .report_count(1).report_size(1)\
     .input(IO.CONSTANT | IO.VARIABLE | IO.ABSOLUTE)\
     .end_collection()
_HID_CONSUMER_REPORT = _cons.encode()

# Pen/touch digitizer: tip switch, in-range, X, Y, and tip pressure.
_dig = HIDReport()
_dig.usage_page(USAGE_PAGE.DIGITIZER)\
    .usage(0x02)\
    .collection(COLL.APPLICATION)\
    .report_id(3)\
    .usage(0x42)\
    .collection(COLL.PHYSICAL)\
    .usage(0x32).usage(0x42)\
    .logical_min(0).logical_max(1)\
    .report_size(1).report_count(2)\
    .input(IO.DATA | IO.VARIABLE | IO.ABSOLUTE)\
    .report_count(1).report_size(6)\
    .input(IO.CONSTANT | IO.VARIABLE | IO.ABSOLUTE)\
    .usage(0x30)\
    .logical_min(0).logical_max(32767)\
    .physical_min(0).physical_max(32767)\
    .unit(0x33).unit_exponent(-3)\
    .report_size(16).report_count(1)\
    .input(IO.DATA | IO.VARIABLE | IO.ABSOLUTE)\
    .usage(0x31)\
    .logical_min(0).logical_max(32767)\
    .physical_min(0).physical_max(32767)\
    .report_size(16).report_count(1)\
    .input(IO.DATA | IO.VARIABLE | IO.ABSOLUTE)\
    .usage(0x30)\
    .logical_min(0).logical_max(1023)\
    .physical_min(0).physical_max(1023)\
    .report_size(10).report_count(1)\
    .input(IO.DATA | IO.VARIABLE | IO.ABSOLUTE)\
    .report_count(1).report_size(6)\
    .input(IO.CONSTANT | IO.VARIABLE | IO.ABSOLUTE)\
    .end_collection()\
    .end_collection()
_HID_DIGITIZER_REPORT = _dig.encode()

# System control: Power Down, Sleep, Wake Up.
_sys = HIDReport()
_sys.usage_page(USAGE_PAGE.GENERIC_DESKTOP)\
    .usage(USAGES.GENERIC_DESKTOP.SYSTEM_CONTROL)\
    .collection(COLL.APPLICATION)\
    .report_id(4)\
    .usage(USAGES.GENERIC_DESKTOP.SYSTEM_POWER_DOWN)\
    .usage(USAGES.GENERIC_DESKTOP.SYSTEM_SLEEP)\
    .usage(USAGES.GENERIC_DESKTOP.SYSTEM_WAKE_UP)\
    .logical_min(0).logical_max(1)\
    .report_size(1).report_count(3)\
    .input(IO.DATA | IO.VARIABLE | IO.ABSOLUTE)\
    .report_count(1).report_size(5)\
    .input(IO.CONSTANT | IO.VARIABLE | IO.ABSOLUTE)\
    .end_collection()
_HID_SYSTEM_CONTROL_REPORT = _sys.encode()


# ── HID function templates ──────────────────────────────────────────

def hid_generic(rc, report_descriptor=None, ep_in_size=8, ep_interval=10,
                subclass=HID_SUBCLASS_NONE, protocol=HID_PROTOCOL_NONE,
                wMaxPacketSize=8, name='HID', ep_address=None):
    """Generic HID — configurable subclass, protocol, and report descriptor."""
    nodes = []
    iface = rc.alloc_interface()
    if report_descriptor is None:
        report_descriptor = _HID_KEYBOARD_REPORT
    nodes.append(InterfaceDescriptor(
        bInterfaceNumber=iface, bNumEndpoints=1,
        bInterfaceClass=CLASS_HID,
        bInterfaceSubClass=subclass,
        bInterfaceProtocol=protocol,
        name=f'{name} Interface',
    ))
    nodes.append(HIDDescriptor(
        bDescriptorType=HID_DESC_TYPE_REPORT,
        wDescriptorLength=len(report_descriptor),
        report_bytes=report_descriptor,
    ))
    if ep_address is None:
        ep_address = rc.alloc_ep_in()
    else:
        rc.reserve_ep_in(ep_address)
    nodes.append(EndpointDescriptor(
        bEndpointAddress=ep_address,
        bmAttributes=EP_ATTR_INTERRUPT,
        wMaxPacketSize=wMaxPacketSize, bInterval=ep_interval,
        name=f'{name} EP IN',
    ))
    return nodes


def hid_keyboard(rc, boot_protocol=True, name='Keyboard', ep_address=None):
    """Standard HID keyboard (boot protocol)."""
    return hid_generic(
        rc, report_descriptor=_HID_KEYBOARD_REPORT,
        subclass=HID_SUBCLASS_BOOT if boot_protocol else HID_SUBCLASS_NONE,
        protocol=HID_PROTOCOL_KEYBOARD,
        name=name, ep_address=ep_address,
    )


def hid_mouse(rc, boot_protocol=True, name='Mouse', ep_address=None):
    """Standard HID mouse (boot protocol)."""
    return hid_generic(
        rc, report_descriptor=_HID_MOUSE_REPORT,
        subclass=HID_SUBCLASS_BOOT if boot_protocol else HID_SUBCLASS_NONE,
        protocol=HID_PROTOCOL_MOUSE,
        name=name, ep_address=ep_address,
    )


def hid_joystick(rc, name='Joystick', ep_address=None):
    """Standard 4-axis joystick with hat switch and 12 buttons."""
    return hid_generic(
        rc, report_descriptor=_HID_JOYSTICK_REPORT,
        subclass=HID_SUBCLASS_NONE, protocol=HID_PROTOCOL_NONE,
        name=name, ep_address=ep_address,
    )


def hid_gamepad(rc, name='Gamepad', ep_address=None):
    """Alias for hid_joystick."""
    return hid_joystick(rc, name=name, ep_address=ep_address)


def hid_consumer_control(rc, name='Consumer Control', ep_address=None):
    """Media control keys: Play/Pause, Next, Prev, Stop, Mute, Vol+, Vol-."""
    return hid_generic(
        rc, report_descriptor=_HID_CONSUMER_REPORT,
        subclass=HID_SUBCLASS_NONE, protocol=HID_PROTOCOL_NONE,
        ep_in_size=8, ep_interval=16,
        name=name, ep_address=ep_address,
    )


def hid_digitizer(rc, name='Digitizer', ep_address=None):
    """Pen digitizer with tip switch, in-range, X/Y, and tip pressure."""
    return hid_generic(
        rc, report_descriptor=_HID_DIGITIZER_REPORT,
        subclass=HID_SUBCLASS_NONE, protocol=HID_PROTOCOL_NONE,
        ep_in_size=10, ep_interval=2,
        name=name, ep_address=ep_address,
    )


def hid_system_control(rc, name='System Control', ep_address=None):
    """System Power Down, Sleep, Wake Up controls."""
    return hid_generic(
        rc, report_descriptor=_HID_SYSTEM_CONTROL_REPORT,
        subclass=HID_SUBCLASS_NONE, protocol=HID_PROTOCOL_NONE,
        ep_in_size=2, ep_interval=16,
        name=name, ep_address=ep_address,
    )
