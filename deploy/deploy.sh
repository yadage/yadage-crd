#!/bin/bash
docker login -u "$DOCKERLOGIN" -p "$DOCKERPW"

docker build -t yadage/crdctrl:$TRAVIS_BRANCH -f images/crdctrl/Dockerfile images/crdctrl/
docker push yadage/crdctrl:$TRAVIS_BRANCH

