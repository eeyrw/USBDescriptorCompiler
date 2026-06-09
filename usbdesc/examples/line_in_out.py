"""UAC2 Line I/O device — full-duplex professional audio interface.

Demonstrates the high-level composite API for line-level input/output.
Default: 2 channels, 24-bit, 48 kHz with independent volume controls.
"""
from usbdesc.composite import CompositeDevice, uac2_line_in_out
from usbdesc.export.c_array import CArrayExporter
from usbdesc.topology import TopologyGraph


def create_line_in_out():
    dev = CompositeDevice(
        idVendor=0x1234, idProduct=0x5678,
        manufacturer='Pro Audio', product='Line I/O',
        bcdUSB=0x0200,
    )
    dev.add(uac2_line_in_out)
    return dev.build()


if __name__ == '__main__':
    nodes = create_line_in_out()
    print(TopologyGraph(nodes).to_ascii())
    print(CArrayExporter().export_groups(nodes, prefix='line_io'))
