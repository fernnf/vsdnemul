DOCKER_PRJ="vsdn/ryuctl:latest"
DOCKER_NAME=ryuctl
DOCKER_APP=docker

all: build

clean: del

build:
	$(DOCKER_APP) build  -t $(DOCKER_PRJ) .

run:
	$(DOCKER_APP) run -d -p 6653:6653/tcp --name $(DOCKER_NAME) --privileged $(DOCKER_PRJ)

del:
	$(DOCKER_APP) rm -f $(DOCKER_NAME) && $(DOCKER_APP) rmi $(DOCKER_NAME)