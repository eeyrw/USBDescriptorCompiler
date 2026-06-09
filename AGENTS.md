# AGENTS.md

## Project overview

USB Descriptor Generator — a Python library (`usbdesc`) for generating USB device descriptors (HID, CDC, UAC1/UAC2).

## Commands

```bash
# Install with dev deps (editable, includes pytest)
pip install -e ".[dev]"

# Run pytest (after install)
pytest tests/ -v

# Quick smoke test
python -c "from usbdesc.device_class.audio.uac2 import InputTerminal; print(InputTerminal(1, 0x0101).encode().hex())"
```

## Architecture

Two-layer design: `device_class/` defines descriptor types (pure data models), `composite/` wires them into complete USB devices.

- **`usbdesc/core/`** — `Field` namedtuple, `DescriptorNode` base class with auto-calculated `bLength`, multi-byte LE helpers (`u8`, `u16le`, `u24le`, `u32le`), `hs_iso_packet_size()`, `DescriptorEncoder`
- **`usbdesc/standard/`** — `DeviceDescriptor`, `DeviceQualifierDescriptor`, `OtherSpeedConfigurationDescriptor`, `ConfigurationDescriptor`, `InterfaceDescriptor`, `EndpointDescriptor`, `IADDescriptor`, `StringDescriptor`
- **`usbdesc/device_class/`** — all device class descriptor definitions:
  - `device_class/audio/uac2.py` — UAC2 nodes (22 classes): `ACHeader`, `InputTerminal`, `OutputTerminal`, `FeatureUnit`, `MixerUnit`, `SelectorUnit`, `EffectUnit`, `ProcessingUnit`, `ExtensionUnit`, `ClockSource`, `ClockSelector`, `ClockMultiplier`, `SampleRateConverter`, `ASGeneral`, `FormatTypeI`, `Encoder`, `Decoder`, `ClassSpecificIsoEP`, `MIDIInJack`, `MIDIOutJack`, `MIDIOutBulkEP`, `MIDIInBulkEP`
  - `device_class/audio/uac1.py` — UAC1 nodes (11 classes) with correct 2-byte `wChannelConfig`, 3-byte sample rates, variable `bControlSize`
  - `device_class/cdc.py` — `CDCHeader`, `CDCCallManagement`, `CDCACM`, `CDCUnion`
  - `device_class/hid.py` — `HIDDescriptor`; `hid_report.py` — `HIDReport` builder with `USAGE_PAGE`, `USAGES`, `COLL`, `IO` enums
  - `device_class/webusb.py` — `BOSDescriptor`, `WebUSBDescriptor`
- **`usbdesc/composite/`** — device assembly layer:
  - `composite/allocator.py` — `ResourceAllocator` (tracks interface/endpoint/terminal/clock/jack IDs)
  - `composite/builder.py` — `DescriptorSet`, `CompositeDevice` (auto-calculates `wTotalLength`, inserts IADs, handles USB 2.0 HS qualifier/other-speed)
  - `composite/audio_uac2.py` — UAC2 primitives (`uac2_setup`, `uac2_audio_path`) + convenience wrappers (`uac2_speaker`, `uac2_line_out`, `uac2_microphone`, `uac2_line_in`, `uac2_headset`, `uac2_line_in_out`)
  - `composite/audio_uac1.py` — UAC1 primitives (`uac1_setup`, `uac1_audio_path`) + convenience wrappers (`uac1_speaker`, `uac1_line_out`, `uac1_microphone`, `uac1_line_in`, `uac1_headset`, `uac1_line_in_out`)
  - `composite/hid.py` — 6 pre-built HID report constants + `hid_generic`, `hid_keyboard`, `hid_mouse`, `hid_joystick`, `hid_gamepad`, `hid_consumer_control`, `hid_digitizer`, `hid_system_control`
  - `composite/midi.py` — `midi_function`
  - `composite/cdc.py` — `cdc_acm`
  - `composite/msc.py` — `msc_bulk_only`, `webusb_platform`
- **`usbdesc/export/`** — `CArrayExporter`, `PythonBytesExporter`, `JsonExporter`
- **`usbdesc/topology.py`** — `TopologyGraph`: scans descriptors and generates ASCII / Mermaid connection diagrams of the audio topology (CLK→IT→FU→OT→AS→EP chains, MIDI jack routing)
- **`usbdesc/examples/`** — 15 example scripts: `simple_uac2_speaker`, `line_in_out`, `multi_audio_path`, `multi_function_device`, `high_speed_uac2`, `uac1_headset`, `webusb_device`, `topology_demo`, `hid_report_builder`, `midi_simple`/`midi_multi_port`/`midi_external`/`midi_audio_composite`/`midi_hid_composite`/`midi_independent`

## Key facts

- **Zero runtime dependencies** — stdlib only. Dev dependencies: `pytest>=7.0`.
- **Python >= 3.7** minimum.
- **Every descriptor node** extends `DescriptorNode`. Subclasses implement `_subfields()` returning fields excluding `bLength`; the base class auto-prepends `bLength` with the correct value.
- Setuptools with `[tool.setuptools.packages.find]`; `include = ["usbdesc*"]`.
- Tests in `tests/` use pytest; 242 tests cover core types, standard descriptors, all UAC1/UAC2 nodes, HID, CDC, all exporters, composite device building, endpoint configuration, device-level settings, USB 2.0 high-speed mode, and topology graph analysis.
