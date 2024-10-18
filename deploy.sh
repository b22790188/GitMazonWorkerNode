#!/bin/bash

REPO_OWNER=$1
REPO_NAME=$2
CONTAINER_PORT=${3:-8080}
CPU_LIMIT=$4
MEMORY_LIMIT=$5
REPO_OWNER_LOWER=$(echo "$REPO_OWNER" | tr '[:upper:]' '[:lower:]')
REPO_NAME_LOWER=$(echo "$REPO_NAME" | tr '[:upper:]' '[:lower:]')


if [ "$(sudo docker ps -a -q -f name=${REPO_OWNER}_${REPO_NAME})" ]; then
	echo "Container ${REPO_OWNER}_${REPO_NAME} found. Removing"
	sudo docker rm -f ${REPO_OWNER}_${REPO_NAME}
fi


sudo docker pull b22790188/${REPO_OWNER_LOWER}_${REPO_NAME_LOWER}:latest

sudo docker container run -d -p ${CONTAINER_PORT}:8080 --name ${REPO_OWNER}_${REPO_NAME} --cpus=${CPU_LIMIT} --memory=${MEMORY_LIMIT}g  b22790188/${REPO_OWNER_LOWER}_${REPO_NAME_LOWER}:latest
