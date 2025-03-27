import NFC_PN532 as nfc
from machine import Pin, SPI, reset
import time

def init_pn532(max_retries=3):
    for attempt in range(max_retries):
        try:
            cs = Pin(4, Pin.OUT)
            cs.off()
            time.sleep(0.5)
            cs.on()
            time.sleep(0.5)
            
            spi_dev = SPI(1, baudrate=1000000)
            pn532 = nfc.PN532(spi_dev, cs)
            ic, ver, rev, support = pn532.get_firmware_version()
            print(f'Found PN532 v{ver}.{rev}')
            pn532.SAM_configuration()
            return pn532
        except Exception as e:
            print(f'Attempt {attempt+1} failed: {e}')
            time.sleep(1)
    return None

led = Pin(2, Pin.OUT)
led.off()

pn532 = init_pn532()
if not pn532:
    print("Failed to initialize PN532, resetting...")
    reset()

last_card = None

def blink_led(times, delay=0.2):
    for _ in range(times):
        led.on()
        time.sleep(delay)
        led.off()
        time.sleep(delay)

while True:
    try:
        uid = pn532.read_passive_target(timeout=100)
        if uid:
            string_ID = '-'.join(map(str, uid))
            if string_ID != last_card:
                last_card = string_ID
                print('Card:', string_ID)
                blink_led(1)
        else:
            last_card = None
        time.sleep(0.1)
    except Exception as e:
        print(f"Error: {e}, resetting...")
        time.sleep(1)
        reset()
