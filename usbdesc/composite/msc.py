"""MSC and WebUSB function templates — Mass Storage and WebUSB platform capability."""

from usbdesc.standard.interface import InterfaceDescriptor
from usbdesc.standard.endpoint import EndpointDescriptor

from usbdesc.device_class.webusb import WebUSBDescriptor, BOSDescriptor

from usbdesc.core.types import (
    CLASS_MASS_STORAGE,
    EP_ATTR_BULK,
)


def msc_bulk_only(rc, subclass=0x06, protocol=0x50, name='MSC',
                  ep_out_address=None, ep_in_address=None):
    """Mass Storage Class — Bulk-Only Transport."""
    nodes = []
    iface = rc.alloc_interface()
    nodes.append(InterfaceDescriptor(
        bInterfaceNumber=iface, bNumEndpoints=2,
        bInterfaceClass=CLASS_MASS_STORAGE,
        bInterfaceSubClass=subclass,
        bInterfaceProtocol=protocol,
        name=f'{name} Interface',
    ))
    ep_out = ep_out_address if ep_out_address is not None else rc.alloc_ep_out()
    if ep_out_address is not None:
        rc.reserve_ep_out(ep_out_address)
    nodes.append(EndpointDescriptor(
        bEndpointAddress=ep_out,
        bmAttributes=EP_ATTR_BULK,
        wMaxPacketSize=64, bInterval=0,
        name=f'{name} EP OUT',
    ))
    ep_in = ep_in_address if ep_in_address is not None else rc.alloc_ep_in()
    if ep_in_address is not None:
        rc.reserve_ep_in(ep_in_address)
    nodes.append(EndpointDescriptor(
        bEndpointAddress=ep_in,
        bmAttributes=EP_ATTR_BULK,
        wMaxPacketSize=64, bInterval=0,
        name=f'{name} EP IN',
    ))
    return nodes


def webusb_platform(rc, landing_page_url=''):
    """WebUSB platform capability descriptor — BOS + WebUSB descriptor.

    Adds a Binary Object Store (BOS) descriptor and a WebUSB platform
    capability descriptor that advertises a landing page URL.
    """
    iLanding = rc.alloc_string(landing_page_url) if landing_page_url else 0
    return [
        BOSDescriptor(
            wTotalLength=0, bNumDeviceCaps=1,
            name='BOS Descriptor',
        ),
        WebUSBDescriptor(
            iLandingPage=iLanding, bcdVersion=0x0100,
            name='WebUSB Platform Capability',
        ),
    ]
