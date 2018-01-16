#!/bin/sh

export PATH=$PATH:/usr/share/openvswitch/scripts/

ovs-ctl --system-id=random start

ovs-vsctl add-br switch0 -- set Bridge switch0 datapath_type=netdev

/bin/sh
