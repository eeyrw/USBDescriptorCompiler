"""USB Standard Configuration Descriptor (bDescriptorType=0x02).

Defined in USB Specification 2.0, Section 9.6.3. The Configuration
Descriptor describes a specific device configuration, including power
requirements and the number of interfaces supported. A USB device may
support multiple configurations, but only one is active at a time.

Also provides the Other Speed Configuration Descriptor (bDescriptorType=0x07),
used by USB 2.0 high-speed capable devices to describe the alternate-speed
configuration.
"""

from usbdesc.core.types import DESC_TYPE_CONFIGURATION, DESC_TYPE_OTHER_SPEED, CONFIG_ATTR_BUS_POWERED
from usbdesc.core.base import DescriptorNode, u8, u16le


class ConfigurationDescriptor(DescriptorNode):
    """USB Configuration Descriptor (bDescriptorType=0x02).

    Describes a specific USB device configuration: its power requirements,
    the number of interfaces it contains, and its total descriptor length
    (wTotalLength, which includes all interface and endpoint descriptors
    nested within this configuration).

    USB Specification 2.0, Section 9.6.3.
    """

    def __init__(self, wTotalLength=0, bNumInterfaces=0, iConfiguration=0,
                 bConfigurationValue=1, bmAttributes=CONFIG_ATTR_BUS_POWERED,
                 bMaxPower=50, desc_type=DESC_TYPE_CONFIGURATION, name=''):
        """Create a Configuration Descriptor.

        Parameters
        ----------
        wTotalLength : int
            16-bit total length of this configuration's descriptor set
            (including all nested interface, endpoint, and class-specific
            descriptors). Set automatically by CompositeDevice; specify 0
            when constructing manually.
        bNumInterfaces : int
            Number of interfaces in this configuration.
        iConfiguration : int
            String descriptor index for configuration name (0 if none).
        bConfigurationValue : int
            Value used by SetConfiguration to select this configuration.
        bmAttributes : int
            Bitmap of configuration attributes (bus/self-powered, remote wakeup).
            Use CONFIG_ATTR_* constants from usbdesc.core.types.
        bMaxPower : int
            Maximum power consumption in units of 2 mA (e.g. 50 = 100 mA).
        desc_type : int
            The descriptor type byte (0x02 for Configuration, 0x07 for
            Other Speed Configuration). Overridden by subclasses.
        name : str
            Optional descriptor name for debugging.
        """
        super().__init__(name)
        self.wTotalLength = wTotalLength
        self.bNumInterfaces = bNumInterfaces
        self.iConfiguration = iConfiguration
        self.bConfigurationValue = bConfigurationValue
        self.bmAttributes = bmAttributes
        self.bMaxPower = bMaxPower
        self.desc_type = desc_type

    def _subfields(self):
        return [
            *u8('bDescriptorType', self.desc_type),
            *u16le('wTotalLength', self.wTotalLength),
            *u8('bNumInterfaces', self.bNumInterfaces),
            *u8('bConfigurationValue', self.bConfigurationValue),
            *u8('iConfiguration', self.iConfiguration),
            *u8('bmAttributes', self.bmAttributes),
            *u8('bMaxPower', self.bMaxPower),
        ]


class OtherSpeedConfigurationDescriptor(ConfigurationDescriptor):
    """USB Other Speed Configuration Descriptor (bDescriptorType=0x07).

    Used by USB 2.0 devices operating at high-speed that also support
    full-speed operation (or vice versa). Reports the configuration that
    would be active at the "other" speed not currently in use. Structurally
    identical to ConfigurationDescriptor but reports descriptor type 0x07.

    USB Specification 2.0, Section 9.6.4.
    """

    def __init__(self, wTotalLength=0, bNumInterfaces=0, iConfiguration=0,
                 bConfigurationValue=1, bmAttributes=CONFIG_ATTR_BUS_POWERED,
                 bMaxPower=50, name=''):
        """Create an Other Speed Configuration Descriptor.

        Parameters match ConfigurationDescriptor exactly, but the
        descriptor type is fixed to 0x07 (DESC_TYPE_OTHER_SPEED).

        Parameters
        ----------
        wTotalLength : int
            Total length of the other-speed configuration descriptor set.
        bNumInterfaces : int
            Number of interfaces in this configuration.
        iConfiguration : int
            String descriptor index for configuration name.
        bConfigurationValue : int
            Configuration value for SetConfiguration.
        bmAttributes : int
            Configuration attributes bitmap.
        bMaxPower : int
            Maximum power consumption in 2 mA units.
        name : str
            Optional descriptor name for debugging.
        """
        super().__init__(wTotalLength, bNumInterfaces, iConfiguration,
                         bConfigurationValue, bmAttributes, bMaxPower,
                         desc_type=DESC_TYPE_OTHER_SPEED, name=name)
