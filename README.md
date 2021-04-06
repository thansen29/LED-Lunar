# LED-Lunar (name tba)

|<img width="378" alt="Screen Shot 2021-03-25 at 7 08 44 PM" src="https://user-images.githubusercontent.com/24940289/112554918-98ed4300-8d9d-11eb-9c1b-a25d4d1f805a.png">|<img width="369" alt="Screen Shot 2021-03-25 at 7 09 02 PM" src="https://user-images.githubusercontent.com/24940289/112554920-9ab70680-8d9d-11eb-900e-de987798fa4f.png">|
|-----|-----|

## Hardware used

- 32x32 RGB LED Matrix Panel
- Raspberry Pi Zero WH
- Adafruit RGB Matrix Bonnet
- 5V 4A power supply
- Normally Open (NO) power button

## Instructions for setup

- Set up your raspberry pi first, sudo apt-get update then sudo apt-get upgrade.
- Clone this repo. cd LED-Lunar and run
```
sudo sh scripts/install
```

- I highly recommend the hardware hack to solder a wire between pins 4 and 18. It solves the flickering problem and is a must if you have a static image displayed. If you're using the hardware mod, then you'll also need to turn off onboard sound. In /boot/config.txt, change `dtparam=audio=on` to `dtparam=audio=off` and reboot.
- Then you can run
```
sudo python3 src/moon_phase.py --led-brightness 25 -m adafruit-hat-pwm --led-pwm-lsb-nanoseconds=50 -p7
```
- Tweak those options as you see fit, this is just what worked for me.

## Run script on boot
To run the script on boot, I used crontab.
`sudo crontab -e`
```
@reboot cd /home/pi/Documents/LED-Lunar && sudo python3 src/moon_phase.py --led-brightness 25 -m adafruit-hat-pwm --led-pwm-lsb-nanoseconds=50 -p7
```

<i>Disclaimer: you might need to tweak the path a bit </i>

## Notes
- Most of the code isn't hard coded for this size panel, but you'll need to tweak a few things if using a different sized matrix, like the text location, the circle's center point vertically, and radius of the circle.
- Raspberry pis don't have a real time clock by default. So internet connection is required for accurately updating the time, unless you buy a RTC and connect it.
- These instructions worked with my hardware. Mileage may vary with different setups.

## Future potential work
- Add a real time clock so that internet is not required
- Add a potentiometer to change the brightness while the program is running
- 3D print a backing to cover everything up
