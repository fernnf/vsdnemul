#!/bin/sh
/usr/share/openvswitch/scripts/ovs-ctl --system-id=random start

/usr/bin/ovs-vsctl --no-wait set-manager ptcp:6640

/bin/bash
