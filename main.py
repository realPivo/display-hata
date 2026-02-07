import argparse
import threading
import time

from luma.core.render import canvas

from device import create_device
from screens import all_screens


def main():
    parser = argparse.ArgumentParser(description="display-hata OLED screen cycler")
    parser.add_argument("--emulator", action="store_true", help="Use pygame emulator instead of real hardware")
    args = parser.parse_args()

    device = create_device(emulator=args.emulator)

    try:
        all_screens[0].prefetch()

        while True:
            for i, screen in enumerate(all_screens):
                # Prefetch the next screen's data while this one is displayed.
                next_screen = all_screens[(i + 1) % len(all_screens)]
                prefetch_thread = threading.Thread(target=next_screen.prefetch, daemon=True)
                prefetch_thread.start()

                if screen.live:
                    deadline = time.monotonic() + screen.interval
                    while time.monotonic() < deadline:
                        with canvas(device) as draw:
                            screen.draw(draw, device.width, device.height)
                        time.sleep(0.5)
                else:
                    with canvas(device) as draw:
                        screen.draw(draw, device.width, device.height)
                    time.sleep(screen.interval)

                prefetch_thread.join()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
