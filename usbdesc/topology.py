"""USB descriptor topology — complete connection diagram including standard descriptors.

Usage:
    from usbdesc.topology import TopologyGraph
    graph = TopologyGraph(nodes)
    print(graph.to_ascii())       # ASCII tree of full descriptor hierarchy
    print(graph.to_mermaid())     # Mermaid diagram (for markdown)
"""

from usbdesc.core.types import (
    TERM_USB_STREAMING, CLOCK_INT_FIXED,
    CLASS_AUDIO, CLASS_HID, CLASS_CDC, CLASS_CDC_DATA,
    AUDIO_SUBCLASS_CONTROL, AUDIO_SUBCLASS_STREAMING, AUDIO_SUBCLASS_MIDI,
    EP_ATTR_ISOCHRONOUS, EP_ATTR_BULK, EP_ATTR_INTERRUPT,
    TERMINAL_TYPE_LOOKUP, CLOCK_TYPE_NAMES, EFFECT_TYPE_NAMES,
    PROCESS_TYPE_NAMES, ENDPOINT_ATTR_NAMES, CLASS_NAMES,
)

# Feature Unit control short names (matching 2-bit offset constants)
_FU_CTRL_NAMES = {
    0: 'Mute', 2: 'Vol', 4: 'Bass', 6: 'Mid', 8: 'Treb',
    10: 'GEQ', 12: 'AGC', 14: 'Dly', 16: 'Bst', 18: 'Loud',
    20: 'InGain', 22: 'Pad', 24: 'Phase', 26: 'Under', 28: 'Over',
    30: 'HPF',
}
from usbdesc.standard.device import DeviceDescriptor as _Device
from usbdesc.standard.qualifier import DeviceQualifierDescriptor as _DeviceQual
from usbdesc.standard.config import ConfigurationDescriptor as _ConfigDesc, OtherSpeedConfigurationDescriptor as _OtherSpeed
from usbdesc.standard.interface import InterfaceDescriptor as _IfaceDesc
from usbdesc.standard.endpoint import EndpointDescriptor as _EPDesc
from usbdesc.device_class.audio.uac2 import (
    InputTerminal as _IT, OutputTerminal as _OT, FeatureUnit as _FU,
    MixerUnit as _MU, SelectorUnit as _SU, EffectUnit as _EF,
    ProcessingUnit as _PU, ExtensionUnit as _XU,
    ClockSource as _Clock, ClockSelector as _CS, ClockMultiplier as _CM,
    SampleRateConverter as _SRC,
    ACHeader as _ACHdr, ASGeneral as _ASGen, FormatTypeI as _FmtI,
    ClassSpecificIsoEP as _IsoEP,
    MIDIInJack as _MJIn, MIDIOutJack as _MJOut,
    MIDIOutBulkEP as _MEPOut, MIDIInBulkEP as _MEPIn,
)
from usbdesc.device_class.hid import HIDDescriptor as _HIDDesc
from usbdesc.device_class.cdc import (
    CDCHeader as _CDCHeader, CDCCallManagement as _CDCCall,
    CDCACM as _CDCACM, CDCUnion as _CDCUnion,
)
from usbdesc.device_class.hid_report import parse_hid_report

_TERM_NAMES = dict(TERMINAL_TYPE_LOOKUP)
_TERM_NAMES[TERM_USB_STREAMING] = 'USB'

_IFACE_CLASS_NAMES = {k: v for k, v in CLASS_NAMES.items() if k != 0x00}
_IFACE_CLASS_NAMES[CLASS_CDC_DATA] = 'CDC-Data'
_IFACE_SUBCLASS_NAMES = {
    AUDIO_SUBCLASS_CONTROL: 'AC', AUDIO_SUBCLASS_STREAMING: 'AS',
    AUDIO_SUBCLASS_MIDI: 'MIDI',
}


class _Node:
    """Internal graph node representing a topology element."""
    __slots__ = ('kind', 'uid', 'label', 'sources', 'attrs', 'meta')
    def __init__(self, kind, uid, label='', sources=None, attrs=None, meta=''):
        self.kind = kind
        self.uid = uid
        self.label = label
        self.sources = sources or []
        self.attrs = attrs or {}
        self.meta = meta


class TopologyGraph:
    """Scans USB descriptor nodes and generates connection diagrams.

    Supports ASCII tree rendering and Mermaid markdown diagrams for audio
    topology (CLK→IT→FU→OT→AS→EP chains), MIDI jack routing, and full
    descriptor hierarchy.
    """
    def __init__(self, descriptors):
        """Build a topology graph from a flat list of descriptor nodes.

        Parses all descriptors, builds internal graph nodes with source
        relationships, then resolves wildcard references (``???#id``)
        into concrete connections.
        """
        self.nodes = {}
        self._hid_reports = []
        self._parse(descriptors)

    def _add(self, kind, uid, label='', sources=None, attrs=None, meta=''):
        """Add or merge a graph node of the given kind and unique ID.

        If a node with the same ``kind#uid`` key already exists, its
        label, sources, and attributes are merged rather than replaced.
        """
        key = f'{kind}#{uid}'
        if key in self.nodes:
            if label:
                self.nodes[key].label = label
            if sources:
                for s in sources:
                    if s not in self.nodes[key].sources:
                        self.nodes[key].sources.append(s)
            if attrs:
                self.nodes[key].attrs.update(attrs)
        else:
            self.nodes[key] = _Node(kind, uid, label, sources or [], attrs or {}, meta)

    def _parse(self, descriptors):
        """Parse a list of descriptors and build the internal graph.

        Uses a type-dispatch table (``_type_dispatch``) that maps each
        descriptor class to a private ``_handle_*`` method.  For each
        descriptor in the list, the matching handler is called.
        Standard interface descriptors also track the current interface
        key so that subsequent nodes (endpoints, audio units, etc.) can
        link back to it.  After scanning all descriptors, wildcard
        references (``???#id``) are resolved into concrete node keys.
        """
        _type_dispatch = {
            _Device: self._handle_device,
            _DeviceQual: self._handle_qualifier,
            _ConfigDesc: self._handle_config,
            _OtherSpeed: self._handle_other_speed,
            _IfaceDesc: self._handle_interface,
            _EPDesc: self._handle_endpoint,
            _IT: self._handle_input_terminal,
            _OT: self._handle_output_terminal,
            _FU: self._handle_feature_unit,
            _MU: self._handle_mixer_unit,
            _SU: self._handle_selector_unit,
            _EF: self._handle_effect_unit,
            _PU: self._handle_processing_unit,
            _XU: self._handle_extension_unit,
            _Clock: self._handle_clock_source,
            _CS: self._handle_clock_selector,
            _CM: self._handle_clock_multiplier,
            _SRC: self._handle_src,
            _ACHdr: self._handle_ac_header,
            _ASGen: self._handle_as_general,
            _FmtI: self._handle_format_type,
            _IsoEP: self._handle_iso_ep,
            _HIDDesc: self._handle_hid,
            _CDCHeader: self._handle_cdc,
            _CDCCall: self._handle_cdc,
            _CDCACM: self._handle_cdc,
            _CDCUnion: self._handle_cdc,
            _MJIn: self._handle_midi_in_jack,
            _MJOut: self._handle_midi_out_jack,
            _MEPOut: self._handle_midi_out_ep,
            _MEPIn: self._handle_midi_in_ep,
        }

        cur_iface_key = None
        cur_as_link = 0

        for n in descriptors:
            handler = None
            for cls, h in _type_dispatch.items():
                if isinstance(n, cls):
                    handler = h
                    break
            if handler:
                if isinstance(n, _ASGen):
                    cur_as_link = getattr(n, 'bTerminalLink', 0)
                if isinstance(n, _IsoEP):
                    result = handler(n, cur_iface_key, cur_as_link)
                else:
                    result = handler(n, cur_iface_key)
                if isinstance(n, _IfaceDesc):
                    cur_iface_key = result
                    cur_as_link = 0

        self._resolve_wildcards()

    def _handle_device(self, n, _prev):
        vid = n.idVendor if hasattr(n, 'idVendor') else getattr(n, 'idVendor', 0)
        pid = n.idProduct if hasattr(n, 'idProduct') else getattr(n, 'idProduct', 0)
        bcd = n.bcdUSB if hasattr(n, 'bcdUSB') else getattr(n, 'bcdUSB', 0)
        label = f'Device 0x{vid:04X}:0x{pid:04X} USB {bcd>>8}.{bcd&0xFF:02d}'
        self._add('DEV', 0, label, meta=f'VID={vid:04X} PID={pid:04X}')
        return 'DEV#0'

    def _handle_qualifier(self, n, _prev):
        bcd = n.bcdUSB if hasattr(n, 'bcdUSB') else getattr(n, 'bcdUSB', 0)
        label = f'Qualifier USB {bcd>>8}.{bcd&0xFF:02d}'
        self._add('QUAL', 0, label)
        return _prev

    def _handle_config(self, n, _prev):
        pwr = n.bMaxPower if hasattr(n, 'bMaxPower') else getattr(n, 'bMaxPower', 0)
        label = f'Config ({(pwr*2)}mA)'
        self._add('CFG', 0, label, sources=['DEV#0'], meta=f'bMaxPower={pwr}')
        return 'CFG#0'

    def _handle_other_speed(self, n, _prev):
        self._add('OS_CFG', 0, 'OtherSpeed Config', sources=['DEV#0'])
        return _prev

    def _handle_interface(self, n, _prev):
        num = getattr(n, 'bInterfaceNumber', 0)
        alt = getattr(n, 'bAlternateSetting', 0)
        ncls = getattr(n, 'bInterfaceClass', 0)
        nsub = getattr(n, 'bInterfaceSubClass', 0)
        cls_name = _IFACE_CLASS_NAMES.get(ncls, f'Class 0x{ncls:02X}')
        if ncls == CLASS_AUDIO:
            sub_name = _IFACE_SUBCLASS_NAMES.get(nsub, f'0x{nsub:02X}')
        else:
            sub_name = f'0x{nsub:02X}'
        label = f'IF{num}: {cls_name}/{sub_name}' if alt == 0 else f'IF{num}a{alt}: {cls_name}/{sub_name}'
        iface_key = f'IFACE#{num}#a{alt}'
        self.nodes[iface_key] = _Node('IFACE', num, label,
                                       sources=['CFG#0'],
                                       meta=f'class=0x{ncls:02X} subclass=0x{nsub:02X}')
        return iface_key

    def _handle_endpoint(self, n, cur_iface_key):
        ep = getattr(n, 'bEndpointAddress', 0)
        attrs = getattr(n, 'bmAttributes', 0)
        pkt = getattr(n, 'wMaxPacketSize', 0)
        is_in = bool(ep & 0x80)
        attr_name = ENDPOINT_ATTR_NAMES.get(attrs & 3, f'0x{attrs:02X}')
        label = f'EP {">>" if is_in else "<<"} 0x{ep:02X} ({attr_name},{pkt}B)'
        self._add('EP', ep, label,
                  sources=[cur_iface_key] if cur_iface_key else [],
                  meta=f'bmAttr=0x{attrs:02X}')
        return cur_iface_key

    def _handle_input_terminal(self, n, cur_iface_key):
        tid = getattr(n, 'bTerminalID', 0)
        typ = getattr(n, 'wTerminalType', 0)
        tname = _TERM_NAMES.get(typ, f'0x{typ:04X}')
        if typ == TERM_USB_STREAMING:
            label = 'USB IN (host→dev)'
        else:
            label = f'IN: {tname}'
        srcs = []
        csrc = getattr(n, 'bCSourceID', 0)
        if csrc:
            srcs.append(f'CLK#{csrc}')
        assoc = getattr(n, 'bAssocTerminal', 0)
        if assoc:
            srcs.append(f'???#{assoc}')
        if cur_iface_key:
            srcs.append(cur_iface_key)
        self._add('IT', tid, label, sources=srcs)
        self.nodes[f'IT#{tid}'].attrs['term_type'] = typ
        self.nodes[f'IT#{tid}'].attrs['channels'] = getattr(n, 'bNrChannels', 0)
        return cur_iface_key

    def _handle_output_terminal(self, n, cur_iface_key):
        tid = getattr(n, 'bTerminalID', 0)
        typ = getattr(n, 'wTerminalType', 0)
        tname = _TERM_NAMES.get(typ, f'0x{typ:04X}')
        label = f'{tname}' if typ == TERM_USB_STREAMING else f'OUT: {tname}'
        if typ == TERM_USB_STREAMING:
            label = 'USB OUT (dev→host)'
        srcs = []
        sid = getattr(n, 'bSourceID', 0)
        if sid:
            srcs.append(f'???#{sid}')
        if cur_iface_key:
            srcs.append(cur_iface_key)
        self._add('OT', tid, label, sources=srcs)
        self.nodes[f'OT#{tid}'].attrs['term_type'] = typ
        return cur_iface_key

    def _handle_feature_unit(self, n, cur_iface_key):
        uid = getattr(n, 'bUnitID', 0)
        src = getattr(n, 'bSourceID', 0)
        ctrl = getattr(n, 'controls_per_channel', [])

        def _decode_controls(bm):
            names = []
            for off, name in _FU_CTRL_NAMES.items():
                v = (bm >> off) & 3
                if v == 1:
                    names.append(f'{name}:R')
                elif v == 3:
                    names.append(f'{name}:RW')
            return names

        parts = []
        if ctrl:
            master_ctrls = _decode_controls(ctrl[0])
            if master_ctrls:
                parts.append('M:[' + ','.join(master_ctrls) + ']')
            ch_ctrls = []
            for ch_bm in ctrl[1:]:
                names = _decode_controls(ch_bm)
                if names:
                    ch_ctrls.append(','.join(names))
            if ch_ctrls:
                unique = dict.fromkeys(ch_ctrls)
                dedup = list(unique)
                suffix = f'  (×{len(ch_ctrls)}ch)' if len(dedup) == 1 and len(ch_ctrls) > 1 else ''
                parts.append('[' + dedup[0] + ']' + suffix if len(dedup) == 1
                              else '[' + '|'.join(dedup) + ']')
        label = 'FU' if not parts else 'FU ' + ' '.join(parts)
        srcs = [f'???#{src}'] if src else []
        if cur_iface_key:
            srcs.append(cur_iface_key)
        self._add('FU', uid, label, sources=srcs)
        return cur_iface_key

    def _handle_mixer_unit(self, n, cur_iface_key):
        uid = getattr(n, 'bUnitID', 0)
        srcs = [f'???#{s}' for s in getattr(n, 'baSourceID', [])]
        if cur_iface_key:
            srcs.append(cur_iface_key)
        self._add('MU', uid, 'Mixer', sources=srcs)
        return cur_iface_key

    def _handle_selector_unit(self, n, cur_iface_key):
        uid = getattr(n, 'bUnitID', 0)
        srcs = [f'???#{s}' for s in getattr(n, 'baSourceID', [])]
        if cur_iface_key:
            srcs.append(cur_iface_key)
        self._add('SU', uid, 'Selector', sources=srcs)
        return cur_iface_key

    def _handle_effect_unit(self, n, cur_iface_key):
        uid = getattr(n, 'bUnitID', 0)
        ef = getattr(n, 'wEffectType', 0)
        ef_name = EFFECT_TYPE_NAMES.get(ef, f'EF 0x{ef:04X}')
        srcs = [f'???#{getattr(n, "bSourceID", 0)}'] if getattr(n, 'bSourceID', 0) else []
        if cur_iface_key:
            srcs.append(cur_iface_key)
        self._add('EF', uid, ef_name, sources=srcs)
        return cur_iface_key

    def _handle_processing_unit(self, n, cur_iface_key):
        uid = getattr(n, 'bUnitID', 0)
        pt = getattr(n, 'wProcessType', 0)
        pt_name = PROCESS_TYPE_NAMES.get(pt, f'PU 0x{pt:04X}')
        srcs = [f'???#{s}' for s in getattr(n, 'baSourceID', [])]
        if cur_iface_key:
            srcs.append(cur_iface_key)
        self._add('PU', uid, pt_name, sources=srcs)
        return cur_iface_key

    def _handle_extension_unit(self, n, cur_iface_key):
        uid = getattr(n, 'bUnitID', 0)
        srcs = [f'???#{s}' for s in getattr(n, 'baSourceID', [])]
        if cur_iface_key:
            srcs.append(cur_iface_key)
        self._add('XU', uid, 'ExtUnit', sources=srcs)
        return cur_iface_key

    def _handle_clock_source(self, n, cur_iface_key):
        cid = getattr(n, 'bClockID', 0)
        attr = getattr(n, 'bmAttributes', CLOCK_INT_FIXED)
        clock_type = attr & 0x03
        attr_name = CLOCK_TYPE_NAMES.get(clock_type, f'0x{clock_type:02X}')
        if attr & 0x04:
            attr_name += '+SOF'
        srcs = [cur_iface_key] if cur_iface_key else []
        self._add('CLK', cid, attr_name, sources=srcs)
        self.nodes[f'CLK#{cid}'].attrs['clock_attr'] = attr
        return cur_iface_key

    def _handle_clock_selector(self, n, _prev):
        cid = getattr(n, 'bClockID', 0)
        srcs = [f'CLK#{s}' for s in getattr(n, 'baCSourceID', [])]
        self._add('CS', cid, 'ClkSel', sources=srcs)
        return _prev

    def _handle_clock_multiplier(self, n, _prev):
        cid = getattr(n, 'bClockID', 0)
        src = getattr(n, 'bCSourceID', 0)
        self._add('CM', cid, f'x2', sources=[f'CLK#{src}'] if src else [])
        return _prev

    def _handle_src(self, n, _prev):
        uid = getattr(n, 'bUnitID', 0)
        src = getattr(n, 'bSourceID', 0)
        self._add('SRC', uid, 'SRC', sources=[f'???#{src}'] if src else [])
        return _prev

    def _handle_ac_header(self, n, cur_iface_key):
        name = getattr(n, '_name', '')
        if cur_iface_key:
            self._add('ACHDR', 0, f'AC Header ({name})', sources=[cur_iface_key])
        return cur_iface_key

    def _handle_as_general(self, n, cur_iface_key):
        link = getattr(n, 'bTerminalLink', 0)
        ch = getattr(n, 'bNrChannels', 0)
        label = f'AS {ch}ch'
        srcs = [f'???#{link}'] if link else []
        if cur_iface_key:
            srcs.append(cur_iface_key)
        self._add('AS', link, label, sources=srcs)
        self.nodes[f'AS#{link}'].attrs['channels'] = ch
        self.nodes[f'AS#{link}'].attrs['format'] = getattr(n, 'bFormatType', 1)
        return cur_iface_key

    def _handle_format_type(self, n, cur_iface_key):
        bits = getattr(n, 'bBitResolution', 0)
        if cur_iface_key:
            self._add('FMT', 0, f'{bits}-bit', sources=[cur_iface_key])
        return cur_iface_key

    def _handle_iso_ep(self, n, cur_iface_key, as_link=0):
        srcs = [f'AS#{as_link}'] if as_link else []
        if cur_iface_key:
            srcs.append(cur_iface_key)
        self._add('ISO', as_link, 'Audio CS EP', sources=srcs)
        return cur_iface_key

    def _handle_hid(self, n, cur_iface_key):
        bcd = getattr(n, 'bcdHID', 0)
        raw = getattr(n, 'report_bytes', None)
        if raw:
            self._hid_reports.append(raw)
        if cur_iface_key:
            self._add('HID', 0, f'HID {bcd>>8}.{(bcd&0xF0)>>4}', sources=[cur_iface_key])
        return cur_iface_key

    def _handle_cdc(self, n, cur_iface_key):
        if cur_iface_key:
            name = type(n).__name__.replace('CDC', '').replace('Descriptor', '')
            if not name:
                name = 'Header'
            self._add('CDC', 0, name, sources=[cur_iface_key])
        return cur_iface_key

    def _handle_midi_in_jack(self, n, cur_iface_key):
        jid = getattr(n, 'bJackID', 0)
        srcs = [cur_iface_key] if cur_iface_key else []
        self._add('MJ_IN', jid, f'MIDI IN Jack#{jid}', sources=srcs)
        return cur_iface_key

    def _handle_midi_out_jack(self, n, cur_iface_key):
        jid = getattr(n, 'bJackID', 0)
        raw_srcs = [f'MJ_IN#{s}' for s in getattr(n, 'baSourceID', [])]
        if cur_iface_key:
            raw_srcs.append(cur_iface_key)
        self._add('MJ_OUT', jid, f'MIDI OUT Jack#{jid}', sources=raw_srcs)
        return cur_iface_key
    def _handle_midi_out_ep(self, n, _prev):
        for jid in getattr(n, 'baAssocJackID', []):
            ep_key = f'MEP_OUT#{jid}'
            self._add('MEP_OUT', jid, f'MIDI Bulk EP OUT')
            jack_key = f'MJ_IN#{jid}'
            if jack_key in self.nodes:
                if ep_key not in self.nodes[jack_key].sources:
                    self.nodes[jack_key].sources.append(ep_key)
        return _prev

    def _handle_midi_in_ep(self, n, _prev):
        for jid in getattr(n, 'baAssocJackID', []):
            ep_key = f'MEP_IN#{jid}'
            jack_key = f'MJ_OUT#{jid}'
            self._add('MEP_IN', jid, f'MIDI Bulk EP IN', sources=[jack_key])
            if jack_key in self.nodes:
                pass
        return _prev
    def _resolve_wildcards(self):
        audio_ids = {}
        jack_ids = {}
        other_ids = {}
        _audio_prefixes = {'CLK', 'IT', 'OT', 'FU', 'MU', 'SU',
                           'PU', 'EF', 'XU', 'SRC', 'CM', 'CS'}
        for key in self.nodes:
            parts = key.rsplit('#', 1)
            if len(parts) != 2:
                continue
            kind, uid_str = parts
            try:
                uid = int(uid_str)
            except ValueError:
                continue
            if kind in _audio_prefixes:
                audio_ids[uid] = key
            elif kind.startswith('MJ_') or kind.startswith('MEP_'):
                jack_ids[uid] = key
            else:
                other_ids[uid] = key

        def _resolve_wc(kind, uid):
            if kind in _audio_prefixes:
                return audio_ids.get(uid)
            if kind.startswith('MJ_') or kind.startswith('MEP_'):
                return jack_ids.get(uid)
            return audio_ids.get(uid) or jack_ids.get(uid) or other_ids.get(uid)

        for key, node in list(self.nodes.items()):
            node_kind = key.split('#')[0]
            resolved = []
            for src in node.sources:
                if src.startswith('???'):
                    _, sid_str = src.split('#')
                    sid = int(sid_str)
                    target = _resolve_wc(node_kind, sid)
                    if target:
                        resolved.append(target)
                else:
                    resolved.append(src)
            node.sources = resolved

    def to_ascii(self):
        """Render the topology as an ASCII tree diagram.

        Produces a multi-section output: a USB descriptor tree (device,
        configs, interfaces, endpoints), followed by an audio topology
        section (clock sources, terminals, units, AS/ISO chains, MIDI
        jacks), and optionally a parsed HID report tree.
        """
        lines = []

        consumers = {}
        for key, node in self.nodes.items():
            for src in node.sources:
                consumers.setdefault(src, []).append(key)

        lines.append('USB Descriptor Tree')
        lines.append('-' * 20)

        roots = sorted(k for k in self.nodes if k.startswith('DEV#'))
        for i, root in enumerate(roots):
            self._ascii_tree(root, lines, prefix='', is_last=(i == len(roots) - 1),
                             consumers=consumers, visited=set(),
                             skip_types={'IT#', 'OT#', 'FU#', 'MU#', 'SU#',
                                         'CLK#', 'CS#', 'CM#', 'SRC#',
                                         'MJ_', 'MEP_', 'PU#', 'EF#', 'XU#',
                                         'FMT#', 'AS#', 'ISO#'})

        audio_roots = sorted(k for k in self.nodes
                              if k.startswith('CLK#')
                              or k.startswith('MEP_')
                              or k.startswith('MJ_IN#')
                              or k.startswith('MJ_OUT#')
                              or k.startswith('IT#')
                              or k.startswith('OT#'))

        if audio_roots:
            lines.append('')
            lines.append('Audio Topology')
            lines.append('-' * 14)

            roots = [k for k in audio_roots
                     if all(s.startswith(('IFACE', 'CFG#', 'DEV#'))
                            or not s for s in self.nodes[k].sources)]
            for i, root in enumerate(roots):
                self._ascii_tree(root, lines, prefix='',
                                 is_last=(i == len(roots) - 1),
                                 consumers=consumers, visited=set(),
                                 skip_types={'IFACE', 'CFG#', 'DEV#',
                                             'ACHDR', 'FMT#', 'HID#', 'CDC#',
                                             'EP#', 'QUAL#', 'OS_CFG#'})

        if self._hid_reports:
            lines.append('')
            lines.append('HID Report')
            lines.append('-' * 10)
            for i, raw in enumerate(self._hid_reports):
                if len(self._hid_reports) > 1:
                    lines.append(f'  Report #{i+1} ({len(raw)} bytes)')
                for line in parse_hid_report(raw):
                    lines.append(f'  {line}')

        return '\n'.join(lines)

    def _ascii_tree(self, key, lines, prefix='', is_last=False, consumers=None,
                    visited=None, skip_types=None):
        if visited is None:
            visited = set()
        if skip_types is None:
            skip_types = set()
        if key in visited:
            return
        visited.add(key)

        node = self.nodes.get(key)
        if node is None:
            return

        label = node.label or node.kind
        branch = '└── ' if is_last else '├── '
        lines.append(f'{prefix}{branch}{label}')

        if consumers and key in consumers:
            children = [c for c in sorted(consumers[key])
                        if not any(c.startswith(t) for t in skip_types)]
            for i, child in enumerate(children):
                child_is_last = (i == len(children) - 1)
                new_prefix = prefix + ('    ' if is_last else '│   ')
                self._ascii_tree(child, lines, new_prefix, child_is_last,
                                 consumers, visited.copy(), skip_types)

    def to_mermaid(self):
        """Render the topology as a Mermaid ``graph TD`` markdown diagram.

        Each node type gets a distinct shape (clock sources are circles,
        feature/mixer units are hexagons, AS/ISO are asymmetric shapes,
        etc.).  Edges represent source→consumer relationships between
        topology elements.
        """
        lines = ['graph TD']
        uid_counter = {}

        def safe_id(key):
            kid = key.replace('#', '_').replace(' ', '_').replace('(', '').replace(')', '').replace('>', '_').replace('<', '_')
            if kid not in uid_counter:
                uid_counter[kid] = 1
            else:
                uid_counter[kid] += 1
                kid = f'{kid}_{uid_counter[kid]-1}'
            return kid

        _shape_map = {
            ('DEV#',): '[%s]',
            ('CFG#',): '[%s]',
            ('IFACE',): '[%s]',
            ('QUAL',): '[%s]',
            ('OS_CFG',): '[%s]',
            ('CLK#',): '((%s))',
            ('IT#',): '(%s)',
            ('OT#',): '(%s)',
            ('FU#',): '{%s}',
            ('MU#',): '{%s}',
            ('SU#',): '{%s}',
            ('PU#',): '{%s}',
            ('EF#',): '{%s}',
            ('XU#',): '{%s}',
            ('AS#',): '>%s]',
            ('ISO#',): '>%s]',
            ('MJ_',): '{{%s}}',
            ('MEP_',): '{{%s}}',
            ('EP#',): '[/%s/]',
        }

        def _get_shape(key):
            for prefixes, shape in _shape_map.items():
                for prefix in prefixes:
                    if key.startswith(prefix):
                        return shape
            return '(%s)'

        for key, node in self.nodes.items():
            sid = safe_id(key)
            label = node.label or node.kind
            shape = _get_shape(key)
            lines.append(f'    {sid}{shape % label}')

        for key, node in self.nodes.items():
            sid = safe_id(key)
            for src in node.sources:
                if src in self.nodes:
                    lines.append(f'    {safe_id(src)} --> {sid}')

        return '\n'.join(lines)
