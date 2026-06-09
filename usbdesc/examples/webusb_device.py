"""WebUSB-enabled USB device with BOS descriptor and platform capability.

Demonstrates adding WebUSB platform capability to a composite device.
The BOS descriptor added by webusb_platform() enables Chrome's WebUSB API.
"""
from usbdesc.composite import (
    CompositeDevice,
    uac2_speaker, midi_function, webusb_platform,
)
from usbdesc.export.c_array import CArrayExporter
from usbdesc.topology import TopologyGraph


def create_webusb_device():
    dev = CompositeDevice(
        idVendor=0x1234, idProduct=0x5678,
        manufacturer='WebUSB', product='Audio + MIDI',
        bcdUSB=0x0200,
    )
    dev.add(uac2_speaker)
    dev.add(midi_function)
    dev.add(lambda rc: webusb_platform(rc, landing_page_url='https://example.com'))
    return dev.build()


if __name__ == '__main__':
    nodes = create_webusb_device()
    print(TopologyGraph(nodes).to_ascii())
    print()
    print(f'// {len(nodes)} nodes')
    print(CArrayExporter().export_groups(nodes, prefix='webusb'))
