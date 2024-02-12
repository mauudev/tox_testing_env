#!/bin/bash

docker container prune -f
docker network prune -f
docker volume prune -f
