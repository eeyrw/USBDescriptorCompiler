"""CDC (Communications Device Class) functional descriptors.

Defines class-specific descriptors for CDC (e.g., CDC-ACM) used to describe
communication device capabilities like call management, abstract control
model, and interface groupings.
"""

from usbdesc.core.types import CDC_DESC_TYPE_CS_INTERFACE, CDCSubtype
from usbdesc.core.base import DescriptorNode, u8, u16le


class CDCHeader(DescriptorNode):
    """CDC Header Functional descriptor. Declares CDC compliance version."""

    def __init__(self, bcdCDC=0x0120, name=''):
        super().__init__(name)
        self.bcdCDC = bcdCDC

    def _subfields(self):
        return [
            *u8('bDescriptorType', CDC_DESC_TYPE_CS_INTERFACE),
            *u8('bDescriptorSubtype', CDCSubtype.HEADER),
            *u16le('bcdCDC', self.bcdCDC),
        ]


class CDCCallManagement(DescriptorNode):
    """CDC Call Management Functional descriptor. Specifies call management capabilities."""

    def __init__(self, bmCapabilities, bDataInterface, name=''):
        super().__init__(name)
        self.bmCapabilities = bmCapabilities
        self.bDataInterface = bDataInterface

    def _subfields(self):
        return [
            *u8('bDescriptorType', CDC_DESC_TYPE_CS_INTERFACE),
            *u8('bDescriptorSubtype', CDCSubtype.CALL_MANAGEMENT),
            *u8('bmCapabilities', self.bmCapabilities),
            *u8('bDataInterface', self.bDataInterface),
        ]


class CDCACM(DescriptorNode):
    """CDC Abstract Control Model Functional descriptor. Defines ACM capabilities."""

    def __init__(self, bmCapabilities, name=''):
        super().__init__(name)
        self.bmCapabilities = bmCapabilities

    def _subfields(self):
        return [
            *u8('bDescriptorType', CDC_DESC_TYPE_CS_INTERFACE),
            *u8('bDescriptorSubtype', CDCSubtype.ABSTRACT_CONTROL),
            *u8('bmCapabilities', self.bmCapabilities),
        ]


class CDCUnion(DescriptorNode):
    """CDC Union Functional descriptor. Groups the master and slave interfaces."""

    def __init__(self, bMasterInterface, baInterfaceNr, name=''):
        super().__init__(name)
        self.bMasterInterface = bMasterInterface
        self.baInterfaceNr = list(baInterfaceNr)

    def _subfields(self):
        fields = [
            *u8('bDescriptorType', CDC_DESC_TYPE_CS_INTERFACE),
            *u8('bDescriptorSubtype', CDCSubtype.UNION),
            *u8('bMasterInterface', self.bMasterInterface),
        ]
        for i, nr in enumerate(self.baInterfaceNr):
            fields.extend(u8(f'bSlaveInterface[{i}]', nr))
        return fields
