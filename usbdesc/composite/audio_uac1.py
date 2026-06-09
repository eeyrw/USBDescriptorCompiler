"""UAC 1.0 audio function templates — primitives and convenience wrappers.

Provides uac1_setup() / uac1_audio_path() for building UAC 1.0 audio topologies,
plus pre-built convenience functions: speaker, line out, microphone, line in,
headset, and line in/out.

Unlike UAC2, UAC1 uses 16-bit wChannelConfig, 3-byte sample rates, and
variable bControlSize. The ACHeader is deferred — the caller must supply
baInterfaceNr[] after collecting all streaming interface numbers.
"""

from usbdesc.standard.interface import InterfaceDescriptor
from usbdesc.standard.endpoint import EndpointDescriptor

from usbdesc.device_class.audio.uac1 import (
    ACHeader as UAC1ACHeader,
    InputTerminal as UAC1InputTerminal,
    OutputTerminal as UAC1OutputTerminal,
    FeatureUnit as UAC1FeatureUnit,
    ASGeneral as UAC1ASGeneral,
    FormatTypeI as UAC1FormatTypeI,
    ClassSpecificIsoEP as UAC1ClassSpecificIsoEP,
)

from usbdesc.core.types import (
    CLASS_AUDIO,
    AUDIO_SUBCLASS_CONTROL, AUDIO_SUBCLASS_STREAMING,
    TERM_USB_STREAMING, TERM_SPEAKER, TERM_MICROPHONE,
    TERM_LINE_CONNECTOR,
    EP_ATTR_ISOCHRONOUS,
    EP_ISO_SYNC_ASYNC, EP_ISO_SYNC_ADAPTIVE,
    FORMAT_TYPE_I,
)

from usbdesc.composite.builder import _channel_config, terminal_type_desc


def uac1_setup(rc, name='Audio'):
    """Allocate UAC1 AC control interface.

    Returns (nodes, ac_iface_number). ACHeader is NOT included —
    the caller must insert it once all streaming interface numbers
    are known via baInterfaceNr[].
    """
    nodes = []
    iface = rc.alloc_interface()
    nodes.append(InterfaceDescriptor(
        bInterfaceNumber=iface, bInterfaceClass=CLASS_AUDIO,
        bInterfaceSubClass=AUDIO_SUBCLASS_CONTROL,
        name=f'{name} Control',
    ))
    return nodes, iface


def uac1_audio_path(rc, direction, channels, terminal_type,
                    sample_rate=48000, bit_depth=16,
                    volume=True, mute=False,
                    ep_address=None, label=''):
    """Build a single UAC1 audio path.

    Returns (ac_nodes, as_nodes, as_iface_number).
    All AC descriptors (terminals, units) are separated from AS descriptors
    so the caller can interleave them correctly with the AC interface.
    """
    ac_nodes = []
    subslot = bit_depth // 8
    desc = label or terminal_type_desc(terminal_type)

    if direction == 'OUT':
        it = rc.alloc_terminal_id()
        ac_nodes.append(UAC1InputTerminal(
            bTerminalID=it, wTerminalType=TERM_USB_STREAMING,
            bNrChannels=channels,
            wChannelConfig=_channel_config(channels),
            name=f'{desc} USB Input Terminal',
        ))
        src = it
        if volume or mute:
            bm = 0
            if mute:
                bm |= 0x01
            if volume:
                bm |= 0x02
            ctrl = [bm] + [0x00] * channels
            fu = rc.alloc_unit_id()
            ac_nodes.append(UAC1FeatureUnit(
                bUnitID=fu, bSourceID=src,
                controls_per_channel=ctrl, bControlSize=1,
                name=f'{desc} Feature Unit',
            ))
            src = fu
        ot = rc.alloc_terminal_id()
        ac_nodes.append(UAC1OutputTerminal(
            bTerminalID=ot, wTerminalType=terminal_type,
            bSourceID=src, name=f'{desc} Output Terminal',
        ))
        as_link = ot
        if ep_address is None:
            ep_address = rc.alloc_ep_out()
        else:
            rc.reserve_ep_out(ep_address)
    else:
        it = rc.alloc_terminal_id()
        ac_nodes.append(UAC1InputTerminal(
            bTerminalID=it, wTerminalType=terminal_type,
            bNrChannels=channels,
            wChannelConfig=_channel_config(channels),
            name=f'{desc} Input Terminal',
        ))
        src = it
        if volume or mute:
            bm = 0
            if mute:
                bm |= 0x01
            if volume:
                bm |= 0x02
            ctrl = [bm] + [0x00] * channels
            fu = rc.alloc_unit_id()
            ac_nodes.append(UAC1FeatureUnit(
                bUnitID=fu, bSourceID=src,
                controls_per_channel=ctrl, bControlSize=1,
                name=f'{desc} Feature Unit',
            ))
            src = fu
        ot = rc.alloc_terminal_id()
        ac_nodes.append(UAC1OutputTerminal(
            bTerminalID=ot, wTerminalType=TERM_USB_STREAMING,
            bSourceID=src, name=f'{desc} USB Output Terminal',
        ))
        as_link = ot
        if ep_address is None:
            ep_address = rc.alloc_ep_in()
        else:
            rc.reserve_ep_in(ep_address)

    as_iface = rc.alloc_interface()
    max_pkt = channels * subslot * ((sample_rate + 999) // 1000)
    as_nodes = [
        InterfaceDescriptor(
            bInterfaceNumber=as_iface, bAlternateSetting=0,
            bInterfaceClass=CLASS_AUDIO,
            bInterfaceSubClass=AUDIO_SUBCLASS_STREAMING,
            name=f'{desc} Alt 0',
        ),
        InterfaceDescriptor(
            bInterfaceNumber=as_iface, bAlternateSetting=1,
            bNumEndpoints=1, bInterfaceClass=CLASS_AUDIO,
            bInterfaceSubClass=AUDIO_SUBCLASS_STREAMING,
            name=f'{desc} Alt 1',
        ),
        UAC1ASGeneral(
            bTerminalLink=as_link, wFormatTag=FORMAT_TYPE_I,
            name=f'{desc} AS General',
        ),
        UAC1FormatTypeI(
            bNrChannels=channels, bSubframeSize=subslot,
            bBitResolution=bit_depth,
            sample_rates=[sample_rate],
            name=f'{desc} Format Type I',
        ),
        EndpointDescriptor(
            bEndpointAddress=ep_address,
            bmAttributes=EP_ATTR_ISOCHRONOUS | (EP_ISO_SYNC_ADAPTIVE if direction == 'OUT' else EP_ISO_SYNC_ASYNC),
            wMaxPacketSize=max_pkt,
            bInterval=1,
            name=f'{desc} Audio EP',
        ),
        UAC1ClassSpecificIsoEP(
            bmAttributes=0x00,
            bLockDelayUnits=0, wLockDelay=0,
            name=f'{desc} Audio CS EP',
        ),
    ]
    return ac_nodes, as_nodes, as_iface


# ── UAC1 convenience wrappers ────────────────────────────────────────

def uac1_speaker(rc, channels=2, sample_rate=48000, bit_depth=16,
                 volume=True, mute=False, name='UAC1 Speaker',
                 ep_address=None):
    """UAC1 stereo speaker output function (16-bit by default)."""
    ac_iface = rc.alloc_interface()
    ac, ast, as_iface = uac1_audio_path(rc, 'OUT', channels, TERM_SPEAKER,
                                        sample_rate, bit_depth, volume, mute,
                                        ep_address, label=name)
    return [
        InterfaceDescriptor(
            bInterfaceNumber=ac_iface, bInterfaceClass=CLASS_AUDIO,
            bInterfaceSubClass=AUDIO_SUBCLASS_CONTROL,
            name=f'{name} Control',
        ),
        UAC1ACHeader(baInterfaceNr=[as_iface], name=f'{name} AC Header'),
    ] + ac + ast


def uac1_line_out(rc, channels=2, sample_rate=48000, bit_depth=24,
                  volume=True, mute=False, name='UAC1 Line Out',
                  ep_address=None):
    """UAC1 line output function (24-bit by default)."""
    ac_iface = rc.alloc_interface()
    ac, ast, as_iface = uac1_audio_path(rc, 'OUT', channels, TERM_LINE_CONNECTOR,
                                        sample_rate, bit_depth, volume, mute,
                                        ep_address, label=name)
    return [
        InterfaceDescriptor(
            bInterfaceNumber=ac_iface, bInterfaceClass=CLASS_AUDIO,
            bInterfaceSubClass=AUDIO_SUBCLASS_CONTROL,
            name=f'{name} Control',
        ),
        UAC1ACHeader(baInterfaceNr=[as_iface], name=f'{name} AC Header'),
    ] + ac + ast


def uac1_microphone(rc, channels=1, sample_rate=48000, bit_depth=16,
                    volume=True, mute=False, name='UAC1 Microphone',
                    ep_address=None):
    """UAC1 mono microphone input function."""
    ac_iface = rc.alloc_interface()
    ac, ast, as_iface = uac1_audio_path(rc, 'IN', channels, TERM_MICROPHONE,
                                        sample_rate, bit_depth, volume, mute,
                                        ep_address, label=name)
    return [
        InterfaceDescriptor(
            bInterfaceNumber=ac_iface, bInterfaceClass=CLASS_AUDIO,
            bInterfaceSubClass=AUDIO_SUBCLASS_CONTROL,
            name=f'{name} Control',
        ),
        UAC1ACHeader(baInterfaceNr=[as_iface], name=f'{name} AC Header'),
    ] + ac + ast


def uac1_line_in(rc, channels=2, sample_rate=48000, bit_depth=24,
                 volume=True, mute=False, name='UAC1 Line In',
                 ep_address=None):
    """UAC1 stereo line input function (24-bit by default)."""
    ac_iface = rc.alloc_interface()
    ac, ast, as_iface = uac1_audio_path(rc, 'IN', channels, TERM_LINE_CONNECTOR,
                                        sample_rate, bit_depth, volume, mute,
                                        ep_address, label=name)
    return [
        InterfaceDescriptor(
            bInterfaceNumber=ac_iface, bInterfaceClass=CLASS_AUDIO,
            bInterfaceSubClass=AUDIO_SUBCLASS_CONTROL,
            name=f'{name} Control',
        ),
        UAC1ACHeader(baInterfaceNr=[as_iface], name=f'{name} AC Header'),
    ] + ac + ast


def uac1_headset(rc, channels=2, sample_rate=48000, bit_depth=16,
                 volume_out=True, mute=False, volume_in=True,
                 ep_out_address=None, ep_in_address=None, name='UAC1 Headset'):
    """UAC1 headset function — stereo speaker OUT + mono microphone IN."""
    ac_iface = rc.alloc_interface()
    ac_out, as_out, as_out_nr = uac1_audio_path(rc, 'OUT', channels, TERM_SPEAKER,
                                                sample_rate, bit_depth, volume_out, mute,
                                                ep_out_address, label='Headset OUT')
    ac_in, as_in, as_in_nr = uac1_audio_path(rc, 'IN', 1, TERM_MICROPHONE,
                                             sample_rate, bit_depth, volume_in, False,
                                             ep_in_address, label='Headset IN')
    return [
        InterfaceDescriptor(
            bInterfaceNumber=ac_iface, bInterfaceClass=CLASS_AUDIO,
            bInterfaceSubClass=AUDIO_SUBCLASS_CONTROL,
            name=f'{name} Control',
        ),
        UAC1ACHeader(baInterfaceNr=[as_out_nr, as_in_nr], name=f'{name} AC Header'),
    ] + ac_out + ac_in + as_out + as_in


def uac1_line_in_out(rc, channels=2, sample_rate=48000, bit_depth=24,
                     volume_out=True, mute=False, volume_in=True,
                     ep_out_address=None, ep_in_address=None,
                     name='UAC1 Line I/O'):
    """UAC1 full-duplex line input/output function (24-bit by default)."""
    ac_iface = rc.alloc_interface()
    ac_out, as_out, as_out_nr = uac1_audio_path(rc, 'OUT', channels, TERM_LINE_CONNECTOR,
                                                sample_rate, bit_depth, volume_out, mute,
                                                ep_out_address, label='Line OUT')
    ac_in, as_in, as_in_nr = uac1_audio_path(rc, 'IN', channels, TERM_LINE_CONNECTOR,
                                             sample_rate, bit_depth, volume_in, False,
                                             ep_in_address, label='Line IN')
    return [
        InterfaceDescriptor(
            bInterfaceNumber=ac_iface, bInterfaceClass=CLASS_AUDIO,
            bInterfaceSubClass=AUDIO_SUBCLASS_CONTROL,
            name=f'{name} Control',
        ),
        UAC1ACHeader(baInterfaceNr=[as_out_nr, as_in_nr], name=f'{name} AC Header'),
    ] + ac_out + ac_in + as_out + as_in
