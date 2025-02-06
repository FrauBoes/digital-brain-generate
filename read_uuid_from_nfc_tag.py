from smartcard.System import readers
from smartcard.util import toHexString

def read_nfc_tag():
    # Get available readers
    r = readers()
    
    for re in r:
        print(re)

    if len(r) == 0:
        print("No smart card readers found.")
        return

    # Use the second reader, which is the NFC reader ("Generic EMV Smartcard Reader 01")
    # The first reader is the smart card reader ("Generic EMV Smartcard Reader 02")
    reader = r[1]
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
