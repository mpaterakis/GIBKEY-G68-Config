
<h1 align="center">GIBKEY G68 Config</h1>

<p align="center">A configuration tool for GIBKEY G68 keyboards. Remapping and RGB functions are fully supported, with a nice GUI!
    <img src="icon.ico">
</p>

## Preview
![GUI Preview](preview.png)

## Usage
### Method 1: Ready-to-Run!
Download the latest GIBKEY-G68-Config-vX.X.zip file [from the releases section](https://github.com/mpaterakis/GIBKEY-G68-Config/releases/latest), extract it and run the exe! _That's it, have fun!_

### Method 2: Running the script in your local Python
1. Download and extract the contents of the source code file [from the releases section](https://github.com/mpaterakis/GIBKEY-G68-Config/releases/latest). 
2. Install `pyusb` using pip (`pip install pyusb`).
3. Run the `gibkey-config.py` script using python (`python gibkey-config.py <arguments>`).

### Arguments
* Run the program with no arguments to load into the GUI
* You can also use the following arguments for extra functionality:
```
  -h, --help            show this help message and exit
  -s, --silent          Shoosh.
  -p, --pattern PATTERN
                        Specify the lighting pattern (e.g., 'wave', 'static')
  -b, --brightness [0-100]
                        Set brightness level (0-100).
  -c, --color [000000-FFFFFF]
                        Set RGB color (000000-FFFFFF).
  -d, --direction [normal/reverse]
                        Set animation direction (normal/reverse).
  -sp, --speed [1-5]    Set animation speed (1-5).
  -kc, --key-color [key=color] [[key=color] ...]
                        Set inidividual key rgb (key=color). For example '-kc a=ffffff b=000000 enter=010101'
  -km, --key-map [key=mapped_key] [[key=mapped_key] ...]
                        Set inidividual key map (key=mapped_key). For FN mappings, append _fn to the key name. For example '-km a=up b=escape x=u pageup_fn=home'.
  --list-keys           List all usable key names.
  --list-patterns       List all usable pattern names.
  -o, --config-output <filepath>
                        Save the given config in a JSON file.
  -i, --config-input <filepath>
                        Load the config from a JSON file.
```

## Some history
When I ordered this keyboard, and before I had even received it, I noticed that the drivers mentioned a VID of 0x258A and a PID of 0x0049. This matched the Royal Kludge RKG68, the CIY X79 and other similar boards using sinowealth-based controllers.
When I received it, [I tried to dump its firmware](https://github.com/carlossless/sinowealth-kb-tool/issues/95), to no avail. I also tried [the open source utility for the RK keyboards](https://github.com/rnayabed/rangoli), which also failed to do much of anything, besides recognizing the device.

So I decided to follow rangioli's example and start sniffing USB packets via Wireshark. I've never done anything USB-related before, but was up for a fun challenge; and it worked! I managed to break down the different packets into their components (check the commit history to see them in the end of the script file), and after a LOT of trial and error I had the usb functionality fully reversed.

## What about other keyboards?
While I assume that this program will work with other 8051 (258A:0049) devices as well, it might need some tinkering. Specifically around the USB configuration part. This keyboard only receives data through interface 2 (MI_2), which might be different in other keyboards. Your mileage may vary.

## Copyright
This application uses a precompiled DLL file from [libusb](https://github.com/libusb/libusb), which is licensed under the LGPL 2.1. libusb is copyright by the libusb project, and its license is included in `COPYING.libusb`. For more information, visit: https://libusb.info
