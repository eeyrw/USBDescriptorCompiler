"""Custom multi-path UAC2 audio topology using unified primitives.

Demonstrates composing arbitrary audio topologies with uac2_setup()
and uac2_audio_path(). Three independent audio paths share a single
AC control interface and internal clock.

Topology:
  OUT path 1: USB → FU (Volume) → Speaker → AS OUT (stereo)
  OUT path 2: USB → FU (Volume) → Line Out → AS OUT (stereo)
  IN  path 1: Mic → FU (Volume) → USB → AS IN (mono)
"""
from usbdesc.composite import (
    CompositeDevice, ResourceAllocator,
    uac2_setup, uac2_audio_path,
)
from usbdesc.core.types import (
    TERM_SPEAKER, TERM_LINE_CONNECTOR, TERM_MICROPHONE,
    FUNCTION_PRO_AUDIO,
)
from usbdesc.export.c_array import CArrayExporter
from usbdesc.topology import TopologyGraph


def create_multi_path_audio():

    def build(rc):
        nodes, clk = uac2_setup(rc, FUNCTION_PRO_AUDIO, 'Multi I/O')

        ac1, as1 = uac2_audio_path(rc, 'OUT', 2, TERM_SPEAKER,
                                    sample_rate=48000, bit_depth=24,
                                    volume=True, clock_id=clk,
                                    label='Speaker')

        ac2, as2 = uac2_audio_path(rc, 'OUT', 4, TERM_LINE_CONNECTOR,
                                    sample_rate=48000, bit_depth=24,
                                    volume=True, clock_id=clk,
                                    label='LineOut')

        ac3, as3 = uac2_audio_path(rc, 'IN', 1, TERM_MICROPHONE,
                                    sample_rate=48000, bit_depth=16,
                                    volume=True, clock_id=clk,
                                    label='Mic')

        return nodes + ac1 + ac2 + ac3 + as1 + as2 + as3

    dev = CompositeDevice(
        idVendor=0x1234, idProduct=0x5678,
        manufacturer='Pro Audio', product='Multi-Path',
        bcdUSB=0x0200,
    )
    dev.add(build)
    return dev.build()


if __name__ == '__main__':
    nodes = create_multi_path_audio()
    print(TopologyGraph(nodes).to_ascii())
    print()
    print(f'// Built {len(nodes)} descriptor nodes')
    print(CArrayExporter().export_groups(nodes, prefix='multi_path'))
