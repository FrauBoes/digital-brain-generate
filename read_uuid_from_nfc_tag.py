import uuid
from smartcard.System import readers
from smartcard.util import toHexString

'''
Read UUIDv4 from an NFC tag

Equipment needed: NFC tag, USB NFC reader

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
5. Run this script by running `python read_uuid_from_nfc_tag.py`
'''

def read_block(connection, block):
    """ Read 4 bytes from the specified NFC tag block """
    READ_CMD = [0xFF, 0xB0, 0x00, block, 0x04]
    response, sw1, sw2 = connection.transmit(READ_CMD)
    if sw1 == 0x90 and sw2 == 0x00:
        return response
    else:
        print(f"Failed to read block {block}, status words: {sw1:02X} {sw2:02X}")
        return None

def main():
    '''
    Select the first available NFC reader.

    In the case of the black reader: 
    The first reader is the NFC reader ("Generic EMV Smartcard Reader 0")
    The second reader is the smart card reader ("Generic EMV Smartcard Reader 01")
    '''
    r = readers()
    if len(r) == 0:
        print("No NFC reader found!")
        exit()

    print(f"Using NFC reader: {r[0]}")

    # Connect to the NFC reader
    connection = r[0].createConnection()
    connection.connect()

    # Read UUID from Blocks 4, 5, 6, and 7
    uuid_bytes = []
    for block in range(4, 8):
        data = read_block(connection, block)
        if data:
            uuid_bytes.extend(data)
        else:
            print("Failed to read complete UUID.")
            exit()

    # Convert UUID bytes to standard UUID string format
    uuid_str = str(uuid.UUID(bytes=bytes(uuid_bytes)))
    
    print(f"UUID read from tag: {uuid_str}")

if __name__ == "__main__":
    main()
