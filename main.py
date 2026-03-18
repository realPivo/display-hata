import argparse
import threading
import time

from luma.core.render import canvas

from buttons import create_buttons
from device import create_device, is_raspberry_pi
from screens import all_screens


def main():
    parser = argparse.ArgumentParser(description="display-hata OLED screen cycler")
    parser.add_argument(
        "--emulator",
        action="store_true",
        help="Use pygame emulator instead of real hardware",
    )
    parser.add_argument(
        "--gif",
        type=str,
        help="Save animation to a GIF file (e.g., output.gif). Overrides --emulator.",
    )
    args = parser.parse_args()

    device = create_device(emulator=args.emulator, gif_file=args.gif)
    hardware = not args.emulator and not args.gif and is_raspberry_pi()
    buttons = create_buttons(hardware)

    try:
        all_screens[0].prefetch()
        i = 0

        while True:
            screen = all_screens[i]

            next_i = (i + 1) % len(all_screens)
            prefetch_thread = threading.Thread(
                target=all_screens[next_i].prefetch, daemon=True
            )
            prefetch_thread.start()

            interrupted = False
            if screen.live:
                deadline = time.monotonic() + screen.interval
                while time.monotonic() < deadline:
                    with canvas(device) as draw:
                        screen.draw(draw, device.width, device.height)
                    interrupted = buttons.wait(0.5)
                    if interrupted:
                        break
            else:
                with canvas(device) as draw:
                    screen.draw(draw, device.width, device.height)
                interrupted = buttons.wait(screen.interval)

            prefetch_thread.join()

            if interrupted and buttons.target_index is not None:
                target = buttons.target_index
                buttons.target_index = None
                all_screens[target].prefetch()
                i = target
            else:
                i = next_i
    except KeyboardInterrupt:
        pass
    finally:
        buttons.cleanup()


if __name__ == "__main__":
    main()
