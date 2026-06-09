"""USB Standard Interface Descriptor (bDescriptorType=0x04).

Defined in USB Specification 2.0, Section 9.6.5. The Interface Descriptor
describes a specific interface within a configuration, including the number
of endpoints it uses, its class/subclass/protocol codes, and its alternate
setting index. A configuration can contain multiple interfaces, and each
interface may have multiple alternate settings (e.g. for bandwidth management
in USB audio devices).
"""

from usbdesc.core.types import DESC_TYPE_INTERFACE
from usbdesc.core.base import DescriptorNode, u8


class InterfaceDescriptor(DescriptorNode):
    """USB Interface Descriptor (bDescriptorType=0x04).

    Describes a USB interface within a configuration, specifying its
    class, subclass, and protocol codes, the number of endpoints it
    contains, and its alternate setting index. Interfaces with alternate
    setting 0 are required; alternate settings > 0 represent device
    operating modes that can be selected dynamically (e.g. zero-bandwidth
    audio interface vs. active audio streaming interface).

    USB Specification 2.0, Section 9.6.5.
    """

    def __init__(self, bInterfaceNumber=0, bAlternateSetting=0,
                 bNumEndpoints=0, bInterfaceClass=0x00, bInterfaceSubClass=0x00,
                 bInterfaceProtocol=0x00, iInterface=0, name=''):
        """Create an Interface Descriptor.

        Parameters
        ----------
        bInterfaceNumber : int
            Interface number (0-based), identifying this interface within
            the configuration.
        bAlternateSetting : int
            Alternate setting index for this interface. Setting 0 is the
            default; higher values provide alternate operating modes.
        bNumEndpoints : int
            Number of endpoints used by this interface (excluding endpoint 0).
        bInterfaceClass : int
            USB-IF class code (e.g. 0x01 for Audio, 0x03 for HID, 0x02 for
            CDC). 0x00 is reserved per the specification for interface
            descriptors when bDeviceClass is not 0x00.
        bInterfaceSubClass : int
            USB-IF subclass code (class-specific).
        bInterfaceProtocol : int
            USB-IF protocol code (class-specific).
        iInterface : int
            String descriptor index for interface name (0 if none).
        name : str
            Optional descriptor name for debugging.
        """
        super().__init__(name)
        self.bInterfaceNumber = bInterfaceNumber
        self.bAlternateSetting = bAlternateSetting
        self.bNumEndpoints = bNumEndpoints
        self.bInterfaceClass = bInterfaceClass
        self.bInterfaceSubClass = bInterfaceSubClass
        self.bInterfaceProtocol = bInterfaceProtocol
        self.iInterface = iInterface

    def _subfields(self):
        return [
            *u8('bDescriptorType', DESC_TYPE_INTERFACE),
            *u8('bInterfaceNumber', self.bInterfaceNumber),
            *u8('bAlternateSetting', self.bAlternateSetting),
            *u8('bNumEndpoints', self.bNumEndpoints),
            *u8('bInterfaceClass', self.bInterfaceClass),
            *u8('bInterfaceSubClass', self.bInterfaceSubClass),
            *u8('bInterfaceProtocol', self.bInterfaceProtocol),
            *u8('iInterface', self.iInterface),
        ]
