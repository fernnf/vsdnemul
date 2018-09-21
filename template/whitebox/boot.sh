 #!/bin/sh
export PATH=$PATH:/usr/share/openvswitch/scripts/
ovs-ctl --system-id=random start
/bin/sh
