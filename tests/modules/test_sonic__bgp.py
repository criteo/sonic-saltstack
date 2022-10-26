"""Unit tests for sonic bgp functions."""
import json

import pytest

from salt import exceptions

from _modules.sonic import _extract_bgp_neighbor_info, get_bgp_neighbors

RES_DIR = "tests/modules/resources"


def test__extract_bgp_neighbor_info__frr_7_0():
    """Test _extract_bgp_neighbor for FRR 7.0."""
    with open(f"{RES_DIR}/bgp_neighbor_frr_7.0.json") as resource:
        fake_neighbor = resource.read()

    neighbors = json.loads(fake_neighbor)
    ip = "198.51.100.0"

    assert _extract_bgp_neighbor_info(ip, neighbors[ip]) == {
        "remote_as": 65500,
        "local_as": 65000,
        "remote_address": "198.51.100.0",
        "peer_group": "PEER-GROUP-SPINE",
        "import_policy": "FABRIC-IN",
        "export_policy": "FABRIC-OUT",
        "description": "PEER-GROUP-SPINE:spine1.test",
        "state": "up",
        "vrf": "default",
    }


def test__extract_bgp_neighbor_info__frr_7_2():
    """Test _extract_bgp_neighbor for FRR 7.2."""
    with open(f"{RES_DIR}/bgp_neighbor_frr_7.2.json") as resource:
        fake_neighbor = resource.read()

    neighbors = json.loads(fake_neighbor)
    ip = "203.0.113.9"

    assert _extract_bgp_neighbor_info(ip, neighbors[ip]) == {
        "remote_as": 65509,
        "local_as": 65197,
        "remote_address": "203.0.113.9",
        "peer_group": "PEER-GROUP-SPINE",
        "import_policy": "FABRIC-IN",
        "export_policy": "FABRIC-OUT",
        "description": "PEER-GROUP-SPINE:spine9.test",
        "state": "up",
        "vrf": "default",
    }


def test__extract_bgp_neighbor_info__family_not_found():
    """Test _extract_bgp_neighbor when no family found."""
    with open(f"{RES_DIR}/bgp_neighbor_frr_7.2.json") as resource:
        fake_neighbor = resource.read()

    neighbors = json.loads(fake_neighbor)
    ip = "203.0.113.9"
    neighbors[ip]["addressFamilyInfo"].pop("ipv4Unicast")

    assert _extract_bgp_neighbor_info(ip, neighbors[ip]) == {
        "remote_as": 65509,
        "local_as": 65197,
        "remote_address": "203.0.113.9",
        "peer_group": "PEER-GROUP-SPINE",
        "import_policy": None,
        "export_policy": None,
        "description": "PEER-GROUP-SPINE:spine9.test",
        "state": "up",
        "vrf": "default",
    }



def test_get_bgp_neighbors__present(mocker):
    """Test get_bgp_neighbors when present."""
    with open(f"{RES_DIR}/bgp_neighbor_frr_7.0.json") as resource:
        fake_neighbor = resource.read()

    mocker.patch("_modules.sonic._get_bgp_neighbor", return_value=fake_neighbor)

    assert get_bgp_neighbors("198.51.100.0") == {
        "198.51.100.0": {
            "remote_as": 65500,
            "local_as": 65000,
            "remote_address": "198.51.100.0",
            "peer_group": "PEER-GROUP-SPINE",
            "import_policy": "FABRIC-IN",
            "export_policy": "FABRIC-OUT",
            "description": "PEER-GROUP-SPINE:spine1.test",
            "state": "up",
            "vrf": "default",
        }
    }


def test_get_bgp_neighbors__present__frr_output(mocker):
    """Test get_bgp_neighbors when present with FRR output."""
    with open(f"{RES_DIR}/bgp_neighbor_frr_7.0.json") as resource:
        fake_neighbor = resource.read()
    bgp_info = json.loads(fake_neighbor)

    mocker.patch("_modules.sonic._get_bgp_neighbor", return_value=fake_neighbor)

    assert get_bgp_neighbors("198.51.100.0", frr_output=True) == bgp_info


def test_get_bgp_neighbors__present__empty(mocker):
    """Test get_bgp_neighbors when empty data."""
    mocker.patch("_modules.sonic._get_bgp_neighbor", return_value="{}")

    assert get_bgp_neighbors("198.51.100.0") == {}


def test_get_bgp_neighbors__present__not_found(mocker):
    """Test get_bgp_neighbors when neighbor not found."""
    mocker.patch(
        "_modules.sonic._get_bgp_neighbor", return_value='{"bgpNoSuchNeighbor":true}'
    )

    with pytest.raises(exceptions.CommandExecutionError):
        get_bgp_neighbors("198.51.100.0")
