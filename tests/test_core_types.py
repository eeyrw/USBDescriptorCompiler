import pytest
from usbdesc.device_class.audio.uac2 import ACHeader
from usbdesc.core.types import FUNCTION_DESKTOP_SPEAKER


class TestCustomNames:
    def test_custom_name_preserved(self):
        hdr = ACHeader(bCategory=FUNCTION_DESKTOP_SPEAKER, name='My AC Header')
        assert hdr.name == 'My AC Header'

    def test_default_name_is_class_name(self):
        hdr = ACHeader(bCategory=FUNCTION_DESKTOP_SPEAKER)
        assert hdr.name == 'ACHeader'
