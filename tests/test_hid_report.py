import pytest
from usbdesc.device_class.hid_report import (
    HIDReport, USAGE_PAGE, USAGES, COLL, IO,
    _encode_item, _ITEM_TYPE_GLOBAL, _ITEM_TYPE_MAIN,
)


class TestEncodeItem:
    def test_no_data(self):
        out = _encode_item(_ITEM_TYPE_GLOBAL, 1, None)
        assert out == bytes([0x14])

    def test_1_byte(self):
        out = _encode_item(_ITEM_TYPE_GLOBAL, 1, 0x01)
        assert len(out) == 2
        assert out[0] == 0x15
        assert out[1] == 0x01

    def test_2_byte(self):
        out = _encode_item(_ITEM_TYPE_GLOBAL, 1, 0x03FF)
        assert len(out) == 3
        assert out[0] == 0x16

    def test_4_byte(self):
        out = _encode_item(_ITEM_TYPE_GLOBAL, 1, 0x10000)
        assert len(out) == 5

    def test_negative_1_byte(self):
        out = _encode_item(_ITEM_TYPE_GLOBAL, 1, -127)
        assert out[1] == 0x81

    def test_usage_page(self):
        out = _encode_item(_ITEM_TYPE_GLOBAL, 0, USAGE_PAGE.GENERIC_DESKTOP)
        assert out == bytes([0x05, 0x01])


class TestHIDReport:
    def test_empty_encodes_empty(self):
        r = HIDReport()
        assert r.encode() == b''

    def test_usage_page(self):
        r = HIDReport()
        r.usage_page(USAGE_PAGE.GENERIC_DESKTOP)
        assert r.encode() == bytes([0x05, 0x01])

    def test_basic_keyboard_start(self):
        r = HIDReport()
        r.usage_page(USAGE_PAGE.GENERIC_DESKTOP)\
         .usage(USAGES.GENERIC_DESKTOP.KEYBOARD)\
         .collection(COLL.APPLICATION)
        assert r.encode() == bytes([0x05, 0x01, 0x09, 0x06, 0xA1, 0x01])

    def test_collection_end_collection(self):
        r = HIDReport()
        r.collection(COLL.PHYSICAL).end_collection()
        assert r.encode() == bytes([0xA1, 0x00, 0xC0])

    def test_byte_count(self):
        r = HIDReport()
        r.usage_page(USAGE_PAGE.GENERIC_DESKTOP)\
         .usage(USAGES.GENERIC_DESKTOP.KEYBOARD)\
         .collection(COLL.APPLICATION)\
         .end_collection()
        assert len(r) == len(r.encode())
        assert len(r.encode()) == 7

    def test_logical_min_max(self):
        r = HIDReport()
        r.logical_min(0).logical_max(1)
        raw = r.encode()
        assert raw[0] == 0x15
        assert raw[1] == 0x00
        assert raw[2] == 0x25
        assert raw[3] == 0x01

    def test_report_size_count(self):
        r = HIDReport()
        r.report_size(8).report_count(6)
        raw = r.encode()
        assert raw[0] == 0x75 and raw[1] == 8
        assert raw[2] == 0x95 and raw[3] == 6

    def test_input_flags(self):
        r = HIDReport()
        r.input(IO.DATA | IO.VARIABLE | IO.ABSOLUTE)
        raw = r.encode()
        assert raw == bytes([0x81, 0x02])

    def test_output_flags(self):
        r = HIDReport()
        r.output(IO.CONSTANT)
        raw = r.encode()
        assert raw == bytes([0x91, 0x01])

    def test_chaining_returns_self(self):
        r = HIDReport()
        result = r.usage_page(1).usage(2).logical_min(0)
        assert result is r

    def test_complete_keyboard_terminates_with_c0(self):
        r = HIDReport()
        r.usage_page(USAGE_PAGE.GENERIC_DESKTOP)\
         .usage(USAGES.GENERIC_DESKTOP.KEYBOARD)\
         .collection(COLL.APPLICATION)\
         .end_collection()
        assert r.encode()[-1] == 0xC0

    def test_report_id(self):
        r = HIDReport()
        r.report_id(3)
        assert r.encode() == bytes([0x85, 0x03])

    def test_push_pop(self):
        r = HIDReport()
        r.push().pop()
        assert r.encode() == bytes([0xA4, 0xB4])

    def test_consumer_media_keys(self):
        r = HIDReport()
        r.usage_page(USAGE_PAGE.CONSUMER)\
         .usage(USAGES.CONSUMER.PLAY_PAUSE)\
         .collection(COLL.APPLICATION)\
         .usage(USAGES.CONSUMER.VOLUME_INCREMENT)\
         .usage(USAGES.CONSUMER.VOLUME_DECREMENT)\
         .logical_min(0).logical_max(1)\
         .report_size(1).report_count(3)\
         .input(IO.DATA | IO.VARIABLE | IO.ABSOLUTE)\
         .end_collection()
        assert r.encode()[-1] == 0xC0
        assert len(r.encode()) > 0
