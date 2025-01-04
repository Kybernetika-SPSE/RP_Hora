import network
import urequests
import os
from time import sleep
from machine import Pin  

led = Pin(2, Pin.OUT)

for _ in range(15):
    led.on()
    sleep(0.2)
    led.off()
    sleep(0.2)
