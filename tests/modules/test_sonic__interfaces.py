"""Unit tests for sonic interface functions."""
from tests.modules.resources.fake_data import interfaces

from _modules.sonic import get_ip_addresses


def test_get_ip_addresses__no_interfaces(mocker):
    """Test when no interfaces found (unsupported device for example)."""
    mocker.patch("_modules.sonic._get_interfaces_brief", return_value=None)
    assert get_ip_addresses("Unknown") == {}


def test_get_ip_addresses__no_matching_interfaces(mocker):
    """Test when no interfaces matches."""
    mocker.patch("_modules.sonic._get_interfaces_brief", return_value=interfaces)
    assert get_ip_addresses("Unknown") == {}


def test_get_ip_addresses__ipv4_only(mocker):
    """Test when ipv4 only."""
    mocker.patch("_modules.sonic._get_interfaces_brief", return_value=interfaces)
    assert get_ip_addresses("Ethernet0") == {"ipv4": ["198.51.100.65/31"]}


def test_get_ip_addresses__ipv6_only(mocker):
    """Test when ipv6 only."""
    mocker.patch("_modules.sonic._get_interfaces_brief", return_value=interfaces)
    assert get_ip_addresses("Ethernet16") == {
        "ipv6": ["2001:db8:1234:4567:abc:0:1:101/127", "2001:db8::d6dc/64"]
    }


def test_get_ip_addresses__both_stack(mocker):
    """Test when both ipv4 and ipv6 are available."""
    mocker.patch("_modules.sonic._get_interfaces_brief", return_value=interfaces)
    assert get_ip_addresses("Ethernet36") == {
        "ipv4": ["192.0.2.129/31"],
        "ipv6": ["2001:db8:1234:5654:1234:0:1:101/127", "2001:db8::d6dc/64"],
    }
