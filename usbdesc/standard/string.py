from usbdesc.core.base import DescriptorNode
from usbdesc.core.base import u8

STRING_DESC_TYPE = 0x03
LANGID_EN_US = 0x0409


class StringDescriptor(DescriptorNode):
    """USB string descriptor (bDescriptorType=0x03).

    Encodes the given UTF-8 text as UTF-16LE.
    Index 0 is reserved for the language ID array; pass raw bytes.
    """

    def __init__(self, text, index=0, name=''):
        super().__init__(name)
        self.index = index
        if index == 0:
            self._raw = text   # raw bytes for LANGID array
        else:
            self._raw = text.encode('utf-16-le')
        self._decoded = text if index != 0 else None

    def _subfields(self):
        if self.index == 0:
            total = len(self._raw) // 2
            fields = [*u8('bDescriptorType', STRING_DESC_TYPE)]
            for i in range(total):
                lo = self._raw[i * 2]
                hi = self._raw[i * 2 + 1]
                val = lo | (hi << 8)
                fields.extend([*u8(f'wLANGID[{i}][0]', lo),
                               *u8(f'wLANGID[{i}][1]', hi)])
            return fields
        else:
            fields = [*u8('bDescriptorType', STRING_DESC_TYPE)]
            for i, b in enumerate(self._raw):
                fields.extend(u8(f'bString[{i}]', b))
            return fields


def langid_descriptor(langids=(LANGID_EN_US,)):
    """String descriptor for index 0 — language ID array.

    ``langids``: tuple of 16-bit LANGID values (default: US English 0x0409).
    """
    total = len(langids)
    buf = bytes()
    for lid in langids:
        buf += bytes([lid & 0xFF, (lid >> 8) & 0xFF])
    return StringDescriptor(buf, index=0, name='String LANGIDs')
