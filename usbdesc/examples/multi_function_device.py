"""Multi-function USB composite device — audio + HID + MIDI + CDC.

Demonstrates building a complex device with four simultaneous functions,
all sharing one USB connection with automatic resource allocation.
"""
from usbdesc.composite import (
    CompositeDevice,
    uac2_speaker, midi_function, hid_keyboard, cdc_acm,
)
from usbdesc.export.c_array import CArrayExporter
from usbdesc.topology import TopologyGraph


def create_multi_function_device():
    dev = CompositeDevice(
        idVendor=0x1234, idProduct=0x5678,
        manufacturer='Multi Dev', product='Composite',
        bDeviceClass=0xEF, bDeviceSubClass=0x02, bDeviceProtocol=0x01,
        bMaxPower=250,
    )
    dev.add(uac2_speaker)
    dev.add(midi_function)
    dev.add(hid_keyboard)
    dev.add(cdc_acm)
    return dev.build()


if __name__ == '__main__':
    nodes = create_multi_function_device()
    print(TopologyGraph(nodes).to_ascii())
    print()
    print(CArrayExporter().export_groups(nodes, prefix='multi_func'))
