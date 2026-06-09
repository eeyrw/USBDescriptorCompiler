# USB Descriptor Generator (`usbdesc`)

A Python library for generating USB device descriptors. Supports HID, CDC, UAC1/UAC2, MIDI, WebUSB, and USB 2.0 High-Speed mode. Designed for embedded firmware projects that need correct USB descriptor generation at compile time or runtime.

**Zero runtime dependencies** — stdlib only. Python >= 3.7.

## Installation

```bash
# Install with dev dependencies (includes pytest)
pip install -e ".[dev]"

# Run tests
pytest tests/ -v
```

## Quick Start

```python
from usbdesc import CompositeDevice, uac2_speaker, CArrayExporter

dev = CompositeDevice(idVendor=0x1234, idProduct=0x5678)
dev.add(uac2_speaker)
print(CArrayExporter().export(dev.build()))
```

## High-Level API

Use pre-built function templates to quickly assemble composite USB devices:

```python
from usbdesc import CompositeDevice
from usbdesc import (
    uac2_speaker, uac2_microphone, uac2_headset,          # UAC2 audio
    uac2_line_out, uac2_line_in, uac2_line_in_out,        # UAC2 line I/O
    uac1_speaker, uac1_microphone, uac1_headset,          # UAC1 audio
    uac1_line_out, uac1_line_in, uac1_line_in_out,        # UAC1 line I/O
    midi_function, hid_keyboard, hid_mouse, hid_generic,  # MIDI / HID
    hid_joystick, hid_consumer_control, hid_system_control, # more HID
    cdc_acm, msc_bulk_only, webusb_platform,              # CDC / MSC / WebUSB
)

dev = CompositeDevice(
    idVendor=0x1234, idProduct=0x5678,
    bcdUSB=0x0200, manufacturer='MyCo', product='Device',
    high_speed=True, bMaxPower=200,       # USB 2.0 HS
    ep_out_base=1, ep_in_base=1,          # endpoint numbering
)

dev.add(uac2_speaker(channels=2, sample_rate=48000, bit_depth=16, volume=True))
dev.add(uac2_line_in_out(channels=2, sample_rate=96000, bit_depth=24))
dev.add(midi_function(in_jacks=1, out_jacks=1))
dev.add(hid_keyboard)
dev.add(cdc_acm)

desc_set = dev.build()  # Returns a DescriptorSet
```

### Available Templates

| Function | Description |
|---|---|
| `uac2_speaker(rc)` | UAC2 stereo speaker output |
| `uac2_line_out(rc)` | UAC2 line output (24-bit default) |
| `uac2_microphone(rc)` | UAC2 mono microphone input |
| `uac2_line_in(rc)` | UAC2 line-level input |
| `uac2_headset(rc)` | UAC2 headset (speaker + mic) |
| `uac2_line_in_out(rc)` | UAC2 full-duplex line I/O |
| `uac1_speaker(rc)` | UAC1 speaker output |
| `uac1_line_out(rc)` | UAC1 line output |
| `uac1_microphone(rc)` | UAC1 microphone input |
| `uac1_line_in(rc)` | UAC1 line input |
| `uac1_headset(rc)` | UAC1 headset |
| `uac1_line_in_out(rc)` | UAC1 full-duplex line I/O |
| `midi_function(rc)` | MIDI streaming (1 or multi-port) |
| `hid_keyboard(rc)` | HID boot keyboard |
| `hid_mouse(rc)` | HID boot mouse |
| `hid_joystick(rc)` | 4-axis joystick + 12 buttons |
| `hid_consumer_control(rc)` | Media keys (Play/Pause/Mute/etc) |
| `hid_system_control(rc)` | System Power/Sleep/Wake |
| `hid_digitizer(rc)` | Pen digitizer (tip/X/Y/pressure) |
| `hid_generic(rc)` | Custom HID with your report descriptor |
| `cdc_acm(rc)` | Virtual COM port (CDC ACM) |
| `msc_bulk_only(rc)` | Mass Storage (Bulk-Only) |
| `webusb_platform(rc)` | WebUSB BOS platform capability |

## Audio Topology Primitives

For custom audio topologies beyond the convenience wrappers, compose with `uac2_setup` + `uac2_audio_path` (or the UAC1 equivalents):

```python
from usbdesc import uac2_setup, uac2_audio_path
from usbdesc.core.types import TERM_SPEAKER, TERM_LINE_CONNECTOR

def my_pro_audio(rc):
    nodes, clock = uac2_setup(rc)
    nodes += uac2_audio_path(rc, 'OUT', 2, TERM_SPEAKER, clock_id=clock)
    nodes += uac2_audio_path(rc, 'OUT', 4, TERM_LINE_CONNECTOR, clock_id=clock)
    nodes += uac2_audio_path(rc, 'IN', 2, TERM_LINE_CONNECTOR, clock_id=clock)
    return nodes

dev = CompositeDevice(idVendor=0x1234, idProduct=0x5678)
dev.add(my_pro_audio)
```

Each `uac2_audio_path` builds:

- **OUT direction**: USB Stream IT → (FeatureUnit) → <TerminalType> OT → AS Alt0/Alt1 → ASGeneral → FormatTypeI → IsoEP
- **IN direction**: <TerminalType> IT → (FeatureUnit) → USB Stream OT → AS Alt0/Alt1 → ASGeneral → FormatTypeI → IsoEP

## USB 2.0 High-Speed Mode

Enable `high_speed=True` in `CompositeDevice` to generate Device Qualifier (0x06) and Other Speed Configuration (0x07) descriptors. High-Speed isochronous `wMaxPacketSize` uses the special 16-bit encoding:

```python
dev = CompositeDevice(idVendor=0x1234, idProduct=0x5678, high_speed=True)
dev.add(uac2_speaker(bit_depth=24, sample_rate=192000, hs_transactions=3))
```

The descriptor chain includes: Device → Device Qualifier → Configuration → Other Speed Config → interfaces.

## Custom Endpoint Addresses

Pin specific endpoint addresses for hardware matching. Unspecified endpoints auto-allocate; reserved addresses are skipped:

```python
dev.add(uac2_speaker(ep_address=0x03))                    # pin EP OUT = 0x03
dev.add(midi_function(ep_out_address=0x05, ep_in_address=0x84))
dev.add(hid_keyboard(ep_address=0x82))
```

## HID Report Descriptors

The library includes a programmatic HID report builder::

```python
from usbdesc.device_class.hid_report import HIDReport, USAGE_PAGE, USAGES, COLL, IO

report = HIDReport()
report.usage_page(USAGE_PAGE.GENERIC_DESKTOP)\
      .usage(USAGES.GENERIC_DESKTOP.MOUSE)\
      .collection(COLL.APPLICATION)\
      .usage(USAGES.GENERIC_DESKTOP.POINTER)\
      .collection(COLL.PHYSICAL)\
      .usage_page(USAGE_PAGE.BUTTON)\
      .usage_min(1).usage_max(3)\
      .logical_min(0).logical_max(1)\
      .report_size(1).report_count(3)\
      .input(IO.DATA | IO.VARIABLE | IO.ABSOLUTE)\
      .end_collection()\
      .end_collection()
raw = report.encode()

# Use with hid_generic:
dev.add(hid_generic(rc, report_descriptor=raw))
```

## MIDI Device Types

```python
# Simple embedded 1 IN / 1 OUT
dev.add(midi_function(in_jacks=1, out_jacks=1))

# Multi-port 2 IN / 2 OUT
dev.add(midi_function(in_jacks=2, out_jacks=2))

# External DIN-5 jacks
from usbdesc.core.types import MIDI_JACK_EXTERNAL
dev.add(midi_function(in_jacks=1, out_jacks=1, jack_type=MIDI_JACK_EXTERNAL))

# Loopback mode (IN → OUT routing)
dev.add(midi_function(in_jacks=1, out_jacks=1, loopback=True))
```

## Topology Visualization

Generate ASCII or Mermaid diagrams of your USB descriptor tree:

```python
from usbdesc.topology import TopologyGraph

desc_set = dev.build()
graph = TopologyGraph(desc_set)
print(graph.to_ascii())     # ASCII tree view
print(graph.to_mermaid())   # Mermaid markdown diagram
```

Output includes standard descriptor hierarchy (Device → Config → IF → EP), audio topology (CLK → IT → FU → OT → AS → EP), MIDI jack routing, and decoded HID report descriptors.

## Export Formats

```python
from usbdesc.export.c_array import CArrayExporter
from usbdesc.export.python_bytes import PythonBytesExporter
from usbdesc.export.json_ import JsonExporter

# C uint8_t array with per-byte field annotations
print(CArrayExporter().export(desc_set, 'my_desc'))

# Grouped output — one array per GetDescriptor() request type
print(CArrayExporter().export_groups(desc_set, prefix='my_device'))

# Raw bytes for runtime transfer
raw = PythonBytesExporter().export(desc_set)

# Structured JSON for debugging
print(JsonExporter().export(desc_set))
```

## Library Architecture

```
usbdesc/
├── __init__.py             Public API re-exports
├── core/
│   ├── base.py             Field, DescriptorNode, LE helpers, HS ISO encoding
│   ├── types.py            All USB constants and enum definitions
│   └── encoder.py          Flat bytearray encoder
├── standard/
│   ├── device.py           DeviceDescriptor
│   ├── qualifier.py        DeviceQualifierDescriptor
│   ├── config.py           ConfigurationDescriptor, OtherSpeedConfiguration
│   ├── interface.py        InterfaceDescriptor
│   ├── endpoint.py         EndpointDescriptor
│   ├── iad.py              Interface Association Descriptor
│   └── string.py           StringDescriptor, LANGID helper
├── device_class/
│   ├── audio/
│   │   ├── uac1.py         UAC 1.0 descriptors (11 classes)
│   │   └── uac2.py         UAC 2.0 + MIDI descriptors (22 classes)
│   ├── cdc.py              CDC functional descriptors (4 classes)
│   ├── hid.py              HID class descriptor
│   ├── hid_report.py       Programmatic HID report builder
│   └── webusb.py           BOS + WebUSB platform capability
├── composite/
│   ├── allocator.py        ResourceAllocator — automatic ID assignment
│   ├── builder.py          DescriptorSet, CompositeDevice
│   ├── audio_uac2.py       UAC2 primitives + convenience wrappers
│   ├── audio_uac1.py       UAC1 primitives + convenience wrappers
│   ├── hid.py              HID report constants + function templates
│   ├── midi.py             MIDI streaming function template
│   ├── cdc.py              CDC ACM function template
│   └── msc.py              MSC Bulk-Only + WebUSB platform template
├── topology.py             TopologyGraph — ASCII / Mermaid diagrams
├── export/
│   ├── c_array.py          CArrayExporter — C uint8_t arrays with annotations
│   ├── python_bytes.py     PythonBytesExporter — raw bytes
│   └── json_.py            JsonExporter — structured JSON
└── examples/               15 example device scripts
```

## Reference Documentation

- `usb3.2_descriptor_tables.md` — USB 3.2 Rev 1.1 descriptor layout tables (17 types)
- `UAC2_DESCRIPTOR_CATALOG.txt` — UAC2 complete descriptor catalog (35 descriptor tables)
- `USB_SEPCS/` — USB specification PDFs (CDC 1.2, HID, UAC 1.0/2.0, USB 2.0/3.2)

## License

MIT
