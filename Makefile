CWD := $(abspath $(patsubst %/,%,$(dir $(abspath $(lastword $(MAKEFILE_LIST))))))

build-containers:
	docker build -t wiremock ./dockerfiles/wiremock

studio:
	docker run -it --rm --name wiremock-studio -p 9000:9000 -p 8000-8100:8000-8100 up9inc/wiremock-studio:latest

run-wiremock:
	docker run -d --rm -p 8080:8080 -v ${CWD}/src/stubs:/home/wiremock wiremock

stop-all-containers:
	docker ps | grep -v CONTAINER | awk '{print $$1}' | xargs docker stop

delete-all-containers:
	docker ps -a | grep -v CONTAINER | awk '{print $$1}' | xargs docker rm

dump-from-minikube:
	python ${CWD}/src/scripts/dump_stubs_from_minikube.py
