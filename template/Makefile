MAKE=make

all: build

clean: del

build:
	$(MAKE) -C whitebox/ build
	$(MAKE) -C vsdnbox/ build
	$(MAKE) -C openvirtex/ build
	$(MAKE) -C onos/ build
	$(MAKE) -C host/ build
	$(MAKE) -C flowvisor/ build

del:
	$(MAKE) -C whitebox/ clean
	$(MAKE) -C vsdnbox/ clean
	$(MAKE) -C openvirtex/ clean
	$(MAKE) -C onos/ clean
	$(MAKE) -C host/ clean
	$(MAKE) -C flowvisor/ clean

