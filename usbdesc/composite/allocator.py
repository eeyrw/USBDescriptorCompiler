"""ResourceAllocator — auto-assigns USB resource IDs for building composite devices.

Tracks interface numbers, endpoint addresses (OUT/IN), terminal/unit/clock
entity IDs, MIDI jack IDs, and string descriptor indices. All allocation
methods return a monotonically increasing ID and advance the counter.
"""


class ResourceAllocator:
    """Auto-assigns USB resource IDs for building composite devices.

    Attributes:
        ep_out_base: Starting number for OUT endpoint addresses.
        ep_in_base: Starting number for IN endpoint addresses.
    """

    def __init__(self, ep_out_base=1, ep_in_base=1):
        self._iface = 0
        self._ep_out = ep_out_base
        self._ep_in = ep_in_base
        self._entity_id = 0
        self._jack_id = 0
        self._reserved_out = set()
        self._reserved_in = set()
        self._string_idx = 0
        self._strings = {}
        self._iface_count = 0

    def alloc_interface(self):
        """Allocate the next available interface number."""
        n = self._iface
        self._iface += 1
        self._iface_count += 1
        return n

    def alloc_ep_out(self):
        """Allocate the next available OUT endpoint address (0x0N, no direction bit)."""
        while self._ep_out in self._reserved_out:
            self._ep_out += 1
        n = self._ep_out
        self._ep_out += 1
        return n

    def alloc_ep_in(self):
        """Allocate the next available IN endpoint address (0x8N, with direction bit)."""
        while self._ep_in in self._reserved_in:
            self._ep_in += 1
        n = 0x80 | self._ep_in
        self._ep_in += 1
        return n

    def reserve_ep_out(self, addr):
        """Reserve a specific OUT endpoint address so alloc won't return it."""
        self._reserved_out.add(addr)

    def reserve_ep_in(self, addr):
        """Reserve a specific IN endpoint address so alloc won't return it."""
        self._reserved_in.add(addr & 0x7F)

    def alloc_entity_id(self):
        """Allocate the next audio entity ID (shared by terminals, units, clocks)."""
        self._entity_id += 1
        return self._entity_id

    def alloc_terminal_id(self):
        """Allocate the next audio terminal ID (alias for alloc_entity_id)."""
        return self.alloc_entity_id()

    def alloc_unit_id(self):
        """Allocate the next audio unit ID (alias for alloc_entity_id)."""
        return self.alloc_entity_id()

    def alloc_clock_id(self):
        """Allocate the next audio clock source ID (alias for alloc_entity_id)."""
        return self.alloc_entity_id()

    def alloc_jack_id(self):
        """Allocate the next MIDI jack ID."""
        self._jack_id += 1
        return self._jack_id

    def alloc_string(self, text=''):
        """Allocate a string descriptor index, optionally storing the string text."""
        self._string_idx += 1
        i = self._string_idx
        if text:
            self._strings[i] = text
        return i

    def interface_count(self):
        """Return the total number of allocated interfaces."""
        return self._iface_count

    def string_map(self):
        """Return a copy of the stored string index-to-text mapping."""
        return dict(self._strings)
