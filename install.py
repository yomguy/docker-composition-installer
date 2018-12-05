#!/usr/bin/python
"""
The MIT License (MIT)
Copyright (c) 2016 Guillaume Pellerin @yomguy

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""

import os
import argparse
import platform
from pwd import getpwnam
from grp import getgrnam
from shutil import copyfile

sysvinit_script = """#!/bin/sh
### BEGIN INIT INFO
# Provides:	    %s
# Required-Start:	docker
# Required-Stop:	docker
# Default-Start:	2 3 4 5
# Default-Stop:		0 1 6
# Short-Description:	Docker Services
### END INIT INFO

set -e

[ -f /etc/default/$(basename $0) ] && . /etc/default/$(basename $0)

[ -z "$env" ] && env=prod

PROJECT_NAME=%s
BASE_YAML_FILE=%s
OPTIONAL_YAML_FILE=/srv/$PROJECT_NAME/env/${env}.yml

if [ -f $OPTIONAL_YAML_FILE ]; then
    YAMLFILES="$BASE_YAML_FILE -f $OPTIONAL_YAML_FILE"
else
    YAMLFILES="$BASE_YAML_FILE"
fi

OPTS="-f $YAMLFILES -p $PROJECT_NAME"
UPOPTS="-d --no-build --no-deps"

. /lib/lsb/init-functions

case "$1" in
    start)
        log_daemon_msg "Starting $PROJECT_NAME composition" "$PROJECT_NAME" || true
        if su -c "docker-compose $OPTS up $UPOPTS > /dev/null 2>&1" root ; then
            log_end_msg 0 || true
        else
            log_end_msg 1 || true
        fi
        ;;

    stop)
        log_daemon_msg "Stopping $PROJECT_NAME composition" "$PROJECT_NAME" || true
        if su -c "docker-compose $OPTS stop > /dev/null 2>&1" root; then
            log_end_msg 0 || true
        else
            log_end_msg 1 || true
        fi
        ;;

    reload|force-reload)
        log_daemon_msg "Reloading $PROJECT_NAME composition" "$PROJECT_NAME" || true
        if docker-compose $OPTS up $UPOPTS > /dev/null 2>&1 ; then
            log_end_msg 0 || true
        else
            log_end_msg 1 || true
        fi
        ;;

    restart|try-restart)
        log_daemon_msg "Restarting $PROJECT_NAME composition" "$PROJECT_NAME" || true
        if docker-compose $OPTS stop > /dev/null 2>&1; docker-compose $OPTS up $UPOPTS > /dev/null 2>&1 ; then
            log_end_msg 0 || true
        else
            log_end_msg 1 || true
        fi
        ;;

    status)
        docker-compose $OPTS ps && exit 0 || exit $?
        ;;

    *)
        log_action_msg "Usage: /etc/init.d/$PROJECT_NAME {start|stop|reload|force-reload|restart|try-restart|status}" || true
        exit 1
        ;;
esac

exit 0
"""

systemd_service = """
[Unit]
Description=%s composition
Requires=docker.service
After=docker.service
ConditionPathExists=%s

[Service]
ExecStart=%s -f %s up -d
ExecStop=%s -f %s stop

[Install]
WantedBy=local.target
"""

class DockerCompositionInstaller(object):

    docker = '/etc/init.d/docker'
    docker_compose = '/usr/local/bin/docker-compose'

    def __init__(self, config='docker-compose.yml', init_type='sysvinit', cron=False, user='root', logrotate=False):
        self.init_type = init_type
        self.path = os.path.dirname(os.path.realpath(__file__))
        self.config = config
        self.root = self.get_root()
        self.config = os.path.abspath(self.get_root() + os.sep + self.config)
        self.name = self.config.split(os.sep)[-2].lower()
        self.cron = cron
        self.cron_path = self.root + os.sep + 'etc/cron.d/app'
        self.user = user
        self.logrotate = logrotate
        self.logrotate_path = self.root + os.sep + 'etc/logrotate.d/app'


    def get_root(self):
        path = self.path
        while not self.config in os.listdir(path):
            path = os.sep.join(path.split(os.sep)[:-1])
            if not path:
                raise ValueError('The YAML docker composition was not found, please type "install.py -h" for more infos.')
        return path

    def install_docker(self):
        if not os.path.exists(self.docker):
            print 'Installing docker first...'
            os.system('wget -qO- https://get.docker.com/ | sh')
        if not os.path.exists(self.docker_compose):
            print 'Installing docker-compose...'
            os.system('pip install docker-compose')

    def install_daemon_sysvinit(self):
        script = '/etc/init.d/' + self.name
        print 'Writing sysvinit script in ' + script
        data = sysvinit_script % (self.name, self.name, self.config)
        f = open(script, 'w')
        f.write(data)
        f.close()
        os.system('chmod 755 ' + script)
        os.system('update-rc.d ' + self.name + ' defaults')

    def install_daemon_systemd(self):
        service = '/lib/systemd/system/' + self.name + '.service'
        print 'Writing systemd service in ' +  service
        data = systemd_service % (self.name, self.config, self.docker_compose,
            self.config, self.docker_compose, self.config)
        f = open(service, 'w')
        f.write(data)
        f.close()
        os.system('systemctl enable ' + service)
        os.system('systemctl daemon-reload')

    def install_cron(self):
        # the cron script should be in etc/cron.d/ relative to the app directory
        log_path = "var/log/cron"
        if not os.path.exists(log_path) :
            os.makedirs(log_path, 0o755)
            os.chown(log_path, getpwnam(self.user).pw_uid, getgrnam(self.user).gr_gid)
        f = open(self.cron_path)
        rule = f.read()
        f.close()
        f = open('/etc/cron.d/' + self.name, 'w')
        f.write(rule % self.root)
        f.close()

    def uninstall_daemon_sysvinit(self):
        script = '/etc/init.d/' + self.name
        os.system('update-rc.d -f ' + self.name + ' remove')
        os.system('rm ' + script)

    def uninstall_daemon_systemd(self):
        service = '/lib/systemd/system/' + self.name + '.service'
        os.system('systemctl disable ' + service)
        os.system('systemctl daemon-reload')
        os.system('rm ' + service)

    def uninstall_cron(self):
        os.system('rm /etc/cron.d/' + self.name)

    def install_logrotate(self):
        # the cron script should be in etc/cron.d/ relative to the app directory
        log_path = "var/log/app"
        if not os.path.exists(log_path) :
            os.makedirs(log_path, 0o755)
            os.chown(log_path, getpwnam(self.user).pw_uid, getgrnam(self.user).gr_gid)
        f = open(self.logrotate_path)
        rule = f.read()
        f.close()
        f = open('/etc/logrotate.d/' + self.name, 'w')
        f.write(rule % self.root)
        f.close()

    def uninstall_logrotate(self):
        os.system('rm /etc/logrotate.d/' + self.name)

    def uninstall(self):
        print 'Uninstalling ' + self.name + ' composition as a daemon...'
        if self.init_type == 'sysvinit':
            self.uninstall_daemon_sysvinit()
        elif self.init_type == 'systemd':
            self.uninstall_daemon_systemd()
        if self.cron:
            self.uninstall_cron()
        if self.logrotate:
            self.uninstall_logrotate()
        print 'Done'

    def install(self):
        print 'Installing ' + self.name + ' composition as a daemon...'
        self.install_docker()
        if self.init_type == 'sysvinit':
            self.install_daemon_sysvinit()
        elif self.init_type == 'systemd':
            self.install_daemon_systemd()
        if self.cron:
            self.install_cron()
        if self.logrotate:
            self.install_logrotate()
        print 'Done'


def main():
    description ="""Install this docker composition program as a daemon with boot init (sysvinit by default)."""
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument('--uninstall', help='uninstall the daemon', action='store_true')
    parser.add_argument('--cron', help='install cron backup rule', action='store_true')
    parser.add_argument('--user', help='specify user', type=str)
    parser.add_argument('--systemd', help='use systemd', action='store_true')
    parser.add_argument('--logrotate', help='install logrotate rule', action='store_true')
    parser.add_argument('composition_file', nargs='?', help='the path of the YAML composition file to use (optional)')

    config = 'docker-compose.yml'
    init_type = 'sysvinit'
    args = vars(parser.parse_args())

    if args['systemd']:
        init_type = 'systemd'
    if args['composition_file']:
        config = args['composition_file']

    installer = DockerCompositionInstaller(config, init_type, args['cron'], args['user'], args['logrotate'])
    if args['uninstall']:
        installer.uninstall()
    else:
        installer.install()

if __name__ == '__main__':
    if not 'Linux' in platform.system():
        print 'Sorry, this script in only compatible with Linux for the moment...\n'
    else:
        main()
