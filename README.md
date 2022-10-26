# SONiC Saltstack modules

## Current supported versions

* 201911
* 202205 (soon)

## BGP requirements

BGP configuration modules requires to change FRR implementation in SONiC.

It requires `/etc/frr` of the BGP container to be a mounted volume to `/etc/sonic/frr`. This patch will be shared to the community.

## Installation

SONiC modules requires some custom script to be installed:
* /opt/salt/scripts/criteo_fdbshow
* /opt/salt/scripts/criteo_intf_information

These scripts are available [SONiC utilities](https://github.com/kpetremann/criteo-sonic-utilities)

This code assume some grains are set for each SONiC devices:
    hwsku: some-hardware
    nos: sonic
    sonic_asic_type: some-asic
    sonic_build_date: some-date
    sonic_build_version: 201911
    sonic_built_by: someone
    sonic_commit_id: some-commit-id

This is set automatically via our [SONiC Salt Deployer](https://github.com/kpetremann/sonic-salt-deployer).
