"""CDC ACM function template — virtual COM port.

Builds a CDC Abstract Control Model device with control interface
(CDC Header, Call Management, ACM, Union) + data interface (Bulk OUT/IN).
"""

from usbdesc.standard.interface import InterfaceDescriptor
from usbdesc.standard.endpoint import EndpointDescriptor

from usbdesc.device_class.cdc import CDCHeader, CDCCallManagement, CDCACM, CDCUnion

from usbdesc.core.types import (
    CLASS_CDC, CLASS_CDC_DATA,
    EP_ATTR_BULK, EP_ATTR_INTERRUPT,
)


def cdc_acm(rc, bmCapabilities=0x06, subclass=0x02, protocol=0x01,
            name='CDC ACM',
            ep_int_address=None, ep_out_address=None, ep_in_address=None):
    """CDC ACM virtual COM port — control interface + data interface."""
    nodes = []
    iface_ctrl = rc.alloc_interface()
    nodes.append(InterfaceDescriptor(
        bInterfaceNumber=iface_ctrl, bNumEndpoints=1,
        bInterfaceClass=CLASS_CDC,
        bInterfaceSubClass=subclass,
        bInterfaceProtocol=protocol,
        name=f'{name} Control',
    ))
    nodes.append(CDCHeader())
    iface_data = rc.alloc_interface()
    call_mgmt_caps = (bmCapabilities >> 4) & 0x03 if bmCapabilities & 0xF0 else 0x00
    nodes.append(CDCCallManagement(
        bmCapabilities=call_mgmt_caps,
        bDataInterface=iface_data))
    nodes.append(CDCACM(bmCapabilities=bmCapabilities))
    nodes.append(CDCUnion(bMasterInterface=iface_ctrl, baInterfaceNr=[iface_data]))
    ep_int = ep_int_address if ep_int_address is not None else rc.alloc_ep_in()
    if ep_int_address is not None:
        rc.reserve_ep_in(ep_int_address)
    int_interval = 16 if getattr(rc, '_high_speed', False) else 255
    nodes.append(EndpointDescriptor(
        bEndpointAddress=ep_int,
        bmAttributes=EP_ATTR_INTERRUPT,
        wMaxPacketSize=16, bInterval=int_interval,
        name=f'{name} Interrupt EP IN',
    ))

    iface_data = rc.alloc_interface()
    nodes.append(InterfaceDescriptor(
        bInterfaceNumber=iface_data, bNumEndpoints=2,
        bInterfaceClass=CLASS_CDC_DATA,
        bInterfaceSubClass=0x00, bInterfaceProtocol=0x00,
        name=f'{name} Data',
    ))
    ep_out = ep_out_address if ep_out_address is not None else rc.alloc_ep_out()
    if ep_out_address is not None:
        rc.reserve_ep_out(ep_out_address)
    nodes.append(EndpointDescriptor(
        bEndpointAddress=ep_out,
        bmAttributes=EP_ATTR_BULK,
        wMaxPacketSize=64, bInterval=0,
        name=f'{name} Data EP OUT',
    ))
    ep_in_data = ep_in_address if ep_in_address is not None else rc.alloc_ep_in()
    if ep_in_address is not None:
        rc.reserve_ep_in(ep_in_address)
    nodes.append(EndpointDescriptor(
        bEndpointAddress=ep_in_data,
        bmAttributes=EP_ATTR_BULK,
        wMaxPacketSize=64, bInterval=0,
        name=f'{name} Data EP IN',
    ))
    return nodes
