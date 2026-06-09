"""USB MIDI + HID composite — MIDI controller with keyboard controls.

Demonstrates a MIDI device that also exposes HID keyboard controls
(useful for DAW transport, CC control, etc.).
"""
from usbdesc.composite import CompositeDevice, midi_function, hid_keyboard
from usbdesc.export.c_array import CArrayExporter
from usbdesc.topology import TopologyGraph


def create_midi_hid_composite():
    dev = CompositeDevice(
        idVendor=0x1234, idProduct=0x5678,
        manufacturer='Controller Co', product='MIDI Controller',
    )
    dev.add(midi_function)
    dev.add(hid_keyboard)
    return dev.build()


if __name__ == '__main__':
    nodes = create_midi_hid_composite()
    print(TopologyGraph(nodes).to_ascii())
    print()
    print(CArrayExporter().export_groups(nodes, prefix='midi_hid'))
