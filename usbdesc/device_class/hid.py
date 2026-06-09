"""HID (Human Interface Device) class descriptor.

Describes the HID specification version, country code, and the associated
HID report descriptor that defines the device's input/output/feature reports.
"""

from usbdesc.core.types import (
    HID_DESC_TYPE_HID, HID_DESC_TYPE_REPORT, HID_BCD, HID_COUNTRY_NONE,
)
from usbdesc.core.base import DescriptorNode, u8, u16le


class HIDDescriptor(DescriptorNode):
    """HID Class descriptor (bDescriptorType=0x21). Describes HID specification version, country code, and the associated HID report descriptor."""

    def __init__(self, bcdHID=HID_BCD, bCountryCode=HID_COUNTRY_NONE,
                 bNumDescriptors=1, bDescriptorType=HID_DESC_TYPE_REPORT,
                 wDescriptorLength=0, report_bytes=None, name=''):
        super().__init__(name)
        self.bcdHID = bcdHID
        self.bCountryCode = bCountryCode
        self.bNumDescriptors = bNumDescriptors
        self.bDescriptorType = bDescriptorType
        self.wDescriptorLength = wDescriptorLength
        self.report_bytes = report_bytes

    def _subfields(self):
        return [
            *u8('bDescriptorType', HID_DESC_TYPE_HID),
            *u16le('bcdHID', self.bcdHID),
            *u8('bCountryCode', self.bCountryCode),
            *u8('bNumDescriptors', self.bNumDescriptors),
            *u8('bDescriptorType2', self.bDescriptorType),
            *u16le('wDescriptorLength', self.wDescriptorLength),
        ]
