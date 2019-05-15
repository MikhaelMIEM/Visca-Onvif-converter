# Description
This is a WIP PTZ Optics VISCA UDP to ONVIF converter service.
# Usage
### Installation
```sh
$ git clone https://github.com/mikhaelmiem/voc
$ pip3 install --user -r voc/requirements.txt
```

### Running
```
$ python3 voc/main.py
```

### Building for Microsoft Windows
Install pyinstaller:
```sh
$ pip3 install --user pyinstaller
```
Assemble main.exe:
```sh
$ cd voc
$ pyinstaller --onefile main.py --windowed
$ cp -vr {cameras.conf,logging.conf,1.png,wsdl} dist
```
Or run the provided build script:
```sh
$ ./winbuild.sh
```
Assembled files will be located in ```dist``` directory

### Configuration
```logging.conf``` can be adjusted according to https://docs.python.org/3/library/logging.config.html
```cameras.conf``` contains ```CAMERAS``` list each of which contains several attributes for a particular ONFIV device.

Example configuration:
```json
{
    "CAMERAS": [
        {
            "IP":       "192.168.15.42",
            "PORT":     80,
            "VISCA_PORT": 50542,
            "LOGIN":    "admin",
            "PASSWORD": "password",
            "PRESET_RANGE": {"min": 1, "max": 3}
        },
        {
            "IP":       "192.168.15.43",
            "PORT":     80,
            "VISCA_PORT": 50543,
            "LOGIN":    "admin",
            "PASSWORD": "password",
            "PRESET_RANGE": {"min": 1, "max": 3}
        }
    ]
}
```