def create_device(emulator=False, gif_file=None):
    # Check for GIF request first
    if gif_file:
        from luma.emulator.device import gifanim

        return gifanim(filename=gif_file, width=128, height=64, mode="1")

    elif emulator or not _is_raspberry_pi():
        from luma.emulator.device import pygame

        return pygame(width=128, height=64, mode="1")

    else:
        from luma.core.interface.serial import i2c
        from luma.oled.device import sh1106

        serial = i2c(port=1, address=0x3C)
        return sh1106(serial)


def _is_raspberry_pi():
    try:
        with open("/proc/device-tree/model") as f:
            return "raspberry pi" in f.read().lower()
    except FileNotFoundError:
        return False
