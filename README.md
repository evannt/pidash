# Pidash

Automatically refreshing slideshow display for the Inky Impression powered by a Raspberry Pi. Pidash will automatically refresh the Inky Impression with a collection of images provided by the user. Additionally, Pidash hosts a local webpage allowing users to make updates to their image collection, display, and device settings.

## Hardware

- RaspberryPi Zero 2 w
- Inky Impression (4" | 5.7" | 7.3" | 13.3")
- Micro SD Card (8gb+)
- Picture Frame
- Usb-A to Micro Usb

## Installation

### Clone the repository
``` bash
git clone https://github.com/evannt/pidash.git
```

### Navigate to the project directory
``` bash
cd pidash
```

### Run the install script
``` bash
sudo bash install/install.sh
```

After a successful install, the script will prompt you to restart the Raspberry Pi. After restarting you will be greeted with the default splash image and will have access to a local webpage corresponding to the hostname of your device.

## Update

Navigate to the project directory
``` bash
cd pidash
```

### Retrieve the latest changes
``` bash
git pull
```

### Run the update script
``` bash
sudo bash install/update.sh
```

## Uninstall

### Run the uninstall script
``` bash
sudo bash install/uninstall.sh
```

## License

[GPL-3.0 license](https://github.com/evannt/pidash/blob/main/LICENSE)
