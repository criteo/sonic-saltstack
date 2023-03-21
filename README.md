# SONiC Saltstack modules

## Current supported versions

* 201911
* 202205 (soon)

## BGP requirements

BGP configuration modules require a change to FRR implementation in SONiC.

It requires `/etc/frr` of the BGP container to be a mounted volume to `/etc/sonic/frr`:
* for SONiC >= 202205, you need to enable [split-unified](https://github.com/sonic-net/sonic-buildimage/commit/9d3814045bf950576bb274180ffec001abac1c32)
* for SONiC < 202205, you need to apply the [patch manually](https://github.com/criteo/criteo-sonic-utilities#frr-mounted-configuration).

## Installation

SONiC modules require some custom script to be installed:
* /opt/salt/scripts/criteo_fdbshow
* /opt/salt/scripts/criteo_intf_information

These scripts are available [SONiC utilities](https://github.com/criteo/criteo-sonic-utilities)

This code assumes some grains are set for each SONiC device:
```yaml
hwsku: some-hardware
nos: sonic
sonic_asic_type: some-asic
sonic_build_date: some-date
sonic_build_version: 201911
sonic_built_by: someone
sonic_commit_id: some-commit-id
```

This is automatically set by our [SONiC Salt Deployer](https://github.com/criteo/sonic-salt-deployer).
