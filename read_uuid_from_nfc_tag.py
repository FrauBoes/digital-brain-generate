from smartcard.System import readers
from smartcard.util import toHexString

'''
Read the UID from a NFC tag

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

def read_nfc_tag():
    # Get available readers
    r = readers()
    
    for re in r:
        print(re)

    if len(r) == 0:
        print("No smart card readers found.")
        return

    '''
    Use the first reader, which is the NFC reader ("Generic EMV Smartcard Reader 0")
    The second reader is the smart card reader ("Generic EMV Smartcard Reader 01")
    '''
    reader = r[0]
    print(f"Using reader: {reader}")
    
    connection = reader.createConnection()
    connection.connect()

    # APDU Command to get UID (ISO14443A standard)
    GET_UID = [0xFF, 0xCA, 0x00, 0x00, 0x00]
    data, sw1, sw2 = connection.transmit(GET_UID)

    if sw1 == 0x90 and sw2 == 0x00:
        print("NFC Tag UID:", toHexString(data))
    else:
        print(f"Failed to read UID. Status words: {sw1:02X} {sw2:02X}")

if __name__ == "__main__":
    read_nfc_tag()
