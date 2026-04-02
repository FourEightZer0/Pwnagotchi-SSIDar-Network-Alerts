import logging
import time
import subprocess
import pwnagotchi.plugins as plugins


class SSIDar(plugins.Plugin):
    __author__ = "FourEightZer0"

    def __init__(self):
        self.options = {}
        self._targets = []
        self._last_match = None
        self._last_beep = 0
        self._cooldown = 5
        self._beep_cmd = ["python3", "/home/pi/beep.py"]

        self._message_until = 0
        self._current_ssid = None

    def on_loaded(self):
        self._targets = [
            str(x).strip().lower()
            for x in self.options.get("targets", [])
            if str(x).strip()
        ]
        self._cooldown = int(self.options.get("cooldown", 5))

        logging.info("[SSIDar] loaded")
        logging.info("[SSIDar] targets=%s", self._targets)

    def on_unfiltered_ap_list(self, agent, access_points):
        try:
            now = time.time()

            for ap in access_points:
                if not isinstance(ap, dict):
                    continue

                ssid = str(ap.get("hostname", "")).strip()
                if not ssid or ssid == "<hidden>":
                    continue

                ssid_l = ssid.lower()

                for target in self._targets:
                    if target in ssid_l:
                        if self._last_match != ssid:
                            logging.info("[SSIDar] MATCH: %s", ssid)
                            self._last_match = ssid

                            # 👇 show message for 10 seconds
                            self._current_ssid = ssid
                            self._message_until = now + 10

                        if now - self._last_beep >= self._cooldown:
                            self._run_beep()
                            self._last_beep = now

                        return

            self._last_match = None

        except Exception as e:
            logging.exception("[SSIDar] callback error: %s", e)

    def on_ui_update(self, ui):
        try:
            now = time.time()

            if self._message_until > now and self._current_ssid:
                ui.set("status", f"Hi {self._current_ssid} nice to see you again")
            else:
                # let normal UI resume
                self._current_ssid = None

        except Exception as e:
            logging.exception("[SSIDar] UI error: %s", e)

    def _run_beep(self):
        try:
            subprocess.Popen(self._beep_cmd)
        except Exception as e:
            logging.exception("[SSIDar] beep launcher error: %s", e)