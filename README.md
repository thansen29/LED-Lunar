# LED Lunar Phase Display

## Description

Displays the current phase the moon is in on a 32x32 LED matrix using a Raspberry Pi. Since November 2026 it can also show a [gingerbread man](#gingerbread-man), still or waving.

|<img width="378" alt="Screen Shot 2021-03-25 at 7 08 44 PM" src="https://user-images.githubusercontent.com/24940289/112554918-98ed4300-8d9d-11eb-9c1b-a25d4d1f805a.png">|<img width="369" alt="Screen Shot 2021-03-25 at 7 09 02 PM" src="https://user-images.githubusercontent.com/24940289/112554920-9ab70680-8d9d-11eb-900e-de987798fa4f.png">|
|-----|-----|

## Hardware used

- 32x32 RGB LED Matrix Panel
- Raspberry Pi Zero WH
- Adafruit RGB Matrix Bonnet
- 5V 4A power supply
- Normally Open (NO) power button

## Instructions for setup

_Last updated 2026-11-15. Tested on a Raspberry Pi Zero WH running the Raspberry Pi OS that was current in November 2026._

> **Changed 2026-11-15 (decision 10 in [docs/decisions.md](docs/decisions.md)).** This section used to say to run `sudo sh scripts/install` (about 10 minutes), then `sudo python3 src/moon_phase.py ... -m adafruit-hat-pwm ...`. On current Raspberry Pi OS that script's Python build fails with `longintrepr.h: No such file or directory`, yet still prints "Installation complete!". The LED library version pinned in this repo (March 2021) is too old for current Python. The moon command also only worked if the repo was at `/home/pi/Documents/LED-Lunar`. The steps below are what worked instead.

1. Set up your Raspberry Pi first: `sudo apt-get update`, then `sudo apt-get upgrade`.
2. Clone this repo (or copy the folder to the Pi). Then fetch the LED library and switch it to a version that builds with current Python:
   ```
   cd LED-Lunar
   git submodule update --init
   cd submodules/matrix
   git fetch origin
   git checkout b4dc553
   ```
3. Install the build tools and build the library's Python bindings. On a Pi Zero this took about half an hour, and it prints nothing while it compiles. To watch progress, add `-v` after `install`.
   ```
   sudo apt-get install -y python3-dev python3-pip cython3 cmake
   sudo pip install --break-system-packages .
   ```
   `--break-system-packages` is needed because Raspberry Pi OS refuses a plain `sudo pip install`. The scripts run as `sudo python3`, so the library has to go into the system Python.
4. Check that it installed. This should print a file path, not an error:
   ```
   sudo python3 -c "import rgbmatrix.graphics; print(rgbmatrix.__file__)"
   cd ../..
   ```
5. If a script stops with `snd_bcm2835: found that the Pi sound module is loaded`, add `dtparam=audio=off` to `/boot/firmware/config.txt` and reboot. The LED library and the Pi's built-in sound can't run at the same time.

## Running

From the `LED-Lunar` folder:
```
# moon phase
sudo env PYTHONPATH="$PWD" python3 src/moon_phase.py --led-brightness 25 -m adafruit-hat --led-pwm-lsb-nanoseconds=50 -p7

# gingerbread man, still
sudo python3 src/gingerbread.py --led-brightness 25 -m adafruit-hat --led-pwm-lsb-nanoseconds=50 -p7

# gingerbread man, slowly waving one hand
sudo python3 src/gingerbread.py --mode wave --led-brightness 25 -m adafruit-hat --led-pwm-lsb-nanoseconds=50 -p7
```
- `src/moon_phase.py` has the repo's folder written into it (line 6). `env PYTHONPATH="$PWD"` lets it run wherever the repo is. The gingerbread script finds its folder by itself.
- If you did the hardware hack in [Notes](#notes), use `adafruit-hat-pwm` instead of `adafruit-hat`.
- Tweak those options as you see fit, this is just what worked for me.
- Press Ctrl-C to stop.

## Gingerbread man

<img width="600" alt="Gingerbread man on the 32x32 panel: still on the left, the raised hand from the wave on the right" src="assets/gingerbread-preview.png">

_A preview render, not a photo of the panel: `--mode still` on the left, the raised hand from `--mode wave` on the right. Colours on real LEDs look different._

- The art is text grids in `src/gingerbread_art.py`, one character per LED.
- To preview it without the Pi, run `python3 scripts/preview_gingerbread.py` and open the HTML file it prints. It shows the wave moving.
- To redo the image above after changing the art, run `python3 scripts/preview_gingerbread.py --png assets/gingerbread-preview.png`.
- `sh scripts/test` checks the art. It needs no LED hardware.
- Design decisions are in `docs/decisions.md`.

## Run script on boot
To run the script on boot, I used crontab.
`sudo crontab -e`
```
@reboot cd /home/pi/Documents/LED-Lunar && sudo env PYTHONPATH=/home/pi/Documents/LED-Lunar python3 src/moon_phase.py --led-brightness 25 -m adafruit-hat --led-pwm-lsb-nanoseconds=50 -p7
```
Or, for the gingerbread man:
```
@reboot cd /home/pi/Documents/LED-Lunar && sudo python3 src/gingerbread.py --mode wave --led-brightness 25 -m adafruit-hat --led-pwm-lsb-nanoseconds=50 -p7
```

<i>Disclaimer: you might need to tweak the path a bit </i>

## Notes
- I highly recommend the hardware hack to solder a wire between pins 4 and 18. It solves the flickering problem and is a must if you have a static image displayed.
- The commands above use `adafruit-hat`. If you did the hardware hack, use `adafruit-hat-pwm` instead.
- Most of the code isn't hard coded for this size panel, but you'll need to tweak a few things if using a different sized matrix, like the text location, the circle's center point vertically, and radius of the circle.
- Raspberry pis don't have a real time clock by default. So internet connection is required for accurately updating the time, unless you buy a RTC and connect it.
- These instructions worked with my hardware. Mileage may vary with different setups.

## Future potential work
- Add a real time clock so that internet is not required
- Add a potentiometer to change the brightness while the program is running
- 3D print a backing to cover everything up
