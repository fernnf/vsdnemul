# vSDNEmu

vSDNEmu  an SDN library for developing computer topology based on container docker. The library is able to create a computer, switches, router or another device for building your owner topology more realistic as possible. Furthermore, the developer can create device templates, with services or applications for working together on topology.

### Requirements 

 - [Docker ](www.docker.com) (17.12.0-ce or later)
 - [Python](www.python.org) (3.6 or later)
 - [OpenvSwitch ](openvswitch.org) (2.7 or later)
 - [IPRoute2](http://kernel.org/pub/linux/utils/net/iproute2/) (4.11.0 or later)
 - Any Linux OS (4.3 or later) - (Developed and Tested on Fedora 26) 

### Installation

1. Clone vsdnemu from github: 
> $ git clone https://github.com/FernandoFarias/vsdnagent.git

2. Install the vsdnemu library:
> $ cd vsdnemu 
> 
>  $ chmod +x install.sh
>  
> $ ./install.sh all 
3. Test a simple topology script
> $ cd examples
>
> $ sudo python3 simplotopo.py
  
