"""SONiC execution modules to get info or change configuration.

SONiC is handled like a Linux server.
Please keep in mind that in some cases, changing the configuration needs a complete reload of the
configuration, stopping the service during few seconds.
"""

# pylint: disable=C0302

import difflib
import json
import logging
import re
from collections import defaultdict
from datetime import datetime
from ipaddress import IPv4Network, ip_address

import yaml
from salt.exceptions import CommandExecutionError

__virtualname__ = "sonic"

log = logging.getLogger(__name__)
CONFIGDB_FILE = "/etc/sonic/config_db.json"
FRR_FILE = "/etc/sonic/frr/frr.conf"
SNMP_FILE = "/etc/sonic/snmp.yml"
SONIC_DIR = "/etc/sonic/"


def __virtual__():
    return __salt__["grains.get"]("nos") == "sonic"


def _salt_call(command, *args, **kwargs):
    return __salt__[command](*args, **kwargs)


def _utils_call(command, *args, **kwargs):
    return __utils__[command](*args, **kwargs)


def _diff(config_a, config_b, name_a="before", name_b="after"):
    config_a_list = config_a.splitlines(keepends=True)
    config_b_list = config_b.splitlines(keepends=True)

    diff = difflib.unified_diff(config_a_list, config_b_list, fromfile=name_a, tofile=name_b)
    return "".join(list(diff))


##
# Interface
##


def get_interfaces(interface=""):
    """Get interface(s) details.

    Including common info (status, description...) and both transceiver and optical levels.

    :param interface: interface name
    """
    # enforce empty string if interface is None
    if not interface:
        interface = ""

    res = __salt__["cmd.run"]("/opt/salt/scripts/criteo_intf_information {}".format(interface))

    if __context__["retcode"] != 0:
        raise CommandExecutionError("Failed to run criteo_intf_information script")

    return json.loads(res)


def _get_interfaces_brief():
    return __salt__["network.interfaces"]()


def get_ip_addresses(interface):
    """Get IPv4 and IPv6 addresses of a SONiC device (or any other Linux based device).

    :param interface: interface name we want (ex: Ethernet0)

    CLI Example:

    .. code-block:: bash

        salt "sonic.tor" sonic.get_ip_addresses Ethernet0

    Output example:

    .. code-block:: python

        {
            "ipv4": ["192.0.2.0/31"],
            "ipv6": ["2001:db8::/127", "2001:db8::/64"],
        }
    """
    interfaces = _get_interfaces_brief()

    if not interfaces or interface not in interfaces:
        return {}

    addresses = defaultdict(list)

    for addr in interfaces[interface].get("inet", {}):
        prefix_len = IPv4Network("0.0.0.0/{}".format(addr["netmask"])).prefixlen
        cidr = "{}/{}".format(addr["address"], prefix_len)
        addresses["ipv4"].append(cidr)

    for addr in interfaces[interface].get("inet6", {}):
        cidr = "{}/{}".format(addr["address"], addr["prefixlen"])
        addresses["ipv6"].append(cidr)

    return dict(addresses)


def _convert_interface_counters_napalm_fmt(counters):
    data = {}
    for interface, stats in counters.items():
        data[interface] = {
            "rx_broadcast_packets": None,
            "tx_broadcast_packets": None,
            "rx_unicast_packets": None,
            "tx_unicast_packets": None,
            "rx_multicast_packets": None,
            "tx_multicast_packets": None,
            "rx_octets": int(stats.get("RX_OK", "0").replace(",", "")),
            "tx_octets": int(stats.get("TX_OK", "0").replace(",", "")),
            "rx_errors": int(stats.get("RX_ERR", "0").replace(",", "")),
            "rx_discards": int(stats.get("RX_DRP", "0").replace(",", "")),
            "tx_errors": int(stats.get("TX_ERR", "0").replace(",", "")),
            "tx_discards": int(stats.get("TX_DRP", "0").replace(",", "")),
        }

    return {"out": data}


def get_interface_counters(interface="", napalm_output=False):
    """Get interface counters.

    Values set to None means unsupported.

    :param interface: interface name we want (ex: Ethernet0)
    :param napalm_output: expose info in the same data structure than napalm (to ease integration)

    .. code-block:: bash

        salt "sonic.tor" sonic.get_interface_counters Ethernet0 napalm_output=True

    Output example:

    .. code-block:: python

        {
            "sonic.tor": {
                "out": {
                    "Ethernet0": {
                        "rx_unicast_packets": None,
                        "rx_discards": 0,
                        "rx_octets": None,
                        "tx_unicast_packets": None,
                        "tx_broadcast_packets": None,
                        "tx_errors": 0,
                        "rx_multicast_packets": None,
                        "tx_discards": 0,
                        "rx_errors": 2,
                        "tx_octets": None,
                        "rx_broadcast_packets": None,
                        "tx_multicast_packets": None
                    }
                }
            }
        }
    """
    # enforce empty string when interface is None
    if not interface:
        interface = ""

    res = _salt_call("cmd.run", "portstat -j")
    data = json.loads(res)

    if interface:
        data = {interface: data.get(interface, {})}

    if napalm_output:
        return _convert_interface_counters_napalm_fmt(data)

    return data


##
# LLDP
##


def _extract_cap(capabilities):
    capabilities = _utils_call("data_mgmt.normalize_plural", capabilities)

    enabled_cap = [x["type"] for x in capabilities if x["enabled"]]
    all_cap = [x["type"] for x in capabilities]

    return enabled_cap, all_cap


def _convert_lldp_napalm_fmt(lldp_info):
    interfaces = {}
    lldp_info = _utils_call("data_mgmt.normalize_plural", lldp_info)

    for interface in lldp_info:
        name, detail = interface.popitem()

        if "id" in detail["chassis"]:
            # if the server is not configured values are in chassis
            chassis_info = detail["chassis"]
            remote_name = ""
        else:
            # if the server is configured values are in chassis[name]
            remote_name, chassis_info = detail["chassis"].popitem()

        enabled_cap = None
        all_cap = None
        if "capability" in chassis_info:
            enabled_cap, all_cap = _extract_cap(chassis_info["capability"])

        interfaces[name] = [
            {
                "parent_interface": name,
                "remote_chassis_id": chassis_info["id"]["value"],
                "remote_port": detail["port"]["id"]["value"],
                "remote_port_description": detail["port"].get("descr"),
                "remote_system_capab": all_cap,
                "remote_system_description": chassis_info.get("descr"),
                "remote_system_enable_capab": enabled_cap,
                "remote_system_name": remote_name,
            }
        ]

    return {"out": interfaces}


def _convert_mac_napalm_fmt(mac_info):
    output = [
        {
            "mac": mac_info_item["MacAddress"],
            "interface": mac_info_item["Port"],
            "vlan": mac_info_item["Vlan"],
            "static": bool(mac_info_item["Type"] == "Static"),
            "active": "N/A",
            "moves": "N/A",
            "last_move": "N/A",
        }
        for mac_info_item in mac_info
    ]

    return output


def _get_lldp(interface):
    return __salt__["cmd.run"]("lldpctl -f json {}".format(interface))


def lldp(interface="", napalm_output=False):
    """Get lldp info of one or all interfaces.

    :param interface: interface name we want (ex: Ethernet0), default shows info for all interfaces
    :param napalm_output: expose info in the same data structure than napalm (to ease integration)

    CLI Example:

    .. code-block:: bash

        salt "sonic.tor" sonic.lldp Ethernet0 napalm_output=True

    Output example:

    .. code-block:: python

        {
            "out": {
                "Ethernet0": [
                    {
                        "remote_system_description": "sonic.tor:Ethernet0",
                        "remote_port_description": "sonic.tor:Ethernet0",
                        "remote_system_enable_capab": ["Bridge", "Router"],
                        "remote_system_capab": ["Bridge", "Router", "Wlan", "Station"],
                        "remote_port": "Ethernet0",
                        "remote_system_name": "sonic.spine",
                        "remote_chassis_id": "90:10:00:01:02:03",
                        "parent_interface": "Ethernet0",
                    }
                ]
            }
        }
    """
    # enforce empty string when interface is None
    if not interface:
        interface = ""

    data = _get_lldp(interface)
    if not data:
        return None

    try:
        lldp_info = json.loads(data)["lldp"]["interface"]
    except KeyError:
        return None

    if napalm_output:
        return _convert_lldp_napalm_fmt(lldp_info)

    return lldp_info


def get_mac_from_port(interface=None, napalm_output=False):
    """Get MAC info using criteo_fdbshow.

    If the interface is specified, return the MAC table for this specific interface.
    If the interface is not specified, return the full MAC table.
    """
    criteo_fdbshow_command = "/usr/bin/python /opt/salt/scripts/criteo_fdbshow"
    if interface:
        criteo_fdbshow_command += " -p {}".format(interface)

    # An old version of criteo_fdbshow outputs JSON by default and does not support
    # the "-j" option, newer version requires "-j" to output JSON.
    if "201911" not in __salt__["grains.get"]("sonic_build_version"):
        criteo_fdbshow_command += " -j"

    macport_info_output = __salt__["cmd.run"](criteo_fdbshow_command)

    macport_info = json.loads(macport_info_output)

    if napalm_output:
        return _convert_mac_napalm_fmt(macport_info)

    return macport_info


def get_port_from_mac(mac="", napalm_output=False):
    """Get interface of a MAC using criteo_fdbshow."""
    criteo_fdbshow_command = "/usr/bin/python /opt/salt/scripts/criteo_fdbshow"

    # An old version of criteo_fdbshow outputs JSON by default and does not support
    # the "-j" option, newer version requires "-j" to output JSON.
    if "201911" not in __salt__["grains.get"]("sonic_build_version"):
        criteo_fdbshow_command += " -j"

    full_mactable_output = __salt__["cmd.run"](criteo_fdbshow_command)

    full_mactable = json.loads(full_mactable_output)

    macport_info = [x for x in full_mactable if x["MacAddress"] == mac]

    if macport_info == []:
        return None

    if napalm_output:
        return _convert_mac_napalm_fmt(macport_info)

    return macport_info


##
# snmp
##


def get_snmp_config():
    """Get snmp configuration from snmp.yml file.

    CLI Example:

    .. code-block:: bash

        salt "sonic.tor" sonic.get_snmp_config
    """
    # check file existence
    _salt_call("file.file_exists", SNMP_FILE)
    if __context__["retcode"] != 0:
        raise CommandExecutionError("File {} does not exist".format(SNMP_FILE))

    # load file
    data = _salt_call("file.read", SNMP_FILE)

    # is yaml ?
    try:
        data_yaml = yaml.safe_load(data)
    except yaml.YAMLError as exc:
        raise CommandExecutionError("File {} cannot be loaded".format(SNMP_FILE)) from exc

    return data_yaml


def _apply_snmp_config(remote_tmpfile):
    # return nothing if done with success
    res = __salt__["cmd.run"]("sudo cp {} {}".format(remote_tmpfile, SONIC_DIR))

    if res:
        return res

    __salt__["cmd.run"]("sudo systemctl restart snmp.service")
    return ""


def snmp_config(template_name, context=None, saltenv="base", test=False):
    """Push and replace the snmp configuration file.

    It erases the current configuration.

    :param template: Jinja Template to generate the configuration
    :param context: variables to map with the template
    :param saltenv: Salt environment
    :param test: test mode (dry run)

    Output example:


    CLI Example:

    .. code-block:: python

       {
            "dry_run": False,
            "pushed": "push SNMP configuration",
            "changed": True,
       }
    """
    # generate the config
    template_content = __salt__["cp.get_file_str"](template_name, saltenv=saltenv)
    if not template_content:
        raise CommandExecutionError("Unable to get {}".format(template_name))

    rendered = __salt__["file.apply_template_on_contents"](
        contents=template_content,
        template="jinja",
        context=context,
        defaults=None,
        saltenv=saltenv,
    )
    log.debug("configuration to push: %s", rendered)

    # push the config
    __salt__["file.mkdir"]("/etc/sonic/tmp/")
    remote_tmpfile = "/etc/sonic/tmp/snmp.yml"
    __salt__["file.write"](remote_tmpfile, rendered)

    result = None

    current = str(get_snmp_config())
    expected = str(yaml.safe_load(rendered))
    changes = _diff(current, expected)

    if test:
        result = None if changes else True
        comment = "- Configuration expected:\n{}\n- Changes needed:\n{}".format(rendered, changes)
        changes = None

    else:
        if changes:
            out = _apply_snmp_config(remote_tmpfile)
            if __context__["retcode"] != 0:
                __salt__["file.remove"](remote_tmpfile)
                __context__["retcode"] = 1
                raise CommandExecutionError(
                    "Unable to push snmp configuration: {}, change {}".format(out, changes)
                )
            comment = "- Configuration pushed and loaded"
        else:
            comment = "- No change detected"

        result = True

    __salt__["file.remove"](remote_tmpfile)

    return {
        "result": result,
        "dry_run": test,
        "changes": changes,
        "comment": comment,
    }


##
# config_db
##


def get_configdb():
    """Get startup configuration from config_db.json file.

    CLI Example:

    .. code-block:: bash

        salt "sonic.tor" sonic.get_configdb
    """
    # check file existence
    _salt_call("file.file_exists", CONFIGDB_FILE)
    if __context__["retcode"] != 0:
        raise CommandExecutionError("File {} does not exist".format(CONFIGDB_FILE))

    # load file
    data = _salt_call("file.read", CONFIGDB_FILE)

    # is json ?
    try:
        data_json = json.loads(data)
    except KeyError as exc:
        raise CommandExecutionError("File {} cannot be loaded".format(CONFIGDB_FILE)) from exc

    return data_json


def get_running_configdb():
    """Get running config_db configuration.

    CLI Example:

    .. code-block:: bash

        salt "tor1" sonic.get_running_configdb
    """
    running_configdb = __salt__["cmd.run"]("show runningconfiguration all")

    # is json ?
    try:
        data_json = json.loads(running_configdb)
    except KeyError as exc:
        raise CommandExecutionError("Running config_db is not JSON") from exc

    return data_json


def _apply_configdb_config(remote_tmpfile):
    # return nothing if done with success
    res = __salt__["cmd.run"]("sudo cp {} {}".format(remote_tmpfile, SONIC_DIR))

    if res:
        return res

    return ""


def _check_candidate_configdb_config(remote_tmpfile):
    """Read and check the config_db.json format.

    sonic-cfgen is a tool that we can use for JSON format verificaton
    command line exemple:
    sonic-cfggen -j /etc/sonic/config_db.json --print-data

    """
    return __salt__["cmd.run"]("sudo sonic-cfggen -j {}".format(remote_tmpfile))


def configdb_config(template_name, context=None, saltenv="base", reload_conf=False, test=False):
    """Push and replace the config_db configuration file.

    It erases the current configuration.

    :param template: Jinja Template to generate the configuration
    :param context: variables to map with the template
    :param saltenv: Salt environment
    :param test: test mode (dry run)

    Output example:


    CLI Example:

    .. code-block:: python

       {
            "dry_run": False,
            "pushed": "push CONFIG_DB configuration",
            "changed": True,
       }
    """
    # generate the config
    template_content = __salt__["cp.get_file_str"](template_name, saltenv=saltenv)
    if not template_content:
        raise CommandExecutionError("Unable to get {}".format(template_name))

    rendered = __salt__["file.apply_template_on_contents"](
        contents=template_content,
        template="jinja",
        context=context,
        defaults=None,
        saltenv=saltenv,
    )
    log.debug("configuration to push: %s", rendered)

    # upload the config_db file
    __salt__["file.mkdir"]("/etc/sonic/tmp/")
    remote_tmpfile = "/etc/sonic/tmp/config_db.json"
    __salt__["file.write"](remote_tmpfile, rendered)

    # check the new config_db.json file
    out = _check_candidate_configdb_config(remote_tmpfile)

    if __context__["retcode"] != 0:
        raise CommandExecutionError("Invalid config_db configuration: {}".format(out))

    if not test:
        current = str(get_configdb())
        out = _apply_configdb_config(remote_tmpfile)
        if __context__["retcode"] != 0:
            __salt__["file.remove"](remote_tmpfile)
            raise CommandExecutionError("Unable to push config_db configuration: {}".format(out))
        new_config = str(get_configdb())
        if reload_conf:
            __salt__["cmd.run"]("sudo config reload -y")

        changes = _diff(current, new_config)
        changed = bool(changes)
        comment = "- Configuration pushed and loaded"
    else:
        changes = None
        changed = None
        comment = "- Configuration discarded:\n{}".format(rendered)

    # clean temp file
    __salt__["file.remove"](remote_tmpfile)

    return {
        "result": changed,
        "dry_run": test,
        "changes": changes,
        "comment": comment,
    }


##
# BGP session route map installed
##


def _extract_bgp_neighbor_info(neighbor_ip, bgp_data):
    # Get the ip version: 4 for IPv4, 6 for IPv6
    ip_vers = ip_address(neighbor_ip).version

    unicast_field = "ipv{}Unicast".format(ip_vers)  # FRR 7.2.1
    unicast_field_legacy = "IPv{} Unicast".format(ip_vers)  # FRR 7.0.1

    if unicast_field in bgp_data["addressFamilyInfo"]:
        unicast_info = bgp_data["addressFamilyInfo"][unicast_field]
    elif unicast_field_legacy in bgp_data["addressFamilyInfo"]:
        unicast_info = bgp_data["addressFamilyInfo"][unicast_field_legacy]
    else:
        unicast_info = {}  # no specific configuration found in safi config

    state = "up" if bgp_data["bgpState"] == "Established" else "down"

    bgp_info = {
        "remote_as": bgp_data["remoteAs"],
        "local_as": bgp_data["localAs"],
        "remote_address": neighbor_ip,
        "peer_group": bgp_data.get("peerGroup"),
        "description": bgp_data.get("nbrDesc"),
        "import_policy": unicast_info.get("routeMapForIncomingAdvertisements"),
        "export_policy": unicast_info.get("routeMapForOutgoingAdvertisements"),
        "vrf": "default",  # TODO: change once VRF is supported by SONiC
        "state": state,
    }

    return bgp_info


def _get_bgp_neighbor(neighbor):
    return __salt__["cmd.run"]("vtysh -c 'show bgp neighbor {} json'".format(neighbor))


def get_bgp_neighbors(neighbor="", frr_output=False):
    """Get BGP neighbors information.

    :param neighbor: neighbor address
    :param frr_output: provide raw output from FRR

    CLI Example:

    .. code-block:: bash

        salt "sonic.tor" sonic.get_bgp_neighbors 192.0.2.1

    Output example:

    .. code-block:: python

        {
            "192.0.2.1": {
                "peer_group": "SPINES",
                "import_policy": "FABRIC-IN",
                "vrf": "default",
                "remote_address": "192.0.2.1",
                "local_as": 65000,
                "remote_as": 65001,
                "description": "sonic.spine",
                "export_policy": "FABRIC-OUT",
                "state": "up",
            }
        }
    """
    # enforce empty string when neighbor is None
    if not neighbor:
        neighbor = ""

    data = _get_bgp_neighbor(neighbor)

    try:
        bgp_data = json.loads(data)
    except KeyError as exc:
        raise CommandExecutionError("Unable to load BGP configuration") from exc

    if not bgp_data:
        return {}

    if bgp_data.get("bgpNoSuchNeighbor"):
        raise CommandExecutionError("No BGP session with {}".format("neighbor_ip"))

    if frr_output:
        return bgp_data

    result = {}
    for neighbor_ip, data in bgp_data.items():
        result[neighbor_ip] = _extract_bgp_neighbor_info(neighbor_ip, data)

    return result


def get_bgp_startup_config():
    """Return startup BGP configuration in String format.

    CLI Example:

    .. code-block:: bash

        salt "sonic.tor" sonic.get_bgp_startup_config
    """
    # check file existence
    _salt_call("file.file_exists", FRR_FILE)
    if __context__["retcode"] != 0:
        raise CommandExecutionError("File {} does not exist".format(FRR_FILE))

    # load file
    data = _salt_call("file.read", FRR_FILE)

    return data


def get_bgp_config():
    """Return running BGP configuration in String format.

    CLI Example:

    .. code-block:: bash

        salt "sonic.tor" sonic.get_bgp_config

    Output example:

    .. code-block:: text

        !
        frr version 7.0.1-sonic
        frr defaults traditional
        hostname sonic.tor
        log syslog informational
        log facility local4
        ...
    """
    running_config = __salt__["cmd.run"]("show run bgp")

    # Clean the config
    running_config = re.sub(
        r"^Building configuration\.\.\.\s+$", "", running_config, flags=re.MULTILINE
    )
    running_config = re.sub(r"^Current configuration:\s*$", "", running_config, flags=re.MULTILINE)

    return running_config


def save_bgp_config():
    """Save running BGP configuration to startup configuration.

    CLI Example:

    .. code-block:: bash

        salt "sonic.tor" sonic.save_bgp_config
    """
    __salt__["cmd.run"]("vtysh --writeconfig")
    return True


def get_route_maps():
    """Get route-map list set on a device.

    CLI Example:

    .. code-block:: bash

        salt "sonic.tor" sonic.get_route_maps

    Output example:

    .. code-block:: python

        [
            "FABRIC-OUT",
            "FABRIC_MAINTENANCE-OUT",
            "DENY",
            "FABRIC-IN",
        ]
    """
    # for now we only need the name of the route-maps, ? is a small hack
    route_map = __salt__["cmd.run"]("show route-map ?", "").split("\n")

    # doing some cleaning
    del route_map[2]
    del route_map[1]
    del route_map[0]
    route_map = [r.strip() for r in route_map]

    return route_map


def _upload_candidate_bgp_config(remote_tmpfile, content):
    __salt__["file.write"](remote_tmpfile, content)


def _clean_candidate_bgp_config(remote_tmpfile):
    __salt__["file.remove"](remote_tmpfile)


def _push_bgp_config(remote_tmpfile):
    # return nothing if done with success
    res = __salt__["cmd.run"]("sudo vtysh --inputfile {}".format(remote_tmpfile))

    if res:
        return res

    __salt__["cmd.run"]("sudo vtysh --writeconfig")
    return ""


def _check_candidate_bgp_config(remote_tmpfile):
    return __salt__["cmd.run"]("sudo vtysh --dryrun --inputfile {}".format(remote_tmpfile))


def bgp_config(template_name, context=None, push_only_if_changes=False, saltenv="base", test=False):
    """Push configuration changes to FRR, and save startup config.

    It does not replace the current configuration, it pushed line by line the config.

    FRR /etc/frr must be a mounted volume to /etc/sonic/frr.

    :param template: Jinja Template to generate the configuration
    :param context: variables to map with the template
    :param push_only_if_changes: push the config only if there are changes detected
    :param saltenv: Salt environment
    :param test: test mode (dry run)

    Important notices:
    - lines pushed are applied line by line, so it can result in mixed up configuration
    if you already have configuration
    - push_only_if_changes parameters only check if there are changes in routing_policy!
    see details in _utils.frr_detect_diff module.

    Output example:

    .. code-block:: python

        {
            "dry_run": False,
            "pushed": "route-map TEST permit 100",
            "changed": True,
        }
    """
    # generate the config
    template_content = __salt__["cp.get_file_str"](template_name, saltenv=saltenv)
    if not template_content:
        raise CommandExecutionError("Unable to get {}".format(template_name))

    rendered = __salt__["file.apply_template_on_contents"](
        contents=template_content,
        template="jinja",
        context=context,
        defaults=None,
        saltenv=saltenv,
    )
    log.debug("configuration to push: %s", rendered)

    # push and merge the config
    now = int(datetime.now().timestamp())
    __salt__["file.mkdir"]("/etc/sonic/tmp/")
    remote_tmpfile = "/etc/sonic/tmp/.{}_bgp.patch".format(now)
    _upload_candidate_bgp_config(remote_tmpfile, rendered)

    out = _check_candidate_bgp_config(remote_tmpfile)

    if __context__["retcode"] != 0:
        raise CommandExecutionError("Invalid BGP configuration: {}".format(out))

    if test:
        changes = None
        result = None
        comment = "- Configuration discarded:\n{}".format(rendered)
    else:
        current = get_bgp_config()

        if push_only_if_changes and not __utils__["frr_detect_diff.is_different"](
            current, rendered
        ):
            changes = None
            result = True
            comment = "- No changes detected in routing_policy:\n{}".format(rendered)
        else:
            out = _push_bgp_config(remote_tmpfile)

            if __context__["retcode"] != 0:
                _clean_candidate_bgp_config(remote_tmpfile)
                # raise CommandExecutionError("Unable to push BGP configuration: {}".format(out))
                comment = "- Unable to push BGP configuration: {}".format(out)
                result = False
            else:
                result = True
                comment = "- Configuration pushed and loaded"

            new_config = get_bgp_config()
            changes = _diff(current, new_config)

    _clean_candidate_bgp_config(remote_tmpfile)

    return {
        "result": result,
        "dry_run": test,
        "changes": changes,
        "comment": comment,
    }


def list_users():
    """Return non-system users.

    CLI example::

    .. code-block:: bash

        salt sonic.tor sonic.list_users

    Output example:

    .. code-block:: python

        [
            "user1",
            "user2"
        ]
    """
    users = __salt__["cmd.run"]("awk -F: '($3>=1000)&&($1!=\"nobody\"){print $1}' /etc/passwd")
    return users.split("\n")


def list_all_users():
    """Return all users including system users.

    CLI example::

    .. code-block:: bash

        salt sonic.tor sonic.list_all_users

    Output example:

    .. code-block:: python

        [
            "admin",
            "nobody",
            "user1",
            "user2",
            ...
        ]
    """
    return __salt__["user.list_users"]()


def _psu_status_legacy():
    """Get PSU information for legacy SONiC."""
    cmd_output = __salt__["cmd.run"]("show platform psustatus")

    parsed_output = re.findall(r"(PSU [0-9]) *([a-zA-Z]+)", cmd_output)
    psu_output = {}
    try:
        for psu_index, _ in enumerate(parsed_output):
            psu_output["Power Supply {} Status".format(psu_index + 1)] = (
                parsed_output[psu_index][1] == "OK"
            )
    except (IndexError, KeyError):
        return None

    return psu_output


def psu_status():
    """Get PSU information."""
    cmd_output = __salt__["cmd.run"]("show platform psustatus --json")

    if __context__["retcode"] != 0:
        return _psu_status_legacy()

    parsed_output = json.loads(cmd_output)
    psu_output = {}
    try:
        for info in parsed_output:
            index = int(info["index"])
            psu_output["Power Supply {} Status".format(index)] = info["status"] == "OK"
    except (IndexError, KeyError):
        return None

    return psu_output


def fan_status():
    """Get FAN information."""
    cmd_output = __salt__["cmd.run"]("show platform fan")

    if not cmd_output:
        return None

    status_index = 0
    fan_index = 0
    lines = cmd_output.split("\n")

    # Find columns of FAN and Status
    if "Status" in lines[0] and "FAN" in lines[0]:
        header = lines[0].split()
        status_index = header.index("Status")
        fan_index = header.index("FAN")
    else:
        return None

    # Extract FAN and Status
    results = {}
    try:
        for line in lines[2:]:
            columns = line.split()
            if columns:
                fan = columns[fan_index]
                results[fan] = columns[status_index] == "OK"
    except (IndexError, KeyError):
        return None

    # Print the results
    return results
