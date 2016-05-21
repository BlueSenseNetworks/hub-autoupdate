import ConfigParser
import logging
import os
from subprocess import call
import argparse
from time import sleep

log_directory = '/var/log/node-hub'
log_file = 'daemon.log'
config_file = '/etc/bsn/bsnd.ini'


def configure_logging():
    if not os.path.exists(log_directory):
        os.makedirs(log_directory)

    logging.basicConfig(format='%(asctime)s %(message)s', filename=log_directory + '/' + log_file, level=logging.DEBUG)


def main():
    packages = [
        ('bsn-base', {
            'ensure': 'present'
        }),
        ('bsn-supernode', {
            'ensure': 'present'
        }),
        ('bsn-status-page', {
            'ensure': 'present'
        })
    ]

    services = [
        ('bsnd.service', {
            'ensure': 'started',
            'enabled': True
        }),
        ('bsn-config-watch.path', {
            'ensure': 'started',
            'enabled': True
        }),
        ('bsn-autoupdate.timer', {
            'ensure': 'started',
            'enabled': True
        }),
        ('bsn-firstboot.service', {
            'enabled': True
        }),
        ('bluetooth-auto-power@hci0.service', {
            'ensure': 'started',
            'enabled': True
        }),
        ('bluetooth-auto-power@hci1.service', {
            'ensure': 'started',
            'enabled': True
        }),
        ('restart-wpa_supplicant@wlan0.path', {
            'ensure': 'started',
            'enabled': True
        }),
        ('wpa_supplicant@wlan0.service', {
            'ensure': 'started',
            'enabled': True
        }),
        ('bsn-status-page.service', {
            'ensure': 'started',
            'enabled': True
        }),
        ('bsn-supernode.service', {
            'ensure': 'started',
            'enabled': True
        })
    ]

    parser = argparse.ArgumentParser(description='Enable and start required systemd units')
    parser.add_argument('--no-start', action='store_false', help='whether or not to start the required units',
                        dest='start')
    parser.add_argument('--onetime', action='store_true', help='whether or not to start the required units')
    args = parser.parse_args()

    configure_logging()

    config = ConfigParser.ConfigParser()
    config.read(config_file)
    update_interval = config.get('Update', 'interval')
    stability = config.get('Update', 'stability')

    if stability == 'production':
        repo_path = 'http://packages.bluesense.co'
    else:
        repo_path = 'http://' + stability + '-packages.bluesense.co'

    logging.debug('Setting package repository to: ' + repo_path)
    call('sed -i \'s/Server = .*bluesense.co$/Server = ' + repo_path.replace('/', '\/') + '/g\' /etc/pacman.conf',
         shell=True)

    logging.debug('Setting node environment to: ' + stability)
    call('export NODE_ENV=' + stability, shell=True)

    logging.debug('Started update daemon,  interval: ' + update_interval)
    while True:
        try:
            call('pacman -Sy', shell=True)
            for package, state in packages:
                if state['ensure'] == 'present':
                    call('pacman -S --needed --noconfirm ' + package, shell=True)
                elif state['ensure'] == 'absent':
                    call('pacman -R --noconfirm ' + package, shell=True)

            call('systemctl daemon-reload', shell=True)
            for service, state in services:
                print service
                if state['enabled']:
                    call('systemctl enable ' + service, shell=True)
                else:
                    call('systemctl disable ' + service, shell=True)

                if 'ensure' in state:
                    if state['ensure'] == 'started' and args.start:
                        call('systemctl start ' + service, shell=True)

                    if state['ensure'] == 'stopped':
                        call('systemctl stop ' + service, shell=True)
        except Exception, ex:
            print ex

        if args.onetime:
            break

        sleep(float(update_interval))


if __name__ == "__main__":
    main()
