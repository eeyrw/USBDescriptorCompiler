"""BOS and WebUSB platform capability descriptors.

BOS (Binary Object Store) is a top-level USB descriptor container for device
capability descriptors. WebUSB extends this with a platform capability
descriptor that enables web-based USB access through a landing page URL.
"""

from usbdesc.core.base import DescriptorNode, u8, u16le, Field
from usbdesc.core.types import DESC_TYPE_BOS


class BOSDescriptor(DescriptorNode):
    """USB Binary Object Store (BOS) descriptor (bDescriptorType=0x0F). Container for device capability descriptors."""

    def __init__(self, wTotalLength=0, bNumDeviceCaps=0, name=''):
        super().__init__(name)
        self.wTotalLength = wTotalLength
        self.bNumDeviceCaps = bNumDeviceCaps

    def _subfields(self):
        return [
            *u8('bDescriptorType', DESC_TYPE_BOS),
            *u16le('wTotalLength', self.wTotalLength),
            *u8('bNumDeviceCaps', self.bNumDeviceCaps),
        ]


# WebUSB Platform Capability UUID: {3408b638-09a9-47a0-8bfd-a0768815b665}
WEBUSB_UUID = bytes([
    0x38, 0xB6, 0x08, 0x34, 0xA9, 0x09, 0xA0, 0x47,
    0x8B, 0xFD, 0xA0, 0x76, 0x88, 0x15, 0xB6, 0x65,
])


class WebUSBDescriptor(DescriptorNode):
    """WebUSB Platform Capability descriptor. Includes the WebUSB UUID and landing page URL string index."""

    def __init__(self, iLandingPage=0, bcdVersion=0x0100, name=''):
        super().__init__(name)
        self.iLandingPage = iLandingPage
        self.bcdVersion = bcdVersion

    def _subfields(self):
        fields = [
            *u8('bDescriptorType', 0x10),
            *u8('bDevCapabilityType', 0x05),
            *u8('bReserved', 0),
        ]
        for i, b in enumerate(WEBUSB_UUID):
            fields.extend(u8(f'PlatformCapabilityUUID[{i}]', b))
        fields.extend([
            *u16le('bcdVersion', self.bcdVersion),
            *u8('bVendorCode', 0x01),
            *u8('iLandingPage', self.iLandingPage),
        ])
        return fields
