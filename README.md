# SONiC Saltstack modules

## Current supported versions

* 201911
* 202205 (soon)

### Important note

BGP configuration modules requires to change FRR implementation in SONiC.

It requires `/etc/frr` of the BGP container to be a mounted volume to `/etc/sonic/frr`. This patch will be shared to the community.

## Installation

SONiC modules requires some custom script to be installed:
* /opt/salt/scripts/criteo_fdbshow
* /opt/salt/scripts/criteo_intf_information

These scripts are available [SONiC utilities](https://github.com/kpetremann/criteo-sonic-utilities)
