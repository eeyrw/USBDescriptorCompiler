"""USB Standard Device Descriptor (bDescriptorType=0x01).

Defined in USB Specification 2.0, Section 9.6.1. The Device Descriptor
describes the overall USB device capabilities, including vendor/product
identification, USB specification compliance level, and the number of
supported configurations. Every USB device must provide exactly one
Device Descriptor.

See also: DeviceQualifierDescriptor (for USB 2.0 high-speed capable devices).
"""

from usbdesc.core.types import DESC_TYPE_DEVICE
from usbdesc.core.base import DescriptorNode, u8, u16le


class DeviceDescriptor(DescriptorNode):
    """USB Device Descriptor (bDescriptorType=0x01).

    Describes the overall USB device capabilities such as vendor and
    product IDs, supported USB specification version (bcdUSB), device
    class information, maximum control endpoint packet size, and the
    number of available configurations.

    USB Specification 2.0, Section 9.6.1.
    """

    def __init__(self, idVendor=0x0000, idProduct=0x0000, bcdDevice=0x0000,
                 iManufacturer=0, iProduct=0, iSerialNumber=0,
                 bNumConfigurations=1, bDeviceClass=0x00, bDeviceSubClass=0x00,
                 bDeviceProtocol=0x00, bMaxPacketSize0=64,
                 bcdUSB=0x0200, name=''):
        """Create a Device Descriptor.

        Parameters
        ----------
        idVendor : int
            16-bit USB-IF assigned Vendor ID (VID).
        idProduct : int
            16-bit vendor-assigned Product ID (PID).
        bcdDevice : int
            16-bit BCD device release number.
        iManufacturer : int
            String descriptor index for manufacturer name (0 if none).
        iProduct : int
            String descriptor index for product name (0 if none).
        iSerialNumber : int
            String descriptor index for serial number (0 if none).
        bNumConfigurations : int
            Number of configurations this device supports.
        bDeviceClass : int
            USB-IF class code (0x00 = per-interface, 0xFF = vendor-specific).
        bDeviceSubClass : int
            USB-IF subclass code.
        bDeviceProtocol : int
            USB-IF protocol code.
        bMaxPacketSize0 : int
            Maximum control endpoint 0 packet size (8, 16, 32, or 64).
        bcdUSB : int
            BCD USB specification version (e.g. 0x0200 for USB 2.0).
        name : str
            Optional descriptor name for debugging.
        """
        super().__init__(name)
        self.idVendor = idVendor
        self.idProduct = idProduct
        self.bcdDevice = bcdDevice
        self.iManufacturer = iManufacturer
        self.iProduct = iProduct
        self.iSerialNumber = iSerialNumber
        self.bNumConfigurations = bNumConfigurations
        self.bDeviceClass = bDeviceClass
        self.bDeviceSubClass = bDeviceSubClass
        self.bDeviceProtocol = bDeviceProtocol
        self.bMaxPacketSize0 = bMaxPacketSize0
        self.bcdUSB = bcdUSB

    def _subfields(self):
        return [
            *u8('bDescriptorType', DESC_TYPE_DEVICE),
            *u16le('bcdUSB', self.bcdUSB),
            *u8('bDeviceClass', self.bDeviceClass),
            *u8('bDeviceSubClass', self.bDeviceSubClass),
            *u8('bDeviceProtocol', self.bDeviceProtocol),
            *u8('bMaxPacketSize0', self.bMaxPacketSize0),
            *u16le('idVendor', self.idVendor),
            *u16le('idProduct', self.idProduct),
            *u16le('bcdDevice', self.bcdDevice),
            *u8('iManufacturer', self.iManufacturer),
            *u8('iProduct', self.iProduct),
            *u8('iSerialNumber', self.iSerialNumber),
            *u8('bNumConfigurations', self.bNumConfigurations),
        ]
