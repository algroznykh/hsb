"""
A script to run a command on recieving an UDP packet.
Configuration file example:
[udp-server]
udp-port = 1234
command = notify-send
log-file = /usr/local/var/log/udp-listener.log

(c) 2016 Aleksandr Groznykh <groznykh.aleksandr@gmail.com>

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; version 2 of the License.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program or from the site that you downloaded it
from; if not, write to the Free Software Foundation, Inc., 59 Temple
Place, Suite 330, Boston, MA  02111-1307   USA
"""

import sys
import socket
import argparse
from ConfigParser import SafeConfigParser
import logging
import subprocess
import re

RX = r"COMMAND=(?P<name>.*?)&RANDOM_BLOB=(?P<id>.+?==)"
id_len = 5

def listen():
    curids = []
    logging.info('listening on {}:{}'.format(udp_ip, udp_port))
    while True:
        if len(curids) >= id_len:
            curids = curids[1:]
        data, addr = sock.recvfrom(1024) # buffer size is 1024 bytes
        logging.debug("incoming message: {}".format(data))
        m = re.match(RX, data)
        if not m:
            logging.error("Cannot parse the message")
            continue
        elif m.group('id') not in curids:
            curids.append(m.group('id'))
            logging.info('Running "{}" with argument: "{}"'
                    .format(command, m.group('name')))
            try:
                subprocess.Popen([command, m.group('name')])
            except Exception, e:
                logging.error('An error occured while running "{}": {}'
                        .format(command, e))


if __name__ == '__main__':
    argparser = argparse.ArgumentParser()
    argparser.add_argument("config", help="path to configuration file")
    args = argparser.parse_args()
    confparser = SafeConfigParser()
    confparser.read(args.config)
    logging.basicConfig(format = '%(asctime)s %(levelname)s %(message)s',
                        strea=sys.stdout,
                        filename=confparser.get('udp-server', 'log-file'),
                        level=logging.DEBUG)
    sock = socket.socket(socket.AF_INET6, # Internet
                     socket.SOCK_DGRAM) # UDP
    udp_ip = ''
    udp_port = confparser.getint('udp-server', 'udp-port')
    command = confparser.get('udp-server', 'command')
    sock.bind((udp_ip, udp_port))
    listen()

