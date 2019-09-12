DOCKER_PRJ="vsdn/vsdnbox:latest"
DOCKER_NAME=vsdnbox
DOCKER_APP=docker

all: build

clean: del

build:
	$(DOCKER_APP) build  -t $(DOCKER_PRJ) .

run:
	$(DOCKER_APP) run -d --name $(DOCKER_NAME) --privileged $(DOCKER_PRJ)

del:
	$(DOCKER_APP) rm -f $(DOCKER_NAME) && $(DOCKER_APP) rmi $(DOCKER_NAME)