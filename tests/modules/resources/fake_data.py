"""Resources for unit tests."""
interfaces = {
    "Ethernet0": {
        "hwaddr": "00:53:00:01:02:03",
        "inet": [
            {
                "netmask": "255.255.255.254",
                "address": "198.51.100.65",
                "label": "Ethernet0",
                "broadcast": None,
            }
        ],
        "up": True,
    },
    "Ethernet16": {
        "hwaddr": "00:53:00:01:02:03",
        "inet6": [
            {"prefixlen": "127", "scope": "global", "address": "2001:db8:1234:4567:abc:0:1:101"},
            {"prefixlen": "64", "scope": "link", "address": "2001:db8::d6dc"},
        ],
        "up": True,
    },
    "Ethernet36": {
        "hwaddr": "00:53:00:01:02:03",
        "inet": [
            {
                "netmask": "255.255.255.254",
                "address": "192.0.2.129",
                "label": "Ethernet36",
                "broadcast": None,
            }
        ],
        "inet6": [
            {"prefixlen": "127", "scope": "global", "address": "2001:db8:1234:5654:1234:0:1:101"},
            {"prefixlen": "64", "scope": "link", "address": "2001:db8::d6dc"},
        ],
        "up": True,
    },
}
