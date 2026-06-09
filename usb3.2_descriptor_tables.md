# USB 3.2 Revision 1.1 — Descriptor Layout Reference
## Extracted from Chapter 9 (USB Device Framework) and BOS/Capability Sections

---

## Standard Descriptor Types (Table 9-6)

| Descriptor Type | Value |
|---|---|
| DEVICE | 1 |
| CONFIGURATION | 2 |
| STRING | 3 |
| INTERFACE | 4 |
| ENDPOINT | 5 |
| Reserved | 6 |
| Reserved | 7 |
| INTERFACE_POWER | 8 |
| OTG | 9 |
| DEBUG | 10 |
| INTERFACE_ASSOCIATION | 11 |
| **BOS** | **15** (0x0F) |
| **DEVICE CAPABILITY** | **16** (0x10) |
| **SUPERSPEED_USB_ENDPOINT_COMPANION** | **48** (0x30) |
| **SUPERSPEED_PLUS_ISOCHRONOUS_ENDPOINT_COMPANION** | **49** (0x31) |

Bit 7 of descriptor type is reserved for base USB specs defining new descriptor types.

---

## Device Capability Type Codes (Table 9-14)

| Capability | Code |
|---|---|
| Wireless_USB | 0x01 |
| **USB 2.0 EXTENSION** | **0x02** |
| **SUPERSPEED_USB** | **0x03** |
| **CONTAINER_ID** | **0x04** |
| PLATFORM | 0x05 |
| POWER_DELIVERY_CAPABILITY | 0x06 |
| BATTERY_INFO_CAPABILITY | 0x07 |
| PD_CONSUMER_PORT_CAPABILITY | 0x08 |
| PD_PROVIDER_PORT_CAPABILITY | 0x09 |
| **SUPERSPEED_PLUS** | **0x0A** |
| PRECISION_TIME_MEASUREMENT | 0x0B |
| Wireless_USB_Ext | 0x0C |
| BILLBOARD | 0x0D |
| AUTHENTICATION | 0x0E |
| BILLBOARD_EX | 0x0F |
| CONFIGURATION SUMMARY | 0x10 |
| FWStatus Capability | 0x11 |
| Reserved | 0x00, 0x12–0xFF |

---

## 1. Device Descriptor (Table 9-11)

**Total size: 18 bytes** (for USB 3.x devices, bMaxPacketSize0 = 09H = 512-byte packets; encoded as 2^value)

| Offset | Field | Size | Description |
|---|---|---|---|
| 0 | bLength | 1 | Size of this descriptor (18) |
| 1 | bDescriptorType | 1 | DEVICE (1) |
| 2 | bcdUSB | 2 | USB Spec Release (BCD). **USB 3.1 = 0x0310**, USB 3.0 = 0x0300, USB 3.2 = 0x0320. When operating in USB 2.0 mode: **0x0210** (2.1). Format: 0xJJMN for version JJ.M.N |
| 4 | bDeviceClass | 1 | Class code |
| 5 | bDeviceSubClass | 1 | Subclass code |
| 6 | bDeviceProtocol | 1 | Protocol code |
| 7 | bMaxPacketSize0 | 1 | **09H (fixed for Gen X speed)** → 2^9 = 512 bytes |
| 8 | idVendor | 2 | Vendor ID (USB-IF assigned) |
| 10 | idProduct | 2 | Product ID |
| 12 | bcdDevice | 2 | Device release number (BCD) |
| 14 | iManufacturer | 1 | String index — manufacturer |
| 15 | iProduct | 1 | String index — product |
| 16 | iSerialNumber | 1 | String index — serial number |
| 17 | bNumConfigurations | 1 | Number of configurations at current operating speed |

---

## 2. Configuration Descriptor (Table 9-23)

**Total size: 9 bytes**

| Offset | Field | Size | Description |
|---|---|---|---|
| 0 | bLength | 1 | Size (9) |
| 1 | bDescriptorType | 1 | CONFIGURATION (2) |
| 2 | wTotalLength | 2 | Total length of all descriptors for this config |
| 4 | bNumInterfaces | 1 | Number of interfaces |
| 5 | bConfigurationValue | 1 | Value for SetConfiguration() |
| 6 | iConfiguration | 1 | String index |
| 7 | bmAttributes | 1 | Bitmap: D7=1 (reserved), D6=Self-powered, D5=Remote Wakeup, D4..0=0 |
| 8 | bMaxPower | 1 | Max power consumption. **Units**: 2 mA (high-speed), **8 mA (Gen X speed)** |

---

## 3. Interface Descriptor (Table 9-25)

**Total size: 9 bytes**

| Offset | Field | Size | Description |
|---|---|---|---|
| 0 | bLength | 1 | Size (9) |
| 1 | bDescriptorType | 1 | INTERFACE (4) |
| 2 | bInterfaceNumber | 1 | Zero-based interface index |
| 3 | bAlternateSetting | 1 | Alternate setting value |
| 4 | bNumEndpoints | 1 | Endpoint count (excl. Default Control Pipe) |
| 5 | bInterfaceClass | 1 | Class code |
| 6 | bInterfaceSubClass | 1 | Subclass code |
| 7 | bInterfaceProtocol | 1 | Protocol code |
| 8 | iInterface | 1 | String index |

---

## 4. Interface Association Descriptor (Table 9-24)

**Total size: 8 bytes**

| Offset | Field | Size | Description |
|---|---|---|---|
| 0 | bLength | 1 | Size (8) |
| 1 | bDescriptorType | 1 | INTERFACE_ASSOCIATION (11) |
| 2 | bFirstInterface | 1 | First interface number |
| 3 | bInterfaceCount | 1 | Number of contiguous interfaces |
| 4 | bFunctionClass | 1 | Function class code (never zero) |
| 5 | bFunctionSubClass | 1 | Function subclass code |
| 6 | bFunctionProtocol | 1 | Function protocol code |
| 7 | iFunction | 1 | String index for function |

---

## 5. Standard Endpoint Descriptor (Table 9-26)

**Total size: 7 bytes**

| Offset | Field | Size | Description |
|---|---|---|---|
| 0 | bLength | 1 | Size (7) |
| 1 | bDescriptorType | 1 | ENDPOINT (5) |
| 2 | bEndpointAddress | 1 | Bits 3..0=Endpoint Number, Bits 6..4=0, Bit 7=Direction (0=OUT, 1=IN) |
| 3 | bmAttributes | 1 | Bits 1..0=Transfer Type (00=Ctrl, 01=Isoch, 10=Bulk, 11=Intr); see below |
| 4 | wMaxPacketSize | 2 | Max packet size. **For SuperSpeed**: Control=512, Bulk=1024. Intr/Isoch=1024 if bMaxBurst>0, else 0–1024 (Isoch) or 1–1024 (Intr) |
| 6 | bInterval | 1 | Service interval in **125 µs units**. For SS isoch/intr: range 1–16. Value is exponent: period = 2^(bInterval-1). **Reserved/unused for SS bulk/control** |

### bmAttributes bit assignments

**Bits 1..0 — Transfer Type:**
- 00 = Control
- 01 = Isochronous
- 10 = Bulk
- 11 = Interrupt

**If Isochronous endpoint:**
- Bits 3..2: Synchronization Type (00=No Sync, 01=Async, 10=Adaptive, 11=Synchronous)
- Bits 5..4: Usage Type (00=Data, 01=Feedback, 10=Implicit Feedback, 11=Reserved)

**If Interrupt endpoint:**
- Bits 3..2: Reserved
- Bits 5..4: Usage Type (00=Periodic, 01=Notification, 10/11=Reserved)

**If Bulk or Control:**
- Bits 5..2: Reserved, set to zero

---

## 6. BOS Descriptor (Table 9-12)

**bDescriptorType = 15 (0x0F)**  
**Total size: 5 bytes** (header only, + sub-descriptors via wTotalLength)

| Offset | Field | Size | Value | Description |
|---|---|---|---|---|
| 0 | bLength | 1 | Number | Size of descriptor (5 for the BOS header itself) |
| 1 | bDescriptorType | 1 | 0x0F | BOS Descriptor type |
| 2 | wTotalLength | 2 | Number | Length of BOS descriptor + all sub descriptors |
| 4 | bNumDeviceCaps | 1 | Number | Number of separate Device Capability descriptors in the BOS |

---

## 7. Device Capability Descriptor — Generic Header (Table 9-13)

**bDescriptorType = 16 (0x10)**

| Offset | Field | Size | Description |
|---|---|---|---|
| 0 | bLength | 1 | Size of this descriptor |
| 1 | bDescriptorType | 1 | DEVICE CAPABILITY (0x10) |
| 2 | bDevCapabilityType | 1 | Capability type (see Table 9-14) |
| 3 | Capability-Dependent | Var | Capability-specific data |

---

## 8. USB 2.0 Extension Descriptor (Table 9-15)

**bDevCapabilityType = 0x02**  
**Total size: 7 bytes**

Required for Enhanced SuperSpeed devices; device shall support LPM in USB 2.0 HS mode.

| Offset | Field | Size | Value | Description |
|---|---|---|---|---|
| 0 | bLength | 1 | 7 | Size |
| 1 | bDescriptorType | 1 | 0x10 | DEVICE CAPABILITY |
| 2 | bDevCapabilityType | 1 | 0x02 | USB 2.0 EXTENSION |
| 3 | bmAttributes | 4 | Bitmap | Device-level feature bitmap |

### bmAttributes bit assignments

| Bit(s) | Description |
|---|---|
| 0 | Reserved. Shall be set to zero. |
| 1 | **LPM**. 1 = device supports Link Power Management protocol. Enhanced SuperSpeed devices **shall** set this bit. |
| 31:2 | Reserved. Shall be set to zero. |

---

## 9. SuperSpeed USB Device Capability Descriptor (Table 9-16)

**bDevCapabilityType = 0x03**  
**Total size: 10 bytes**

Required for all Enhanced SuperSpeed devices.

| Offset | Field | Size | Value | Description |
|---|---|---|---|---|
| 0 | bLength | 1 | 10 | Size |
| 1 | bDescriptorType | 1 | 0x10 | DEVICE CAPABILITY |
| 2 | bDevCapabilityType | 1 | 0x03 | SUPERSPEED_USB |
| 3 | bmAttributes | 1 | Bitmap | Device feature bitmap |
| 4 | wSpeedsSupported | 2 | Bitmap | Speeds supported by this device |
| 6 | bFunctionalitySupport | 1 | Number | Lowest speed at which all functionality is available |
| 7 | bU1DevExitLat | 1 | Number | U1 Device Exit Latency (worst-case U1→U0) |
| 8 | wU2DevExitLat | 2 | Number | U2 Device Exit Latency (worst-case U2→U0) |

### bmAttributes (byte 3)

| Bit(s) | Description |
|---|---|
| 0 | Reserved. Set to zero. |
| 1 | **LTM Capable**. 1 = device capable of generating Latency Tolerance Messages. |
| 7:2 | Reserved. Set to zero. |

### wSpeedsSupported (bytes 4–5, LE)

| Bit | Description |
|---|---|
| 0 | Low-Speed USB supported |
| 1 | Full-Speed USB supported |
| 2 | High-Speed USB supported |
| 3 | **Gen 1 speed** (SuperSpeed) supported |
| 15:4 | Reserved. Set to zero. |

### bFunctionalitySupport (byte 6)

Lowest speed at which **all functionality** is available. Uses the same bit assignments as wSpeedsSupported:
| Value | Speed |
|---|---|
| 0 | Low-Speed |
| 1 | Full-Speed |
| 2 | High-Speed |
| 3 | Gen 1 (SuperSpeed) |

### bU1DevExitLat (byte 7)

| Value | Meaning |
|---|---|
| 0x00 | Zero |
| 0x01 | < 1 µs |
| 0x02 | < 2 µs |
| … | … |
| 0x0A | < 10 µs |
| 0x0B–0xFF | Reserved |

### wU2DevExitLat (bytes 8–9, LE)

| Value | Meaning |
|---|---|
| 0x0000 | Zero |
| 0x0001 | < 1 µs |
| 0x0002 | < 2 µs |
| … | … |
| 0x07FF | < 2047 µs |
| 0x0800–0xFFFF | Reserved |

---

## 10. SuperSpeedPlus USB Device Capability Descriptor (Table 9-19)

**bDevCapabilityType = 0x0A**  
**Min size: 16 bytes** (bLength = 12 + 4 × (SSAC + 1) sublink attributes)

Required for all SuperSpeed Plus devices.

| Offset | Field | Size | Value | Description |
|---|---|---|---|---|
| 0 | bLength | 1 | 12+4×(SSAC+1) | Size |
| 1 | bDescriptorType | 1 | 0x10 | DEVICE CAPABILITY |
| 2 | bDevCapabilityType | 1 | 0x0A | SUPERSPEED_PLUS |
| 3 | bReserved | 1 | 0 | Reserved |
| 4 | bmAttributes | 4 | Bitmap | SuperSpeedPlus features (LE) |
| 8 | wFunctionalitySupport | 2 | Number | Minimum bandwidth for full functionality (LE) |
| 10 | wReserved | 2 | 0 | Reserved (LE) |
| 12 | bmSublinkSpeedAttr[0] | 4 | Bitmap | First sublink speed attribute |
| 16 | bmSublinkSpeedAttr[1..SSAC] | 4 each | Bitmap | Additional sublink speed attributes |

### bmAttributes (bytes 4–7, LE, 32 bits)

| Bit(s) | Field | Description |
|---|---|---|
| 4:0 | **SSAC** (Sublink Speed Attribute Count) | Number of sublink speed attribute bitmaps **minus 1**. Min = 0 (one attribute). Number of Sublink Speed Attributes = SSAC + 1. |
| 8:5 | **SSIC** (Sublink Speed ID Count) | Number of unique Sublink Speed IDs **minus 1**. Number of Sublink Speed IDs = SSIC + 1. |
| 31:9 | Reserved | |

### wFunctionalitySupport (bytes 8–9, LE, 16 bits)

| Bit(s) | Field | Description |
|---|---|---|
| 3:0 | **SSID** (Sublink Speed Attribute ID) | Minimum lane speed for full functionality |
| 7:4 | Reserved | |
| 11:8 | **Min Rx Lane Count** | Minimum receive lane count for full functionality |
| 15:12 | **Min Tx Lane Count** | Minimum transmit lane count for full functionality |

### bmSublinkSpeedAttr[N] (4 bytes each, LE)

| Bit(s) | Field | Description |
|---|---|---|
| 3:0 | **SSID** (Sublink Speed Attribute ID) | Uniquely identifies the speed of the sublink. Max 16 unique SSIDs. |
| 5:4 | **LSE** (Lane Speed Exponent) | Base-10 exponent × 3: 0=bits/s, 1=Kb/s, 2=Mb/s, 3=Gb/s |
| 7:6 | **ST** (Sublink Type) | Bit 6: 0=Symmetric, 1=Asymmetric. Bit 7: 0=Rx, 1=Tx. Attributes shall be paired (Rx→Tx with same SSID). |
| 13:8 | Reserved | |
| 15:14 | **LP** (Link Protocol) | 0=SuperSpeed, 1=SuperSpeedPlus, 2–3=Reserved |
| 31:16 | **LSM** (Lane Speed Mantissa) | Mantissa combined with LSE for max bit rate: bit rate = LSM × 10^(LSE×3) |

---

## 11. Container ID Descriptor (Table 9-17)

**bDevCapabilityType = 0x04**  
**Total size: 20 bytes**

Required for all USB hubs, optional for other devices.

| Offset | Field | Size | Value | Description |
|---|---|---|---|---|
| 0 | bLength | 1 | 20 | Size |
| 1 | bDescriptorType | 1 | 0x10 | DEVICE CAPABILITY |
| 2 | bDevCapabilityType | 1 | 0x04 | CONTAINER_ID |
| 3 | bReserved | 1 | 0 | Reserved |
| 4 | ContainerID | 16 | UUID | 128-bit UUID (per IETF RFC 4122), unique per device instance across all operating modes |

---

## 12. Platform Descriptor (Table 9-18)

**bDevCapabilityType = 0x05**

| Offset | Field | Size | Value | Description |
|---|---|---|---|---|
| 0 | bLength | 1 | 20+ | Size |
| 1 | bDescriptorType | 1 | 0x10 | DEVICE CAPABILITY |
| 2 | bDevCapabilityType | 1 | 0x05 | PLATFORM |
| 3 | bReserved | 1 | 0 | Reserved |
| 4 | PlatformCapabilityUUID | 16 | UUID | 128-bit UUID identifying the platform capability |
| 20 | CapabilityData | Variable | Binary | Platform-specific data (may be zero bytes) |

---

## 13. PTM Capability Descriptor (Table 9-20)

**bDevCapabilityType = 0x0B**  
**Total size: 3 bytes**

| Offset | Field | Size | Value | Description |
|---|---|---|---|---|
| 0 | bLength | 1 | 3 | Size |
| 1 | bDescriptorType | 1 | 0x10 | DEVICE CAPABILITY |
| 2 | bDevCapabilityType | 1 | 0x0B | PRECISION_TIME_MEASUREMENT |

---

## 14. Configuration Summary Descriptor (Table 9-21)

**bDevCapabilityType = 0x10**

| Offset | Field | Size | Value | Description |
|---|---|---|---|---|
| 0 | bLength | 1 | 9+N | Size |
| 1 | bDescriptorType | 1 | 0x10 | DEVICE CAPABILITY |
| 2 | bDevCapabilityType | 1 | 0x10 | CONFIGURATION SUMMARY |
| 3 | bcdVersion | 2 | 0x0100 | BCD version |
| 5 | bClass | 1 | Class | Function class code |
| 6 | bSubClass | 1 | Subclass | Function subclass code |
| 7 | bProtocol | 1 | Protocol | Function protocol code |
| 8 | bConfigurationCount | 1 | N | Number of configurations containing this function |
| 9 | bConfigurationIndex[0] | 1 | Number | First config descriptor index |
| ... | ... | ... | ... |
| 8+N | bConfigurationIndex[N−1] | 1 | Number | Last config descriptor index |

---

## 15. FWStatus Capability (Table 9-22)

**bDevCapabilityType = 0x11**

| Offset | Field | Size | Value | Description |
|---|---|---|---|---|
| 0 | bLength | 1 |  | Size |
| 1 | bDescriptorType | 1 | 0x10 | DEVICE CAPABILITY |
| 2 | bDevCapabilityType | 1 | 0x11 | FWStatus Capability |
| 3 | bcdDescriptorVersion | 1 | 1 | Version (initial value = 1) |
| 5 | bmAttributes | 4 | Bitmap | Bit 0 = Get FW Image Hash support, Bit 1 = Disallow FW Update support, Bits 2–31 = Reserved |

---

## 16. SuperSpeed Endpoint Companion Descriptor (Table 9-28)

**bDescriptorType = 48 (0x30)**  
**Total size: 6 bytes**

Returned for each endpoint (except Default Control Pipe) when operating at Gen X speed. Follows its endpoint descriptor immediately.

| Offset | Field | Size | Value | Description |
|---|---|---|---|---|
| 0 | bLength | 1 | 6 | Size |
| 1 | bDescriptorType | 1 | 0x30 | SUPERSPEED_USB_ENDPOINT_COMPANION |
| 2 | bMaxBurst | 1 | 0–15 | Max packets per burst. 0 = 1 packet, 15 = 16 packets. Control: set to 0. |
| 3 | bmAttributes | 1 | Bitmap | Endpoint-type-dependent (see below) |
| 4 | wBytesPerInterval | 2 | Number | Total bytes transferred per Service Interval (LE). Periodic endpoints only. Control/Bulk: set to 0. |

### bmAttributes bit assignments

**If Bulk Endpoint:**

| Bit(s) | Description |
|---|---|
| 4:0 | **MaxStreams**. 0 = no streams. 1–16: number of streams = 2^MaxStreams. |
| 7:5 | Reserved. Set to zero. |

**If Control or Interrupt Endpoint:**

| Bit(s) | Description |
|---|---|
| 7:0 | Reserved. Set to zero. |

**If Isochronous Endpoint:**

| Bit(s) | Description |
|---|---|
| 1:0 | **Mult**. Zero-based: max packets per SI = (bMaxBurst + 1) × (Mult + 1). Max value = 2. Set to 0 if bMaxBurst=0. |
| 6:2 | Reserved. Set to zero. |
| 7 | **SSP ISO Companion**. 1 = SuperSpeedPlus Isochronous Endpoint Companion follows. If set, Mult is ignored and actual Mult = ceil(dwBytesPerInterval / bMaxBurst / wMaxPacketSize). |

### wBytesPerInterval (bytes 4–5, LE)

- **Isochronous endpoints**: Total bytes transferred per service interval (bus reservation).
  - If SSP ISO Companion bit = 0: used for bandwidth reservation. Device may use less via non-USB mechanisms.
  - If SSP ISO Companion bit = 1: shall be set to 1; actual value reported in SS+ Isochronous EP Companion.
- **Bulk/Control**: Reserved, set to zero.

---

## 17. SuperSpeedPlus Isochronous Endpoint Companion Descriptor (Table 9-29)

**bDescriptorType = 49 (0x31)**  
**Total size: 8 bytes**

Returned for isochronous endpoints requiring >48KB per Service Interval when operating above Gen 1 speed. Follows the SuperSpeed Endpoint Companion descriptor immediately.

| Offset | Field | Size | Value | Description |
|---|---|---|---|---|
| 0 | bLength | 1 | 8 | Size |
| 1 | bDescriptorType | 1 | 0x31 | SUPERSPEED_PLUS_ISOCHRONOUS_ENDPOINT_COMPANION |
| 2 | wReserved | 2 | 0 | Reserved (LE) |
| 4 | dwBytesPerInterval | 4 | Number | Total bytes transferred per Service Interval (LE). Must be < MAX_ISO_BYTES_PER_BI_GEN1 × NumLanes × LSM / LANE_SPEED_MANTISSA_GEN1 |

---

## Key Constants (Table 9-32)

| Name | Value | Units |
|---|---|---|
| LANE_SPEED_MANTISSA_GEN1 | 5 | N/A |
| UNIT_LOAD (single lane, unconfigured) | 150 | mA |
| UNIT_LOAD (multi-lane, unconfigured) | 250 | mA |
| MAX_ISO_BYTES_PER_BI_GEN1 | 48 × 1024 | bytes |

---

## USB 3.x Device Descriptor Key Differences

1. **bcdUSB**: 0x0310 (USB 3.1), 0x0300 (USB 3.0), expected 0x0320 for USB 3.2. When operating in USB 2.0 mode: 0x0210.
2. **bMaxPacketSize0**: Fixed at 0x09 (512 bytes) — encoded as 2^9.
3. **wMaxPacketSize** (standard endpoint descriptor):
   - Control: 512
   - Bulk: 1024
   - Isoch/Interrupt: 1024 if bMaxBurst > 0; otherwise 0–1024 (Isoch) or 1–1024 (Interrupt)
4. **bMaxPower** (configuration descriptor): Units = 8 mA at Gen X speed (vs 2 mA at high-speed).
5. **bInterval** (endpoint descriptor): In **125 µs** units. Range 1–16 for SS isoch/intr. Not used for SS bulk/control.
6. **Other_speed_configuration and device_qualifier**: NOT supported. Use BOS descriptor instead.
7. Every endpoint (except EP0) is followed by a **SuperSpeed Endpoint Companion** descriptor when operating at Gen X speed.
