# DOCKER_NAME=ngcpcfg-bullseye
FROM docker.mgm.sipwise.com/sipwise-bullseye:latest

# Important! Update this no-op ENV variable when this Dockerfile
# is updated with the current date. It will force refresh of all
# of the base images and things like `apt-get update` won't be using
# old cached versions when the Dockerfile is built.
ENV REFRESHED_AT 2022-08-08

RUN apt-get update && apt-get install --assume-yes libhash-merge-perl libtemplate-perl \
  libyaml-libyaml-perl libyaml-tiny-perl libyaml-perl \
  libdata-validate-ip-perl libio-interface-perl libregexp-ipv6-perl \
  fakeroot git lsof make strace pkwalify \
  python3-pytest python3-junitxml file

RUN echo './t/testrunner' >>/root/.bash_history

WORKDIR /code/

################################################################################
# Instructions for usage
# ----------------------
# When you want to build the base image from scratch
# (jump to the next section if you don't want to build yourself!):
#
# % docker build --tag="ngcpcfg-bullseye" -f ./t/Dockerfile .
# % docker run --rm -i -t -v /tmp/results:/results:rw -v $(pwd):/code:rw ngcpcfg-bullseye:latest bash
#
# Use the existing docker image:
# % docker pull docker.mgm.sipwise.com/ngcpcfg-bullseye
# % docker run --rm -i -t -v /tmp/results:/results:rw -v $(pwd):/code:ro docker.mgm.sipwise.com/ngcpcfg-bullseye:latest bash
#
# Inside docker (the command is in history, just press UP button):
#   cd /code && ./t/testrunner
################################################################################
