"""Export descriptor nodes as raw Python bytes."""

from usbdesc.core.base import DescriptorNode


class PythonBytesExporter:
    """Export descriptor nodes as raw bytes.

    Produces a flat byte sequence suitable for runtime transfer or
    binary file output.
    """
    def export(self, nodes):
        """Encode a list of descriptor nodes into a single bytes object.

        Each ``DescriptorNode`` is encoded via its ``encode()`` method;
        raw ``bytes`` or ``bytearray`` objects are appended as-is.
        Returns a concatenated ``bytes`` result.
        """
        result = bytearray()
        for n in nodes:
            if isinstance(n, DescriptorNode):
                result.extend(n.encode())
            elif isinstance(n, (bytes, bytearray)):
                result.extend(n)
        return bytes(result)
