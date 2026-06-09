import pytest
from usbdesc.composite import (
    CompositeDevice, ResourceAllocator,
    uac2_speaker, uac2_headset, uac2_microphone,
    uac2_line_out, uac2_line_in, uac2_line_in_out,
    uac1_speaker, uac1_microphone,
    uac1_line_out, uac1_line_in, uac1_line_in_out, uac1_headset,
    uac1_setup, uac1_audio_path,
    uac2_setup, uac2_audio_path,
    midi_function, hid_generic, hid_keyboard, hid_mouse,
    cdc_acm, msc_bulk_only, webusb_platform,
)
from usbdesc.device_class.audio.uac1 import ACHeader as UAC1ACHeader
from usbdesc.core.types import (
    CONFIG_ATTR_BUS_POWERED,
    FUNCTION_MICROPHONE, TERM_MICROPHONE, TERM_SPEAKER, TERM_LINE_CONNECTOR,
    FUNCTION_IO_BOX,
    MIDI_JACK_EMBEDDED, MIDI_JACK_EXTERNAL,
    HID_SUBCLASS_NONE, HID_PROTOCOL_NONE,
)


class TestResourceAllocator:
    def test_interface_sequential(self):
        rc = ResourceAllocator()
        assert rc.alloc_interface() == 0
        assert rc.alloc_interface() == 1
        assert rc.alloc_interface() == 2
        assert rc.interface_count() == 3

    def test_ep_out_sequential(self):
        rc = ResourceAllocator()
        assert rc.alloc_ep_out() == 1
        assert rc.alloc_ep_out() == 2

    def test_ep_in_has_bit7(self):
        rc = ResourceAllocator()
        assert rc.alloc_ep_in() == 0x81
        assert rc.alloc_ep_in() == 0x82

    def test_terminal_ids_unique(self):
        rc = ResourceAllocator()
        ids = [rc.alloc_terminal_id() for _ in range(5)]
        assert ids == [1, 2, 3, 4, 5]

    def test_unit_ids_unique(self):
        rc = ResourceAllocator()
        ids = [rc.alloc_unit_id() for _ in range(3)]
        assert ids == [1, 2, 3]

    def test_clock_ids_unique(self):
        rc = ResourceAllocator()
        ids = [rc.alloc_clock_id() for _ in range(2)]
        assert ids == [1, 2]

    def test_jack_ids_unique(self):
        rc = ResourceAllocator()
        ids = [rc.alloc_jack_id() for _ in range(4)]
        assert ids == [1, 2, 3, 4]

    def test_entity_ids_shared_namespace(self):
        rc = ResourceAllocator()
        t1 = rc.alloc_terminal_id()
        u1 = rc.alloc_unit_id()
        c1 = rc.alloc_clock_id()
        assert t1 == 1
        assert u1 == 2
        assert c1 == 3

    def test_nested_allocation(self):
        rc = ResourceAllocator()
        t1 = rc.alloc_terminal_id()
        u1 = rc.alloc_unit_id()
        assert t1 != u1
        assert t1 + 1 == u1

    def test_strings(self):
        rc = ResourceAllocator()
        assert rc.alloc_string('Test') == 1
        assert rc.alloc_string() == 2
        assert rc.string_map() == {1: 'Test'}


class TestCompositeDevice:
    def test_empty_build(self):
        dev = CompositeDevice(idVendor=0x1234, idProduct=0x5678)
        nodes = dev.build()
        assert len(nodes) == 2
        assert 'Device' in nodes[0].name
        assert 'Configuration' in nodes[1].name

    def test_wTotalLength_correct(self):
        dev = CompositeDevice(idVendor=0x1234, idProduct=0x5678)
        dev.add(uac2_speaker)
        nodes = dev.build()
        config = nodes[1]
        payload = nodes[2:]
        expected = config.encode()[0] + sum(n.encode()[0] for n in payload)
        assert config.wTotalLength == expected

    def test_manufacturer_and_product_strings(self):
        dev = CompositeDevice(
            idVendor=0x1234, idProduct=0x5678,
            manufacturer='Test', product='Composite',
        )
        dev.add(uac2_speaker)
        nodes = dev.build()
        assert nodes[0].iManufacturer == 1
        assert nodes[0].iProduct == 2

    def test_max_power_configurable(self):
        dev = CompositeDevice(idVendor=0x1234, idProduct=0x5678, bMaxPower=200)
        dev.add(uac2_speaker)
        nodes = dev.build()
        assert nodes[1].encode()[8] == 200


class TestUAC2:
    def test_speaker_produces_nodes(self):
        dev = CompositeDevice(idVendor=0x1234, idProduct=0x5678)
        dev.add(uac2_speaker)
        nodes = dev.build()
        assert len(nodes) > 10

    def test_speaker_channel_config_stereo(self):
        dev = CompositeDevice(idVendor=0x1234, idProduct=0x5678)
        dev.add(lambda rc: uac2_speaker(rc, channels=2))
        nodes = dev.build()
        names = [f.name for f in sum([list(n.fields()) for n in nodes], [])]
        assert any('bmChannelConfig[0]' in names for _ in [1])

    def test_speaker_16bit_48k(self):
        dev = CompositeDevice(idVendor=0x1234, idProduct=0x5678)
        dev.add(lambda rc: uac2_speaker(rc, bit_depth=16, sample_rate=48000))
        nodes = dev.build()
        encoded = sum([list(n.encode()) for n in nodes], [])
        assert 16 in encoded

    def test_speaker_24bit_96k(self):
        dev = CompositeDevice(idVendor=0x1234, idProduct=0x5678)
        dev.add(lambda rc: uac2_speaker(rc, bit_depth=24, sample_rate=96000,
                                        channels=2))
        nodes = dev.build()
        encoded = sum([list(n.encode()) for n in nodes], [])
        assert 24 in encoded

    def test_microphone_produces_nodes(self):
        dev = CompositeDevice(idVendor=0x1234, idProduct=0x5678)
        dev.add(lambda rc: uac2_microphone(rc, channels=1))
        nodes = dev.build()
        assert any('Mic' in n.name for n in nodes)

    def test_microphone_no_volume(self):
        dev = CompositeDevice(idVendor=0x1234, idProduct=0x5678)
        dev.add(lambda rc: uac2_microphone(rc, volume=False, mute=False))
        nodes = dev.build()
        assert not any('Feature Unit' in n.name for n in nodes)

    def test_headset_full_duplex(self):
        dev = CompositeDevice(idVendor=0x1234, idProduct=0x5678)
        dev.add(uac2_headset)
        nodes = dev.build()
        names = [n.name for n in nodes]
        assert any('OUT' in n for n in names)
        assert any('IN' in n for n in names)

    def test_speaker_plus_mic_plus_midi(self):
        dev = CompositeDevice(idVendor=0x1234, idProduct=0x5678)
        dev.add(uac2_speaker)
        dev.add(lambda rc: uac2_microphone(rc))
        dev.add(midi_function)
        nodes = dev.build()
        iface_numbers = set()
        for n in nodes[2:]:
            encoded = n.encode()
            if encoded[1] == 0x04:
                iface_numbers.add(encoded[2])
        assert len(iface_numbers) == 6  # IF0(spk AC)+IF1(spk AS)+IF2(mic AC)+IF3(mic AS)+IF4(midi AC)+IF5(midi)


class TestUAC1:
    def test_speaker_produces_nodes(self):
        dev = CompositeDevice(idVendor=0x1234, idProduct=0x5678)
        dev.add(uac1_speaker)
        nodes = dev.build()
        assert any('UAC1' in n.name or 'uac1' in n.name.lower() or
                   'Speaker' in n.name for n in nodes)

    def test_microphone_produces_nodes(self):
        dev = CompositeDevice(idVendor=0x1234, idProduct=0x5678)
        dev.add(uac1_microphone)
        nodes = dev.build()
        assert any('Mic' in n.name for n in nodes)

    def test_uac1_speaker_mic_combo(self):
        dev = CompositeDevice(idVendor=0x1234, idProduct=0x5678)
        dev.add(uac1_speaker)
        dev.add(uac1_microphone)
        nodes = dev.build()
        iface_numbers = set()
        for n in nodes[2:]:
            encoded = n.encode()
            if encoded[1] == 0x04:
                iface_numbers.add(encoded[2])
        assert len(iface_numbers) == 4

    def test_uac1_speaker_has_baInterfaceNr(self):
        dev = CompositeDevice(idVendor=0x1234, idProduct=0x5678)
        dev.add(uac1_speaker)
        nodes = dev.build()
        encoded = sum([list(n.encode()) for n in nodes], [])
        assert 0x01 in encoded

    def test_uac1_line_out_bit_depth(self):
        dev = CompositeDevice(idVendor=0x1234, idProduct=0x5678)
        dev.add(lambda rc: uac1_line_out(rc, bit_depth=24, sample_rate=96000))
        nodes = dev.build()
        encoded = sum([list(n.encode()) for n in nodes], [])
        assert 24 in encoded

    def test_uac1_line_in_out_full_duplex(self):
        dev = CompositeDevice(idVendor=0x1234, idProduct=0x5678)
        dev.add(uac1_line_in_out)
        nodes = dev.build()
        names = [n.name for n in nodes]
        assert any('Line' in n for n in names)

    def test_uac1_headset(self):
        dev = CompositeDevice(idVendor=0x1234, idProduct=0x5678)
        dev.add(uac1_headset)
        nodes = dev.build()
        names = [n.name for n in nodes]
        assert any('Headset' in n for n in names)

    def test_uac1_line_in(self):
        dev = CompositeDevice(idVendor=0x1234, idProduct=0x5678)
        dev.add(uac1_line_in)
        nodes = dev.build()
        assert any('Line' in n.name for n in nodes)
        assert any('IN' in n.name or 'In ' in n.name for n in nodes)

    def test_uac1_custom_multi_path(self):
        dev = CompositeDevice(idVendor=0x1234, idProduct=0x5678)
        def my_uac1(rc):
            nodes, ac_iface = uac1_setup(rc, 'Custom')
            ac1, as1, as1_nr = uac1_audio_path(rc, 'OUT', 2, TERM_SPEAKER,
                                               label='Spk')
            ac2, as2, as2_nr = uac1_audio_path(rc, 'IN', 2, TERM_LINE_CONNECTOR,
                                               label='Line')
            nodes.insert(1, UAC1ACHeader(baInterfaceNr=[as1_nr, as2_nr],
                                         name='Custom AC Header'))
            return nodes + ac1 + ac2 + as1 + as2
        dev.add(my_uac1)
        nodes = dev.build()
        assert any('Spk' in n.name for n in nodes)
        assert any('Line' in n.name for n in nodes)


class TestMIDI:
    def test_default_produces_nodes(self):
        dev = CompositeDevice(idVendor=0x1234, idProduct=0x5678)
        dev.add(midi_function)
        nodes = dev.build()
        assert any('MIDI' in n.name for n in nodes)

    def test_external_jacks(self):
        dev = CompositeDevice(idVendor=0x1234, idProduct=0x5678)
        dev.add(lambda rc: midi_function(rc, jack_type=MIDI_JACK_EXTERNAL))
        nodes = dev.build()
        encoded = sum([list(n.encode()) for n in nodes], [])
        assert MIDI_JACK_EXTERNAL in encoded

    def test_multiple_in_out(self):
        dev = CompositeDevice(idVendor=0x1234, idProduct=0x5678)
        dev.add(lambda rc: midi_function(rc, in_jacks=2, out_jacks=2))
        nodes = dev.build()
        jack_count = sum(1 for n in nodes if 'Jack' in n.name)
        assert jack_count == 4

    def test_in_only(self):
        dev = CompositeDevice(idVendor=0x1234, idProduct=0x5678)
        dev.add(lambda rc: midi_function(rc, in_jacks=1, out_jacks=0))
        nodes = dev.build()
        names = [n.name for n in nodes]
        assert any('IN Jack' in n for n in names)
        assert not any('OUT Jack' in n for n in names)


class TestHID:
    def test_keyboard(self):
        dev = CompositeDevice(idVendor=0x1234, idProduct=0x5678)
        dev.add(hid_keyboard)
        nodes = dev.build()
        assert any('Keyboard' in n.name for n in nodes)

    def test_mouse(self):
        dev = CompositeDevice(idVendor=0x1234, idProduct=0x5678)
        dev.add(hid_mouse)
        nodes = dev.build()
        assert any('Mouse' in n.name for n in nodes)

    def test_generic_custom(self):
        custom_report = bytes([0x05, 0x01, 0x09, 0x01, 0xC0])
        dev = CompositeDevice(idVendor=0x1234, idProduct=0x5678)
        dev.add(lambda rc: hid_generic(
            rc, report_descriptor=custom_report,
            subclass=HID_SUBCLASS_NONE, protocol=HID_PROTOCOL_NONE,
        ))
        nodes = dev.build()
        assert any('HID' in n.name for n in nodes)


class TestCDC:
    def test_acm(self):
        dev = CompositeDevice(idVendor=0x1234, idProduct=0x5678)
        dev.add(cdc_acm)
        nodes = dev.build()
        assert any('CDC' in n.name for n in nodes)


class TestMSC:
    def test_bulk_only(self):
        dev = CompositeDevice(idVendor=0x1234, idProduct=0x5678)
        dev.add(msc_bulk_only)
        nodes = dev.build()
        assert any('MSC' in n.name for n in nodes)


class TestWebUSB:
    def test_platform(self):
        dev = CompositeDevice(idVendor=0x1234, idProduct=0x5678)
        dev.add(webusb_platform)
        nodes = dev.build()
        assert any('WebUSB' in n.name for n in nodes)


class TestMultiFunction:
    def test_speaker_plus_hid(self):
        dev = CompositeDevice(idVendor=0x1234, idProduct=0x5678)
        dev.add(uac2_speaker)
        dev.add(hid_keyboard)
        nodes = dev.build()
        assert any('Speaker' in n.name for n in nodes)
        assert any('Keyboard' in n.name for n in nodes)

    def test_five_functions(self):
        dev = CompositeDevice(idVendor=0x1234, idProduct=0x5678)
        dev.add(uac2_speaker)
        dev.add(midi_function)
        dev.add(hid_keyboard)
        dev.add(cdc_acm)
        dev.add(msc_bulk_only)
        nodes = dev.build()
        config = nodes[1]
        payload = nodes[2:]
        assert config.wTotalLength == config.encode()[0] + sum(
            n.encode()[0] for n in payload
        )


class TestEndpointConfiguration:
    def test_fixed_ep_address_speaker(self):
        dev = CompositeDevice(idVendor=0x1234, idProduct=0x5678)
        dev.add(lambda rc: uac2_speaker(rc, ep_address=0x05))
        nodes = dev.build()
        encoded = sum([list(n.encode()) for n in nodes], [])
        assert 0x05 in encoded

    def test_fixed_ep_midi(self):
        dev = CompositeDevice(idVendor=0x1234, idProduct=0x5678)
        dev.add(lambda rc: midi_function(rc, ep_out_address=0x03,
                                          ep_in_address=0x84))
        nodes = dev.build()
        encoded = sum([list(n.encode()) for n in nodes], [])
        assert 0x03 in encoded
        assert 0x84 in encoded

    def test_fixed_ep_hid(self):
        dev = CompositeDevice(idVendor=0x1234, idProduct=0x5678)
        dev.add(lambda rc: hid_keyboard(rc, ep_address=0x82))
        nodes = dev.build()
        encoded = sum([list(n.encode()) for n in nodes], [])
        assert 0x82 in encoded

    def test_ep_out_base_skips(self):
        dev = CompositeDevice(idVendor=0x1234, idProduct=0x5678,
                              ep_out_base=3)
        dev.add(uac2_speaker)
        nodes = dev.build()
        ep_values = []
        for n in nodes:
            encoded = n.encode()
            if encoded[1] == 0x05:
                ep_values.append((n.name, encoded[2]))
        assert any(v == 3 for _, v in ep_values), \
            f'Expected EP 3, got {ep_values}'

    def test_reserve_ep_skips_allocated(self):
        rc = ResourceAllocator(ep_out_base=1)
        rc.reserve_ep_out(3)
        rc.reserve_ep_out(5)
        e1 = rc.alloc_ep_out()
        e2 = rc.alloc_ep_out()
        e3 = rc.alloc_ep_out()
        e4 = rc.alloc_ep_out()
        assert e1 == 1
        assert e2 == 2
        assert e3 == 4
        assert e4 == 6

    def test_reserve_ep_in_skips_allocated(self):
        rc = ResourceAllocator(ep_in_base=1)
        rc.reserve_ep_in(0x83)
        e1 = rc.alloc_ep_in()
        e2 = rc.alloc_ep_in()
        assert e1 == 0x81
        assert e2 == 0x82


class TestDeviceConfiguration:
    def test_bcdUSB_configurable(self):
        dev = CompositeDevice(idVendor=0x1234, idProduct=0x5678,
                              bcdUSB=0x0110)
        dev.add(uac2_speaker)
        nodes = dev.build()
        assert nodes[0].bcdUSB == 0x0110
        assert nodes[0].encode()[2] == 0x10
        assert nodes[0].encode()[3] == 0x01

    def test_bMaxPacketSize0_configurable(self):
        dev = CompositeDevice(idVendor=0x1234, idProduct=0x5678,
                              bMaxPacketSize0=8)
        dev.add(uac2_speaker)
        nodes = dev.build()
        assert nodes[0].bMaxPacketSize0 == 8
        assert nodes[0].encode()[7] == 8

    def test_bMaxPower_configurable(self):
        dev = CompositeDevice(idVendor=0x1234, idProduct=0x5678,
                              bMaxPower=200)
        dev.add(uac2_speaker)
        nodes = dev.build()
        assert nodes[1].encode()[8] == 200

    def test_bmAttributes_configurable(self):
        dev = CompositeDevice(idVendor=0x1234, idProduct=0x5678,
                              bmAttributes=0xC0)
        dev.add(uac2_speaker)
        nodes = dev.build()
        assert nodes[1].encode()[7] == 0xC0


class TestHighSpeed:
    def test_device_qualifier_included(self):
        dev = CompositeDevice(idVendor=0x1234, idProduct=0x5678,
                              high_speed=True)
        dev.add(uac2_speaker)
        nodes = dev.build()
        names = [n.name for n in nodes]
        assert 'Device' in names[0]
        assert 'Device Qualifier' in names[1]
        assert 'Configuration' in names[2]
        assert 'Other Speed Config' in names[-1]

    def test_no_qualifier_without_hs(self):
        dev = CompositeDevice(idVendor=0x1234, idProduct=0x5678,
                              high_speed=False)
        dev.add(uac2_speaker)
        nodes = dev.build()
        names = [n.name for n in nodes]
        assert 'Device Qualifier' not in names
        assert 'Other Speed Config' not in names

    def test_qualifier_descriptor_type(self):
        dev = CompositeDevice(idVendor=0x1234, idProduct=0x5678,
                              high_speed=True)
        dev.add(uac2_speaker)
        nodes = dev.build()
        qual = nodes[1]
        assert qual.encode()[1] == 0x06

    def test_other_speed_descriptor_type(self):
        dev = CompositeDevice(idVendor=0x1234, idProduct=0x5678,
                              high_speed=True)
        dev.add(uac2_speaker)
        nodes = dev.build()
        other = nodes[-1]
        assert other.encode()[1] == 0x07

    def test_other_speed_wTotalLength_matches(self):
        dev = CompositeDevice(idVendor=0x1234, idProduct=0x5678,
                              high_speed=True)
        dev.add(uac2_speaker)
        nodes = dev.build()
        other = nodes[-1]
        assert other.wTotalLength == 9  # minimal: just the config descriptor itself

    def test_hs_transactions_encoded(self):
        dev = CompositeDevice(idVendor=0x1234, idProduct=0x5678,
                              high_speed=True)
        dev.add(lambda rc: uac2_speaker(rc, hs_transactions=3))
        nodes = dev.build()
        found = False
        for n in nodes:
            encoded = n.encode()
            if encoded[1] == 0x05:
                wMaxPkt = encoded[4] | (encoded[5] << 8)
                if wMaxPkt & 0x1800:
                    found = True
        assert found, 'No HS encoded wMaxPacketSize found'

    def test_hs_full_duplex_headset(self):
        dev = CompositeDevice(idVendor=0x1234, idProduct=0x5678,
                              high_speed=True, bMaxPower=200)
        dev.add(uac2_headset)
        nodes = dev.build()
        assert len(nodes) > 15
        assert 'Device Qualifier' in nodes[1].name

    def test_hs_line_in_out(self):
        dev = CompositeDevice(idVendor=0x1234, idProduct=0x5678,
                              high_speed=True)
        dev.add(lambda rc: uac2_line_in_out(rc, hs_transactions=2))
        nodes = dev.build()
        assert len(nodes) > 15


class TestLineFunctions:
    def test_line_out_produces_nodes(self):
        dev = CompositeDevice(idVendor=0x1234, idProduct=0x5678)
        dev.add(uac2_line_out)
        nodes = dev.build()
        assert any('Line' in n.name for n in nodes)
        assert any('OUT' in n.name or 'Out' in n.name for n in nodes)

    def test_line_in_produces_nodes(self):
        dev = CompositeDevice(idVendor=0x1234, idProduct=0x5678)
        dev.add(uac2_line_in)
        nodes = dev.build()
        assert any('Line' in n.name for n in nodes)
        assert any('IN' in n.name or 'In' in n.name for n in nodes)

    def test_line_in_out_full_duplex(self):
        dev = CompositeDevice(idVendor=0x1234, idProduct=0x5678)
        dev.add(uac2_line_in_out)
        nodes = dev.build()
        names = [n.name for n in nodes]
        assert any(name.startswith('Line') for name in names)
        out_count = sum(1 for n in nodes if n.encode()[1] == 0x05
                        and n.encode()[2] & 0x80 == 0)
        in_count = sum(1 for n in nodes if n.encode()[1] == 0x05
                       and n.encode()[2] & 0x80)
        assert out_count >= 1
        assert in_count >= 1

    def test_line_out_24bit_96k(self):
        dev = CompositeDevice(idVendor=0x1234, idProduct=0x5678)
        dev.add(lambda rc: uac2_line_out(rc, bit_depth=24, sample_rate=96000))
        nodes = dev.build()
        encoded = sum([list(n.encode()) for n in nodes], [])
        assert 24 in encoded

    def test_line_in_out_with_midi(self):
        dev = CompositeDevice(idVendor=0x1234, idProduct=0x5678)
        dev.add(uac2_line_in_out)
        dev.add(midi_function)
        nodes = dev.build()
        assert any('MIDI' in n.name for n in nodes)


class TestCustomPath:
    def test_setup_returns_clock_id(self):
        rc = ResourceAllocator()
        nodes, clk = uac2_setup(rc)
        assert clk > 0
        assert len(nodes) == 3

    def test_custom_single_path(self):
        rc = ResourceAllocator()
        nodes, clk = uac2_setup(rc)
        ac, ast = uac2_audio_path(rc, 'OUT', 2, TERM_SPEAKER, clock_id=clk)
        nodes += ac + ast
        dev = CompositeDevice(idVendor=0x1234, idProduct=0x5678)
        dev.add(lambda _: nodes)
        result = dev.build()
        assert any('Speaker' in n.name for n in result)

    def test_custom_multi_path_device(self):
        dev = CompositeDevice(idVendor=0x1234, idProduct=0x5678)
        def my_pro_audio(rc):
            n, c = uac2_setup(rc, category=FUNCTION_IO_BOX, name='Multi I/O')
            ac1, as1 = uac2_audio_path(rc, 'OUT', 2, TERM_SPEAKER,
                                        volume=True, clock_id=c, label='Main')
            ac2, as2 = uac2_audio_path(rc, 'OUT', 2, TERM_LINE_CONNECTOR,
                                        volume=True, clock_id=c, label='LineOut')
            ac3, as3 = uac2_audio_path(rc, 'IN', 2, TERM_LINE_CONNECTOR,
                                        volume=True, clock_id=c, label='LineIn')
            n += ac1 + ac2 + ac3 + as1 + as2 + as3
            return n
        dev.add(my_pro_audio)
        nodes = dev.build()
        names = [n.name for n in nodes]
        assert sum(1 for n in names if 'Main' in n) > 0
        assert sum(1 for n in names if 'LineOut' in n) > 0
        assert sum(1 for n in names if 'LineIn' in n) > 0
