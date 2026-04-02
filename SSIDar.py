import logging
import threading
import time

import pwnagotchi.plugins as plugins

try:
    import RPi.GPIO as GPIO
except ImportError:
    GPIO = None


class SSIDar(plugins.Plugin):
    __author__ = "OpenAI"
    __version__ = "1.3.0"
    __license__ = "GPL3"
    __description__ = "SSIDar: Beeps every few minutes while watched WiFi networks are nearby."

    def __init__(self):
        self.options = {}
        self._gpio_pin = 17
        self._interval = 300
        self._presence_timeout = 120
        self._targets = []
        self._match_mode = "contains"
        self._gpio_ready = False
        self._beep_lock = threading.Lock()
        self._last_beep = 0
        self._last_seen_any = 0
        self._last_matches = []

    def on_loaded(self):
        self._gpio_pin = int(self.options.get("gpio", 17))
        self._interval = int(self.options.get("interval", 300))
        self._presence_timeout = int(self.options.get("presence_timeout", 120))
        self._match_mode = str(self.options.get("match_mode", "contains")).strip().lower()
        self._targets = [str(x).strip() for x in self.options.get("targets", []) if str(x).strip()]

        logging.info("[SSIDar] loaded")
        logging.info(
            "[SSIDar] gpio=%s interval=%s presence_timeout=%s match_mode=%s targets=%s",
            self._gpio_pin,
            self._interval,
            self._presence_timeout,
            self._match_mode,
            self._targets,
        )

        if GPIO is None:
            logging.warning("[SSIDar] RPi.GPIO is not available")
            return

        try:
            GPIO.setwarnings(False)
            GPIO.setmode(GPIO.BCM)
            GPIO.setup(self._gpio_pin, GPIO.OUT, initial=GPIO.LOW)
            self._gpio_ready = True
            logging.info("[SSIDar] GPIO ready on BCM pin %s", self._gpio_pin)
        except Exception as e:
            logging.exception("[SSIDar] failed to initialize GPIO: %s", e)

    def on_unload(self, ui):
        if GPIO is None:
            return

        try:
            if self._gpio_ready:
                GPIO.output(self._gpio_pin, GPIO.LOW)
                GPIO.cleanup(self._gpio_pin)
                logging.info("[SSIDar] cleaned up GPIO %s", self._gpio_pin)
        except Exception as e:
            logging.exception("[SSIDar] cleanup error: %s", e)

    def on_ap_list(self, agent, access_points):
        if not self._gpio_ready or not self._targets:
            return

        now = time.time()
        matched_targets = set()
        matched_ssids = set()

        for ap in access_points:
            ssid = self._extract_ssid(ap)
            if not ssid:
                continue

            matched_target = self._matches(ssid)
            if matched_target:
                matched_targets.add(matched_target)
                matched_ssids.add(ssid)

        if matched_targets:
            self._last_seen_any = now
            self._last_matches = sorted(matched_ssids)

        is_present = (now - self._last_seen_any) <= self._presence_timeout

        if is_present and (now - self._last_beep) >= self._interval:
            logging.info(
                "[SSIDar] watched network nearby: matched_ssids=%s",
                self._last_matches,
            )
            self._last_beep = now
            self._beep_async()

    def _extract_ssid(self, ap):
        if not isinstance(ap, dict):
            return None

        for key in ("hostname", "ssid", "essid", "name"):
            value = ap.get(key)
            if value is None:
                continue

            value = str(value).strip()
            if value:
                return value

        return None

    def _matches(self, ssid):
        ssid_lower = ssid.lower()

        for target in self._targets:
            target_lower = target.lower()

            if self._match_mode == "exact":
                if ssid_lower == target_lower:
                    return target
            else:
                if target_lower in ssid_lower:
                    return target

        return None

    def _beep_async(self):
        t = threading.Thread(target=self._double_beep, daemon=True)
        t.start()

    def _double_beep(self):
        if not self._gpio_ready or GPIO is None:
            return

        with self._beep_lock:
            try:
                GPIO.output(self._gpio_pin, GPIO.HIGH)
                time.sleep(0.08)
                GPIO.output(self._gpio_pin, GPIO.LOW)

                time.sleep(0.06)

                GPIO.output(self._gpio_pin, GPIO.HIGH)
                time.sleep(0.12)
                GPIO.output(self._gpio_pin, GPIO.LOW)
            except Exception as e:
                logging.exception("[SSIDar] beep error: %s", e)
