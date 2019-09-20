#!/bin/sh

fvconfig load /etc/flowvisor/config.json

chown -R flowvisor:flowvisor /usr/share/db/flowvisor/

sudo -u flowvisor flowvisor -l
