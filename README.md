# docker-composition-installer
Generic script to install a docker composition as a daemon

Just copy install.py somewhere in your docker-compose project if you need it as a daemon with boot init scripts.

Compatible only with Linux for now (sysvinit or systemd).

## Usage

```
usage: install.py [-h] [--uninstall] [--systemd] [config_file]

positional arguments:
  config_file  the path of the YAML composition to install

optional arguments:
  -h, --help   show this help message and exit
  --uninstall  uninstall the daemon
  --systemd    use systemd
```

## Licence

The MIT License (MIT)
Copyright (c) 2016 Guillaume Pellerin @yomguy

