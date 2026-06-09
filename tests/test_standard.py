import pytest
from usbdesc.standard.device import DeviceDescriptor
from usbdesc.standard.qualifier import DeviceQualifierDescriptor
from usbdesc.standard.config import ConfigurationDescriptor, OtherSpeedConfigurationDescriptor
from usbdesc.standard.interface import InterfaceDescriptor
from usbdesc.standard.endpoint import EndpointDescriptor
from usbdesc.core.types import (
    DESC_TYPE_DEVICE, DESC_TYPE_CONFIGURATION,
    DESC_TYPE_INTERFACE, DESC_TYPE_ENDPOINT,
    DESC_TYPE_DEVICE_QUAL, DESC_TYPE_OTHER_SPEED,
    CONFIG_ATTR_BUS_POWERED,
)


class TestDeviceDescriptor:
    def test_bLength(self):
        dd = DeviceDescriptor()
        assert dd.fields()[0].value == 18

    def test_bcdUSB(self):
        dd = DeviceDescriptor()
        encoded = dd.encode()
        assert encoded[2] == 0x00
        assert encoded[3] == 0x02


class TestConfigurationDescriptor:
    def test_bLength(self):
        cd = ConfigurationDescriptor()
        assert cd.fields()[0].value == 9

    def test_default_bmAttributes(self):
        cd = ConfigurationDescriptor()
        encoded = cd.encode()
        assert encoded[7] == CONFIG_ATTR_BUS_POWERED

    def test_bMaxPower_50(self):
        cd = ConfigurationDescriptor(bMaxPower=50)
        encoded = cd.encode()
        assert encoded[8] == 50


class TestInterfaceDescriptor:
    def test_bLength(self):
        iface = InterfaceDescriptor()
        assert iface.fields()[0].value == 9

    def test_bInterfaceNumber(self):
        iface = InterfaceDescriptor(bInterfaceNumber=2)
        encoded = iface.encode()
        assert encoded[2] == 2

    def test_bAlternateSetting(self):
        iface = InterfaceDescriptor(bAlternateSetting=1)
        encoded = iface.encode()
        assert encoded[3] == 1


class TestEndpointDescriptor:
    def test_bLength(self):
        ep = EndpointDescriptor()
        assert ep.fields()[0].value == 7

    def test_bEndpointAddress(self):
        ep = EndpointDescriptor(bEndpointAddress=0x81)
        encoded = ep.encode()
        assert encoded[2] == 0x81

    def test_wMaxPacketSize(self):
        ep = EndpointDescriptor(wMaxPacketSize=512)
        encoded = ep.encode()
        assert encoded[4] == 0x00
        assert encoded[5] == 0x02


class TestDeviceQualifier:
    def test_bLength(self):
        qual = DeviceQualifierDescriptor()
        assert qual.fields()[0].value == 10

    def test_descriptor_type(self):
        qual = DeviceQualifierDescriptor()
        encoded = qual.encode()
        assert encoded[1] == DESC_TYPE_DEVICE_QUAL

    def test_bMaxPacketSize0(self):
        qual = DeviceQualifierDescriptor(bMaxPacketSize0=64)
        encoded = qual.encode()
        assert encoded[7] == 64

    def test_bReserved_is_zero(self):
        qual = DeviceQualifierDescriptor()
        encoded = qual.encode()
        assert encoded[9] == 0


class TestOtherSpeedConfig:
    def test_bLength(self):
        osc = OtherSpeedConfigurationDescriptor()
        assert osc.fields()[0].value == 9

    def test_descriptor_type(self):
        osc = OtherSpeedConfigurationDescriptor()
        encoded = osc.encode()
        assert encoded[1] == DESC_TYPE_OTHER_SPEED

    def test_config_value(self):
        osc = OtherSpeedConfigurationDescriptor(bConfigurationValue=1)
        encoded = osc.encode()
        assert encoded[5] == 1
