#! /bin/bash

GRB_VERSION=10.0.1
GRB_SHORT_VERSION=10.0
wget -v https://packages.gurobi.com/${GRB_SHORT_VERSION}/gurobi${GRB_VERSION}_linux64.tar.gz
tar -xvf gurobi${GRB_VERSION}_linux64.tar.gz
rm -f gurobi${GRB_VERSION}_linux64.tar.gz
mkdir -p /opt/gurobi
mv -f gurobi*/* /opt/gurobi
rm -rf /opt/gurobi/linux64/docs
