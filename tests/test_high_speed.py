import pytest
from usbdesc.core.base import hs_iso_packet_size, Field


class TestHSIsoPacketSize:
    def test_basic_1_transaction(self):
        w = hs_iso_packet_size(1024, 1)
        assert w == 1024

    def test_2_transactions(self):
        w = hs_iso_packet_size(512, 2)
        assert w == (1 << 11) | 512

    def test_3_transactions(self):
        w = hs_iso_packet_size(1024, 3)
        assert w == (2 << 11) | 1024

    def test_full_bandwidth(self):
        w = hs_iso_packet_size(1024, 3)
        assert (w & 0x7FF) == 1024
        assert ((w >> 11) & 3) == 2

    def test_auto_multi_transaction(self):
        w = hs_iso_packet_size(2000, 1)
        assert ((w >> 11) & 3) == 1  # auto-upgraded to 2 transactions
        assert w & 0x7FF == 1000     # packet split across 2 transactions

    def test_default_is_single_transaction(self):
        w = hs_iso_packet_size(256)
        assert w == 256
        assert (w >> 11) & 3 == 0
