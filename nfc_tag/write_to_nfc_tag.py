import uuid
from smartcard.System import readers
from smartcard.util import toHexString

'''
Write a random UUIDv4 to an NFC tag

Equipment needed: NFC tag, USB NFC reader

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

print('write_to_nfc_tag start')

# Generate random UUIDv4
generated_uuid = uuid.uuid4()
uuid_bytes = list(generated_uuid.bytes)  # Convert to list of 16 bytes

# Convert to hex for display
uuid_hex = toHexString(uuid_bytes)
print(f"... generated UUIDv4: {generated_uuid}")
print(f"... gUUID as Hex Bytes: {uuid_hex}")

# Select the first available NFC reader
r = readers()
if len(r) == 0:
    print("... no NFC reader found!")
    exit()

print(f"... using NFC reader: {r[0]}")

# Connect to the NFC reader
connection = r[0].createConnection()
connection.connect()

# Write UUIDv4 to Blocks 4, 5, 6, and 7
for i, block in enumerate(range(4, 8)):
    WRITE_CMD = [0xFF, 0xD6, 0x00, block, 0x04] + uuid_bytes[i * 4: (i + 1) * 4]
    response, sw1, sw2 = connection.transmit(WRITE_CMD)
    if sw1 == 0x90 and sw2 == 0x00:
        print(f"... successfully wrote to Block {block}: {toHexString(uuid_bytes[i * 4: (i + 1) * 4])}")
    else:
        print(f"... failed to write to Block {block}, status words: {sw1:02X} {sw2:02X}")

print("... writing process completed!")
print('write_to_nfc_tag end')
