#!/bin/bash
export PATH=$PATH:/usr/share/openvswitch/scripts/
ovs-ctl --system-id=random start
ovs-vscl set-manager ptcp:6640
/bin/bash
