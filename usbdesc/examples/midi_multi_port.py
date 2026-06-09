"""Multi-port USB MIDI device — 2 IN jacks, 2 OUT jacks.

Demonstrates multiple MIDI jacks sharing one streaming interface.
Each jack gets its own bulk endpoint association.
"""
from usbdesc.composite import CompositeDevice, midi_function
from usbdesc.export.c_array import CArrayExporter
from usbdesc.topology import TopologyGraph


def create_midi_multi_port():
    dev = CompositeDevice(
        idVendor=0x1234, idProduct=0x5678,
        manufacturer='MIDI Pro', product='Multi-Port MIDI',
    )
    dev.add(lambda rc: midi_function(rc, in_jacks=2, out_jacks=2))
    return dev.build()


if __name__ == '__main__':
    nodes = create_midi_multi_port()
    print(TopologyGraph(nodes).to_ascii())
    print()
    print(CArrayExporter().export_groups(nodes, prefix='midi_multi'))
