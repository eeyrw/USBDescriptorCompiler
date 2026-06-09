"""Custom HID report descriptor using the programmatic builder.

Demonstrates HIDReport to construct a report descriptor with
multiple collections: keyboard + consumer media keys + system controls.
"""
from usbdesc.composite import CompositeDevice, hid_generic
from usbdesc.device_class.hid_report import HIDReport, USAGE_PAGE, USAGES, COLL, IO
from usbdesc.core.types import HID_SUBCLASS_NONE, HID_PROTOCOL_NONE
from usbdesc.export.c_array import CArrayExporter
from usbdesc.topology import TopologyGraph


def create_custom_hid_report():
    """Build a compound HID report: keyboard + media keys + system controls."""
    report = HIDReport()

    # --- Keyboard (report ID 1) ---
    report.usage_page(USAGE_PAGE.GENERIC_DESKTOP)\
          .usage(USAGES.GENERIC_DESKTOP.KEYBOARD)\
          .collection(COLL.APPLICATION)\
          .report_id(1)\
          .usage_page(USAGE_PAGE.KEYBOARD)\
          .usage_min(0xE0).usage_max(0xE7)\
          .logical_min(0).logical_max(1)\
          .report_size(1).report_count(8)\
          .input(IO.DATA | IO.VARIABLE | IO.ABSOLUTE)\
          .report_count(1).report_size(8)\
          .input(IO.CONSTANT | IO.VARIABLE | IO.ABSOLUTE)\
          .report_count(2).report_size(8)\
          .logical_min(0).logical_max(0x00FF)\
          .usage_min(0).usage_max(0x91)\
          .input(IO.DATA | IO.ARRAY | IO.ABSOLUTE)\
          .end_collection()

    # --- Consumer media keys (report ID 2) ---
    report.collection(COLL.APPLICATION)\
          .report_id(2)\
          .usage_page(USAGE_PAGE.CONSUMER)\
          .usage(USAGES.CONSUMER.CONSUMER_CONTROL)\
          .logical_min(0).logical_max(0x03FF)\
          .report_size(16).report_count(1)\
          .input(IO.DATA | IO.ARRAY | IO.ABSOLUTE)\
          .end_collection()

    # --- System controls (report ID 3) ---
    report.collection(COLL.APPLICATION)\
          .report_id(3)\
          .usage_page(USAGE_PAGE.GENERIC_DESKTOP)\
          .usage(USAGES.GENERIC_DESKTOP.SYSTEM_CONTROL)\
          .logical_min(0).logical_max(1)\
          .report_size(1).report_count(1)\
          .usage(USAGES.GENERIC_DESKTOP.SYSTEM_SLEEP)\
          .usage(USAGES.GENERIC_DESKTOP.SYSTEM_WAKE_UP)\
          .usage(USAGES.GENERIC_DESKTOP.SYSTEM_POWER_DOWN)\
          .input(IO.DATA | IO.VARIABLE | IO.ABSOLUTE | IO.NO_PREFERRED)\
          .end_collection()

    return report


if __name__ == '__main__':
    report = create_custom_hid_report()
    raw = report.encode()
    print(f'Custom HID report: {len(raw)} bytes')
    print(f'Hex: {raw.hex()}')

    # Wrap in a composite device
    def build_func(rc):
        return hid_generic(
            rc, report_descriptor=raw, ep_in_size=8, ep_interval=1,
            subclass=HID_SUBCLASS_NONE, protocol=HID_PROTOCOL_NONE,
        )

    dev = CompositeDevice(
        idVendor=0x1234, idProduct=0x5678,
        manufacturer='HID Demo', product='Custom HID',
    )
    dev.add(build_func)
    nodes = dev.build()

    print()
    print(TopologyGraph(nodes).to_ascii())
    print()
    print(CArrayExporter().export_groups(nodes, prefix='custom_hid'))
