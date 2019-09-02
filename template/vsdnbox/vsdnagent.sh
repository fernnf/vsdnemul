#!/bin/sh
#
echo "Initializing openvswitch ..."
/usr/share/openvswitch/scripts/ovs-ctl --system-id=random start
/usr/bin/ovs-vsctl --no-wait set-manager ptcp:6640
sleep 1
echo "Done"

echo "Initializing vSDNAgent ..."
echo "Testing Env"
echo "Get orches addr: $ORCH_ADDR"

cd /code/vsdnagent
python3 main.py 6653
