from smartcard.System import readers
import re
import time

'''
Read UUIDv4 from an NFC tag

Equipment needed: NFC tag with URL record, USB NFC reader

MacOS
1. Plug in reader and install drivers from manufacturer's website: https://www.akasa.co.uk/search.php?seed=AK-CR-15BK
2. Install middleware to enable card readers, for example https://pcsclite.apdu.fr/ or pcsc.
3. Run `pcsctest` to check reader is recognized by the computer
4. Put tag on reader, a green light should light up.
5. Install all requirements by running `pip install -r requirements.txt` inside this project
6. Run this script by running `python read_uuid_from_nfc_tag.py`

Windows
1. Plug in reader. It should be recognized automatically and no drivers need to be installed.
2. Check reader is listed:
    2.1. In the Device Manager under Smart card readers
    2.2. In the Command Prompt (run as admin) by running `sc query scardvr`
3. Put tag on reader, a green light should light up.
4. Install all requirements by running `pip install -r requirements.txt` inside this project
'''

URI_PREFIX = "https://"

UUID_V4_REGEX = re.compile(
    r"[a-f0-9]{8}-[a-f0-9]{4}-4[a-f0-9]{3}-[89ab][a-f0-9]{3}-[a-f0-9]{12}"
)

def read_ndef_message(connection, start_block=4, max_blocks=36):
    """Read NDEF message starting from block 4 up to max_blocks."""
    data = []
    for block in range(start_block, max_blocks):
        READ_CMD = [0xFF, 0xB0, 0x00, block, 0x04]
        response, sw1, sw2 = connection.transmit(READ_CMD)
        if sw1 == 0x90 and sw2 == 0x00:
            data.extend(response)
        else:
            print(f"❌ Failed to read block {block}, status: {sw1:02X} {sw2:02X}")
            break
    return data

def extract_url(data):
    try:
        # Find start of NDEF URI record
        if 0x55 in data:
            index = data.index(0x55)
            url_bytes = bytes(data[index + 2:])

            # Clean out trailing 0x00 or 0xFE
            url_bytes = url_bytes.split(b'\xFE')[0].rstrip(b'\x00')

            url = URI_PREFIX + url_bytes.decode("utf-8", errors="ignore")
            return url
        return None
    except Exception as e:
        print(f"⚠️ Error extracting URL: {e}")
        return None

def extract_uuid(url):
    match = UUID_V4_REGEX.search(url)
    return match.group(0) if match else None

def read_uuid():
    '''
    Select the first available NFC reader.

    In the case of the black reader: 
    The first reader is the NFC reader ("Generic EMV Smartcard Reader 0")
    The second reader is the smart card reader ("Generic EMV Smartcard Reader 01")
    '''
    print('read_uuid start')

    r = readers()
    if len(r) == 0:
        print("... no NFC reader found!")
        exit()

    print(f"... using NFC reader: {r[0]}")

    try:
        connection = r[0].createConnection()
        connection.connect()
        print("\n📡 Tag detected. Reading...")

        ndef_data = read_ndef_message(connection)
        if not ndef_data:
            print("⚠️ No NDEF data found.")

        url = extract_url(ndef_data)
        if url:
            print(f"🌍 URL: {url}")
            uuid = extract_uuid(url)
            if uuid:
                print('read_uuid end')
                return uuid
            else:
                print("⚠️ No valid UUID found in the URL.")
        else:
            print("⚠️ No URL found in NDEF data.")


    except Exception as e:
        print(f"⚠️ Waiting for tag... ({e})")
        time.sleep(1)
