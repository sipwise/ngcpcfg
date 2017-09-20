# DOCKER_NAME=ngcpcfg-stretch
FROM docker.mgm.sipwise.com/sipwise-stretch:latest

# Important! Update this no-op ENV variable when this Dockerfile
# is updated with the current date. It will force refresh of all
# of the base images and things like `apt-get update` won't be using
# old cached versions when the Dockerfile is built.
ENV REFRESHED_AT 2017-09-20

RUN apt-get update

# sourcecode test dependencies
RUN apt-get install --assume-yes netcat libhash-merge-perl libtemplate-perl libyaml-libyaml-perl libyaml-tiny-perl libyaml-perl
# misc stuff for execution/debugging/devel
RUN apt-get install --assume-yes fakeroot git lsof make strace
# test execution
RUN apt-get install --assume-yes python3-pytest python3-junitxml

RUN echo './t/testrunner' >>/root/.bash_history

WORKDIR /code/

################################################################################
# Instructions for usage
# ----------------------
# When you want to build the base image from scratch (jump to the next section if you don't want to build yourself!):
# % docker build --tag="ngcpcfg-stretch" .
# % docker run --rm -i -t -v $(pwd)/..:/code:rw ngcpcfg-stretch:latest bash
#
# Use the existing docker image:
# % docker pull docker.mgm.sipwise.com/ngcpcfg-stretch
# % docker run --rm -i -t -v $(pwd)/..:/code:rw docker.mgm.sipwise.com/ngcpcfg-stretch:latest bash
#
# Inside docker (the command is in history, just press UP button):
#   ./t/testrunner
################################################################################
