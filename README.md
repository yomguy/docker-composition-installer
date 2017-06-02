# docker-composition-installer

Generic script to install a docker composition program as a daemon with complete boot/init scripts.

Compatible only with Linux for now (sysvinit or systemd init systems).

Dependencies: `python`,  `wget` (for docker), `pip` (for docker-compose)

## Usage

Just copy/drop `install.py` somewhere in your docker-compose project and run it as root or with `sudo`.

It will install Docker and docker-compose automatically only if they are not installed yet.

```
usage: install.py [-h] [--uninstall] [--systemd] [--dry-run] [composition_file]

Install this docker composition program as a daemon with boot init (sysvinit
by default).

positional arguments:
  composition_files  the path of the YAML composition files to use (optional), multiple files can be specified

optional arguments:
  -h, --help        show this help message and exit
  --uninstall       uninstall the daemon
  --systemd         use systemd
  --dy-run          dry run, do not install the daemon but print the service file
```

## Help

Needed for MacOS and Windows versions

## Acknowledgments

Thanks to Rémi Desmonet for helping on sysvinit ;)

## License

The MIT License (MIT)

Copyright (c) 2016-2017 Guillaume Pellerin @yomguy
