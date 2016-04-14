# DOCKER_NAME=ngcpcfg-jessie
FROM docker.mgm.sipwise.com/sipwise-jessie:latest

# Important! Update this no-op ENV variable when this Dockerfile
# is updated with the current date. It will force refresh of all
# of the base images and things like `apt-get update` won't be using
# old cached versions when the Dockerfile is built.
ENV REFRESHED_AT 2016-04-15

RUN apt-get update

# sourcecode test dependencies
RUN apt-get install --assume-yes libyaml-tiny-perl netcat libhash-merge-perl libtemplate-perl libyaml-perl
# misc stuff for execution/debugging/devel
RUN apt-get install --assume-yes fakeroot git make
# test execution
RUN apt-get install --assume-yes python3-pytest python3-nose2 python3-junitxml

RUN echo './t/testrunner' >>/root/.bash_history

WORKDIR /code/

################################################################################
# Instructions for usage
# ----------------------
# When you want to build the base image from scratch (jump to the next section if you don't want to build yourself!):
# % docker build --tag="ngcpcfg-tests-jessie" .
# % docker run --rm -i -t -v $(pwd)/..:/code:rw ngcpcfg-tests-jessie:latest bash
#
# Use the existing docker image:
# % docker pull docker1.mgm.sipwise.com/ngcpcfg-tests-jessie
# % docker run --rm -i -t -v $(pwd)/..:/code:rw docker1.mgm.sipwise.com/ngcpcfg-tests-jessie:latest bash
#
# Inside docker (the command is in history, just press UP button):
#   ./t/testrunner
################################################################################
