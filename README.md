# docker-composition-installer

Generic script to install a docker composition program as a daemon with complete boot/init scripts.

Compatible only with Linux for now (sysvinit or systemd init systems).

Dependencies: python, wget (for docker)

## Usage

Just copy `install.py` somewhere in your docker-compose project and run it as root or with `sudo`.

It will install Docker and docker-compose automatically only if they are not installed yet.

```
usage: install.py [-h] [--uninstall] [--systemd] [config_file]

Install a docker composition as a daemon with boot init (SysVinit by default).

positional arguments:
  config_file  the path of the YAML composition to install

optional arguments:
  -h, --help   show this help message and exit
  --uninstall  uninstall the daemon
  --systemd    use systemd
```

## Help

Needed for MacOS and Windows versions

## License

The MIT License (MIT)

Copyright (c) 2016 Guillaume Pellerin @yomguy
