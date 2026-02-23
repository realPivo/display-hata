import ipaddress
import re
import socket
import subprocess
from pathlib import Path

from screens.base import Screen, load_font


def _get_local_subnet() -> str | None:
    """Detect the local /24 subnet CIDR (e.g. '192.168.1.0/24')."""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(("8.8.8.8", 80))
            local_ip = s.getsockname()[0]
        network = ipaddress.IPv4Network(f"{local_ip}/24", strict=False)
        return str(network)
    except Exception:
        return None


def _count_via_nmap(subnet: str) -> int | None:
    """Active host scan with nmap. Returns host count or None if unavailable."""
    try:
        result = subprocess.run(
            ["nmap", "-sn", "--min-parallelism", "100", subnet],
            capture_output=True,
            text=True,
            timeout=30,
        )
        if result.returncode != 0:
            return None
        # "Nmap done: 256 IP addresses (5 hosts up) scanned in 2.34 seconds"
        match = re.search(r"(\d+) hosts? up", result.stdout)
        return int(match.group(1)) if match else None
    except Exception:
        return None


def _count_via_arp() -> int | None:
    """Count recently-seen devices from the kernel ARP table."""
    try:
        arp_path = Path("/proc/net/arp")
        if not arp_path.exists():
            return None
        lines = arp_path.read_text().splitlines()[1:]  # skip header
        return sum(
            1
            for line in lines
            if (p := line.split())
            and len(p) >= 4
            and p[2] != "0x0"
            and p[3] != "00:00:00:00:00:00"
        )
    except Exception:
        return None


def _count_lan_devices() -> int | None:
    subnet = _get_local_subnet()
    if subnet:
        count = _count_via_nmap(subnet)
        if count is not None:
            return count
    return _count_via_arp()


class LanScreen(Screen):
    name = "lan"

    def __init__(self):
        self.font = load_font("FreePixel.ttf", 20)
        self.count: int | None = None

    def prefetch(self):
        self.count = _count_lan_devices()

    def draw(self, draw, width, height):
        if self.count is None:
            lines = ["LAN", "N/A"]
        elif self.count == 1:
            lines = ["LAN", "1 device"]
        else:
            lines = ["LAN", f"{self.count} devices"]

        spacing = 4
        bboxes = [draw.textbbox((0, 0), line, font=self.font) for line in lines]
        heights = [b[3] - b[1] for b in bboxes]
        widths = [b[2] - b[0] for b in bboxes]

        total_h = sum(heights) + spacing * (len(lines) - 1)
        y = (height - total_h) // 2

        for i, line in enumerate(lines):
            draw.text(
                ((width - widths[i]) // 2, y),
                line,
                fill="white",
                font=self.font,
            )
            y += heights[i] + spacing
