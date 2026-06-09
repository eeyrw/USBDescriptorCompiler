"""Basic USB MIDI device — one IN jack, one OUT jack, embedded.

Minimal MIDI-only device with a single MIDI streaming interface.
Runs standalone to generate a C array.
"""
from usbdesc.composite import CompositeDevice, midi_function
from usbdesc.export.c_array import CArrayExporter
from usbdesc.topology import TopologyGraph


def create_midi_simple():
    dev = CompositeDevice(
        idVendor=0x1234, idProduct=0x5678,
        manufacturer='MIDI Co', product='USB MIDI',
    )
    dev.add(midi_function)
    return dev.build()


if __name__ == '__main__':
    nodes = create_midi_simple()
    print(TopologyGraph(nodes).to_ascii())
    print()
    print(CArrayExporter().export_groups(nodes, prefix='midi'))
