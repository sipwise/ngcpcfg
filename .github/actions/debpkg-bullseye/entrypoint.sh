#!/bin/bash
set -eu -o pipefail

echo "*** Starting execution of '$0' ***"

echo "** Installing build dependencies **"
apt-get -y build-dep .

echo "** Building Debian package **"
dpkg-buildpackage

# We're inside /github/workspace/
echo "** Copying Debian package files to workspace **"
cp ../*.deb ../*.buildinfo  ../workspace/

echo "*** Finished execution of '$0' ***"
