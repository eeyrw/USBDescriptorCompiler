import pytest
from usbdesc.device_class.hid import HIDDescriptor
from usbdesc.core.types import HID_DESC_TYPE_HID, HID_DESC_TYPE_REPORT, HID_BCD


class TestHIDDescriptor:
    def test_bLength(self):
        hid = HIDDescriptor()
        assert hid.fields()[0].value == 9

    def test_descriptor_type_is_HID(self):
        hid = HIDDescriptor()
        encoded = hid.encode()
        assert encoded[1] == HID_DESC_TYPE_HID

    def test_bcdHID(self):
        hid = HIDDescriptor()
        encoded = hid.encode()
        assert encoded[2] == 0x11
        assert encoded[3] == 0x01


class TestHIDExamples:
    def test_joystick_report_present(self):
        from usbdesc.composite import _HID_JOYSTICK_REPORT
        assert len(_HID_JOYSTICK_REPORT) > 0
        assert len(_HID_JOYSTICK_REPORT) > 50  # should be substantial

    def test_consumer_report_present(self):
        from usbdesc.composite import _HID_CONSUMER_REPORT
        assert len(_HID_CONSUMER_REPORT) > 0

    def test_digitizer_report_present(self):
        from usbdesc.composite import _HID_DIGITIZER_REPORT
        assert len(_HID_DIGITIZER_REPORT) > 0

    def test_system_control_report_present(self):
        from usbdesc.composite import _HID_SYSTEM_CONTROL_REPORT
        assert len(_HID_SYSTEM_CONTROL_REPORT) > 0

    def test_joystick_composite_builds(self):
        from usbdesc.composite import CompositeDevice, hid_joystick
        dev = CompositeDevice()
        dev.add(hid_joystick)
        nodes = dev.build()
        assert any(hasattr(n, 'report_bytes') for n in nodes)

    def test_gamepad_is_alias(self):
        from usbdesc.composite import CompositeDevice, hid_gamepad
        dev = CompositeDevice()
        dev.add(hid_gamepad)
        nodes = dev.build()
        assert any('Gamepad' in getattr(n, 'name', '') for n in nodes)

    def test_consumer_control_builds(self):
        from usbdesc.composite import CompositeDevice, hid_consumer_control
        dev = CompositeDevice()
        dev.add(hid_consumer_control)
        nodes = dev.build()
        assert len(nodes) >= 4

    def test_digitizer_builds(self):
        from usbdesc.composite import CompositeDevice, hid_digitizer
        dev = CompositeDevice()
        dev.add(hid_digitizer)
        nodes = dev.build()
        assert len(nodes) >= 4

    def test_system_control_builds(self):
        from usbdesc.composite import CompositeDevice, hid_system_control
        dev = CompositeDevice()
        dev.add(hid_system_control)
        nodes = dev.build()
        assert len(nodes) >= 4

    def test_joystick_report_has_hat_switch(self):
        from usbdesc.composite import _HID_JOYSTICK_REPORT
        # Hat switch usage = 0x39. Check the report bytes contain it.
        report = _HID_JOYSTICK_REPORT
        assert 0x39 in report

    def test_joystick_report_has_axes(self):
        from usbdesc.composite import _HID_JOYSTICK_REPORT
        # X=0x30, Y=0x31, Z=0x32, Rz=0x35
        report = _HID_JOYSTICK_REPORT
        assert 0x30 in report
        assert 0x31 in report
        assert 0x32 in report
        assert 0x35 in report
