from smartcard.System import readers
from smartcard.util import toHexString
from smartcard.Exceptions import NoCardException
import uuid
import threading
import time

stop_flag = False
def wait_for_enter():
    global stop_flag
    input("\n🔁 Running in loop mode. Press [Enter] anytime to stop...\n")
    stop_flag = True

threading.Thread(target=wait_for_enter, daemon=True).start()

r = readers()
if len(r) == 0:
    print("❌ No NFC reader found!")
    exit()

reader = r[0]
print(f"✅ Using NFC reader: {reader}")

previous_uid = None
wait_counter = 0

def get_uid(connection):
    GET_UID = [0xFF, 0xCA, 0x00, 0x00, 0x00]
    try:
        response, sw1, sw2 = connection.transmit(GET_UID)
        if sw1 == 0x90 and sw2 == 0x00:
            return toHexString(response)
    except:
        return None
    return None

while not stop_flag:
    try:
        connection = reader.createConnection()
        try:
            connection.connect()
            uid = get_uid(connection)
            if uid is None or uid == previous_uid:
                if wait_counter % 5 == 0:
                    print("⏳ Waiting for a new tag...")
                wait_counter += 1
                time.sleep(1)
                continue

            wait_counter = 0
            previous_uid = uid
            print(f"\n📇 Detected new tag UID: {uid}")

            # Generate and display UUID + URL
            uuid_str = str(uuid.uuid4())
            url = f"https://digitalbrain.techschool.lu/user/{uuid_str}"

            print("🧠 Digital Brain Entry")
            print(f"🔗 UUID: {uuid_str}")
            print(f"🌍 URL:  {url}\n")

            # Build NDEF URI message
            uri_prefix_code = 0x04
            url_body = url.replace("https://", "")
            url_bytes = url_body.encode("utf-8")
            payload = [uri_prefix_code] + list(url_bytes)
            payload_length = len(payload)

            ndef_record = [0xD1, 0x01, payload_length, 0x55] + payload
            tlv = [0x03, len(ndef_record)] + ndef_record + [0xFE]

            block_start = 4
            for i in range(0, len(tlv), 4):
                block = block_start + (i // 4)
                chunk = tlv[i:i+4]
                while len(chunk) < 4:
                    chunk.append(0x00)

                WRITE_CMD = [0xFF, 0xD6, 0x00, block, 0x04] + chunk
                response, sw1, sw2 = connection.transmit(WRITE_CMD)
                if sw1 == 0x90 and sw2 == 0x00:
                    print(f"✅ Wrote block {block}: {toHexString(chunk)}")
                else:
                    print(f"❌ Failed to write block {block}, status: {sw1:02X} {sw2:02X}")

            print("📲 Tag written! Remove it and place a new one.\n")

        except NoCardException:
            time.sleep(0.5)
            continue

    except Exception as e:
        print(f"⚠️ Error: {e}")
        time.sleep(1)

print("\n👋 Exiting loop. All done!")
