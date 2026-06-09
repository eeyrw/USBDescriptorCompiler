"""USB Standard Endpoint Descriptor (bDescriptorType=0x05).

Defined in USB Specification 2.0, Section 9.6.6. The Endpoint Descriptor
describes a single USB endpoint within an interface, including its address,
direction, transfer type, maximum packet size, and polling interval.
"""

from usbdesc.core.types import DESC_TYPE_ENDPOINT
from usbdesc.core.base import DescriptorNode, u8, u16le


class EndpointDescriptor(DescriptorNode):
    """USB Endpoint Descriptor (bDescriptorType=0x05).

    Describes a USB endpoint: its address (with direction bit), transfer
    type (control, isochronous, bulk, interrupt), maximum packet size
    (wMaxPacketSize), and polling interval. Every active endpoint (except
    endpoint 0) must be described by an Endpoint Descriptor within its
    parent interface descriptor set.

    USB Specification 2.0, Section 9.6.6.
    """

    def __init__(self, bEndpointAddress=0x00, bmAttributes=0x00,
                 wMaxPacketSize=64, bInterval=0, name=''):
        """Create an Endpoint Descriptor.

        Parameters
        ----------
        bEndpointAddress : int
            Endpoint address. Bits 0-3: endpoint number (1-15). Bit 7:
            direction (0 = OUT, 1 = IN). Bits 4-6: reserved (0).
        bmAttributes : int
            Transfer type and synchronization attributes.
            Bits 0-1: transfer type (0=Control, 1=Isochronous, 2=Bulk,
            3=Interrupt). Additional bits are transfer-type-specific
            (e.g. synchronization type for isochronous endpoints).
        wMaxPacketSize : int
            16-bit maximum packet size for this endpoint. For high-speed
            isochronous endpoints, bits 11-12 encode additional
            transactions per microframe; use ``hs_iso_packet_size()``
            to compute this value.
        bInterval : int
            Polling interval. For isochronous and interrupt endpoints in
            full-speed, this is in milliseconds (1-255). For high-speed,
            the encoding is 2^(bInterval-1) microframes. For bulk endpoints,
            this is typically ignored.
        name : str
            Optional descriptor name for debugging.
        """
        super().__init__(name)
        self.bEndpointAddress = bEndpointAddress
        self.bmAttributes = bmAttributes
        self.wMaxPacketSize = wMaxPacketSize
        self.bInterval = bInterval

    def _subfields(self):
        return [
            *u8('bDescriptorType', DESC_TYPE_ENDPOINT),
            *u8('bEndpointAddress', self.bEndpointAddress),
            *u8('bmAttributes', self.bmAttributes),
            *u16le('wMaxPacketSize', self.wMaxPacketSize),
            *u8('bInterval', self.bInterval),
        ]
