#! /bin/bash
# Download Gurobi and install it in /opt/gurobi (run as root).

GRB_VERSION=10.0.1
GRB_SHORT_VERSION=10.0
# download and unpack the linux64 release, then remove the archive
wget -v https://packages.gurobi.com/${GRB_SHORT_VERSION}/gurobi${GRB_VERSION}_linux64.tar.gz
tar -xvf gurobi${GRB_VERSION}_linux64.tar.gz
rm -f gurobi${GRB_VERSION}_linux64.tar.gz
# install and drop the docs to save space
mkdir -p /opt/gurobi
mv -f gurobi*/* /opt/gurobi
rm -rf /opt/gurobi/linux64/docs
