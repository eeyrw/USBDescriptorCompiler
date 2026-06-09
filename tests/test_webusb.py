import pytest
from usbdesc.device_class.webusb import BOSDescriptor, WebUSBDescriptor
from usbdesc.core.types import DESC_TYPE_BOS


class TestBOS:
    def test_bLength(self):
        bos = BOSDescriptor()
        assert bos.fields()[0].value == 5

    def test_descriptor_type(self):
        bos = BOSDescriptor()
        encoded = bos.encode()
        assert encoded[1] == DESC_TYPE_BOS


class TestWebUSB:
    def test_bLength(self):
        wu = WebUSBDescriptor()
        assert wu.fields()[0].value == 24

    def test_uuid_present(self):
        wu = WebUSBDescriptor()
        encoded = wu.encode()
        assert len(encoded) == 24

    def test_bcdVersion(self):
        wu = WebUSBDescriptor(bcdVersion=0x0100)
        encoded = wu.encode()
        assert encoded[20] == 0x00
        assert encoded[21] == 0x01

    def test_vendor_code(self):
        wu = WebUSBDescriptor()
        encoded = wu.encode()
        assert encoded[22] == 0x01

    def test_landing_page(self):
        wu = WebUSBDescriptor(iLandingPage=3)
        encoded = wu.encode()
        assert encoded[23] == 3
