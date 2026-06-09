"""Export descriptor nodes as structured JSON."""

import json as _json

from usbdesc.core.base import DescriptorNode


class JsonExporter:
    """Export descriptor nodes as structured JSON.

    Each descriptor node is represented as an object with name, fields
    (name+value pairs), and raw bytes.  Useful for debugging and
    inspection.
    """
    def export(self, nodes):
        """Encode a list of descriptor nodes into a JSON string.

        Each ``DescriptorNode`` is serialised as a dict with ``name``,
        ``fields`` (a list of ``{name, value}`` objects), and ``raw``
        (a list of byte values).  Returns an indented JSON string.
        """
        result = []
        for n in nodes:
            if isinstance(n, DescriptorNode):
                node_data = {
                    'name': n.name,
                    'fields': [{'name': f.name, 'value': f.value}
                               for f in n.fields()],
                    'raw': list(n.encode()),
                }
                result.append(node_data)
        return _json.dumps(result, indent=2)
