"""UAC 2.0 audio function templates — primitives and convenience wrappers.

Provides uac2_setup() / uac2_audio_path() for building arbitrary audio topologies,
plus pre-built convenience functions: speaker, line out, microphone, line in,
headset, and line in/out.
"""

from usbdesc.standard.interface import InterfaceDescriptor
from usbdesc.standard.endpoint import EndpointDescriptor

from usbdesc.device_class.audio.uac2 import (
    ACHeader, InputTerminal, OutputTerminal, FeatureUnit,
    ClockSource, ASGeneral, FormatTypeI, ClassSpecificIsoEP,
)

from usbdesc.core.base import hs_iso_packet_size
from usbdesc.core.types import (
    CLASS_AUDIO,
    AUDIO_SUBCLASS_CONTROL, AUDIO_SUBCLASS_STREAMING,
    FUNCTION_DESKTOP_SPEAKER, FUNCTION_MICROPHONE, FUNCTION_HEADSET,
    FUNCTION_IO_BOX,
    TERM_USB_STREAMING, TERM_SPEAKER, TERM_MICROPHONE,
    TERM_LINE_CONNECTOR,
    BM_FORMAT_PCM, CLOCK_INT_FIXED,
    EP_ATTR_ISOCHRONOUS,
    EP_ISO_SYNC_ASYNC, EP_ISO_SYNC_ADAPTIVE,
    CTRL_RW,
    UAC2_FU_MUTE, UAC2_FU_VOLUME,
)

from usbdesc.composite.builder import _channel_config, terminal_type_desc


def _build_volume_controls(channels, volume, mute):
    """Build UAC2 Feature Unit control bitmaps for volume and mute.

    Returns a list of control bitmap integers, one per channel plus a master,
    or None if neither volume nor mute is requested.
    """
    if not volume and not mute:
        return None
    ctrl = [0x00000000]
    for _ in range(channels):
        c = 0
        if mute:
            c |= CTRL_RW << UAC2_FU_MUTE
        if volume:
            c |= CTRL_RW << UAC2_FU_VOLUME
        ctrl.append(c)
    return ctrl


def _add_streaming_alt(rc, as_iface, link, channels, subslot,
                       bit_depth, sample_rate, ep_addr, direction,
                       bm_formats=BM_FORMAT_PCM, label='',
                       hs_transactions=1, high_speed=False):
    """Build UAC2 streaming alternate settings (Alt 0 / Alt 1).

    Creates a bandwidth-less Alt 0 interface, an operational Alt 1 interface with
    one isochronous endpoint, and the ASGeneral + FormatTypeI class-specific
    descriptors. For high-speed operation the ISO endpoint uses
    ``hs_iso_packet_size()`` for microframe-based max packet size.
    """
    nodes = [
        InterfaceDescriptor(
            bInterfaceNumber=as_iface, bAlternateSetting=0,
            bInterfaceClass=CLASS_AUDIO,
            bInterfaceSubClass=AUDIO_SUBCLASS_STREAMING,
            bInterfaceProtocol=0x20,
            name=f'{label} Audio Alt 0',
        ),
    ]
    max_pkt = channels * subslot * ((sample_rate + 999) // 1000)
    if high_speed:
        max_pkt = (max_pkt + 7) // 8
    nodes.append(InterfaceDescriptor(
        bInterfaceNumber=as_iface, bAlternateSetting=1,
        bNumEndpoints=1, bInterfaceClass=CLASS_AUDIO,
        bInterfaceSubClass=AUDIO_SUBCLASS_STREAMING,
        bInterfaceProtocol=0x20,
        name=f'{label} Audio Alt 1',
    ))
    nodes.append(ASGeneral(
        bTerminalLink=link,
        bmFormats=bm_formats,
        bNrChannels=channels,
        bmChannelConfig=_channel_config(channels),
        name=f'{label} AS General',
    ))
    nodes.append(FormatTypeI(
        bSubslotSize=subslot, bBitResolution=bit_depth,
        name=f'{label} Format Type I',
    ))
    wMaxPkt = hs_iso_packet_size(max_pkt, hs_transactions)
    iso_sync = EP_ISO_SYNC_ADAPTIVE if direction == 'OUT' else EP_ISO_SYNC_ASYNC
    iso_attr = EP_ATTR_ISOCHRONOUS | iso_sync
    nodes.append(EndpointDescriptor(
        bEndpointAddress=ep_addr,
        bmAttributes=iso_attr,
        wMaxPacketSize=wMaxPkt,
        bInterval=1,
        name=f'{label} Audio EP',
    ))
    nodes.append(ClassSpecificIsoEP(
        bmAttributes=0x00, bmControls=0x00,
        bLockDelayUnits=0, wLockDelay=0,
        name=f'{label} Audio CS EP',
    ))
    return nodes


def uac2_setup(rc, category=FUNCTION_DESKTOP_SPEAKER, name='Audio',
               has_clock=True):
    """Shared UAC2 AC Control Interface setup.

    Returns (nodes, clock_id).
    """
    nodes = []
    iface = rc.alloc_interface()
    nodes.append(InterfaceDescriptor(
        bInterfaceNumber=iface, bInterfaceClass=CLASS_AUDIO,
        bInterfaceSubClass=AUDIO_SUBCLASS_CONTROL,
        bInterfaceProtocol=0x20,
        name=f'{name} Control',
    ))
    nodes.append(ACHeader(bCategory=category, name=f'{name} AC Header'))
    clk = 0
    if has_clock:
        clk = rc.alloc_clock_id()
        nodes.append(ClockSource(
            bClockID=clk, bmAttributes=CLOCK_INT_FIXED,
            bmControls=0x00,
            name=f'{name} Clock',
        ))
    return nodes, clk


def uac2_audio_path(rc, direction, channels, terminal_type,
                    sample_rate=48000, bit_depth=16,
                    volume=True, mute=False,
                    ep_address=None, hs_transactions=1,
                    clock_id=None, label=''):
    """Build a single audio path (OUT or IN).

    direction='OUT': USB Stream IT → (FeatureUnit) → terminal_type OT → AS OUT EP
    direction='IN':  terminal_type IT → (FeatureUnit) → USB Stream OT → AS IN EP

    Returns (ac_nodes, as_nodes) — AC descriptors and AS descriptors separately.
    """
    ac_nodes = []
    subslot = bit_depth // 8
    desc = label or terminal_type_desc(terminal_type)

    if direction == 'OUT':
        it = rc.alloc_terminal_id()
        ac_nodes.append(InputTerminal(
            bTerminalID=it, wTerminalType=TERM_USB_STREAMING,
            bCSourceID=clock_id or 0, bNrChannels=channels,
            bmChannelConfig=_channel_config(channels),
            name=f'{desc} USB Input Terminal',
        ))
        src = it
        ctrls = _build_volume_controls(channels, volume, mute)
        if ctrls:
            fu = rc.alloc_unit_id()
            ac_nodes.append(FeatureUnit(
                bUnitID=fu, bSourceID=src,
                controls_per_channel=ctrls,
                name=f'{desc} Feature Unit',
            ))
            src = fu
        ot = rc.alloc_terminal_id()
        ac_nodes.append(OutputTerminal(
            bTerminalID=ot, wTerminalType=terminal_type,
            bSourceID=src, bCSourceID=clock_id or 0,
            name=f'{desc} Output Terminal',
        ))
        as_link = ot
        if ep_address is None:
            ep_address = rc.alloc_ep_out()
        else:
            rc.reserve_ep_out(ep_address)
    else:
        it = rc.alloc_terminal_id()
        ac_nodes.append(InputTerminal(
            bTerminalID=it, wTerminalType=terminal_type,
            bCSourceID=clock_id or 0, bNrChannels=channels,
            bmChannelConfig=_channel_config(channels),
            name=f'{desc} Input Terminal',
        ))
        src = it
        ctrls = _build_volume_controls(channels, volume, mute)
        if ctrls:
            fu = rc.alloc_unit_id()
            ac_nodes.append(FeatureUnit(
                bUnitID=fu, bSourceID=src,
                controls_per_channel=ctrls,
                name=f'{desc} Feature Unit',
            ))
            src = fu
        ot = rc.alloc_terminal_id()
        ac_nodes.append(OutputTerminal(
            bTerminalID=ot, wTerminalType=TERM_USB_STREAMING,
            bSourceID=src, bCSourceID=clock_id or 0,
            name=f'{desc} USB Output Terminal',
        ))
        as_link = ot
        if ep_address is None:
            ep_address = rc.alloc_ep_in()
        else:
            rc.reserve_ep_in(ep_address)

    as_iface = rc.alloc_interface()
    as_nodes = _add_streaming_alt(rc, as_iface, as_link, channels, subslot,
                                  bit_depth, sample_rate, ep_address,
                                  direction=direction,
                                  label=desc, hs_transactions=hs_transactions,
                                  high_speed=getattr(rc, '_high_speed', False))
    return ac_nodes, as_nodes


# ── UAC2 convenience wrappers ────────────────────────────────────────

def uac2_speaker(rc, channels=2, sample_rate=48000, bit_depth=16,
                 volume=True, mute=False, category=FUNCTION_DESKTOP_SPEAKER,
                 name='Speaker', ep_address=None, hs_transactions=1):
    """UAC2 stereo speaker output function (16-bit by default)."""
    nodes, clk = uac2_setup(rc, category, name)
    ac, as_ = uac2_audio_path(rc, 'OUT', channels, TERM_SPEAKER,
                              sample_rate, bit_depth, volume, mute,
                              ep_address, hs_transactions, clock_id=clk,
                              label=name)
    return nodes + ac + as_


def uac2_line_out(rc, channels=2, sample_rate=48000, bit_depth=24,
                  volume=True, mute=False, category=FUNCTION_IO_BOX,
                  name='Line Out', ep_address=None, hs_transactions=1):
    """UAC2 line output function (24-bit by default)."""
    nodes, clk = uac2_setup(rc, category, name)
    ac, as_ = uac2_audio_path(rc, 'OUT', channels, TERM_LINE_CONNECTOR,
                              sample_rate, bit_depth, volume, mute,
                              ep_address, hs_transactions, clock_id=clk,
                              label=name)
    return nodes + ac + as_


def uac2_microphone(rc, channels=1, sample_rate=48000, bit_depth=16,
                    volume=True, mute=False,
                    category=FUNCTION_MICROPHONE, name='Microphone',
                    ep_address=None, hs_transactions=1):
    """UAC2 mono microphone input function."""
    nodes, clk = uac2_setup(rc, category, name)
    ac, as_ = uac2_audio_path(rc, 'IN', channels, TERM_MICROPHONE,
                              sample_rate, bit_depth, volume, mute,
                              ep_address, hs_transactions, clock_id=clk,
                              label=name)
    return nodes + ac + as_


def uac2_line_in(rc, channels=2, sample_rate=48000, bit_depth=24,
                 volume=True, mute=False, category=FUNCTION_IO_BOX,
                 name='Line In', ep_address=None, hs_transactions=1):
    """UAC2 stereo line input function (24-bit by default)."""
    nodes, clk = uac2_setup(rc, category, name)
    ac, as_ = uac2_audio_path(rc, 'IN', channels, TERM_LINE_CONNECTOR,
                              sample_rate, bit_depth, volume, mute,
                              ep_address, hs_transactions, clock_id=clk,
                              label=name)
    return nodes + ac + as_


def uac2_headset(rc, channels=2, sample_rate=48000, bit_depth=16,
                 volume_out=True, mute=False, volume_in=True,
                 category=FUNCTION_HEADSET,
                 ep_out_address=None, ep_in_address=None,
                 hs_transactions=1):
    """UAC2 headset function — stereo speaker OUT + mono microphone IN."""
    nodes, clk = uac2_setup(rc, category, 'Headset')
    ac_out, as_out = uac2_audio_path(rc, 'OUT', channels, TERM_SPEAKER,
                                     sample_rate, bit_depth, volume_out, mute,
                                     ep_out_address, hs_transactions, clock_id=clk,
                                     label='Headset OUT')
    ac_in, as_in = uac2_audio_path(rc, 'IN', 1, TERM_MICROPHONE,
                                   sample_rate, bit_depth, volume_in, False,
                                   ep_in_address, hs_transactions, clock_id=clk,
                                   label='Headset IN')
    return nodes + ac_out + ac_in + as_out + as_in


def uac2_line_in_out(rc, channels=2, sample_rate=48000, bit_depth=24,
                     volume_out=True, mute=False, volume_in=True,
                     category=FUNCTION_IO_BOX,
                     ep_out_address=None, ep_in_address=None,
                     hs_transactions=1):
    """UAC2 full-duplex line input/output function (24-bit by default)."""
    nodes, clk = uac2_setup(rc, category, 'Line I/O')
    ac_out, as_out = uac2_audio_path(rc, 'OUT', channels, TERM_LINE_CONNECTOR,
                                     sample_rate, bit_depth, volume_out, mute,
                                     ep_out_address, hs_transactions, clock_id=clk,
                                     label='Line OUT')
    ac_in, as_in = uac2_audio_path(rc, 'IN', channels, TERM_LINE_CONNECTOR,
                                   sample_rate, bit_depth, volume_in, False,
                                   ep_in_address, hs_transactions, clock_id=clk,
                                   label='Line IN')
    return nodes + ac_out + ac_in + as_out + as_in
