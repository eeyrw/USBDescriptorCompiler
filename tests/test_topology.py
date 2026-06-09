import pytest
from usbdesc.topology import TopologyGraph
from usbdesc.composite import CompositeDevice
from usbdesc.composite import uac2_speaker, uac2_line_in_out, midi_function


class TestTopology:
    def test_speaker_topology(self):
        dev = CompositeDevice(idVendor=0x1234, idProduct=0x5678)
        dev.add(uac2_speaker)
        graph = TopologyGraph(dev.build())
        assert any('CLK#' in k for k in graph.nodes)
        assert any('IT#' in k for k in graph.nodes)
        assert any('FU#' in k for k in graph.nodes)
        assert any('OT#' in k for k in graph.nodes)

    def test_line_in_out_topology(self):
        dev = CompositeDevice(idVendor=0x1234, idProduct=0x5678)
        dev.add(uac2_line_in_out)
        graph = TopologyGraph(dev.build())
        out_count = sum(1 for k in graph.nodes if k.startswith('OT#'))
        it_count = sum(1 for k in graph.nodes if k.startswith('IT#'))
        assert out_count >= 2
        assert it_count >= 2

    def test_speaker_chain(self):
        dev = CompositeDevice(idVendor=0x1234, idProduct=0x5678)
        dev.add(uac2_speaker)
        graph = TopologyGraph(dev.build())
        consumers = {}
        for key, node in graph.nodes.items():
            for src in node.sources:
                consumers.setdefault(src, []).append(key)
        clk = [k for k in graph.nodes if k.startswith('CLK#')][0]
        assert clk in consumers

    def test_ascii_returns_string(self):
        dev = CompositeDevice(idVendor=0x1234, idProduct=0x5678)
        dev.add(uac2_speaker)
        graph = TopologyGraph(dev.build())
        text = graph.to_ascii()
        assert isinstance(text, str)
        assert len(text) > 0
        assert 'Device 0x1234:0x5678' in text
        assert 'Config' in text
        assert 'Fixed' in text

    def test_mermaid_returns_valid(self):
        dev = CompositeDevice(idVendor=0x1234, idProduct=0x5678)
        dev.add(uac2_speaker)
        graph = TopologyGraph(dev.build())
        mmd = graph.to_mermaid()
        assert mmd.startswith('graph TD')
        assert 'CLK_' in mmd

    def test_complex_topology(self):
        dev = CompositeDevice(idVendor=0x1234, idProduct=0x5678)
        dev.add(uac2_line_in_out)
        dev.add(midi_function)
        graph = TopologyGraph(dev.build())
        assert any('CLK#' in k for k in graph.nodes)
        assert any('MJ_IN#' in k for k in graph.nodes)
        assert len(graph.nodes) >= 10
