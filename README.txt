![Screenshot](Screenshot.png)
![Screenshot](Screenshot2.png)

SSIDar for Pwnagotchi
====================

What it does
------------
SSIDar beeps every few minutes while any watched WiFi network is nearby.

Default behavior
----------------
- Uses GPIO17 for the active buzzer
- Double-beeps when a watched SSID is nearby
- Beeps once every 300 seconds (5 minutes) total
- Supports multiple target SSIDs
- Supports partial matching or exact matching

Files
-----
- SSIDar.py
- config_example.toml

Install
-------
1. Copy SSIDar.py to:
   /usr/local/share/pwnagotchi/custom-plugins/SSIDar.py

2. Add the settings from config_example.toml into:
   /etc/pwnagotchi/config.toml

3. Restart Pwnagotchi:
   sudo systemctl restart pwnagotchi

4. Watch logs:
   sudo journalctl -u pwnagotchi -f

Add this to your config.toml

[main.plugins.ssidar]
enabled = true
gpio = 17
interval = 300
presence_timeout = 120
match_mode = "contains"
targets = [
  "ATT",
  "xfinitywifi",
  "linksys",
  "MyHotspot"
]

Notes
-----
- This is written for an active buzzer on GPIO17 and GND.
- match_mode = "contains" lets "ATT" match "ATT1234".
- match_mode = "exact" requires an exact SSID name match.
