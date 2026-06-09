import pytest
from usbdesc.device_class.audio.uac2 import InputTerminal
from usbdesc.device_class.audio.uac1 import ACHeader as UAC1Header
from usbdesc.export.c_array import CArrayExporter
from usbdesc.export.python_bytes import PythonBytesExporter
from usbdesc.export.json_ import JsonExporter
from usbdesc.core.types import TERM_USB_STREAMING


class TestCArrayExporter:
    def test_export_format(self):
        it = InputTerminal(bTerminalID=1, wTerminalType=TERM_USB_STREAMING)
        output = CArrayExporter().export([it], 'test_desc')
        assert output.startswith('uint8_t test_desc[] = {')
        assert output.strip().endswith('};')

    def test_export_contains_name(self):
        it = InputTerminal(bTerminalID=1, wTerminalType=TERM_USB_STREAMING)
        output = CArrayExporter().export([it], 'test_desc')
        assert 'USB IN Terminal' in output or 'InputTerminal' in output

    def test_export_hex_format(self):
        it = InputTerminal(bTerminalID=1, wTerminalType=TERM_USB_STREAMING)
        output = CArrayExporter().export([it], 'test_desc')
        assert '0x11' in output


class TestPythonBytesExporter:
    def test_export_returns_bytes(self):
        it = InputTerminal(bTerminalID=1, wTerminalType=TERM_USB_STREAMING)
        result = PythonBytesExporter().export([it])
        assert isinstance(result, bytes)
        assert result[0] == 17
        assert result[1] == 0x24

    def test_total_length(self):
        it = InputTerminal(bTerminalID=1, wTerminalType=TERM_USB_STREAMING)
        result = PythonBytesExporter().export([it])
        assert len(result) == 17


class TestJsonExporter:
    def test_export_json(self):
        it = InputTerminal(bTerminalID=1, wTerminalType=TERM_USB_STREAMING)
        import json
        result = JsonExporter().export([it])
        data = json.loads(result)
        assert isinstance(data, list)
        assert len(data) == 1
        assert 'fields' in data[0]
        assert 'raw' in data[0]

    def test_raw_matches_encode(self):
        it = InputTerminal(bTerminalID=1, wTerminalType=TERM_USB_STREAMING)
        import json
        result = JsonExporter().export([it])
        data = json.loads(result)
        assert data[0]['raw'] == list(it.encode())
