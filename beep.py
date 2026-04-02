import RPi.GPIO as GPIO
import time

PIN = 27

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(PIN, GPIO.OUT, initial=GPIO.LOW)

try:
    GPIO.output(PIN, 1)
    time.sleep(0.08)
    GPIO.output(PIN, 0)

    time.sleep(0.06)

    GPIO.output(PIN, 1)
    time.sleep(0.12)
    GPIO.output(PIN, 0)
finally:
    GPIO.cleanup(PIN)