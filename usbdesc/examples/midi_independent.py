"""Digital Piano MIDI — independent IN/OUT paths, no internal loopback.

  PC → [BULK OUT EP] → MIDI IN Jack 1 (embedded) → device sound engine
  Device keyboard → MIDI OUT Jack 1 (embedded) → [BULK IN EP] → PC

Two independent paths: receiving MIDI from host and sending key events
to host are separate.  No baSourceID link between IN and OUT jacks.
"""
from usbdesc.composite import CompositeDevice, midi_function
from usbdesc.export.c_array import CArrayExporter
from usbdesc.topology import TopologyGraph


def create_digital_piano():
    dev = CompositeDevice(
        idVendor=0x1234, idProduct=0x5678,
        manufacturer='Piano Co', product='Digital Piano',
    )
    dev.add(lambda rc: midi_function(rc, loopback=False, name='Piano MIDI'))
    return dev.build()


if __name__ == '__main__':
    nodes = create_digital_piano()
    print(TopologyGraph(nodes).to_ascii())
    print()
    print(CArrayExporter().export_groups(nodes, prefix='piano_midi'))
