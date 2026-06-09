"""Minimal UAC2 stereo speaker using the composite API.

Demonstrates the simplest possible way to create a full UAC2 audio device.
"""
from usbdesc.composite import CompositeDevice, uac2_speaker
from usbdesc.export.c_array import CArrayExporter
from usbdesc.topology import TopologyGraph


def create_simple_uac2_speaker():
    dev = CompositeDevice(
        idVendor=0x1234, idProduct=0x5678,
        manufacturer='Simple Audio', product='UAC2 Speaker',
    )
    dev.add(uac2_speaker)
    return dev.build()


if __name__ == '__main__':
    nodes = create_simple_uac2_speaker()
    print(TopologyGraph(nodes).to_ascii())
    print()
    print(CArrayExporter().export_groups(nodes, prefix='usb'))
