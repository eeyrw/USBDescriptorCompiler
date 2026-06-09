"""UAC1 full-duplex headset using the unified UAC1 primitives.

Demonstrates the UAC1 composite API with uac1_setup() + uac1_audio_path().
"""
from usbdesc.standard.interface import InterfaceDescriptor
from usbdesc.device_class.audio.uac1 import ACHeader as UAC1ACHeader
from usbdesc.composite import (
    CompositeDevice, ResourceAllocator,
    uac1_audio_path,
)
from usbdesc.core.types import (
    TERM_SPEAKER, TERM_MICROPHONE,
    CLASS_AUDIO, AUDIO_SUBCLASS_CONTROL,
)
from usbdesc.export.c_array import CArrayExporter
from usbdesc.topology import TopologyGraph


def create_uac1_headset():

    def build(rc):
        ac_iface = rc.alloc_interface()

        ac_out, as_out, as_nr_out = uac1_audio_path(rc, 'OUT', 2, TERM_SPEAKER,
                                                     sample_rate=48000, bit_depth=16,
                                                     volume=True, label='Speaker')

        ac_in, as_in, as_nr_in = uac1_audio_path(rc, 'IN', 1, TERM_MICROPHONE,
                                                  sample_rate=48000, bit_depth=16,
                                                  volume=True, label='Mic')

        return [
            InterfaceDescriptor(
                bInterfaceNumber=ac_iface, bInterfaceClass=CLASS_AUDIO,
                bInterfaceSubClass=AUDIO_SUBCLASS_CONTROL,
                name='Headset Control',
            ),
            UAC1ACHeader(baInterfaceNr=[as_nr_out, as_nr_in], name='Headset AC Header'),
        ] + ac_out + ac_in + as_out + as_in

    dev = CompositeDevice(
        idVendor=0x1234, idProduct=0x5678,
        manufacturer='UAC1 Audio', product='Headset',
        bcdUSB=0x0110,
    )
    dev.add(build)
    return dev.build()


if __name__ == '__main__':
    nodes = create_uac1_headset()
    print(TopologyGraph(nodes).to_ascii())
    print()
    print(f'// UAC1 headset: {len(nodes)} nodes')
    print(CArrayExporter().export_groups(nodes, prefix='uac1_headset'))
