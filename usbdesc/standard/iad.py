from usbdesc.core.types import DESC_TYPE_IAD
from usbdesc.core.base import DescriptorNode, u8


class IADDescriptor(DescriptorNode):
    """Interface Association Descriptor (bDescriptorType=0x0B).

    Groups consecutive interfaces into a single function.
    Required by Windows for composite USB audio devices.
    """
    def __init__(self, bFirstInterface, bInterfaceCount, bFunctionClass,
                 bFunctionSubClass, bFunctionProtocol, iFunction=0, name=''):
        super().__init__(name)
        self.bFirstInterface = bFirstInterface
        self.bInterfaceCount = bInterfaceCount
        self.bFunctionClass = bFunctionClass
        self.bFunctionSubClass = bFunctionSubClass
        self.bFunctionProtocol = bFunctionProtocol
        self.iFunction = iFunction

    def _subfields(self):
        return [
            *u8('bDescriptorType', DESC_TYPE_IAD),
            *u8('bFirstInterface', self.bFirstInterface),
            *u8('bInterfaceCount', self.bInterfaceCount),
            *u8('bFunctionClass', self.bFunctionClass),
            *u8('bFunctionSubClass', self.bFunctionSubClass),
            *u8('bFunctionProtocol', self.bFunctionProtocol),
            *u8('iFunction', self.iFunction),
        ]
