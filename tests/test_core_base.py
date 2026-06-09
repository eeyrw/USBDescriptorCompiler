import pytest
from usbdesc.core.base import Field, u8, u16le, u24le, u32le
from usbdesc.core.encoder import DescriptorEncoder
from usbdesc.device_class.audio.uac2 import InputTerminal
from usbdesc.core.types import TERM_USB_STREAMING


def test_u8():
    f = u8('test', 0xAB)
    assert len(f) == 1
    assert f[0] == Field('test', 0xAB, 1)


def test_u16le():
    fields = u16le('test', 0x1234)
    assert len(fields) == 2
    assert fields[0] == Field('test[0]', 0x34, 1)
    assert fields[1] == Field('test[1]', 0x12, 1)


def test_u24le():
    fields = u24le('test', 0x0B6000)
    assert len(fields) == 3
    assert fields[0] == Field('test[0]', 0x00, 1)
    assert fields[1] == Field('test[1]', 0x60, 1)
    assert fields[2] == Field('test[2]', 0x0B, 1)


def test_u32le():
    fields = u32le('test', 0x12345678)
    assert len(fields) == 4
    assert fields[0] == Field('test[0]', 0x78, 1)
    assert fields[1] == Field('test[1]', 0x56, 1)
    assert fields[2] == Field('test[2]', 0x34, 1)
    assert fields[3] == Field('test[3]', 0x12, 1)


class TestDescriptorEncoder:
    def test_encodes_nodes(self):
        it = InputTerminal(bTerminalID=1, wTerminalType=TERM_USB_STREAMING)
        result = DescriptorEncoder().encode_nodes([it])
        assert isinstance(result, bytes)
        assert result[0] == 17

    def test_encodes_raw_bytes(self):
        encoder = DescriptorEncoder()
        result = encoder.encode_nodes([b'\x01\x02\x03'])
        assert result == b'\x01\x02\x03'

    def test_encodes_bytearray(self):
        encoder = DescriptorEncoder()
        result = encoder.encode_nodes([bytearray(b'\xff\xfe')])
        assert result == b'\xff\xfe'

    def test_mixed_nodes_and_bytes(self):
        it = InputTerminal(bTerminalID=1, wTerminalType=TERM_USB_STREAMING)
        encoder = DescriptorEncoder()
        result = encoder.encode_nodes([it, b'\x99'])
        assert len(result) == 18

    def test_unknown_type_raises(self):
        encoder = DescriptorEncoder()
        with pytest.raises(TypeError):
            encoder.encode_nodes([42])
