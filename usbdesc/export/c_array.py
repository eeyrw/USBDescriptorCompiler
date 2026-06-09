"""C array exporter with rich field-level annotations."""

import re
from collections import namedtuple

from usbdesc.core.types import (
    DESC_TYPE_NAMES, CLASS_NAMES, ENDPOINT_ATTR_NAMES,
    AC_SUBTYPE_NAMES, AS_SUBTYPE_NAMES, MIDI_SUBTYPE_NAMES,
    CDC_SUBTYPE_NAMES, AUDIO_CATEGORY_NAMES, PROCESS_TYPE_NAMES,
    EFFECT_TYPE_NAMES, CLOCK_TYPE_NAMES, TERMINAL_TYPE_LOOKUP,
)

_MultiInfo = namedtuple('_MultiInfo', ['value', 'is_last', 'nbytes'])


def _decode_ep_attrs(val):
    """Decode endpoint bmAttributes byte into a human-readable string.

    Returns a string such as ``"Bulk"`` or ``"Isochronous Async"``
    by combining the transfer-type and synchronisation-type names.
    """
    t = val & 3
    sync = (val >> 2) & 3
    parts = [ENDPOINT_ATTR_NAMES.get(t, f'xfer=0x{t:X}')]
    if t == 1:
        sync_names = {0: 'NoSync', 1: 'Async', 2: 'Adaptive', 3: 'Sync'}
        parts.append(sync_names.get(sync, f'sync=0x{sync:X}'))
    return ' '.join(parts)


class CArrayExporter:
    """Export descriptor nodes as C byte arrays with rich annotations.

    Two export modes:
      - ``export(nodes)`` — legacy: single flat array from a node list
      - ``export_groups(desc_set)`` — one named array per GetDescriptor()
        request type (device / config / qualifier / other_speed / bos)
    """

    def __init__(self, indent=4, compact=False):
        self.indent = indent
        self.compact = compact

    # ── public API ──────────────────────────────────────────────────

    def export(self, nodes, array_name='usb_desc'):
        """Export a flat list of descriptor nodes as one C array."""
        return self._render_block(nodes, array_name)

    def export_groups(self, desc_set, prefix=''):
        """Export a DescriptorSet as separate named C arrays.

        Returns a string with one ``uint8_t array[] = {...}`` block per
        non-empty descriptor group, each prefixed by a comment identifying
        the GetDescriptor() request it serves.
        """
        blocks = []
        sep = '_' if prefix and not prefix.endswith('_') else ''
        p = f'{prefix}{sep}' if prefix else ''

        def _add(label, req_type, nodes, array_name):
            if not nodes:
                return
            if isinstance(nodes, list):
                header = f'{label}  (GetDescriptor({req_type}), {len(nodes)} nodes)'
            else:
                header = f'{label}  (GetDescriptor({req_type}))'
            blocks.append(f'/* {header} */')
            blocks.append(self._render_block(nodes, f'{p}{array_name}'))

        _add('Device',        'DEVICE',       desc_set.device,           'device_desc')
        _add('Device Qualifier', 'DEVICE_QUALIFIER',
             desc_set.device_qualifier, 'device_qualifier_desc')
        _add('Configuration',  'CONFIGURATION', desc_set.configuration,  'config_desc')
        _add('Other Speed Config', 'OTHER_SPEED_CONFIGURATION',
             desc_set.other_speed_config, 'other_speed_desc')
        _add('BOS',           'BOS',          desc_set.bos,             'bos_desc')

        if desc_set.strings:
            blocks.append('/* String Descriptors  (GetDescriptor(STRING)) */')
            for i, sd in enumerate(desc_set.strings):
                suffix = f'{p}string_{i}' if sd.index == 0 else f'{p}string_{sd.index}'
                blocks.append(self._render_block(sd, suffix))

        return '\n'.join(blocks)

    # ── internal ────────────────────────────────────────────────────

    def _render_block(self, nodes, array_name):
        """Render one or more descriptor nodes as a C byte-array block.

        Returns a string containing ``uint8_t <array_name>[] = { ... };``
        with per-byte field annotations and, unless ``compact`` mode is
        active, a commented header block for each descriptor.
        """
        if isinstance(nodes, list) and len(nodes) == 0:
            return ''
        lines = [f'uint8_t {array_name}[] = {{']
        offset = 0

        items = nodes if isinstance(nodes, list) else [nodes]
        for node in items:
            # descriptor header
            dname = node.name
            dsize = len(node.encode())
            dtype_byte = node.encode()[1] if dsize > 1 else 0
            dtype_name = DESC_TYPE_NAMES.get(dtype_byte, f'0x{dtype_byte:02X}')

            if self.compact:
                lines.append(
                    f'{" " * self.indent}/* [0x{offset:04X}] {dname} '
                    f'({dsize}B, {dtype_name}) */'
                )
            else:
                sep = '─' * 50
                lines.append(f'{" " * self.indent}/* {sep}')
                extra = ''
                if hasattr(node, '_decoded') and node._decoded:
                    extra = f'  "{node._decoded}"'
                lines.append(f'{" " * self.indent} * [{offset:4d}] {dname}{extra}')
                lines.append(f'{" " * self.indent} *   size = {dsize}  '
                             f'descriptor_type = {dtype_name}')
                lines.append(f'{" " * self.indent} * {sep} */')

            # field-level annotations
            fields = node.fields()
            for i, f in enumerate(fields):
                val = int(f.value)
                off = offset + i
                annot = self._annotate(f, fields, i, off, node)
                lines.append(f'{" " * self.indent}0x{val:02X},  // {annot}')

            offset += dsize

        lines.append('};')
        return '\n'.join(lines) + '\n'

    # ── annotation logic ────────────────────────────────────────────

    def _resolve_subtype_name(self, node, val):
        """Resolve bDescriptorSubtype using the node's class for context."""
        clsname = type(node).__name__

        # Audio AC nodes
        if clsname in ('ACHeader', 'InputTerminal', 'OutputTerminal',
                       'FeatureUnit', 'MixerUnit', 'SelectorUnit',
                       'EffectUnit', 'ProcessingUnit', 'ExtensionUnit',
                       'ClockSource', 'ClockSelector', 'ClockMultiplier',
                       'SampleRateConverter'):
            return AC_SUBTYPE_NAMES.get(val)

        # Audio AS nodes
        if clsname in ('ASGeneral', 'FormatTypeI', 'Encoder', 'Decoder',
                       '_CodingUnit'):
            return AS_SUBTYPE_NAMES.get(val)

        # MIDI nodes
        if clsname in ('MSHeader', 'MIDIInJack', 'MIDIOutJack',
                       'MIDIOutBulkEP', 'MIDIInBulkEP'):
            return MIDI_SUBTYPE_NAMES.get(val)

        # CDC nodes
        if clsname in ('CDCHeader', 'CDCCallManagement', 'CDCACM',
                       'CDCUnion'):
            return CDC_SUBTYPE_NAMES.get(val)

        # EP nodes
        if clsname in ('ClassSpecificIsoEP',):
            return 'EP_GENERAL' if val == 0x01 else None

        return None

    def _annotate(self, field, all_fields, idx, off, node):
        """Build a human-readable annotation string for a single field byte.

        Returns a string like ``"[  5] bLength = 9"``, resolving
        well-known field names (bLength, descriptor types, class codes,
        BCD values, terminal types, endpoint attributes, etc.) into
        informative labels.  Multi-byte fields show the combined value
        on the last byte only.
        """
        raw = field.name
        val = int(field.value)
        base = raw.split('[')[0] if '[' in raw else raw

        multi = self._multi_info(all_fields, idx, raw, base)

        parts = [f'[{off:4d}]']

        # ─── bLength ───
        if base == 'bLength':
            parts.append(f'bLength = {val}')

        # ─── descriptor type / subtype ───
        elif base in ('bDescriptorType', 'bDescriptorType2') and not raw.endswith(']'):
            tname = DESC_TYPE_NAMES.get(val)
            parts.append(f'{raw} = 0x{val:02X}' +
                         (f'  ({tname})' if tname else ''))

        elif base == 'bDescriptorSubtype':
            sname = self._resolve_subtype_name(node, val)
            parts.append(f'{raw} = 0x{val:02X}' +
                         (f'  ({sname})' if sname else ''))

        # ─── class / subclass / protocol ───
        elif base == 'bDeviceClass':
            cls_name = CLASS_NAMES.get(val)
            parts.append(f'{base} = {val}' + (f'  ({cls_name})' if cls_name else ''))

        elif base == 'bInterfaceClass':
            cls_name = CLASS_NAMES.get(val)
            parts.append(f'{base} = 0x{val:02X}  ({cls_name})' if cls_name
                         else f'{base} = 0x{val:02X}')

        elif base == 'bInterfaceSubClass':
            # disambiguate by looking at bInterfaceClass in previous fields
            icls = 0
            for f2 in all_fields:
                if f2.name == 'bInterfaceClass':
                    icls = int(f2.value)
                    break
            if icls == 0x01:  # Audio
                sub_map = {0x01: 'Control', 0x02: 'Streaming', 0x03: 'MIDI'}
            elif icls == 0x03:  # HID
                sub_map = {0x00: 'none', 0x01: 'Boot'}
            else:
                sub_map = {}
            sname = sub_map.get(val)
            parts.append(f'{base} = 0x{val:02X}' +
                         (f'  ({sname})' if sname else ''))

        elif base == 'bInterfaceProtocol':
            # disambiguate by looking at bInterfaceClass
            icls = 0
            for f2 in all_fields:
                if f2.name == 'bInterfaceClass':
                    icls = int(f2.value)
                    break
            if val == 0x20:
                parts.append(f'{base} = 0x{val:02X}  (UAC2)')
            elif icls == 0x03:  # HID
                proto_map = {0x00: 'none', 0x01: 'Keyboard', 0x02: 'Mouse'}
                pname = proto_map.get(val)
                parts.append(f'{base} = 0x{val:02X}' +
                             (f'  ({pname})' if pname else ''))
            else:
                parts.append(f'{base} = 0x{val:02X}')

        # ─── bcd fields (show decoded version) ───
        elif base in ('bcdUSB', 'bcdADC', 'bcdHID', 'bcdCDC', 'bcdMSC',
                      'bcdDevice'):
            if multi and multi.is_last:
                full = multi.value
                parts.append(f'{base} = 0x{full:04X}  (v{full>>8}.{full&0xFF:02d})')
            else:
                parts.append(f'{raw} = 0x{val:02X}')

        # ─── wTotalLength ───
        elif base == 'wTotalLength':
            if multi and multi.is_last:
                parts.append(f'{base} = {multi.value}')
            else:
                parts.append(f'{raw} = 0x{val:02X}')

        # ─── wDescriptorLength ───
        elif base == 'wDescriptorLength':
            if multi and multi.is_last:
                parts.append(f'{base} = {multi.value}')
            else:
                parts.append(f'{raw} = 0x{val:02X}')

        # ─── vendor / product id ───
        elif base in ('idVendor', 'idProduct'):
            if multi and multi.is_last:
                parts.append(f'{base} = 0x{multi.value:04X}')
            else:
                parts.append(f'{raw} = 0x{val:02X}')

        # ─── wTerminalType ───
        elif base == 'wTerminalType':
            if multi and multi.is_last:
                tname = TERMINAL_TYPE_LOOKUP.get(multi.value, '')
                parts.append(f'{base} = 0x{multi.value:04X}' +
                             (f'  ({tname})' if tname else ''))
            else:
                parts.append(f'{raw} = 0x{val:02X}')

        # ─── wMaxPacketSize ───
        elif base == 'wMaxPacketSize':
            if multi and multi.is_last:
                full = multi.value
                raw_pkt = full & 0x07FF
                txns = ((full >> 11) & 3) + 1
                if txns > 1:
                    parts.append(f'{base} = {raw_pkt} ×{txns} txns')
                else:
                    parts.append(f'{base} = {raw_pkt}')
            else:
                parts.append(f'{raw} = 0x{val:02X}')

        # ─── bmAttributes (context-dependent) ───
        elif base == 'bmAttributes':
            clsname = type(node).__name__
            if clsname == 'ClockSource':
                clock = val & 3
                sof = ' +SOF' if val & 4 else ''
                cname = CLOCK_TYPE_NAMES.get(clock, f'0x{clock:X}')
                parts.append(f'{base} = 0x{val:02X}  ({cname}{sof})')
            elif 'Endpoint' in clsname or clsname == 'EndpointDescriptor':
                parts.append(f'{base} = 0x{val:02X}  ({_decode_ep_attrs(val)})')
            elif 'Config' in clsname or 'Configuration' in clsname:
                bus = 'Bus-powered' if val & 0x80 else ''
                self_pwr = 'Self-powered' if val & 0x40 else ''
                rw = 'RemoteWakeup' if val & 0x20 else ''
                flags = [f for f in [bus, self_pwr, rw] if f]
                tag = ' '.join(flags) if flags else None
                parts.append(f'{base} = 0x{val:02X}  ({tag})' if tag
                             else f'{base} = 0x{val:02X}')
            else:
                parts.append(f'{base} = 0x{val:02X}')

        # ─── bCategory ───
        elif base == 'bCategory':
            cname = AUDIO_CATEGORY_NAMES.get(val, '')
            parts.append(f'{base} = {val}' +
                         (f'  ({cname})' if cname else ''))

        # ─── bmChannelConfig / wChannelConfig (multi-byte) ───
        elif base in ('bmChannelConfig', 'wChannelConfig'):
            if multi and multi.is_last:
                parts.append(f'{base} = 0x{multi.value:08X}')
            else:
                parts.append(f'{raw} = 0x{val:02X}')

        # ─── bmFormats ───
        elif base == 'bmFormats':
            if multi and multi.is_last:
                parts.append(f'{base} = 0x{multi.value:08X}')
            else:
                parts.append(f'{raw} = 0x{val:02X}')

        # ─── bmaControls (Feature/Effect unit) ───
        elif 'bmaControls' in base:
            parts.append(f'{raw} = 0x{val:02X}')

        # ─── bmControls (1-2 bytes) ───
        elif base == 'bmControls':
            if multi and multi.is_last and multi.value > 0xFF:
                parts.append(f'{base} = 0x{multi.value:04X}')
            else:
                parts.append(f'{raw} = 0x{val:02X}')

        # ─── HID protocol ───
        elif base.startswith('bInterfaceProtocol'):
            pass  # already handled above

        # ─── wProcessType / wEffectType / wExtensionCode ───
        elif base in ('wProcessType', 'wEffectType', 'wExtensionCode',
                      'wEncoderType', 'wDecoderType'):
            if multi and multi.is_last:
                parts.append(f'{base} = 0x{multi.value:04X}')
            else:
                parts.append(f'{raw} = 0x{val:02X}')

        # ─── wFormatTag ───
        elif base == 'wFormatTag':
            if multi and multi.is_last:
                parts.append(f'{base} = 0x{multi.value:04X}')
            else:
                parts.append(f'{raw} = 0x{val:02X}')

        # ─── bString (string descriptor) — suppress per-byte annotation,
        #     the full string is shown in the block header instead.
        elif base == 'bString':
            pass  # fall through to default

        # ─── default single byte ───
        else:
            if multi and multi.is_last:
                parts.append(f'{raw}')
            else:
                parts.append(f'{raw} = {val}')

        # ─── Edge case: catch "bInterfaceProtocol" at the end if not caught
        # by the specific check above (the raw name might have index)

        return '  '.join(parts)

    # ── multi-byte tracking ─────────────────────────────────────────

    def _multi_info(self, fields, idx, raw_name, base_name):
        """Determine if this field is part of a multi-byte group.

        Returns a _MultiInfo or None.
        """
        if '[' not in raw_name:
            return None

        m = re.match(r'(\w+)\[(\d+)\]', raw_name)
        if not m:
            return None

        bn = m.group(1)
        cur_idx = int(m.group(2))

        # Collect all bytes of this field group
        bytes_of_group = []
        for i, f in enumerate(fields):
            fname = f.name
            if re.match(rf'{re.escape(bn)}\[\d+\]', fname):
                bytes_of_group.append(int(f.value))

        # Determine size: look for consecutive indices
        nbytes = len(bytes_of_group)

        # Reconstruct full little-endian value
        if nbytes <= 1:
            return None
        full = 0
        for b in range(nbytes):
            full |= bytes_of_group[b] << (8 * b)

        # Is this the last byte in the group?
        # Check if the next field belongs to the same group
        if idx + 1 < len(fields):
            next_name = fields[idx + 1].name
            next_match = re.match(rf'{re.escape(bn)}\[(\d+)\]', next_name)
            is_last = not bool(next_match)
        else:
            is_last = True

        mi = _MultiInfo(value=full, is_last=is_last, nbytes=nbytes)
        return mi
