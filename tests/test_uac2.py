import pytest
from usbdesc.core.types import (
    ACSubtype, ASSubtype, EPSubtype, MIDISubtype,
    TERM_USB_STREAMING, TERM_SPEAKER,
    CHANNEL_STEREO, BM_FORMAT_PCM,
    CLOCK_INT_FIXED,
    FUNCTION_DESKTOP_SPEAKER,
    FORMAT_TYPE_I,
    UAC2_BCD,
    CS_INTERFACE, CS_ENDPOINT, DESC_TYPE_ENDPOINT,
)
from usbdesc.device_class.audio.uac2 import (
    ACHeader, InputTerminal, OutputTerminal, FeatureUnit,
    ClockSource, ASGeneral, FormatTypeI, ClassSpecificIsoEP,
    MixerUnit, SelectorUnit, ClockSelector, ClockMultiplier,
    SampleRateConverter,
    EffectUnit, ProcessingUnit, ExtensionUnit,
    Encoder, Decoder,
    MIDIInJack, MIDIOutJack, MIDIOutBulkEP, MIDIInBulkEP,
    uac2_ctrl_pair,
)


class TestACHeader:
    def test_bLength(self):
        hdr = ACHeader(bCategory=FUNCTION_DESKTOP_SPEAKER)
        assert hdr.fields()[0].value == 9

    def test_bcdADC(self):
        hdr = ACHeader(bCategory=FUNCTION_DESKTOP_SPEAKER)
        encoded = hdr.encode()
        assert encoded[3] == 0x00
        assert encoded[4] == 0x02

    def test_subtype_is_header(self):
        hdr = ACHeader(bCategory=FUNCTION_DESKTOP_SPEAKER)
        encoded = hdr.encode()
        assert encoded[1] == CS_INTERFACE
        assert encoded[2] == ACSubtype.HEADER


class TestInputTerminal:
    def test_bLength(self):
        it = InputTerminal(bTerminalID=1, wTerminalType=TERM_USB_STREAMING)
        assert it.fields()[0].value == 17

    def test_field_order(self):
        it = InputTerminal(bTerminalID=1, wTerminalType=TERM_USB_STREAMING,
                           bCSourceID=1, bNrChannels=2,
                           bmChannelConfig=CHANNEL_STEREO)
        encoded = it.encode()
        assert encoded[0] == 17
        assert encoded[1] == CS_INTERFACE
        assert encoded[2] == ACSubtype.INPUT_TERMINAL
        assert encoded[3] == 1  # bTerminalID
        assert encoded[4] == 0x01  # wTerminalType[0]
        assert encoded[5] == 0x01  # wTerminalType[1]

    def test_bmChannelConfig_4byte(self):
        it = InputTerminal(bTerminalID=1, wTerminalType=TERM_USB_STREAMING,
                           bmChannelConfig=0x00000003)
        encoded = it.encode()
        assert encoded[9] == 0x03  # bmChannelConfig[0]
        assert encoded[10] == 0x00  # bmChannelConfig[1]
        assert encoded[11] == 0x00  # bmChannelConfig[2]
        assert encoded[12] == 0x00  # bmChannelConfig[3]


class TestOutputTerminal:
    def test_bLength(self):
        ot = OutputTerminal(bTerminalID=2, wTerminalType=TERM_SPEAKER)
        assert ot.fields()[0].value == 12

    def test_has_bCSourceID(self):
        ot = OutputTerminal(bTerminalID=2, wTerminalType=TERM_SPEAKER,
                            bCSourceID=1)
        encoded = ot.encode()
        assert encoded[8] == 1  # bCSourceID

    def test_has_bmControls(self):
        ot = OutputTerminal(bTerminalID=2, wTerminalType=TERM_SPEAKER,
                            bmControls=0xFF)
        encoded = ot.encode()
        assert encoded[9] == 0xFF


class TestFeatureUnit:
    def test_bLength_calculated(self):
        fu = FeatureUnit(bUnitID=4, bSourceID=3,
                         controls_per_channel=[0, 0, 0])
        assert fu.fields()[0].value == 18

    def test_empty_controls(self):
        fu = FeatureUnit(bUnitID=4, bSourceID=3)
        assert fu.fields()[0].value == 6

    def test_controls_per_channel_4byte(self):
        fu = FeatureUnit(bUnitID=4, bSourceID=3,
                         controls_per_channel=[0x0000000F, 0x0000000F])
        encoded = fu.encode()
        ch0_ctrl = list(encoded[5:9])
        assert ch0_ctrl == [0x0F, 0x00, 0x00, 0x00]


class TestClockSource:
    def test_bLength(self):
        cs = ClockSource(bClockID=1, bmAttributes=CLOCK_INT_FIXED)
        assert cs.fields()[0].value == 8

    def test_default_bmControls_is_00(self):
        cs = ClockSource(bClockID=1, bmAttributes=CLOCK_INT_FIXED)
        encoded = cs.encode()
        assert encoded[5] == 0x00


class TestClockSelector:
    def test_variable_length(self):
        csel = ClockSelector(bClockID=2, baCSourceID=[1, 3])
        assert csel.fields()[0].value == 7 + 2


class TestClockMultiplier:
    def test_bLength(self):
        cm = ClockMultiplier(bClockID=3, bCSourceID=1)
        assert cm.fields()[0].value == 7


class TestSampleRateConverter:
    def test_bLength(self):
        src = SampleRateConverter(bUnitID=10, bSourceID=5)
        assert src.fields()[0].value == 8

    def test_has_clock_source_ids(self):
        src = SampleRateConverter(bUnitID=10, bSourceID=5,
                                   bCSourceInID=1, bCSourceOutID=2)
        encoded = src.encode()
        assert encoded[5] == 1  # bCSourceInID
        assert encoded[6] == 2  # bCSourceOutID


class TestASGeneral:
    def test_bLength(self):
        asg = ASGeneral(bTerminalLink=3)
        assert asg.fields()[0].value == 16

    def test_has_bmFormats_not_wFormatTag(self):
        asg = ASGeneral(bTerminalLink=3, bmFormats=BM_FORMAT_PCM)
        encoded = asg.encode()
        assert encoded[6] == 0x01  # bmFormats[0]
        assert encoded[7] == 0x00
        assert encoded[8] == 0x00
        assert encoded[9] == 0x00

    def test_bmChannelConfig_4byte(self):
        asg = ASGeneral(bTerminalLink=3, bmChannelConfig=CHANNEL_STEREO)
        encoded = asg.encode()
        assert encoded[11] == 0x03
        assert encoded[12] == 0x00
        assert encoded[13] == 0x00
        assert encoded[14] == 0x00


class TestFormatTypeI:
    def test_bLength(self):
        fmt = FormatTypeI(bSubslotSize=2, bBitResolution=16)
        assert fmt.fields()[0].value == 6

    def test_no_sample_rates(self):
        fmt = FormatTypeI(bSubslotSize=2, bBitResolution=16)
        encoded = fmt.encode()
        assert encoded[4] == 2  # bSubslotSize
        assert encoded[5] == 16  # bBitResolution


class TestMixerUnit:
    def test_variable_length(self):
        mu = MixerUnit(bUnitID=5, baSourceID=[2, 4], bmMixerControls=[0x00])
        assert mu.fields()[0].value > 13


class TestSelectorUnit:
    def test_variable_length(self):
        su = SelectorUnit(bUnitID=6, baSourceID=[1, 2, 3])
        assert su.fields()[0].value == 7 + 3


class TestClassSpecificIsoEP:
    def test_bLength(self):
        ep = ClassSpecificIsoEP(bmAttributes=0x00, bmControls=0x00)
        assert ep.fields()[0].value == 8

    def test_descriptor_type_is_cs_endpoint(self):
        ep = ClassSpecificIsoEP()
        encoded = ep.encode()
        assert encoded[1] == CS_ENDPOINT  # 0x25


class TestMIDIInJack:
    def test_bLength(self):
        jack = MIDIInJack(bJackID=10)
        assert jack.fields()[0].value == 6

    def test_subtype(self):
        jack = MIDIInJack(bJackID=10)
        encoded = jack.encode()
        assert encoded[2] == 0x02  # MIDI_IN_JACK


class TestMIDIOutJack:
    def test_bLength(self):
        jack = MIDIOutJack(bJackID=11, baSourceID=[10])
        assert jack.fields()[0].value == 6 + 2 + 1  # +2 for 1 source, +1 for iJack

    def test_subtype(self):
        jack = MIDIOutJack(bJackID=11, baSourceID=[10])
        encoded = jack.encode()
        assert encoded[2] == 0x03  # MIDI_OUT_JACK


class TestMIDIBulkEP:
    def test_out_ep(self):
        ep = MIDIOutBulkEP(baAssocJackID=[11])
        encoded = ep.encode()
        assert encoded[2] == 0x01  # OUT subtype

    def test_in_ep(self):
        ep = MIDIInBulkEP(baAssocJackID=[10])
        encoded = ep.encode()
        assert encoded[2] == 0x01  # MS_GENERAL (same subtype for both IN/OUT bulk EPs)


class TestEffectUnit:
    def test_bLength(self):
        ef = EffectUnit(bUnitID=7, wEffectType=0x0001, bSourceID=3,
                        controls_per_channel=[0, 0])
        assert ef.fields()[0].value == 16

    def test_subtype(self):
        ef = EffectUnit(bUnitID=7, wEffectType=0x0001, bSourceID=3,
                        controls_per_channel=[0, 0])
        encoded = ef.encode()
        assert encoded[2] == ACSubtype.EFFECT_UNIT

    def test_wEffectType_encoded(self):
        ef = EffectUnit(bUnitID=7, wEffectType=0x0002, bSourceID=3,
                        controls_per_channel=[0, 0])
        encoded = ef.encode()
        assert encoded[4] == 0x02  # wEffectType[0]
        assert encoded[5] == 0x00  # wEffectType[1]

    def test_controls_per_channel_4byte(self):
        ef = EffectUnit(bUnitID=7, wEffectType=0x0001, bSourceID=3,
                        controls_per_channel=[0x0000000A, 0x0000000F])
        encoded = ef.encode()
        assert encoded[7] == 0x0A  # bmaControls[master][0]
        assert encoded[11] == 0x0F  # bmaControls[ch1][0]


class TestProcessingUnit:
    def test_bLength(self):
        pu = ProcessingUnit(bUnitID=8, wProcessType=0x0001, baSourceID=[3])
        assert pu.fields()[0].value == 15

    def test_subtype(self):
        pu = ProcessingUnit(bUnitID=8, wProcessType=0x0001, baSourceID=[3])
        encoded = pu.encode()
        assert encoded[2] == ACSubtype.PROCESSING_UNIT

    def test_multiple_sources(self):
        pu = ProcessingUnit(bUnitID=8, wProcessType=0x0001, baSourceID=[3, 5])
        assert pu.fields()[0].value == 16

    def test_bmChannelConfig_4byte(self):
        pu = ProcessingUnit(bUnitID=8, wProcessType=0x0001, baSourceID=[3],
                            bmChannelConfig=CHANNEL_STEREO)
        encoded = pu.encode()
        vals = [encoded[9], encoded[10], encoded[11], encoded[12]]
        assert vals == [0x03, 0x00, 0x00, 0x00]


class TestExtensionUnit:
    def test_bLength(self):
        xu = ExtensionUnit(bUnitID=9, wExtensionCode=0x0001, baSourceID=[3])
        assert xu.fields()[0].value == 16

    def test_subtype(self):
        xu = ExtensionUnit(bUnitID=9, wExtensionCode=0x0001, baSourceID=[3])
        encoded = xu.encode()
        assert encoded[2] == ACSubtype.EXTENSION_UNIT

    def test_wExtensionCode(self):
        xu = ExtensionUnit(bUnitID=9, wExtensionCode=0xABCD, baSourceID=[3])
        encoded = xu.encode()
        assert encoded[4] == 0xCD
        assert encoded[5] == 0xAB

    def test_bmControls_is_single_byte(self):
        xu = ExtensionUnit(bUnitID=9, wExtensionCode=0x0001, baSourceID=[3],
                           bmControls=0x03)
        encoded = xu.encode()
        assert encoded[14] == 0x03


class TestEncoder:
    def test_bLength(self):
        enc = Encoder(bEncoderID=1, wEncoderType=0x0001)
        assert enc.fields()[0].value == 7

    def test_subtype(self):
        enc = Encoder(bEncoderID=1, wEncoderType=0x0001)
        encoded = enc.encode()
        assert encoded[2] == ASSubtype.ENCODER

    def test_iEncoder(self):
        enc = Encoder(bEncoderID=1, wEncoderType=0x0001, iEncoder=5)
        encoded = enc.encode()
        assert encoded[6] == 5


class TestDecoder:
    def test_bLength(self):
        dec = Decoder(bDecoderID=1, wDecoderType=0x0001)
        assert dec.fields()[0].value == 7

    def test_subtype(self):
        dec = Decoder(bDecoderID=1, wDecoderType=0x0001)
        encoded = dec.encode()
        assert encoded[2] == ASSubtype.DECODER

    def test_iDecoder(self):
        dec = Decoder(bDecoderID=1, wDecoderType=0x0001, iDecoder=5)
        encoded = dec.encode()
        assert encoded[6] == 5


class TestUAC2CtrlPair:
    def test_both_readwrite(self):
        assert uac2_ctrl_pair(0x03, 0x03) == 0x0F

    def test_readonly_only(self):
        assert uac2_ctrl_pair(0x01, 0x00) == 0x01

    def test_readwrite_only(self):
        assert uac2_ctrl_pair(0x00, 0x03) == 0x0C

    def test_none(self):
        assert uac2_ctrl_pair(0x00, 0x00) == 0x00
