"""USB audio + MIDI composite — stereo speaker with MIDI I/O.

Demonstrates the high-level composite API: a single device with
UAC2 audio output and MIDI streaming on independent interfaces.
"""
from usbdesc.composite import CompositeDevice, uac2_speaker, midi_function
from usbdesc.export.c_array import CArrayExporter
from usbdesc.topology import TopologyGraph


def create_midi_audio_composite():
    dev = CompositeDevice(
        idVendor=0x1234, idProduct=0x5678,
        manufacturer='Synth Co', product='Audio + MIDI',
    )
    dev.add(uac2_speaker)
    dev.add(midi_function)
    return dev.build()


if __name__ == '__main__':
    nodes = create_midi_audio_composite()
    print(TopologyGraph(nodes).to_ascii())
    print()
    print(CArrayExporter().export_groups(nodes, prefix='audio_midi'))
