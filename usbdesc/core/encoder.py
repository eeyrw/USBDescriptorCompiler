"""Descriptor encoding utilities.

Provides DescriptorEncoder, a simple encoder that serializes a mix of
DescriptorNode objects and raw bytes/bytearrays into a flat binary blob.
"""

from usbdesc.core.base import DescriptorNode


class DescriptorEncoder:
    """Serializes a list of descriptors and raw byte chunks into bytes.

    Accepts any mix of ``DescriptorNode`` instances (which provide their
    own ``encode()`` method) and ``bytes``/``bytearray`` objects (included
    as-is). This allows the user to compose a full descriptor set by
    concatenating structured descriptors with raw binary data (e.g. HID
    report descriptors).
    """

    def encode_nodes(self, nodes):
        """Encode a sequence of descriptors and byte chunks.

        Parameters
        ----------
        nodes : list
            A list of ``DescriptorNode`` instances, ``bytes``, or
            ``bytearray`` objects.

        Returns
        -------
        bytes
            The concatenated binary output.

        Raises
        ------
        TypeError
            If any element is neither a ``DescriptorNode`` nor ``bytes``/``bytearray``.
        """
        result = bytearray()
        for n in nodes:
            if isinstance(n, DescriptorNode):
                result.extend(n.encode())
            elif isinstance(n, (bytes, bytearray)):
                result.extend(n)
            else:
                raise TypeError(f'Cannot encode {type(n)}')
        return bytes(result)
