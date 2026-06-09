import pytest
from usbdesc.device_class.cdc import CDCHeader, CDCCallManagement, CDCACM, CDCUnion
from usbdesc.core.types import CDCSubtype, CDC_DESC_TYPE_CS_INTERFACE


class TestCDCHeader:
    def test_bLength(self):
        hdr = CDCHeader()
        assert hdr.fields()[0].value == 5

    def test_bcdCDC(self):
        hdr = CDCHeader(bcdCDC=0x0120)
        encoded = hdr.encode()
        assert encoded[3] == 0x20
        assert encoded[4] == 0x01


class TestCDCCallManagement:
    def test_bLength(self):
        cm = CDCCallManagement(bmCapabilities=0x03, bDataInterface=1)
        assert cm.fields()[0].value == 5

    def test_fields(self):
        cm = CDCCallManagement(bmCapabilities=0x03, bDataInterface=1)
        encoded = cm.encode()
        assert encoded[1] == CDC_DESC_TYPE_CS_INTERFACE
        assert encoded[2] == CDCSubtype.CALL_MANAGEMENT
        assert encoded[3] == 0x03
        assert encoded[4] == 1


class TestCDCACM:
    def test_bLength(self):
        acm = CDCACM(bmCapabilities=0x06)
        assert acm.fields()[0].value == 4


class TestCDCUnion:
    def test_variable_length(self):
        uni = CDCUnion(bMasterInterface=0, baInterfaceNr=[1, 2])
        assert uni.fields()[0].value == 6
