import pprint

from pyroute2 import IPDB, netns, NetNS

if __name__ == '__main__':



    pid_n1 = 12704
    pid_n2 = 12913

    #create_veth_link_containers(src_pid = pid_n1, tgt_pid = pid_n2, src_ifname = "pn1", tgt_ifname = "pn2")

    print(netns.listnetns())

    with IPDB(nl = NetNS(str(pid_n2))) as nsdb:
        pprint.pprint(nsdb.interfaces)
        with nsdb.interfaces["pn2"] as source:
            source.up()
            source.set_mtu(9000)
        pprint.pprint(nsdb.interfaces)
