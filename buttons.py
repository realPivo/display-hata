import threading
import time


class ButtonController:
    BUTTON_MAP = {
        20: 0,  # KEY2 -> screen index 0
        16: 1,  # KEY3 -> screen index 1
    }

    def __init__(self):
        self.interrupt = threading.Event()
        self.target_index: int | None = None
        self._running = True
        self._setup_gpio()
        self._poll_thread = threading.Thread(target=self._poll, daemon=True)
        self._poll_thread.start()

    def _setup_gpio(self):
        import RPi.GPIO as GPIO

        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BCM)
        for pin in self.BUTTON_MAP:
            GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

    def _poll(self):
        import RPi.GPIO as GPIO

        prev = {pin: GPIO.HIGH for pin in self.BUTTON_MAP}
        while self._running:
            for pin, index in self.BUTTON_MAP.items():
                state = GPIO.input(pin)
                if prev[pin] == GPIO.HIGH and state == GPIO.LOW:
                    self.target_index = index
                    self.interrupt.set()
                prev[pin] = state
            time.sleep(0.02)

    def wait(self, timeout: float):
        self.interrupt.wait(timeout)
        if self.interrupt.is_set():
            self.interrupt.clear()
            return True
        return False

    def cleanup(self):
        self._running = False
        import RPi.GPIO as GPIO

        GPIO.cleanup([20, 16])


class DummyButtonController:
    def __init__(self):
        self.target_index = None

    def wait(self, timeout: float):
        time.sleep(timeout)
        return False

    def cleanup(self):
        pass


def create_buttons(is_hardware: bool):
    if is_hardware:
        return ButtonController()
    return DummyButtonController()
