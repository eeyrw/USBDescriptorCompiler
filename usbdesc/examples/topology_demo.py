"""UAC2 audio topology diagram — standalone visualization of descriptor connections.

Demonstrates TopologyGraph to generate ASCII and Mermaid diagrams
from any descriptor node list. Run directly to see the topology of a
multi-path audio + MIDI composite device.
"""
from usbdesc.composite import CompositeDevice
from usbdesc.composite import (
    uac2_setup, uac2_audio_path,
    midi_function,
)
from usbdesc.core.types import (
    TERM_SPEAKER, TERM_LINE_CONNECTOR, TERM_MICROPHONE,
    FUNCTION_IO_BOX,
)
from usbdesc.topology import TopologyGraph
from usbdesc.export.c_array import CArrayExporter


def create_topology_demo():

    def build(rc):
        nodes, clk = uac2_setup(rc, FUNCTION_IO_BOX, 'Multi I/O')

        ac1, as1 = uac2_audio_path(rc, 'OUT', 2, TERM_SPEAKER,
                                    sample_rate=48000, bit_depth=24,
                                    volume=True, clock_id=clk,
                                    label='Main Speaker')

        ac2, as2 = uac2_audio_path(rc, 'OUT', 4, TERM_LINE_CONNECTOR,
                                    sample_rate=48000, bit_depth=24,
                                    volume=True, mute=True, clock_id=clk,
                                    label='Line Out 4ch')

        ac3, as3 = uac2_audio_path(rc, 'IN', 2, TERM_LINE_CONNECTOR,
                                    sample_rate=96000, bit_depth=24,
                                    volume=True, clock_id=clk,
                                    label='Line In Stereo')

        ac4, as4 = uac2_audio_path(rc, 'IN', 1, TERM_MICROPHONE,
                                    sample_rate=48000, bit_depth=16,
                                    volume=True, mute=True, clock_id=clk,
                                    label='Mic In')

        return nodes + ac1 + ac2 + ac3 + ac4 + as1 + as2 + as3 + as4

    dev = CompositeDevice(
        idVendor=0x1234, idProduct=0x5678,
        manufacturer='Pro Audio', product='Topology Demo',
        bcdUSB=0x0200,
    )
    dev.add(build)
    dev.add(midi_function)
    return dev.build()


if __name__ == '__main__':
    nodes = create_topology_demo()
    graph = TopologyGraph(nodes)

    print("=== ASCII Topology ===")
    print(graph.to_ascii())
    print()
    print("=== Mermaid (paste into .md file) ===")
    print(graph.to_mermaid())
    print()

    iface_count = 0
    for n in nodes:
        b = n.encode()
        if len(b) > 1 and b[1] == 0x04:
            iface_count += 1
    print(f"// {len(nodes)} descriptors, ~{iface_count} interface descriptors")
    print(CArrayExporter().export_groups(nodes, prefix='topology_demo'))
