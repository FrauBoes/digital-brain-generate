import uuid
from smartcard.System import readers
from smartcard.util import toHexString

'''
Write a random UID to an NFC tag

Equipment needed: NFC tag, USB NFC reader

The script writes a 16-byte V4 UUID to the tag, starting at block 4

MacOS
1. Plug in reader and install drivers from manufacturer's website: https://www.acs.com.hk/en/products/3/acr122u-usb-nfc-reader/
3. Plug in and put tag on reader, a green light should light up.
5. Install all requirements by running `pip install -r requirements.txt` inside this project
6. Run this script by running `python write_to_nfc_tag.py`

Windows
1. Plug in reader. It should be recognized automatically and no drivers need to be installed.
2. Check reader is listed:
    2.1. In the Device Manager under Smart card readers
3. Put tag on reader, a green light should light up.
4. Install all requirements by running `pip install -r requirements.txt` inside this project
5. Run this script by running `python write_to_nfc_tag.py`
'''

# Generate a random UUID (16 bytes) and convert to a list of integers
random_uuid = list(uuid.uuid4().bytes)
uuid_hex = toHexString(random_uuid)
print(f"Generated UUID: {uuid_hex}")

# Select the first available NFC reader
r = readers()
if len(r) == 0:
    print("No NFC reader found!")
    exit()

print(f"Using NFC reader: {r[0]}")

# Connect to the NFC reader
connection = r[0].createConnection()
connection.connect()

# Write the first 4 bytes of the UUID to Block 4
WRITE_CMD = [0xFF, 0xD6, 0x00, 0x04, 0x04] + random_uuid[:4]
response, sw1, sw2 = connection.transmit(WRITE_CMD)
if sw1 == 0x90 and sw2 == 0x00:
    print(f"Successfully wrote to Block 4: {toHexString(random_uuid[:4])}")
else:
    print(f"Failed to write to Block 4, status words: {sw1:02X} {sw2:02X}")

# Write the next 4 bytes of the UUID to Block 5
WRITE_CMD = [0xFF, 0xD6, 0x00, 0x05, 0x04] + random_uuid[4:8]
response, sw1, sw2 = connection.transmit(WRITE_CMD)
if sw1 == 0x90 and sw2 == 0x00:
    print(f"Successfully wrote to Block 5: {toHexString(random_uuid[4:8])}")
else:
    print(f"Failed to write to Block 5, status words: {sw1:02X} {sw2:02X}")

# Write the next 4 bytes of the UUID to Block 6
WRITE_CMD = [0xFF, 0xD6, 0x00, 0x06, 0x04] + random_uuid[8:12]
response, sw1, sw2 = connection.transmit(WRITE_CMD)
if sw1 == 0x90 and sw2 == 0x00:
    print(f"Successfully wrote to Block 6: {toHexString(random_uuid[8:12])}")
else:
    print(f"Failed to write to Block 6, status words: {sw1:02X} {sw2:02X}")

# Write the final 4 bytes of the UUID to Block 7
WRITE_CMD = [0xFF, 0xD6, 0x00, 0x07, 0x04] + random_uuid[12:16]
response, sw1, sw2 = connection.transmit(WRITE_CMD)
if sw1 == 0x90 and sw2 == 0x00:
    print(f"Successfully wrote to Block 7: {toHexString(random_uuid[12:16])}")
else:
    print(f"Failed to write to Block 7, status words: {sw1:02X} {sw2:02X}")

print("Writing process completed!")
