"""Resources for unit tests."""
# noqa E231
# pylint: disable=C0301

native_one_interface = {
    "Ethernet0": {
        "via": "LLDP",
        "rid": "2",
        "age": "27 days, 23:52:38",
        "chassis": {
            "spine1.1.test": {
                "id": {"type": "mac", "value": "00:53:00:01:02:03"},
                "descr": "some OS with version",
                "ttl": "120",
                "mgmt-ip": "192.0.2.83",
                "capability": [
                    {"type": "Bridge", "enabled": True},
                    {"type": "Router", "enabled": True},
                    {"type": "Wlan", "enabled": False},
                    {"type": "Station", "enabled": False},
                ],
            }
        },
        "port": {
            "id": {"type": "local", "value": "Ethernet0"},
            "descr": "superspine1.test:Ethernet0",
        },
    }
}

napalm_one_interface = {
    "out": {
        "Ethernet0": [
            {
                "parent_interface": "Ethernet0",
                "remote_chassis_id": "00:53:00:01:02:03",
                "remote_port": "Ethernet0",
                "remote_port_description": "superspine1.test:Ethernet0",
                "remote_system_capab": ["Bridge", "Router", "Wlan", "Station"],
                "remote_system_description": "some OS with version",
                "remote_system_enable_capab": ["Bridge", "Router"],
                "remote_system_name": "spine1.1.test",
            }
        ]
    }
}


native_interfaces = [
    {
        "eth0": {
            "via": "LLDP",
            "rid": "1",
            "age": "28 days, 23:23:00",
            "chassis": {
                "tor5.0.mgmt": {
                    "id": {"type": "mac", "value": "00:53:00:01:02:03"},
                    "descr": "some OS with version",
                    "ttl": "120",
                    "mgmt-ip": "192.0.2.1",
                    "capability": {"type": "Bridge", "enabled": True},
                }
            },
            "port": {
                "id": {"type": "ifname", "value": "Ethernet32"},
                "descr": "superspine1.test:eth0",
                "mfs": "2044",
                "auto-negotiation": {
                    "supported": True,
                    "enabled": True,
                    "advertised": [
                        {"type": "10Base-T", "hd": False, "fd": True},
                        {"type": "1000Base-X", "hd": True, "fd": True},
                        {"type": "1000Base-T", "hd": True, "fd": False},
                    ],
                    "current": "full duplex mode",
                },
                "power": {
                    "supported": False,
                    "enabled": False,
                    "paircontrol": False,
                    "device-type": "PD",
                    "pairs": "unknown",
                    "class": "unknown",
                },
            },
            "vlan": {"vlan-id": "1234", "pvid": True, "value": "VLAN1234"},
            "ppvid": {"supported": False, "enabled": False},
            "lldp-med": {
                "device-type": "Network Connectivity Device",
                "capability": [
                    {"type": "Capabilities", "available": False},
                    {"type": "Policy", "available": False},
                    {"type": "MDI/PSE", "available": False},
                    {"type": "MDI/PD", "available": False},
                    {"type": "Inventory", "available": False},
                ],
                "policy": {
                    "apptype": "Voice",
                    "defined": False,
                    "vlan": {"vid": "priority"},
                    "priority": "Internetwork control",
                    "pcp": "6",
                    "dscp": "46",
                },
                "poe": {
                    "device-type": "unknown",
                    "source": "unknown",
                    "priority": "unknown",
                    "power": "200",
                },
                "inventory": {
                    "hardware": "some hardware",
                    "software": "some version",
                    "firmware": "",
                    "serial": "",
                    "manufacturer": "some manufacturer",
                    "model": "",
                    "asset": "",
                },
            },
        }
    },
    {
        "Ethernet124": {
            "via": "LLDP",
            "rid": "13",
            "age": "28 days, 23:13:21",
            "chassis": {
                "spine1.test": {
                    "id": {"type": "mac", "value": "00:53:00:01:02:03"},
                    "descr": "some OS with version",
                    "ttl": "120",
                    "mgmt-ip": "192.0.2.45",
                    "capability": [
                        {"type": "Bridge", "enabled": True},
                        {"type": "Router", "enabled": True},
                    ],
                }
            },
            "port": {
                "id": {"type": "ifname", "value": "Ethernet1/1"},
                "descr": "superspine1.test:Ethernet124",
                "mfs": "9236",
            },
        }
    },
]

napalm_interfaces = {
    "out": {
        "eth0": [
            {
                "parent_interface": "eth0",
                "remote_chassis_id": "00:53:00:01:02:03",
                "remote_port": "Ethernet32",
                "remote_port_description": "superspine1.test:eth0",
                "remote_system_capab": ["Bridge"],
                "remote_system_description": "some OS with version",
                "remote_system_enable_capab": ["Bridge"],
                "remote_system_name": "tor5.0.mgmt",
            }
        ],
        "Ethernet124": [
            {
                "parent_interface": "Ethernet124",
                "remote_chassis_id": "00:53:00:01:02:03",
                "remote_port": "Ethernet1/1",
                "remote_port_description": "superspine1.test:Ethernet124",
                "remote_system_capab": ["Bridge", "Router"],
                "remote_system_description": "some OS with version",
                "remote_system_enable_capab": ["Bridge", "Router"],
                "remote_system_name": "spine1.test",
            }
        ],
    }
}


native_configured_server = [
    {
        "Ethernet16": {
            "via": "LLDP",
            "rid": "1",
            "age": "33 days, 21:52:50",
            "chassis": {
                "id": {"type": "local", "value": "1234"},
                "descr": "somedescription",
                "ttl": "100",
                "mgmt-ip": "192.0.2.1",
            },
            "port": {
                "id": {"type": "mac", "value": "00:53:00:01:02:03"},
                "descr": "somedescription",
            },
        }
    },
    {
        "Ethernet16": {
            "via": "LLDP",
            "rid": "1",
            "age": "0 day, 02:39:50",
            "chassis": {
                "serverhostname1": {
                    "id": {"type": "mac", "value": "00:53:00:01:02:03"},
                    "descr": "somedescription",
                    "ttl": "120",
                    "mgmt-ip": ["192.0.2.1", "2001:db8::aeb8"],
                    "capability": [
                        {"type": "Bridge", "enabled": False},
                        {"type": "Router", "enabled": False},
                        {"type": "Wlan", "enabled": False},
                        {"type": "Station", "enabled": True},
                    ],
                }
            },
            "port": {
                "id": {"type": "mac", "value": "00:53:00:01:02:03"},
                "descr": "someotherdescription",
                "auto-negotiation": {
                    "supported": True,
                    "enabled": True,
                    "advertised": {"type": "1000Base-X", "hd": False, "fd": True},
                    "current": "unknown",
                },
            },
        }
    },
]

napalm_configured_server = {
    "out": {
        "Ethernet16": [
            {
                "parent_interface": "Ethernet16",
                "remote_chassis_id": "00:53:00:01:02:03",
                "remote_port": "00:53:00:01:02:03",
                "remote_port_description": "someotherdescription",
                "remote_system_capab": ["Bridge", "Router", "Wlan", "Station"],
                "remote_system_description": "somedescription",
                "remote_system_enable_capab": ["Station"],
                "remote_system_name": "serverhostname1",
            }
        ]
    }
}

native_unconfigured_server = {
    "Ethernet96": {
        "via": "LLDP",
        "rid": "8",
        "age": "57 days, 01:55:46",
        "chassis": {
            "spine4.9.test": {
                "id": {"type": "mac", "value": "00:53:00:01:02:03"},
                "descr": "some OS with version.",
                "ttl": "120",
                "mgmt-ip": "192.0.2.1",
                "capability": [
                    {"type": "Bridge", "enabled": True},
                    {"type": "Router", "enabled": True},
                ],
            }
        },
        "port": {
            "id": {"type": "ifname", "value": "et-0/0/11"},
            "descr": "tor8.9.test:Ethernet96",
            "mfs": "9114",
        },
        "lldp-med": {
            "device-type": "Network Connectivity Device",
            "capability": [
                {"type": "Capabilities", "available": True},
                {"type": "Policy", "available": True},
                {"type": "Location", "available": True},
                {"type": "MDI/PSE", "available": True},
            ],
        },
        "unknown-tlvs": {
            "unknown-tlv": {
                "oui": "00,90,69",
                "subtype": "1",
                "len": "12",
                "value": "57,48,30,32,31,38,35,31,30,32,34,36",
            }
        },
    }
}

napalm_unconfigured_server = {
    "out": {
        "Ethernet96": [
            {
                "parent_interface": "Ethernet96",
                "remote_chassis_id": "00:53:00:01:02:03",
                "remote_port": "et-0/0/11",
                "remote_port_description": "tor8.9.test:Ethernet96",
                "remote_system_capab": ["Bridge", "Router"],
                "remote_system_description": "some OS with version.",
                "remote_system_enable_capab": ["Bridge", "Router"],
                "remote_system_name": "spine4.9.test",
            }
        ]
    }
}
