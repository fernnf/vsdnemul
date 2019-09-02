DOCKER_PRJ="vsdn/vsdnorches:latest"
DOCKER_NAME=vsdnorches
DOCKER_APP=docker

all: build

clean: del

build:
	$(DOCKER_APP) build --no-cache -t $(DOCKER_PRJ) .

run:
	$(DOCKER_APP) run -d  -p 8080:8080/tcp --name $(DOCKER_NAME) --privileged $(DOCKER_PRJ)

del:
	$(DOCKER_APP) rm -f $(DOCKER_NAME) && $(DOCKER_APP) rmi $(DOCKER_NAME)