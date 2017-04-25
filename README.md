# homeassistant-magicblue
MagicBlue custom component for Home Assistant

## Requirement

- [`https://github.com/Betree/magicblue`](https://github.com/Betree/magicblue)

## Installation
Copy the `magicbluelight.py` file to :
```sh
<YOUR_CONFIG_DIR>/custom_component/lights/magicbluelight.py
```

## Configuration
First, make sure you can see your MagicBlue(s) by running:
```sh
$ magicblueshell
Magic Blue interactive shell v0.2.2
Type "help" for a list of available commands
> help
 ----------------------------
| List of available commands |
 ----------------------------
COMMAND         PARAMETERS                    DETAILS
-------         ----------                    -------
help                                          Show this help
list_devices                                  List Bluetooth LE devices in range
ls              //                            //
connect         mac_address or ID             Connect to light bulb
disconnect                                    Disconnect from current light bulb
set_color       name or hexadecimal value     Change bulb's color
set_warm_light  intensity[0.0-1.0]            Set warm light
turn            on|off                        Turn on / off the bulb
exit                                          Exit the script
> ls
Listing Bluetooth LE devices in range for 5 minutes.Press CTRL+C to stop searching.
ID    Name                           Mac address 
--    ----                           ----------- 
1     LEDBLE-XXXXXXXX                xx:xx:xx:xx:xx:xx
```

Modify the following example and add it to your `configuration.yaml` file:
```sh
light:
  platform: magicbluelight
    name: 'Living Room'
    address: 20:16:01:01:05:a0
    version: 9
```
Multiple devices are supported:
```sh
light:
  - platform: magicbluelight
    name: 'Living Room'
    address: 20:16:01:01:05:a0
    version: 9
  - platform: magicbluelight
    name: 'Bedroom'
    address: 20:16:01:01:03:e5
    version: 9
```

## Notes
- Right now you'll have to manually install the required python module `magicblue`.

## Todo
- Brightness control
- Color control
- Auto install the required module
