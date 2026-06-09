"""MIDI Streaming function template — AC control interface + MIDI interface.

Supports embedded and external jack types, configurable port counts,
loopback routing, and automatic MIDI Streaming Header wTotalLength calculation.
"""

from usbdesc.standard.interface import InterfaceDescriptor
from usbdesc.standard.endpoint import EndpointDescriptor

from usbdesc.device_class.audio.uac1 import ACHeader as UAC1ACHeader
from usbdesc.device_class.audio.uac2 import (
    MIDIInJack, MIDIOutJack, MIDIOutBulkEP, MIDIInBulkEP,
    MSHeader,
)

from usbdesc.core.types import (
    CLASS_AUDIO,
    AUDIO_SUBCLASS_CONTROL, AUDIO_SUBCLASS_MIDI,
    EP_ATTR_BULK,
    CS_INTERFACE, CS_ENDPOINT,
    MIDI_JACK_EMBEDDED,
)


def midi_function(rc, in_jacks=1, out_jacks=1, jack_type=MIDI_JACK_EMBEDDED,
                  name='MIDI', ep_out_address=None, ep_in_address=None,
                  loopback=False):
    """MIDI Streaming — AC control interface + MIDI interface.

    ``loopback=False`` (default): OUT Jacks use empty ``baSourceID`` — independent
    paths. Typical for real devices (keyboard, synth, controller) where incoming
    MIDI is consumed by firmware and outgoing MIDI originates from device events.

    ``loopback=True``: all OUT Jacks reference all IN Jacks via ``baSourceID``,
    representing internal IN→OUT routing.  Suitable for pure USB-MIDI cables
    or debugging where the device acts as a transparent pipe.
    """
    ac_iface = rc.alloc_interface()
    midi_iface = rc.alloc_interface()

    in_ids = [rc.alloc_jack_id() for _ in range(in_jacks)]
    out_ids = [rc.alloc_jack_id() for _ in range(out_jacks)]

    ep_count = 0
    ep_out = None
    ep_in = None
    out_ep_jacks = []
    in_ep_jacks = []
    if in_jacks > 0:
        out_ep_jacks = in_ids
        ep_out = ep_out_address if ep_out_address is not None else rc.alloc_ep_out()
        if ep_out_address is not None:
            rc.reserve_ep_out(ep_out_address)
        ep_count += 1
    if out_jacks > 0:
        in_ep_jacks = out_ids
        ep_in = ep_in_address if ep_in_address is not None else rc.alloc_ep_in()
        if ep_in_address is not None:
            rc.reserve_ep_in(ep_in_address)
        ep_count += 1

    midi_nodes = [
        InterfaceDescriptor(
            bInterfaceNumber=midi_iface, bNumEndpoints=ep_count,
            bInterfaceClass=CLASS_AUDIO,
            bInterfaceSubClass=AUDIO_SUBCLASS_MIDI,
            name=f'{name} Streaming',
        ),
        MSHeader(wTotalLength=0, name=f'{name} MS Header'),
    ]

    for jid in in_ids:
        midi_nodes.append(MIDIInJack(
            bJackID=jid, bJackType=jack_type,
            name=f'{name} IN Jack {jid}',
        ))
    for jid in out_ids:
        src_list = in_ids if loopback else []
        midi_nodes.append(MIDIOutJack(
            bJackID=jid, bJackType=jack_type,
            baSourceID=src_list,
            name=f'{name} OUT Jack {jid}',
        ))

    if out_ep_jacks:
        midi_nodes.append(EndpointDescriptor(
            bEndpointAddress=ep_out,
            bmAttributes=EP_ATTR_BULK,
            wMaxPacketSize=64,
            bInterval=0,
            name=f'{name} OUT EP',
        ))
        midi_nodes.append(MIDIOutBulkEP(
            baAssocJackID=out_ep_jacks,
            name=f'{name} OUT CS EP',
        ))
    if in_ep_jacks:
        midi_nodes.append(EndpointDescriptor(
            bEndpointAddress=ep_in,
            bmAttributes=EP_ATTR_BULK,
            wMaxPacketSize=64,
            bInterval=0,
            name=f'{name} IN EP',
        ))
        midi_nodes.append(MIDIInBulkEP(
            baAssocJackID=in_ep_jacks,
            name=f'{name} IN CS EP',
        ))

    ms_total = 0
    for n in midi_nodes[1:]:
        buf = n.encode()
        if buf[1] in (CS_INTERFACE, CS_ENDPOINT):
            ms_total += len(buf)
    for n in midi_nodes:
        if 'MS Header' in n.name:
            n.wTotalLength = ms_total

    ac_nodes = [
        InterfaceDescriptor(
            bInterfaceNumber=ac_iface,
            bInterfaceClass=CLASS_AUDIO,
            bInterfaceSubClass=AUDIO_SUBCLASS_CONTROL,
            name=f'{name} Control',
        ),
    ]
    ac_nodes.append(UAC1ACHeader(baInterfaceNr=[midi_iface],
                                 name=f'{name} AC Header'))

    return ac_nodes + midi_nodes
