"""Diagnostic: reads GPIO 21, 20, 16 every 0.5s. Press each key and check output."""

import time

import RPi.GPIO as GPIO

PINS = {21: "KEY1", 20: "KEY2", 16: "KEY3"}

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
for pin in PINS:
    GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

print("Press each button in turn. Ctrl+C to stop.\n")
print(f"{'KEY1 (21)':>10} {'KEY2 (20)':>10} {'KEY3 (16)':>10}")

try:
    while True:
        vals = {p: GPIO.input(p) for p in PINS}
        line = f"{'LOW' if vals[21] == 0 else 'high':>10} {'LOW' if vals[20] == 0 else 'high':>10} {'LOW' if vals[16] == 0 else 'high':>10}"
        print(line)
        time.sleep(0.5)
except KeyboardInterrupt:
    pass
finally:
    GPIO.cleanup()
