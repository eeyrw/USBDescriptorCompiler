"""USB 2.0 High-Speed UAC2 speaker with Device Qualifier and Other Speed Config.

Demonstrates building a USB 2.0 HS-capable device. When high_speed=True,
the descriptor chain includes Device Qualifier (0x06) and Other Speed
Configuration (0x07) descriptors required by the USB 2.0 spec.
"""
from usbdesc.composite import CompositeDevice, uac2_speaker, midi_function
from usbdesc.export.c_array import CArrayExporter
from usbdesc.topology import TopologyGraph


def create_high_speed_device():
    dev = CompositeDevice(
        idVendor=0x1234, idProduct=0x5678,
        bcdUSB=0x0200,
        manufacturer='HS Audio', product='UAC2 HS',
        bMaxPacketSize0=64, bMaxPower=200,
        high_speed=True,
    )
    dev.add(uac2_speaker)
    dev.add(midi_function)
    return dev.build()


if __name__ == '__main__':
    nodes = create_high_speed_device()
    print(TopologyGraph(nodes).to_ascii())
    print()
    print(f'// Total nodes: {len(nodes)}')
    print(CArrayExporter().export_groups(nodes, prefix='hs'))
