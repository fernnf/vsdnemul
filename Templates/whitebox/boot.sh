#!/bin/sh

export PATH=$PATH:/usr/share/openvswitch/scripts/

ovs-ctl --system-id=random start

ovs-vsctl add-br switch0 -- set Bridge switch0 datapath_type=netdev protocols=OpenFlow13

ovs-vsctl set-manager ptcp:6640

/bin/sh
