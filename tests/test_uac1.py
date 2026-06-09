import pytest
from usbdesc.core.types import (
    CS_INTERFACE, CS_ENDPOINT,
    TERM_USB_STREAMING, TERM_SPEAKER,
    CHANNEL_STEREO, FORMAT_TYPE_I,
    UAC1_BCD,
)
from usbdesc.device_class.audio.uac1 import (
    ACHeader, InputTerminal, OutputTerminal, FeatureUnit,
    ASGeneral, FormatTypeI, ClassSpecificIsoEP,
    MixerUnit, SelectorUnit, ProcessingUnit, ExtensionUnit,
)


class TestUAC1ACHeader:
    def test_bLength_variable(self):
        hdr = ACHeader(baInterfaceNr=[1, 2])
        assert hdr.fields()[0].value == 8 + 2

    def test_bcdADC(self):
        hdr = ACHeader(baInterfaceNr=[1])
        encoded = hdr.encode()
        assert encoded[3] == 0x00
        assert encoded[4] == 0x01


class TestUAC1InputTerminal:
    def test_bLength(self):
        it = InputTerminal(bTerminalID=1, wTerminalType=TERM_USB_STREAMING)
        assert it.fields()[0].value == 12

    def test_2byte_wChannelConfig(self):
        it = InputTerminal(bTerminalID=1, wTerminalType=TERM_USB_STREAMING,
                           wChannelConfig=CHANNEL_STEREO)
        encoded = it.encode()
        assert encoded[8] == 0x03
        assert encoded[9] == 0x00

    def test_no_bmControls(self):
        it = InputTerminal(bTerminalID=1, wTerminalType=TERM_USB_STREAMING)
        encoded = it.encode()
        assert len(encoded) == 12


class TestUAC1OutputTerminal:
    def test_bLength(self):
        ot = OutputTerminal(bTerminalID=2, wTerminalType=TERM_SPEAKER)
        assert ot.fields()[0].value == 9


class TestUAC1FeatureUnit:
    def test_has_bControlSize(self):
        fu = FeatureUnit(bUnitID=4, bSourceID=3,
                         controls_per_channel=[0x03, 0x00],
                         bControlSize=1)
        encoded = fu.encode()
        assert encoded[5] == 1  # bControlSize


class TestUAC1ASGeneral:
    def test_bLength(self):
        asg = ASGeneral(bTerminalLink=3)
        assert asg.fields()[0].value == 7

    def test_has_wFormatTag(self):
        asg = ASGeneral(bTerminalLink=3, wFormatTag=FORMAT_TYPE_I)
        encoded = asg.encode()
        assert encoded[5] == 0x01
        assert encoded[6] == 0x00


class TestUAC1FormatTypeI:
    def test_includes_sample_rates(self):
        fmt = FormatTypeI(bNrChannels=2, bSubframeSize=2,
                          bBitResolution=16, sample_rates=[48000])
        assert fmt.fields()[0].value == 8 + 3

    def test_3byte_sample_rate(self):
        fmt = FormatTypeI(bNrChannels=2, bSubframeSize=2,
                          bBitResolution=16, sample_rates=[48000])
        encoded = fmt.encode()
        assert encoded[8] == 0x80  # 0x0BB80
        assert encoded[9] == 0xBB
        assert encoded[10] == 0x00


class TestUAC1MixerUnit:
    def test_2byte_wChannelConfig(self):
        mu = MixerUnit(bUnitID=5, baSourceID=[2, 3])
        encoded = mu.encode()
        n_pins = 2
        base = 3 + 1 + 1 + n_pins
        assert encoded[base] == 2  # bNrChannels
        assert encoded[base + 1] == 0x03  # wChannelConfig[0]
        assert encoded[base + 2] == 0x00  # wChannelConfig[1]


class TestUAC1ClassSpecificIsoEP:
    def test_bLength(self):
        ep = ClassSpecificIsoEP(bmAttributes=0x00)
        assert ep.fields()[0].value == 7

    def test_no_bmControls(self):
        ep = ClassSpecificIsoEP(bmAttributes=0x00)
        encoded = ep.encode()
        assert len(encoded) == 7
        assert encoded[1] == CS_ENDPOINT


class TestUAC1SelectorUnit:
    def test_bLength(self):
        su = SelectorUnit(bUnitID=5, baSourceID=[1, 2])
        assert su.fields()[0].value == 4 + 1 + 2 + 1  # header + bNrInPins + 2 sources + iSelector

    def test_variable_length(self):
        su = SelectorUnit(bUnitID=5, baSourceID=[1, 2, 3])
        assert su.fields()[0].value == 4 + 1 + 3 + 1

    def test_subtype(self):
        su = SelectorUnit(bUnitID=5, baSourceID=[1])
        encoded = su.encode()
        assert encoded[2] == 0x05


class TestUAC1ProcessingUnit:
    def test_bLength_basic(self):
        pu = ProcessingUnit(bUnitID=6, wProcessType=0x01, baSourceID=[2])
        assert pu.fields()[0].value > 13

    def test_subtype_is_0x07(self):
        pu = ProcessingUnit(bUnitID=6, wProcessType=0x01, baSourceID=[2])
        encoded = pu.encode()
        assert encoded[2] == 0x07

    def test_wProcessType(self):
        pu = ProcessingUnit(bUnitID=6, wProcessType=0x0201, baSourceID=[2])
        encoded = pu.encode()
        assert encoded[4] == 0x01
        assert encoded[5] == 0x02


class TestUAC1ExtensionUnit:
    def test_bLength_basic(self):
        eu = ExtensionUnit(bUnitID=7, wExtensionCode=0x0001, baSourceID=[3])
        assert eu.fields()[0].value > 13

    def test_subtype_is_0x08(self):
        eu = ExtensionUnit(bUnitID=7, wExtensionCode=0x0001, baSourceID=[3])
        encoded = eu.encode()
        assert encoded[2] == 0x08

    def test_wExtensionCode(self):
        eu = ExtensionUnit(bUnitID=7, wExtensionCode=0xABCD, baSourceID=[3])
        encoded = eu.encode()
        assert encoded[4] == 0xCD
        assert encoded[5] == 0xAB
