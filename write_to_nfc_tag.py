import nfc
import uuid
import ndef

# Generate a random UUIDv4
random_uuid = str(uuid.uuid4())
url = f"https://digitalbrain.techschool.lu/user/{random_uuid}"

def write_to_nfc(tag):
    # Create NDEF records for UUID and URL
    uuid_record = ndef.TextRecord(random_uuid)  # Stores the UUID as plain text
    url_record = ndef.UriRecord(url)  # Stores the URL

    # Write records to NFC tag
    tag.ndef.message = [uuid_record, url_record]
    print(f"Successfully wrote UUID and URL to NFC tag:\nUUID: {random_uuid}\nURL: {url}")

def on_connect(tag):
    if tag.ndef:
        write_to_nfc(tag)
    else:
        print("Tag is not NDEF formatted. Please use an NDEF-compatible tag.")
    return True

# Connect to the NFC reader and write to a tag
clf = nfc.ContactlessFrontend('usb')
if clf:
    clf.connect(rdwr={'on-connect': on_connect})
    clf.close()
else:
    print("No NFC reader found.")
