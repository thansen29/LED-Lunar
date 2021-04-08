# Instructions

You will need to solder a connection to the power button on the SCL and GND pins. 
After having cloned this repo, run the setup script from the scripts directory like `sudo sh install`

If you need to uninstall, run `sudo sh uninstall`

Credit for this script goes to howchoo (https://github.com/Howchoo/pi-power-button)
I only made one small tweak to kill my python script before trying to shutdown. Since I built this using the pi zero, which is fairly slow, all of its resources are being hogged up by the main script running, so it takes over a minute to shut down unless I kill the script first
