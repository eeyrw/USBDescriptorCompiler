"""Foundation layer for USB descriptor encoding.

Defines the core data model (Field namedtuple), multi-byte little-endian field
helper functions, well-known USB constants, and the DescriptorNode base class that
all descriptor types inherit from. DescriptorNode provides automatic bLength
calculation and byte-level serialization.
"""

from collections import namedtuple

Field = namedtuple('Field', ['name', 'value', 'size'])
"""A single named field within a USB descriptor.

Attributes
----------
name : str
    Human-readable field name (e.g. ``'bLength'``, ``'wMaxPacketSize[0]'``).
value : int
    The byte value to be serialized (0-255).
size : int
    The size of this field in bytes (typically 1).
"""


def u8(name, value):
    """Create a single-byte field.

    Parameters
    ----------
    name : str
        Field name.
    value : int
        Byte value (0-255).

    Returns
    -------
    list of Field
        A single-element list containing the field.
    """
    return [Field(name, value, 1)]


def u16le(name, value):
    """Create a 16-bit little-endian field (split into two byte fields).

    Parameters
    ----------
    name : str
        Field name. Individual byte sub-fields are named ``{name}[0]`` and
        ``{name}[1]``.
    value : int
        16-bit value.

    Returns
    -------
    list of Field
        Two fields representing the low and high bytes.
    """
    v = int(value)
    return [Field(f'{name}[0]', v & 0xFF, 1),
            Field(f'{name}[1]', (v >> 8) & 0xFF, 1)]


def u24le(name, value):
    """Create a 24-bit little-endian field (split into three byte fields).

    Parameters
    ----------
    name : str
        Field name.
    value : int
        24-bit value.

    Returns
    -------
    list of Field
        Three fields representing bytes 0-2 in little-endian order.
    """
    v = int(value)
    return [Field(f'{name}[0]', v & 0xFF, 1),
            Field(f'{name}[1]', (v >> 8) & 0xFF, 1),
            Field(f'{name}[2]', (v >> 16) & 0xFF, 1)]


def u32le(name, value):
    """Create a 32-bit little-endian field (split into four byte fields).

    Parameters
    ----------
    name : str
        Field name.
    value : int
        32-bit value.

    Returns
    -------
    list of Field
        Four fields representing bytes 0-3 in little-endian order.
    """
    v = int(value)
    return [Field(f'{name}[0]', v & 0xFF, 1),
            Field(f'{name}[1]', (v >> 8) & 0xFF, 1),
            Field(f'{name}[2]', (v >> 16) & 0xFF, 1),
            Field(f'{name}[3]', (v >> 24) & 0xFF, 1)]


def source_id_fields(baSourceID, name='baSourceID'):
    """Standard baSourceID / baCSourceID array field generation.

    Converts a list of clock/entity source IDs into individual byte fields,
    one per source element. Each element is rendered as ``{name}[i]``.

    Parameters
    ----------
    baSourceID : list of int
        List of source IDs to encode.
    name : str
        Base name for the fields (default ``'baSourceID'``).

    Returns
    -------
    list of Field
        One byte field per source ID element.
    """
    result = []
    for i, src_id in enumerate(baSourceID):
        result.extend(u8(f'{name}[{i}]', src_id))
    return result


def controls_per_channel_fields(controls_per_channel, prefix='bmaControls'):
    """Standard per-channel control bitmap fields (32-bit each).

    Index 0 is the master channel; subsequent indices are channel 1..N.

    Parameters
    ----------
    controls_per_channel : list of int
        List of 32-bit control bitmaps, one per channel.
    prefix : str
        Base name for the fields (default ``'bmaControls'``).

    Returns
    -------
    list of Field
        Four byte fields per channel, little-endian.
    """
    result = []
    for i, ctrl in enumerate(controls_per_channel):
        label = 'master' if i == 0 else f'ch{i}'
        result.extend(u32le(f'{prefix}[{label}]', ctrl))
    return result


# ─── well-known constants ────────────────────────────────────────────

MAX_CONTROL_ENDPOINT_SIZE = 64
"""Maximum USB control endpoint packet size in bytes (full-speed)."""

DEFAULT_CONTROL_ENDPOINT_SIZE = 64
"""Default control endpoint size (64 bytes, full-speed)."""

DEFAULT_AUDIO_SAMPLE_RATE = 48000
"""Default audio sample rate in Hz (48 kHz)."""

MAX_ISO_PACKET_PER_TXN = 1024
"""Maximum isochronous packet payload per transaction (microframe)."""

MAX_ISO_PACKET_MASK = 0x07FF
"""Bitmask for the 11-bit max packet size field in wMaxPacketSize."""

MAX_HS_TXN_BITS = 0x03
"""Bitmask for the 2-bit additional-transactions field in wMaxPacketSize."""

MAX_HS_TXN_COUNT = 3
"""Maximum number of additional transactions per microframe for HS isochronous."""


def hs_iso_packet_size(max_pkt, transactions=1):
    """High-Speed isochronous wMaxPacketSize encoding.

    Bits 0-10: max packet size in bytes (0..1024)
    Bits 11-12: additional transactions per microframe (0=1, 1=2, 2=3)
    Bits 13-15: reserved (must be 0)

    If max_pkt exceeds 1024, it is split across multiple transactions.

    Parameters
    ----------
    max_pkt : int
        Desired maximum packet size per microframe.
    transactions : int
        Number of transactions per microframe (1-3).

    Returns
    -------
    int
        Encoded wMaxPacketSize value suitable for HS isochronous endpoints.

    Raises
    ------
    ValueError
        If the required number of transactions exceeds MAX_HS_TXN_COUNT.
    """
    if max_pkt > MAX_ISO_PACKET_PER_TXN:
        txns_needed = (max_pkt + MAX_ISO_PACKET_PER_TXN - 1) // MAX_ISO_PACKET_PER_TXN
        if txns_needed > MAX_HS_TXN_COUNT:
            raise ValueError(
                f'max_pkt={max_pkt} requires {txns_needed} transactions '
                f'(max {MAX_HS_TXN_COUNT} allowed). '
                f'Reduce packet size or sample rate.'
            )
        if transactions < txns_needed:
            transactions = txns_needed
        pkt = (max_pkt + txns_needed - 1) // txns_needed
    else:
        pkt = max_pkt

    pkt = pkt & MAX_ISO_PACKET_MASK
    txn = (transactions - 1) & MAX_HS_TXN_BITS
    return pkt | (txn << 11)


class DescriptorNode:
    """Base class for all USB descriptor nodes.

    Subclasses define their descriptor-specific fields by overriding
    ``_subfields()``. The base class automatically prepends a ``bLength``
    field calculated as 1 + sum of all sub-field sizes.

    This is a zero-dependency design: calling ``fields()`` returns a list of
    ``Field`` namedtuples, and ``encode()`` serializes them to raw bytes.
    """

    def __init__(self, name=''):
        """Initialize a descriptor node.

        Parameters
        ----------
        name : str
            Optional human-readable name for this descriptor. Defaults to
            the class name (e.g. ``'InputTerminal'``).
        """
        self._name = name or self.__class__.__name__

    @property
    def name(self):
        """Human-readable name for this descriptor node."""
        return self._name

    def _subfields(self):
        """Return descriptor-specific fields (excluding bLength).

        Subclasses **must** override this method. The returned list must
        include all fields except ``bLength``, which is inserted
        automatically by ``fields()``.

        Returns
        -------
        list of Field
            Descriptor payload fields.

        Raises
        ------
        NotImplementedError
            If the subclass does not override this method.
        """
        raise NotImplementedError

    def fields(self):
        """Return the complete ordered list of fields including bLength.

        ``bLength`` is calculated as ``1 + sum of all sub-field sizes``
        and prepended to the sub-fields.

        Returns
        -------
        list of Field
            Complete descriptor fields, with ``bLength`` first.
        """
        sf = self._subfields()
        total = 1 + sum(f.size for f in sf)
        return [Field('bLength', total, 1)] + sf

    def encode(self):
        """Encode the descriptor to raw bytes.

        Returns
        -------
        bytes
            The binary USB descriptor (including bLength).
        """
        return bytes(f.value for f in self.fields())

    def __repr__(self):
        return f'<{self.name}>'
