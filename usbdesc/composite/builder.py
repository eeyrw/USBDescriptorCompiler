"""CompositeDevice — orchestrates full USB descriptor chains for multi-function devices.

Builds a complete DescriptorSet from registered function templates, handling
wTotalLength calculation, IAD insertion, BOS extraction, and USB 2.0 high-speed
descriptors (Device Qualifier + Other Speed Configuration).
"""

from usbdesc.standard.device import DeviceDescriptor
from usbdesc.standard.qualifier import DeviceQualifierDescriptor
from usbdesc.standard.config import ConfigurationDescriptor, OtherSpeedConfigurationDescriptor
from usbdesc.standard.interface import InterfaceDescriptor
from usbdesc.standard.iad import IADDescriptor
from usbdesc.standard.string import StringDescriptor, langid_descriptor

from usbdesc.core.types import (
    CLASS_AUDIO, CLASS_CDC, CLASS_CDC_DATA,
    AUDIO_SUBCLASS_CONTROL,
    CHANNEL_STEREO, CHANNEL_MONO,
    CONFIG_ATTR_BUS_POWERED,
    TERMINAL_TYPE_NAMES,
)

from usbdesc.device_class.audio.uac2 import ACHeader
from usbdesc.device_class.audio.uac1 import ACHeader as UAC1ACHeader
from usbdesc.device_class.webusb import BOSDescriptor

from usbdesc.composite.allocator import ResourceAllocator


class DescriptorSet:
    """USB descriptor groups matching GetDescriptor() request types.

    Each group corresponds to what the host receives from a distinct
    GetDescriptor() call during enumeration.

    Iteration yields all descriptors in a flat sequence (backward-compatible).
    """

    __slots__ = ('device', 'device_qualifier', 'configuration',
                 'other_speed_config', 'bos', 'strings')

    def __init__(self):
        self.device = None
        self.device_qualifier = None
        self.configuration = []       # [ConfigDesc, IAD, IF0, EP0, CS ..., IF1, ...]
        self.other_speed_config = None
        self.bos = []                 # [BOSDescriptor, Cap1, Cap2, ...]
        self.strings = {}             # {index: utf8_string}

    def __iter__(self):
        if self.device:
            yield self.device
        if self.device_qualifier:
            yield self.device_qualifier
        yield from self.configuration
        if self.other_speed_config:
            yield self.other_speed_config
        yield from self.bos

    def __len__(self):
        n = (1 if self.device else 0)
        n += (1 if self.device_qualifier else 0)
        n += len(self.configuration)
        n += (1 if self.other_speed_config else 0)
        n += len(self.bos)
        return n

    def __getitem__(self, idx):
        return list(self)[idx]


class CompositeDevice:
    """Orchestrates the full USB descriptor chain for a composite device.

    Maintains a list of function templates (added via ``add()``). On ``build()``,
    each function is called with the allocator and produces descriptor nodes;
    the builder then assembles them into a ``DescriptorSet`` with correct
    ``wTotalLength``, IAD descriptors for multi-interface functions, BOS &
    WebUSB capabilities, device descriptor, optional qualifier/other-speed for
    high-speed devices, and string descriptors (including language ID).

    Usage::

        dev = CompositeDevice(idVendor=0x1234, idProduct=0x5678,
                              manufacturer='Acme', product='Widget')
        dev.add(uac2_speaker)
        dev.add(cdc_acm)
        desc_set = dev.build()
    """

    def __init__(self, idVendor=0x0000, idProduct=0x0000,
                 bcdDevice=0x0100, bcdUSB=0x0200,
                 manufacturer='', product='', serial='',
                 bDeviceClass=0x00, bDeviceSubClass=0x00, bDeviceProtocol=0x00,
                 bMaxPacketSize0=64,
                 bmAttributes=CONFIG_ATTR_BUS_POWERED, bMaxPower=100,
                 ep_out_base=1, ep_in_base=1,
                 high_speed=False):
        """Create a new composite device builder.

        Args:
            idVendor: USB-IF assigned Vendor ID.
            idProduct: Product ID.
            bcdDevice: Device release number in BCD (e.g. 0x0100 for 1.00).
            bcdUSB: USB specification version in BCD (e.g. 0x0200 for 2.0).
            manufacturer: Manufacturer string (empty for no string).
            product: Product string (empty for no string).
            serial: Serial number string (empty for no string).
            bDeviceClass: Device class code (0x00 = use per-interface class).
            bDeviceSubClass: Device subclass code.
            bDeviceProtocol: Device protocol code.
            bMaxPacketSize0: Max packet size for endpoint 0 (8, 16, 32, or 64).
            bmAttributes: Configuration attributes (e.g. bus/self powered).
            bMaxPower: Max power consumption in 2 mA units (e.g. 100 = 200 mA).
            ep_out_base: First OUT endpoint address number (default 1).
            ep_in_base: First IN endpoint address number (default 1).
            high_speed: If True, generate device qualifier and other-speed
                        configuration for USB 2.0 high-speed operation.
        """
        self._vid = idVendor
        self._pid = idProduct
        self._bcd_device = bcdDevice
        self._bcd_usb = bcdUSB
        self._mfgr = manufacturer
        self._prod = product
        self._serial = serial
        self._dev_class = bDeviceClass
        self._dev_subclass = bDeviceSubClass
        self._dev_protocol = bDeviceProtocol
        self._max_pkt0 = bMaxPacketSize0
        self._bm_attrs = bmAttributes
        self._max_power = bMaxPower
        self._high_speed = high_speed
        self._alloc = ResourceAllocator(ep_out_base, ep_in_base)
        self._functions = []

    def add(self, func):
        """Register a function template to include in the composite device.

        Args:
            func: A callable ``f(rc: ResourceAllocator) -> list[DescriptorNode]``
                  that builds the function's descriptor chain.
        """
        self._functions.append(func)

    def build(self):
        """Build the complete descriptor set.

        Walks all registered functions to collect descriptor nodes, then:

        - Calculates AC header ``wTotalLength`` for UAC2/UAC1 control interfaces.
        - Extracts BOS/WebUSB descriptors into a separate group.
        - Inserts IAD descriptors for multi-interface functions (Audio, CDC).
        - Computes ``wTotalLength`` for the configuration descriptor.
        - Builds the device descriptor with string indices.
        - Builds string descriptors (language ID + stored strings).
        - If ``high_speed``, generates device qualifier and other-speed configuration.

        Returns:
            DescriptorSet: The complete descriptor hierarchy.
        """
        self._alloc._high_speed = self._high_speed
        nodes = []
        for f in self._functions:
            nodes.extend(f(self._alloc))

        ac_start = -1
        for i, n in enumerate(nodes):
            if isinstance(n, InterfaceDescriptor) and getattr(n, 'bInterfaceSubClass', 0) == AUDIO_SUBCLASS_CONTROL:
                ac_start = i
            elif isinstance(n, InterfaceDescriptor) and ac_start >= 0:
                acc_len = sum(len(nodes[j].encode()) for j in range(ac_start + 1, i))
                for j in range(ac_start, i):
                    if isinstance(nodes[j], (ACHeader, UAC1ACHeader)):
                        nodes[j].wTotalLength = acc_len
                ac_start = -1
        if ac_start >= 0:
            acc_len = sum(len(nodes[j].encode()) for j in range(ac_start + 1, len(nodes)))
            for j in range(ac_start, len(nodes)):
                if isinstance(nodes[j], (ACHeader, UAC1ACHeader)):
                    nodes[j].wTotalLength = acc_len

        bos_nodes = []
        config_nodes = []
        i = 0
        while i < len(nodes):
            n = nodes[i]
            if isinstance(n, BOSDescriptor):
                bos_cap_len = 0
                bos_nodes.append(n)
                i += 1
                while i < len(nodes):
                    cap = nodes[i]
                    dt = int(cap.fields()[1].value) if len(cap.fields()) > 1 else 0
                    if dt == 0x10:
                        bos_nodes.append(cap)
                        bos_cap_len += len(cap.encode())
                        i += 1
                    else:
                        break
                n.wTotalLength = 5 + bos_cap_len
            else:
                config_nodes.append(n)
                i += 1
        nodes = config_nodes

        iad_insertions = []
        i = 0
        while i < len(nodes):
            if isinstance(nodes[i], InterfaceDescriptor):
                ncls = getattr(nodes[i], 'bInterfaceClass', 0)
                nsub = getattr(nodes[i], 'bInterfaceSubClass', 0)
                is_iad_start = False
                iad_class = 0
                iad_subclass = 0
                iad_proto = 0
                iad_name = ''

                if ncls == CLASS_AUDIO and nsub == AUDIO_SUBCLASS_CONTROL:
                    is_iad_start = True
                    iad_class = CLASS_AUDIO
                    iad_subclass = AUDIO_SUBCLASS_CONTROL
                    iad_proto = getattr(nodes[i], 'bInterfaceProtocol', 0)
                    iad_name = 'Audio IAD'
                elif ncls == CLASS_CDC:
                    is_iad_start = True
                    iad_class = CLASS_CDC
                    iad_subclass = nsub
                    iad_proto = getattr(nodes[i], 'bInterfaceProtocol', 0)
                    iad_name = 'CDC IAD'

                if is_iad_start:
                    first_if = getattr(nodes[i], 'bInterfaceNumber', 0)
                    start_class = ncls
                    seen_ifaces = {first_if}
                    j = i + 1
                    while j < len(nodes):
                        nxt = nodes[j]
                        if isinstance(nxt, InterfaceDescriptor):
                            ifc = getattr(nxt, 'bInterfaceClass', 0)
                            ifn = getattr(nxt, 'bInterfaceNumber', 0)
                            ifsc = getattr(nxt, 'bInterfaceSubClass', 0)
                            if start_class == CLASS_AUDIO and ifc != CLASS_AUDIO:
                                break
                            if start_class == CLASS_CDC and ifc not in (CLASS_CDC, CLASS_CDC_DATA):
                                break
                            if ifc == start_class and ifsc == nsub and ifn != first_if:
                                break
                            seen_ifaces.add(ifn)
                        j += 1
                    iad = IADDescriptor(
                        bFirstInterface=first_if,
                        bInterfaceCount=len(seen_ifaces),
                        bFunctionClass=iad_class,
                        bFunctionSubClass=iad_subclass,
                        bFunctionProtocol=iad_proto,
                        name=iad_name,
                    )
                    iad_insertions.append((i, iad))
                    i = j
                    continue
            i += 1
        for idx, iad in reversed(iad_insertions):
            nodes.insert(idx, iad)

        payload_len = sum(len(n.encode()) for n in nodes)
        config = ConfigurationDescriptor(
            wTotalLength=0,
            bNumInterfaces=self._alloc.interface_count(),
            bmAttributes=self._bm_attrs,
            bMaxPower=self._max_power,
            name='Configuration',
        )
        config_len = len(config.encode())
        total_len = config_len + payload_len
        config.wTotalLength = total_len
        iMfr = self._alloc.alloc_string(self._mfgr) if self._mfgr else 0
        iProd = self._alloc.alloc_string(self._prod) if self._prod else 0
        iSerial = self._alloc.alloc_string(self._serial) if self._serial else 0
        device = DeviceDescriptor(
            idVendor=self._vid, idProduct=self._pid,
            bcdDevice=self._bcd_device,
            bcdUSB=self._bcd_usb,
            bMaxPacketSize0=self._max_pkt0,
            iManufacturer=iMfr, iProduct=iProd, iSerialNumber=iSerial,
            bDeviceClass=self._dev_class,
            bDeviceSubClass=self._dev_subclass,
            bDeviceProtocol=self._dev_protocol,
            name='Device',
        )
        desc_set = DescriptorSet()
        desc_set.device = device
        desc_set.configuration = [config] + nodes
        desc_set.bos = bos_nodes

        str_nodes = [langid_descriptor()]
        for idx in sorted(self._alloc._strings):
            text = self._alloc._strings[idx]
            if text:
                str_nodes.append(StringDescriptor(text, index=idx,
                                                   name=f'String {idx}'))
        desc_set.strings = str_nodes

        if self._high_speed:
            fs_pkt0 = 64 if self._max_pkt0 >= 64 else self._max_pkt0
            desc_set.device_qualifier = DeviceQualifierDescriptor(
                bDeviceClass=self._dev_class,
                bDeviceSubClass=self._dev_subclass,
                bDeviceProtocol=self._dev_protocol,
                bMaxPacketSize0=fs_pkt0,
                bNumConfigurations=1,
                bcdUSB=self._bcd_usb,
                name='Device Qualifier',
            )
            desc_set.other_speed_config = OtherSpeedConfigurationDescriptor(
                wTotalLength=9,
                bNumInterfaces=self._alloc.interface_count(),
                bmAttributes=self._bm_attrs,
                bMaxPower=self._max_power,
                name='Other Speed Config',
            )
        return desc_set


def _channel_config(channels):
    """Map channel count to a USB channel config bitmap.

    Returns CHANNEL_MONO for 1, CHANNEL_STEREO for 2, and a bitmask
    ``(1 << channels) - 1`` for higher channel counts.
    """
    if channels == 1:
        return CHANNEL_MONO
    if channels == 2:
        return CHANNEL_STEREO
    if channels <= 0:
        return 0
    return (1 << channels) - 1


def terminal_type_desc(term_type):
    """Get a human-readable name for an audio terminal type."""
    return TERMINAL_TYPE_NAMES.get(term_type, 'Audio')
