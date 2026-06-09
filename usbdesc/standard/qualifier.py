"""USB Device Qualifier Descriptor (bDescriptorType=0x06).

Defined in USB Specification 2.0, Section 9.6.2. The Device Qualifier
Descriptor describes device capabilities that would change if the device
were operating at the alternate speed. It is required for USB 2.0 devices
that support both high-speed and full-speed operation. A USB 1.x host
ignores this descriptor.
"""

from usbdesc.core.types import DESC_TYPE_DEVICE_QUAL
from usbdesc.core.base import DescriptorNode, u8, u16le


class DeviceQualifierDescriptor(DescriptorNode):
    """USB Device Qualifier Descriptor (bDescriptorType=0x06).

    Describes the device capabilities at the "other" speed (the speed not
    currently in use). For example, when a high-speed capable device is
    operating at full-speed, the qualifier describes how it would behave
    at high-speed. Only devices with ``bcdUSB >= 0x0200`` need to support
    the GetDescriptor(DEVICE_QUALIFIER) request.

    Contains a subset of DeviceDescriptor fields plus a reserved byte to
    reach the required 10-byte length.

    USB Specification 2.0, Section 9.6.2.
    """

    def __init__(self, bDeviceClass=0x00, bDeviceSubClass=0x00,
                 bDeviceProtocol=0x00, bMaxPacketSize0=64,
                 bNumConfigurations=1, bcdUSB=0x0200, name=''):
        """Create a Device Qualifier Descriptor.

        Parameters
        ----------
        bDeviceClass : int
            Device class code at the other speed.
        bDeviceSubClass : int
            Device subclass code at the other speed.
        bDeviceProtocol : int
            Device protocol code at the other speed.
        bMaxPacketSize0 : int
            Maximum control endpoint 0 packet size at the other speed
            (8, 16, 32, or 64 for full-speed; 64 for high-speed).
        bNumConfigurations : int
            Number of configurations at the other speed (must match the
            number in the Device Descriptor if the device has an
            Other Speed Configuration Descriptor).
        bcdUSB : int
            BCD USB specification version (e.g. 0x0200 for USB 2.0).
        name : str
            Optional descriptor name for debugging.
        """
        super().__init__(name)
        self.bDeviceClass = bDeviceClass
        self.bDeviceSubClass = bDeviceSubClass
        self.bDeviceProtocol = bDeviceProtocol
        self.bMaxPacketSize0 = bMaxPacketSize0
        self.bNumConfigurations = bNumConfigurations
        self.bcdUSB = bcdUSB

    def _subfields(self):
        return [
            *u8('bDescriptorType', DESC_TYPE_DEVICE_QUAL),
            *u16le('bcdUSB', self.bcdUSB),
            *u8('bDeviceClass', self.bDeviceClass),
            *u8('bDeviceSubClass', self.bDeviceSubClass),
            *u8('bDeviceProtocol', self.bDeviceProtocol),
            *u8('bMaxPacketSize0', self.bMaxPacketSize0),
            *u8('bNumConfigurations', self.bNumConfigurations),
            *u8('bReserved', 0),
        ]
