"""USB Descriptor Compiler — generate USB device descriptors in Python.

This library provides a descriptor-node tree model with auto-calculated
``bLength`` fields, a high-level composite device builder with automatic
resource allocation, and multiple export formats (C array, JSON, raw bytes).

Supported USB classes:
- UAC 1.0 / 2.0 (Audio — playback, recording, full-duplex)
- MIDI Streaming (embedded jacks, external DIN-5 jacks, multi-port)
- HID (keyboard, mouse, joystick, consumer control, digitizer, custom)
- CDC ACM (virtual COM port)
- MSC (Mass Storage Class — Bulk-Only Transport)
- WebUSB (BOS + platform capability)

See the README and examples/ directory for usage patterns.
"""

__version__ = "0.1.0"

from usbdesc.core.base import Field, DescriptorNode, u8, u16le, u24le, u32le, hs_iso_packet_size
from usbdesc.core.encoder import DescriptorEncoder

from usbdesc.standard.device import DeviceDescriptor
from usbdesc.standard.qualifier import DeviceQualifierDescriptor
from usbdesc.standard.config import ConfigurationDescriptor, OtherSpeedConfigurationDescriptor
from usbdesc.standard.interface import InterfaceDescriptor
from usbdesc.standard.endpoint import EndpointDescriptor

from usbdesc.composite import (
    CompositeDevice, ResourceAllocator,
    uac2_setup, uac2_audio_path, uac2_speaker, uac2_line_out,
    uac2_microphone, uac2_line_in, uac2_headset, uac2_line_in_out,
    uac1_setup, uac1_audio_path, uac1_speaker, uac1_line_out,
    uac1_microphone, uac1_line_in, uac1_headset, uac1_line_in_out,
    midi_function, hid_keyboard, hid_mouse, hid_generic,
    cdc_acm, msc_bulk_only, webusb_platform,
)

from usbdesc.export.c_array import CArrayExporter
from usbdesc.export.python_bytes import PythonBytesExporter
from usbdesc.export.json_ import JsonExporter
