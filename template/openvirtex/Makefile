DOCKER_PRJ="vsdn/openvirtex:latest"
DOCKER_NAME=openvirtex
DOCKER_APP=docker

all: build

clean: del

build:
	$(DOCKER_APP) build --no-cache -t $(DOCKER_PRJ) .

run:
	$(DOCKER_APP) run -d  --name $(DOCKER_NAME) --privileged $(DOCKER_PRJ)

del:
	$(DOCKER_APP) rm -f $(DOCKER_NAME) && $(DOCKER_APP) rmi $(DOCKER_NAME)